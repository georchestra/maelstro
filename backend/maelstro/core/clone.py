import re
import logging
import json
from functools import cache
from io import BytesIO
from typing import Any
from geonetwork import GnApi
from geoservercloud.services import RestService  # type: ignore
from maelstro.metadata import Meta
from maelstro.config import app_config as config
from maelstro.common.types import GsLayer
from .georchestra import GeorchestraHandler, get_georchestra_handler
from .exceptions import ParamError, MaelstroDetail
from .operations import raise_for_status


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

    def involved_resources(self) -> list[dict[str, Any]]:
        with get_georchestra_handler() as geo_hnd:
            self.geo_hnd = geo_hnd

            zipdata = self.gn_src.get_record_zip(self.uuid).read()
            self.meta = Meta(zipdata)

            resources = []

            geoservers = self.meta.get_gs_layers(config.get_gs_sources())
            for server_url, layer_names in geoservers.items():
                styles = set()
                for layer_name in layer_names:

                    gs_src = self.geo_hnd.get_gs_service(server_url, True)
                    layers = {}
                    for layer_name in layer_names:
                        resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                        raise_for_status(resp)
                        layers[layer_name] = resp.json()

                    for layer in layers.values():
                        styles.update(self.get_styles_from_layer(layer).keys())

                resources.append({
                    'server_url': server_url,
                    'layers': [str(layer_name) for layer_name in layer_names],
                    'styles': list(styles)
                })

        return resources

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
            zipdata = self.gn_src.get_record_zip(self.uuid).read()
            self.meta = Meta(zipdata)
            self.geo_hnd.log_handler.properties["src_title"] = self.meta.get_title()

        if self.meta is None:
            return []

        if self.copy_layers or self.copy_styles:
            self.clone_layers()

        if self.copy_meta:
            mapping: dict[str, list[str]] = {
                "sources": config.get_gs_sources(),
                "destinations": [src["gs_url"] for src in config.get_destinations()],
            }
            pre_info, post_info = self.meta.update_geoverver_urls(mapping)
            self.geo_hnd.log_handler.responses.append(
                {
                    "operation": "Update of geoserver links in zip archive",
                    "before": pre_info,
                    "after": post_info,
                }
            )
            self.geo_hnd.log_handler.properties["dst_title"] = self.meta.get_title()
            results = self.gn_dst.put_record_zip(BytesIO(self.meta.get_zip()))
            self.geo_hnd.log_handler.responses.append(
                {
                    "message": results["msg"],
                    "detail": results["detail"],
                }
            )

        if output_format == "text/plain":
            return self.geo_hnd.log_handler.get_formatted_responses()
        return self.geo_hnd.log_handler.get_json_responses()

    def clone_layers(self) -> None:
        server_layers = self.meta.get_gs_layers(config.get_gs_sources())
        for gs_url, layer_names in server_layers.items():
            if layer_names:
                gs_src = self.geo_hnd.get_gs_service(gs_url, True)
                layers = {}
                for layer_name in layer_names:
                    resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                    raise_for_status(resp)
                    layers[layer_name] = resp.json()

                stores = {}
                workspaces = {}
                styles = {}

                # fill in workspaces used in styles
                if self.copy_styles:
                    for layer_data in layers.values():
                        styles.update(self.get_styles_from_layer(layer_data))

                    for style in styles.values():
                        try:
                            workspaces.update(self.get_workspaces_from_style(style))
                        except KeyError:
                            # skip styles without a workspace
                            pass

                # fill in workspaces  and datastores used in layers
                if self.copy_layers:
                    stores.update(self.get_stores_from_layers(gs_src, layers))

                    for store in stores.values():
                        workspaces.update(self.get_workspaces_from_store(gs_src, store))

                self.check_workspaces(gs_src, workspaces)
                self.check_datastores(gs_src, stores)

                # styles must be cloned first
                if self.copy_styles:
                    for style in styles.values():
                        self.clone_style(gs_src, style)

                # styles must be available when cloning layers
                if self.copy_layers:
                    for layer_name, layer_data in layers.items():
                        self.clone_layer(gs_src, layer_name, layer_data)

    def get_styles_from_layer(self, layer_data: dict[str, Any]) -> dict[str, Any]:
        default_style = layer_data["layer"]["defaultStyle"]
        additional_styles = layer_data["layer"].get("styles", {}).get("style", [])
        if isinstance(additional_styles, dict):
            # in case of a single element in the list, this may be provided by the API
            # as a dict, it must be converted to a list of dicts
            additional_styles = [additional_styles]
        all_styles = {
            style["name"]: style for style in [default_style] + additional_styles
        }
        return all_styles

    def get_workspaces_from_style(self, style: dict[str, Any]) -> dict[str, Any]:
        return {
            # workspace references in style data have no href or other details
            style["workspace"]: None
        }

    def get_stores_from_layers(
        self, gs_src: RestService, layers: dict[GsLayer, Any]
    ) -> dict[str, Any]:
        stores = {}
        resources = {
            layer_data["layer"]["resource"]["name"]: layer_data["layer"]["resource"]
            for layer_data in layers.values()
        }
        for res in resources.values():
            resource_class = res["@class"]
            resource_route = res["href"].replace(gs_src.url, "")
            resource_resp = gs_src.rest_client.get(resource_route)
            raise_for_status(resource_resp)
            resource_info = resource_resp.json()
            store = resource_info[resource_class]["store"]
            stores[store["name"]] = store
        return stores

    def get_workspaces_from_store(
        self, gs_src: RestService, store: dict[str, Any]
    ) -> dict[str, Any]:
        store_class = store["@class"]
        store_route = store["href"].replace(gs_src.url, "")
        store_resp = gs_src.rest_client.get(store_route)
        raise_for_status(store_resp)
        store_info = store_resp.json()
        workspace = store_info[store_class]["workspace"]
        return {workspace["name"]: workspace}

    def check_workspaces(self, gs_src: RestService, workspaces: dict[str, Any]) -> None:
        for workspace_name, workspace in workspaces.items():
            if workspace is None:
                workspace_route = f"/rest/workspaces/{workspace_name}"
            else:
                workspace_route = workspace["href"].replace(gs_src.url, "")
            has_workspace = self.gs_dst.rest_client.get(workspace_route)
            if has_workspace.status_code == 404:
                raise ParamError(
                    MaelstroDetail(
                        context="dst",
                        key=workspace_route,
                        err=f"Workspace {workspace_name} not found on destination Geoserver {self.dst_name}",
                        operations=self.geo_hnd.log_handler.get_json_responses(),
                    )
                )
            raise_for_status(has_workspace)

    def check_datastores(self, gs_src: RestService, datastores: dict[str, Any]) -> None:
        for store_name, store in datastores.items():
            store_route = store["href"].replace(gs_src.url, "")
            has_datastore = self.gs_dst.rest_client.get(store_route)
            if has_datastore.status_code == 404:
                raise ParamError(
                    MaelstroDetail(
                        context="dst",
                        key=store_route,
                        err=f"Datastore {store_name} not found on destination Geoserver {self.dst_name}",
                        operations=self.geo_hnd.log_handler.get_json_responses(),
                    )
                )
            raise_for_status(has_datastore)

    def clone_layer(
        self,
        gs_src: RestService,
        layer_name: GsLayer,
        layer_data: dict[str, Any],
    ) -> None:
        resource_route = layer_data["layer"]["resource"]["href"].replace(gs_src.url, "")

        layer_string = json.dumps(layer_data)
        layer_data = json.loads(layer_string.replace(gs_src.url, self.gs_dst.url))

        has_resource = self.gs_dst.rest_client.get(resource_route)
        has_layer = self.gs_dst.rest_client.get(f"/rest/layers/{layer_name}")

        xml_resource_route = resource_route.replace(".json", ".xml")
        resource_post_route = re.sub(
            r"/[^/]*\.xml$",
            "",
            xml_resource_route,
        )
        resource = gs_src.rest_client.get(xml_resource_route)

        if has_resource.status_code == 200:
            if has_layer.status_code != 200:
                resp = self.gs_dst.rest_client.delete(resource_route)
                raise_for_status(resp)
                resp = self.gs_dst.rest_client.post(
                    resource_post_route,
                    data=resource.content,
                    headers={"content-type": "application/xml"},
                )
            else:
                resp = self.gs_dst.rest_client.put(
                    xml_resource_route,
                    data=resource.content,
                    headers={"content-type": "application/xml"},
                )
        else:
            resp = self.gs_dst.rest_client.post(
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

        resp = self.gs_dst.rest_client.put(
            f"/rest/layers/{layer_name}", json=layer_data
        )
        raise_for_status(resp)

    def clone_style(
        self,
        gs_src: RestService,
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

            dst_style = self.gs_dst.rest_client.get(style_route)
            if dst_style.status_code == 200:
                dst_style = self.gs_dst.rest_client.put(style_route, json=style_info)
                raise_for_status(dst_style)
            else:
                style_post_route = re.sub(
                    r"/styles/.*\.json",
                    "/styles",
                    style_route,
                )
                dst_style = self.gs_dst.rest_client.post(
                    style_post_route, json=style_info
                )
                # raise_for_status(dst_style)

            dst_style_def = self.gs_dst.rest_client.put(
                style_def_route,
                data=style_def.content,
                headers={"content-type": style_def.headers["content-type"]},
            )
            raise_for_status(dst_style_def)
