from collections.abc import Iterator
from typing import Any

import requests

from maelstro.common.models import (
    ApiRecord,
    DatafeederPreview,
    InfoRecord,
    SuccessRecord,
)
from maelstro.common.exceptions import ParamError
from maelstro.config import app_config as config
from .operations import LogCollectionHandler, raise_for_status

ADMIN_PATH = "internal/ingestion/integrity-link"
LINK_ONLY_IMPORT_TYPES = {"empty", "prefilled"}
UPLOAD_TIMEOUT = (30, 3600)


class DatafeederClient:
    def __init__(self, info: dict[str, Any], log_handler: LogCollectionHandler):
        self.base_url = info["url"]
        self.verify = info["verifytls"]
        self.session = requests.Session()
        self.session.auth = info["auth"]
        self.log_handler = log_handler

    def request(
        self, method: str, path: str, allow_not_found: bool = False, **kwargs: Any
    ) -> requests.Response:
        kwargs.setdefault("timeout", 120)
        response = self.session.request(
            method,
            f"{self.base_url}/{path}",
            allow_redirects=False,
            verify=self.verify,
            **kwargs,
        )
        self.log_handler.responses.append(
            ApiRecord(
                method=method,
                status_code=response.status_code,
                url=response.url,
                data_type="Datafeeder",
            )
        )
        if allow_not_found and response.status_code == 404:
            return response
        raise_for_status(response)
        return response

    def json(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.request(method, path, **kwargs).json()


class DatafeederManager:
    def __init__(self, src_name: str, dst_name: str, log_handler: LogCollectionHandler):
        self.log_handler = log_handler
        src_info = config.get_datafeeder_access_info(True, src_name)
        dst_info = config.get_datafeeder_access_info(False, dst_name)
        self.configured = bool(src_info and dst_info)
        self.source = DatafeederClient(src_info, log_handler) if src_info else None
        self.target = DatafeederClient(dst_info, log_handler) if dst_info else None

    def preview(
        self, metadata_uuid: str
    ) -> tuple[DatafeederPreview, dict[str, Any] | None]:
        if not self.configured:
            return DatafeederPreview(configured=False), None
        assert self.source and self.target
        with self.log_handler.logger_context("Datafeeder"):
            response = self.source.request(
                "GET",
                f"{ADMIN_PATH}/by-metadata/{metadata_uuid}",
                allow_not_found=True,
            )
            if response.status_code == 404:
                self.log_handler.log_info(
                    InfoRecord(
                        message="Dataset not found in source Datafeeder", detail={}
                    )
                )
                return (
                    DatafeederPreview(
                        configured=True, found=False, action="no_dataset"
                    ),
                    None,
                )
            link = response.json()
            exported = self.source.json("GET", f"{ADMIN_PATH}/{link['id']}/export")
            import_type = exported["source_import_type"]
            table = exported.get("final_table_name")
            preview = DatafeederPreview(
                configured=True,
                found=True,
                integrity_link_id=str(link["id"]),
                import_type=import_type,
                table_name=table,
            )
            if import_type in LINK_ONLY_IMPORT_TYPES or not table:
                preview.action = "no_table"
                return preview, exported
            target_link = self.target.request(
                "GET",
                f"{ADMIN_PATH}/by-metadata/{metadata_uuid}",
                allow_not_found=True,
            )
            if target_link.status_code != 404:
                preview.action = "already_imported"
                return preview, exported
            status = self.target.json(
                "GET",
                f"{ADMIN_PATH}/data/{exported['integrity_organization']}/{table}",
            )
            preview.table_exists = status["exists"]
            preview.used_by = str(status["used_by"]) if status["used_by"] else None
            preview.action = (
                "conflict"
                if status["used_by"]
                else "reuse_table" if status["exists"] else "copy_table"
            )
            return preview, exported

    def copy(self, metadata_uuid: str) -> str:
        preview, exported = self.preview(metadata_uuid)
        if not preview.configured:
            raise ParamError(
                err="Datafeeder is not configured for source and destination"
            )
        if not preview.found or exported is None:
            raise ParamError(err="Dataset not found in source Datafeeder")
        if preview.action == "conflict":
            raise ParamError(err=f"Target table is used by dataset {preview.used_by}")
        assert self.source and self.target
        with self.log_handler.logger_context("Datafeeder"):
            if preview.action == "already_imported":
                self.log_handler.log_info(
                    SuccessRecord(
                        message="Reused existing Datafeeder dataset", detail={}
                    )
                )
                return "Datafeeder dataset already imported"
            if preview.action == "copy_table":
                path = (
                    f"{ADMIN_PATH}/data/{exported['integrity_organization']}"
                    f"/{exported['final_table_name']}"
                )
                with self.source.request(
                    "GET", f"{ADMIN_PATH}/{preview.integrity_link_id}/data", stream=True
                ) as download:
                    chunks: Iterator[bytes] = download.iter_content(1024 * 1024)
                    result = self.target.json(
                        "PUT", path, data=chunks, timeout=UPLOAD_TIMEOUT
                    )
                self.log_handler.log_info(
                    SuccessRecord(
                        message=f"Copied {result['row_count']} Datafeeder rows",
                        detail=result,
                    )
                )
            elif preview.action == "reuse_table":
                self.log_handler.log_info(
                    SuccessRecord(message="Reused existing target table", detail={})
                )
            result = self.target.json(
                "POST",
                f"{ADMIN_PATH}/import",
                json={"link": exported, "copy_recurrence": True},
                timeout=UPLOAD_TIMEOUT,
            )
            self.log_handler.log_info(
                SuccessRecord(message="Imported Datafeeder dataset", detail=result)
            )
            return f"Datafeeder dataset imported ({result['integrity_link_id']})"
