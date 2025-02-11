from contextlib import contextmanager
from datetime import datetime
import json
from typing import Any, Iterator
from geonetwork import GnApi
from geoservercloud.services import RestService  # type: ignore
from requests.exceptions import HTTPError
from maelstro.config import ConfigError, app_config as config
from .operations import (
    log_handler,
    gs_logger,
)
from .exceptions import ParamError, MaelstroDetail, AuthError


class GeorchestraHandler:
    def __init__(self) -> None:
        self.log_handler = log_handler

    def get_gn_service(self, instance_name: str, is_source: bool) -> GnApi:
        if not self.log_handler.valid:
            raise RuntimeError(
                "GeorchestraHandler context invalid, handler already close"
            )
        gn_info = self.get_service_info(instance_name, is_source, True)
        return GnApi(gn_info["url"], gn_info["auth"])

    def get_gs_service(self, instance_name: str, is_source: bool) -> RestService:
        if not self.log_handler.valid:
            raise RuntimeError(
                "GeorchestraHandler context invalid, handler already close"
            )
        gs_info = self.get_service_info(instance_name, is_source, False)
        gsapi = RestService(gs_info["url"], gs_info["auth"])
        try:
            import geoservercloud.services.restclient  # type: ignore

            geoservercloud.services.restclient.TIMEOUT = 15
            resp = gsapi.rest_client.get("/rest/about/version.json")
        except HTTPError as err:
            if err.response.status_code == 401:
                raise AuthError(
                    MaelstroDetail(
                        server=gs_info["url"],
                        user=gs_info["auth"] and gs_info["auth"].login,
                        err="Invalid credentials",
                    )
                ) from err
        gs_logger.info(
            "Session opened on %s at %s",
            (
                resp.json()["about"]["resource"][0]["@name"],
                resp.json()["about"]["resource"][0]["Version"],
            ),
            gs_info["url"],
        )
        return gsapi

    def get_service_info(
        self, url: str, is_source: bool, is_geonetwork: bool
    ) -> dict[str, Any]:
        try:
            service_info = config.get_access_info(
                is_src=is_source, is_geonetwork=is_geonetwork, instance_id=url
            )
        except ConfigError as err:
            gs_logger.debug(
                "Key not found: %s\n Config:\n%s",
                url,
                json.dumps(config.config, indent=4),
            )
            raise ParamError(
                MaelstroDetail(
                    context="src" if is_source else "dst",
                    key=url,
                    err=f"{'geonetwork' if is_geonetwork else 'geoserver'} not found in config",
                )
            ) from err
        return service_info


@contextmanager
def get_georchestra_handler() -> Iterator[GeorchestraHandler]:
    log_handler.responses.clear()
    log_handler.properties["start_time"] = datetime.now()
    log_handler.valid = True
    yield GeorchestraHandler()
    log_handler.valid = False
