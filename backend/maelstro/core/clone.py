import re
import logging
import json
from io import BytesIO
from typing import Any
from maelstro.metadata import Meta
from maelstro.config import app_config as config
from maelstro.common.types import GsLayer
from .georchestra import GeorchestraHandler, GsRestWrapper, get_georchestra_handler
from .exceptions import ParamError, MaelstroDetail, raise_for_status


logger = logging.getLogger()


class CloneDataset:
    def __init__(self, src_name: str, dst_name: str, uuid: str):
        self.src_name = src_name
        self.dst_name = dst_name
        self.uuid = uuid
        self.copy_meta = False
        self.copy_layers = False
        self.copy_styles = False
        self.meta: Meta
        self.geo_hnd: GeorchestraHandler

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

        with get_georchestra_handler() as geo_hnd:
            self.geo_hnd = geo_hnd
            operations = self._clone_dataset(output_format)
        return operations

    def _clone_dataset(self, output_format: str) -> str | list[Any]:

        if self.uuid:
            gn = self.geo_hnd.get_gn_service(self.src_name, True)
            zipdata = gn.get_record_zip(self.uuid).read()
            self.meta = Meta(zipdata)

        if self.meta is None:
            return []

        if self.copy_layers or self.copy_styles:
            self.clone_layers()

        if self.copy_meta:
            gn_dst = self.geo_hnd.get_gn_service(self.dst_name, False)
            mapping: dict[str, list[str]] = {
                "sources": config.get_gs_sources(),
                "destinations": [src["gs_url"] for src in config.get_destinations()],
            }
            pre_info, post_info = self.meta.update_geoverver_urls(mapping)
            self.geo_hnd.response_handler.responses.append(
                {
                    "operation": "Update of geoserver links in zip archive",
                    "before": pre_info,
                    "after": post_info,
                }
            )
            results = gn_dst.put_record_zip(BytesIO(self.meta.get_zip()))
            self.geo_hnd.response_handler.responses.append(
                {
                    "message": results["msg"],
                    "detail": results["detail"],
                }
            )

        if output_format == "text/plain":
            return self.geo_hnd.response_handler.get_formatted_responses()
        return self.geo_hnd.response_handler.get_json_responses()

    def clone_layers(self) -> None:
        server_layers = self.meta.get_gs_layers(config.get_gs_sources())

        gs_dst = self.geo_hnd.get_gs_service(self.dst_name, False)
        for gs_url, layer_names in server_layers.items():
            if layer_names:
                gs_src = self.geo_hnd.get_gs_service(gs_url, True)
                for layer_name in layer_names:
                    resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                    raise_for_status(resp)
                    layer_data = resp.json()

                    # styles must be cloned first
                    if self.copy_styles:
                        self.clone_styles(gs_src, gs_dst, layer_data)

                    # styles must be available when cloning layers
                    if self.copy_layers:
                        self.clone_layer(gs_src, gs_dst, layer_name, layer_data)

    def clone_layer(
        self,
        gs_src: GsRestWrapper,
        gs_dst: GsRestWrapper,
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
                raise_for_status(resp)
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
                    MaelstroDetail(
                        context="dst",
                        key=resource_post_route,
                        err="Route not found. Check Workspace and datastore",
                    )
                )
        raise_for_status(resp)

        resp = gs_dst.rest_client.put(f"/rest/layers/{layer_name}", json=layer_data)
        raise_for_status(resp)

    def clone_styles(
        self, gs_src: GsRestWrapper, gs_dst: GsRestWrapper, layer_data: dict[str, Any]
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
        gs_src: GsRestWrapper,
        gs_dst: GsRestWrapper,
        style: dict[str, Any],
    ) -> None:
        if gs_src.url in style["href"]:
            style_route = style["href"].replace(gs_src.url, "")
            resp = gs_src.rest_client.get(style_route)
            raise_for_status(resp)
            style_info = resp.json()
            style_format = style_info["style"]["format"]
            style_def_route = style_route.replace(".json", f".{style_format}")
            style_def = gs_src.rest_client.get(style_def_route)

            dst_style = gs_dst.rest_client.get(style_route)
            if dst_style.status_code == 200:
                dst_style = gs_dst.rest_client.put(style_route, json=style_info)
                raise_for_status(dst_style)
            else:
                style_post_route = re.sub(
                    r"/styles/.*\.json",
                    "/styles",
                    style_route,
                )
                dst_style = gs_dst.rest_client.post(style_post_route, json=style_info)
                # raise_for_status(dst_style)

            dst_style_def = gs_dst.rest_client.put(
                style_def_route,
                data=style_def.content,
                headers={"content-type": style_def.headers["content-type"]},
            )
            raise_for_status(dst_style_def)
