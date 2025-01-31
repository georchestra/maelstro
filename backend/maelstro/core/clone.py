import re
import logging
import json
from io import BytesIO
from typing import Any
from requests.exceptions import HTTPError
from fastapi import HTTPException
from geonetwork import GnApi
from geonetwork.exceptions import ParameterException
from geoservercloud.services import RestService as GeoServerService  # type: ignore
from maelstro.metadata import Meta
from maelstro.config import ConfigError, app_config as config
from maelstro.common.types import GsLayer
from .operations import OpLogger, GsOpService


logger = logging.getLogger()


class MaelstroException(HTTPException):
    def __init__(self, err_dict: dict[str, str]):
        if not isinstance(err_dict, dict):
            err_dict = {"data": err_dict}
        super().__init__(int(err_dict.get("status_code", "500")), err_dict)


class AuthError(MaelstroException):
    def __init__(self, err_dict: dict[str, str]):
        # status 501 instead of 401 because repsone truncated by gateway
        super().__init__({**err_dict, "status_code": "501"})


class UrlError(MaelstroException):
    def __init__(self, err_dict: dict[str, str]):
        super().__init__({**err_dict, "status_code": "404"})


class ParamError(MaelstroException):
    def __init__(self, err_dict: dict[str, str]):
        super().__init__({**err_dict, "status_code": "406"})


# TODO: handle requests.exceptions.ConnectTimeout errorxception
class TimeoutError(MaelstroException):
    def __init__(self, err_dict: dict[str, str]):
        super().__init__({**err_dict, "status_code": "406"})


class CloneDataset:
    def __init__(self, src_name: str, dst_name: str, uuid: str, dry: bool = False):
        self.op_logger = OpLogger()
        self.src_name = src_name
        self.dst_name = dst_name
        self.uuid = uuid
        self.copy_meta = False
        self.copy_layers = False
        self.copy_styles = False
        self.dry = dry

    def set_uuid(self, uuid: str) -> None:
        self.uuid = uuid

    def clone_dataset(
        self,
        copy_meta: bool,
        copy_layers: bool,
        copy_styles: bool,
        output_format: str = "text/plain",
    ) -> str | list[Any]:
        self.copy_meta = copy_meta
        self.copy_layers = copy_layers
        self.copy_styles = copy_styles

        try:
            if self.uuid:
                gn = get_gn_service(self.src_name, True, self.op_logger)
                zipdata = gn.get_record_zip(self.uuid).read()
                self.meta = Meta(zipdata)

            if self.meta is None:
                return []

            if copy_layers or copy_styles:
                self.clone_layers()

            if copy_meta:
                gn_dst = get_gn_service(self.dst_name, False, self.op_logger)
                mapping: dict[str, list[str]] = {
                    "sources": config.get_gs_sources(),
                    "destinations": [
                        src["gs_url"] for src in config.get_destinations()
                    ],
                }
                pre_info, post_info = self.meta.update_geoverver_urls(mapping)
                self.op_logger.log_operation(
                    "Update of geoserver links in zip archive",
                    str({"before": pre_info, "after": post_info}),
                    "GnApi",
                    "clone",
                )
                try:
                    results = gn_dst.put_record_zip(BytesIO(self.meta.get_zip()))
                except ParameterException as err:
                    self.op_logger.log_operation(
                        "Record creation failed ({err.args[0]['code']})",
                        err.args[0]["details"],
                        "GnApi",
                        "clone",
                    )
                    raise HTTPException(406, self.op_logger.get_operations()) from err
                self.op_logger.log_operation(
                    results["msg"],
                    results["detail"],
                    "GnApi",
                    "clone",
                )
        except HTTPError as err:
            self.op_logger.log_operation(
                "Failed",
                err.response.url,
                "requests",
                "clone",
            )
            status_code = err.response.status_code
            if status_code in [401, 403, 404]:
                # prevent output truncation by gateway
                status_code += 100
            raise HTTPException(status_code, self.op_logger.get_operations()) from err
        except ParameterException as err:
            self.op_logger.log_operation(
                err.args[0]["msg"],
                err.args[0]["code"],
                "GnApi",
                "clone",
            )
            raise HTTPException(406, self.op_logger.get_operations()) from err

        if output_format == "text/plain":
            return self.op_logger.format_operations()
        return self.op_logger.get_operations()

    def clone_layers(self) -> None:
        server_layers = self.meta.get_gs_layers(config.get_gs_sources())

        gs_dst = get_gs_service(self.dst_name, False, self.op_logger)
        for gs_url, layer_names in server_layers.items():
            if layer_names:
                gs_src = get_gs_service(gs_url, True, self.op_logger)
                for layer_name in layer_names:
                    resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                    resp.raise_for_status()
                    layer_data = resp.json()

                    # styles must be cloned first
                    if self.copy_styles:
                        self.clone_styles(gs_src, gs_dst, layer_data)

                    # styles must be available when cloning layers
                    if self.copy_layers:
                        self.clone_layer(gs_src, gs_dst, layer_name, layer_data)

    def clone_layer(
        self,
        gs_src: GsOpService,
        gs_dst: GsOpService,
        layer_name: GsLayer,
        layer_data: dict[str, Any],
    ) -> None:
        resource_url = layer_data["layer"]["resource"]["href"].replace(gs_src.url, "")
        layer_string = json.dumps(layer_data)
        layer_data = json.loads(layer_string.replace(gs_src.url, gs_dst.url))

        has_resource = gs_dst.rest_client.get(resource_url)
        has_layer = gs_dst.rest_client.get(f"/rest/layers/{layer_name}")

        resource_route = resource_url.replace(".json", ".xml")
        resource_post_route = re.sub(
            r"/[^/]*\.xml$",
            "",
            resource_route,
        )
        resource = gs_src.rest_client.get(resource_route)

        if has_resource.status_code == 200:
            if has_layer.status_code != 200:
                resp = gs_dst.rest_client.delete(resource_url)
                resp.raise_for_status()
                resp = gs_dst.rest_client.post(
                    resource_post_route,
                    data=resource.content,
                    headers={"content-type": "application/xml"},
                )
            else:
                resp = gs_dst.rest_client.put(
                    resource_url.replace(".json", ".xml"),
                    data=resource.content,
                    headers={"content-type": "application/xml"},
                )
        else:
            resp = gs_dst.rest_client.post(
                resource_post_route,
                data=resource.content,
                headers={"content-type": "application/xml"},
            )
            if resp.status_code == 404:
                raise ParamError(
                    {
                        "context": "dst",
                        "key": resource_post_route,
                        "err": "Route not found. Check Workspace and datastore",
                    }
                )
        resp.raise_for_status()

        resp = gs_dst.rest_client.put(f"/rest/layers/{layer_name}", json=layer_data)
        resp.raise_for_status()

    def clone_styles(
        self, gs_src: GsOpService, gs_dst: GsOpService, layer_data: dict[str, Any]
    ) -> None:
        default_style = layer_data["layer"]["defaultStyle"]
        additional_styles = layer_data["layer"].get("styles", {}).get("style", [])
        if isinstance(additional_styles, dict):
            # in case of a single element in the list, this may be provided by the API
            # as a dict, it must be converted to a list of dicts
            additional_styles = [additional_styles]
        all_styles = {
            style["name"]: {
                "workspace": style.get("workspace"),
                "href": style.get("href"),
            }
            for style in [default_style] + additional_styles
        }
        for style in all_styles.values():
            self.clone_style(gs_src, gs_dst, style)

    def clone_style(
        self,
        gs_src: GsOpService,
        gs_dst: GsOpService,
        style: dict[str, Any],
    ) -> None:
        if gs_src.url in style["href"]:
            style_route = style["href"].replace(gs_src.url, "")
            resp = gs_src.rest_client.get(style_route)
            resp.raise_for_status()
            style_info = resp.json()
            style_format = style_info["style"]["format"]
            style_def_route = style_route.replace(".json", f".{style_format}")
            style_def = gs_src.rest_client.get(style_def_route)

            dst_style = gs_dst.rest_client.get(style_route)
            if dst_style.status_code == 200:
                dst_style = gs_dst.rest_client.put(style_route, json=style_info)
                dst_style.raise_for_status()
            else:
                style_post_route = re.sub(
                    r"/styles/.*\.json",
                    "/styles",
                    style_route,
                )
                dst_style = gs_dst.rest_client.post(style_post_route, json=style_info)
                # dst_style.raise_for_status()

            dst_style_def = gs_dst.rest_client.put(
                style_def_route,
                data=style_def.content,
                headers={"content-type": style_def.headers["content-type"]},
            )
            dst_style_def.raise_for_status()


def get_service_info(url: str, is_source: bool, is_geonetwork: bool) -> dict[str, Any]:
    try:
        service_info = config.get_access_info(
            is_src=is_source, is_geonetwork=is_geonetwork, instance_id=url
        )
    except ConfigError as err:
        logger.debug(
            "Key not found: %s\n Config:\n%s", url, json.dumps(config.config, indent=4)
        )
        raise ParamError(
            {
                "context": "src" if is_source else "dst",
                "key": url,
                "err": f"{'geonetwork' if is_geonetwork else 'geoserver'} not found",
            }
        ) from err
    return service_info


def get_gn_service(instance_name: str, is_source: bool, op_logger: OpLogger) -> GnApi:
    gn_info = get_service_info(instance_name, is_source, True)
    return op_logger.add_gn_service(
        GnApi(gn_info["url"], gn_info["auth"]), gn_info["url"], is_source
    )


def get_gs_service(
    instance_name: str, is_source: bool, op_logger: OpLogger
) -> GsOpService:
    gs_info = get_service_info(instance_name, is_source, False)
    gss = GeoServerService(gs_info["url"], gs_info["auth"])
    try:
        resp = gss.rest_client.get("/rest/about/version.json")
    except HTTPError as err:
        if err.response.status_code == 401:
            raise AuthError(
                {
                    "server": gs_info["url"],
                    "user": gs_info["auth"] and gs_info["auth"].login,
                    "err": "Invalid credentials",
                }
            ) from err
    print(
        (
            resp.json()["about"]["resource"][0]["@name"],
            resp.json()["about"]["resource"][0]["Version"],
        )
    )
    return op_logger.add_gs_service(gss, gs_info["url"], is_source)
