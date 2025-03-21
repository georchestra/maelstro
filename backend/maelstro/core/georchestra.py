from contextlib import contextmanager
import json
from typing import Any, Iterator
from geonetwork import GnApi
from geonetwork.gn_logger import logger as gn_logger
from geoservercloud.services import RestService  # type: ignore
from requests.exceptions import HTTPError
from geoservercloud.services.restlogger import gs_logger as gs_logger  # type: ignore
from maelstro.config import ConfigError, app_config as config
from .operations import LogCollectionHandler
from maelstro.common.exceptions import ParamError, AuthError


class GeorchestraHandler:
    def __init__(self, log_handler: LogCollectionHandler) -> None:
        self.log_handler = log_handler

    def get_gn_service(self, instance_name: str, is_source: bool) -> GnApi:
        gn_info = self.get_service_info(instance_name, is_source, True)
        return GnApi(gn_info["url"], gn_info["auth"], gn_info["verifytls"])

    def get_gs_service(self, instance_name: str, is_source: bool) -> RestService:
        gs_info = self.get_service_info(instance_name, is_source, False)
        gsapi = RestService(gs_info["url"], gs_info["auth"])
        try:
            import geoservercloud.services.restclient  # type: ignore

            geoservercloud.services.restclient.TIMEOUT = 15
            resp = gsapi.rest_client.get("/rest/about/version.json")
        except HTTPError as err:
            if err.response.status_code == 401:
                raise AuthError(
                    server=gs_info["url"],
                    user=gs_info["auth"] and gs_info["auth"].login,
                    err="Invalid credentials",
                ) from err
            raise err
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
                context="src" if is_source else "dst",
                key=url,
                err=f"{'geonetwork' if is_geonetwork else 'geoserver'} not found in config",
            ) from err
        return service_info


@contextmanager
def get_georchestra_handler() -> Iterator[GeorchestraHandler]:
    log_handler = LogCollectionHandler()
    gn_logger.addHandler(log_handler)
    gs_logger.addHandler(log_handler)
    yield GeorchestraHandler(log_handler)
    gn_logger.removeHandler(log_handler)
    gs_logger.removeHandler(log_handler)
