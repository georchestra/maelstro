from contextlib import contextmanager
import inspect
import json
from typing import Any
from geonetwork import GnApi
from geoservercloud.services import RestService
from requests.exceptions import HTTPError
from maelstro.config import ConfigError, app_config as config
from geoservercloud.services.restclient import RestClient
from .operations import ResponseHandler, LoggedRequests, add_gn_handling, add_gs_handling, gs_logger
from .exceptions import ParamError, MaelstroDetail, AuthError


WRAPPERS = {
    "GnApiWrapper": add_gn_handling,
    "GsClientWrapper": add_gs_handling
}


class MethodWrapper:
    def __init__(self, response_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_handler = response_handler

    def __init_subclass__(cls, **kwargs):
        super.__init_subclass__(**kwargs)
        for k, v in inspect.getmembers(cls, inspect.isfunction):
            setattr(cls, k, WRAPPERS[cls.__name__](v))


class GnApiWrapper(GnApi, MethodWrapper):
    def __init__(self, response_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_handler = response_handler


class GsClientWrapper(RestClient, MethodWrapper):
    pass


class GsRestWrapper(RestService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self, "rest_client", GsClientWrapper(self.rest_client.url, self.rest_client.auth))


class GeorchestraHandler:
    def __init__(self, response_handler: ResponseHandler):
        self.response_handler = response_handler

    def get_gn_service(self, instance_name: str, is_source: bool) -> GnApiWrapper:
        gn_info = self.get_service_info(instance_name, is_source, True)
        return GnApiWrapper(self.response_handler, gn_info["url"], gn_info["auth"])

    def get_gs_service(self, instance_name: str, is_source: bool) -> GsRestWrapper:
        gs_info = self.get_service_info(instance_name, is_source, False)
        gsapi = GsRestWrapper(gs_info["url"], gs_info["auth"])
        try:
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

    def get_service_info(self, url: str, is_source: bool, is_geonetwork: bool) -> dict[str, Any]:
        try:
            service_info = config.get_access_info(
                is_src=is_source, is_geonetwork=is_geonetwork, instance_id=url
            )
        except ConfigError as err:
            gs_logger.debug(
                "Key not found: %s\n Config:\n%s", url, json.dumps(config.config, indent=4)
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
def get_georchestra_handler() -> GeorchestraHandler:
    with LoggedRequests() as response_handler:
        yield GeorchestraHandler(response_handler)
