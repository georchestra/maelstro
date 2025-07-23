import logging
from functools import cache
from io import BytesIO
from typing import Any
from geonetwork import GnApi
from geoservercloud.services import RestService  # type: ignore
from geoservercloud import GeoServerCloudSync  # type: ignore
from geoservercloud.exceptions import DatastoreMissing, WorkspaceMissing  # type: ignore
from maelstro.metadata import Meta
from maelstro.config import app_config as config
from maelstro.common.types import GsLayer
from maelstro.common.models import CopyPreview, InfoRecord, SuccessRecord
from maelstro.common.exceptions import ParamError
from .georchestra import GeorchestraHandler


logger = logging.getLogger()


class CopyManager:
    def __init__(
        self, src_name: str, dst_name: str, uuid: str, geo_hnd: GeorchestraHandler
    ):
        self.src_name = src_name
        self.dst_name = dst_name
        self.uuid = uuid
        self.include_meta = False
        self.include_layers = False
        self.include_styles = False
        self.meta: Meta
        self.geo_hnd: GeorchestraHandler = geo_hnd
        self.checked_workspaces: set[str] = set()
        self.checked_datastores: set[str] = set()

    @property
    @cache  # pylint: disable=method-cache-max-size-none
    def gn_src(self) -> GnApi:
        return self.geo_hnd.get_gn_service(self.src_name, is_source=True)

    @property
    @cache  # pylint: disable=method-cache-max-size-none
    def gn_dst(self) -> GnApi:
        return self.geo_hnd.get_gn_service(self.dst_name, is_source=False)

    # gs_src cannot be a fixed property since there may be several source Geoservers

    @property
    @cache  # pylint: disable=method-cache-max-size-none
    def gs_dst(self) -> RestService:
        return self.geo_hnd.get_gs_service(self.dst_name, is_source=False)

    def copy_preview(
        self,
        include_meta: bool,
        include_layers: bool,
        include_styles: bool,
    ) -> CopyPreview:
        self.include_meta = include_meta
        self.include_layers = include_layers
        self.include_styles = include_styles

        zipdata = self.gn_src.get_record_zip(self.uuid).read()
        self.meta = Meta(zipdata)

        preview: dict[str, list[dict[str, Any]]] = {
            "geonetwork_resources": [],
            "geoserver_resources": [],
        }

        preview["geonetwork_resources"].append(
            {
                "src": self.src_name,
                "dst": self.dst_name,
                "metadata": (
                    [
                        {
                            "title": self.meta.get_title(),
                            "iso_standard": self.meta.schema,
                        }
                    ]
                    if self.include_meta
                    else []
                ),
            }
        )

        dst_gs_info = self.geo_hnd.get_service_info(
            self.dst_name, is_source=False, is_geonetwork=False
        )
        dst_gs_url = dst_gs_info["url"]

        if self.include_layers or self.include_styles:
            geoservers = self.meta.get_gs_layers(config.get_gs_sources())
            for server_url, layer_names in geoservers.items():
                styles: set[str] = set()
                layers: set[str] = set()
                gs_src = self.geo_hnd.get_gs_service(server_url, True)
                for layer_name in layer_names:
                    layer, status = gs_src.get_layer(None, layer_name)

                    if status == 200:
                        layers.add(str(layer_name))
                        styles.update(layer.all_style_names)

                if layers or styles:
                    # only output servers where some layers or styles have been identified
                    preview["geoserver_resources"].append(
                        {
                            "src": server_url,
                            "dst": dst_gs_url,
                            "layers": list(layers) if self.include_layers else [],
                            "styles": list(styles) if self.include_styles else [],
                        }
                    )

        return CopyPreview(**preview)  # type: ignore

    def copy_dataset(
        self,
        include_meta: bool,
        include_layers: bool,
        include_styles: bool,
    ) -> str:
        self.include_meta = include_meta
        self.include_layers = include_layers
        self.include_styles = include_styles

        if self.uuid:
            zipdata = self.gn_src.get_record_zip(self.uuid).read()
            self.meta = Meta(zipdata)
            self.geo_hnd.log_handler.set_property("src_title", self.meta.get_title())

        if self.meta is None:
            return []

        if self.include_layers or self.include_styles:
            server_layers = self.meta.get_gs_layers(config.get_gs_sources())
            for gs_url, layer_names in server_layers.items():
                if not layer_names:
                    continue
                sync_service = self.geo_hnd.get_gs_sync_service(gs_url, self.dst_name)

                # styles must be copied first
                if self.include_styles:
                    self.copy_styles(sync_service, layer_names)
                if self.include_layers:
                    self.copy_layers(sync_service, layer_names)

        if self.include_meta:
            xsl_transformations = config.get_transformation_pair(
                self.src_name, self.dst_name
            )
            if xsl_transformations:
                transformation_paths = [
                    trans["xsl_path"] for trans in xsl_transformations
                ]

                pre_info, post_info = self.meta.apply_xslt_chain(transformation_paths)
                self.geo_hnd.log_handler.log_info(
                    InfoRecord(
                        message="Apply XSL transformations in zip archive",
                        detail={
                            "transformations": xsl_transformations,
                            "before": pre_info,
                            "after": post_info,
                        },
                    )
                )
            self.geo_hnd.log_handler.set_property("dst_title", self.meta.get_title())

            with self.geo_hnd.log_handler.logger_context("Meta"):
                results = self.gn_dst.put_record_zip(BytesIO(self.meta.get_zip()))
                self.geo_hnd.log_handler.log_info(
                    SuccessRecord(
                        message=results["msg"],
                        detail={"info": results["detail"]},
                    )
                )
            return str(results["msg"])
        return "copy_successful"

    def copy_styles(
        self, sync_service: GeoServerCloudSync, layer_names: set[GsLayer]
    ) -> None:
        # styles must be copied first
        styles = set(
            style_name
            for l in layer_names
            for layer, status in [sync_service.src_instance.get_layer(None, l)]
            for style_name in layer.all_style_names
            if status == 200
        )
        with self.geo_hnd.log_handler.logger_context("Style"):
            for style in styles:
                try:
                    _, status = sync_service.copy_style(style)
                    if status != 200:
                        raise ParamError
                except (DatastoreMissing, WorkspaceMissing) as err:
                    raise ParamError(
                        context="dst",
                        key=f"Style {style}",
                        err=f"{err.detail.message} on destination Geoserver {self.dst_name}",
                        operations=self.geo_hnd.log_handler.get_json_responses(),
                    ) from err
            self.geo_hnd.log_handler.log_info(
                SuccessRecord(
                    message="Styles copied successfully",
                    detail={"styles": list(styles)},
                )
            )

    def copy_layers(
        self, sync_service: GeoServerCloudSync, layer_names: set[GsLayer]
    ) -> None:
        # styles must be available when cloning layers
        with self.geo_hnd.log_handler.logger_context("Layer"):
            for layer_name in layer_names:
                try:
                    _, status = sync_service.copy_layer(None, layer_name)
                    if status != 200:
                        raise ParamError
                except (DatastoreMissing, WorkspaceMissing) as err:
                    raise ParamError(
                        context="dst",
                        key=f"Layer {layer_name}",
                        err=f"{err.detail.message} on destination Geoserver {self.dst_name}",
                        operations=self.geo_hnd.log_handler.get_json_responses(),
                    ) from err
            self.geo_hnd.log_handler.log_info(
                SuccessRecord(
                    message="Layers copied successfully",
                    detail={"layers": list(layer_names)},
                )
            )
