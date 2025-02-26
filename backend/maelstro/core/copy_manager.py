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
from maelstro.common.models import CopyPreview, InfoRecord, SuccessRecord
from maelstro.common.exceptions import ParamError
from .georchestra import GeorchestraHandler
from .operations import raise_for_status


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

        src_gn_info = self.geo_hnd.get_service_info(
            self.src_name, is_source=True, is_geonetwork=True
        )
        src_gn_url = src_gn_info["url"]
        dst_gn_info = self.geo_hnd.get_service_info(
            self.dst_name, is_source=False, is_geonetwork=True
        )
        dst_gn_url = dst_gn_info["url"]

        preview["geonetwork_resources"].append(
            {
                "src": src_gn_url,
                "dst": dst_gn_url,
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

        geoservers = self.meta.get_gs_layers(config.get_gs_sources())
        for server_url, layer_names in geoservers.items():
            styles: set[str] = set()
            for layer_name in layer_names:

                gs_src = self.geo_hnd.get_gs_service(server_url, True)
                layers = {}
                for layer_name in layer_names:
                    resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                    raise_for_status(resp)
                    layers[layer_name] = resp.json()

                for layer in layers.values():
                    styles.update(self.get_styles_from_layer(layer).keys())

            preview["geoserver_resources"].append(
                {
                    "src": server_url,
                    "dst": dst_gs_url,
                    "layers": (
                        [str(layer_name) for layer_name in layer_names]
                        if self.include_layers
                        else []
                    ),
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
            self.copy_layers()

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

    def copy_layers(self) -> None:
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
                if self.include_styles:
                    for layer_data in layers.values():
                        styles.update(self.get_styles_from_layer(layer_data))

                    for style in styles.values():
                        try:
                            workspaces.update(self.get_workspaces_from_style(style))
                        except KeyError:
                            # skip styles without a workspace
                            pass

                # fill in workspaces  and datastores used in layers
                if self.include_layers:
                    stores.update(self.get_stores_from_layers(gs_src, layers))

                    for store in stores.values():
                        workspaces.update(self.get_workspaces_from_store(gs_src, store))

                self.check_workspaces(gs_src, workspaces)
                self.check_datastores(gs_src, stores)

                # styles must be copieed first
                if self.include_styles:
                    with self.geo_hnd.log_handler.logger_context("Style"):
                        for style in styles.values():
                            self.copy_style(gs_src, style)
                        self.geo_hnd.log_handler.log_info(
                            SuccessRecord(
                                message="Styles copied successfully",
                                detail={"styles": list(styles.keys())},
                            )
                        )

                # styles must be available when cloning layers
                if self.include_layers:
                    with self.geo_hnd.log_handler.logger_context("Layer"):
                        for layer_name, layer_data in layers.items():
                            self.copy_layer(gs_src, layer_name, layer_data)
                        self.geo_hnd.log_handler.log_info(
                            SuccessRecord(
                                message="Layers copied successfully",
                                detail={"layers": list(layers.keys())},
                            )
                        )

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
                    context="dst",
                    key=workspace_route,
                    err=f"Workspace {workspace_name} not found on destination Geoserver {self.dst_name}",
                    operations=self.geo_hnd.log_handler.get_json_responses(),
                )
            raise_for_status(has_workspace)

    def check_datastores(self, gs_src: RestService, datastores: dict[str, Any]) -> None:
        for store_name, store in datastores.items():
            store_route = store["href"].replace(gs_src.url, "")
            has_datastore = self.gs_dst.rest_client.get(store_route)
            if has_datastore.status_code == 404:
                raise ParamError(
                    context="dst",
                    key=store_route,
                    err=f"Datastore {store_name} not found on destination Geoserver {self.dst_name}",
                    operations=self.geo_hnd.log_handler.get_json_responses(),
                )
            raise_for_status(has_datastore)

    def copy_layer(
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
                    context="dst",
                    key=resource_post_route,
                    err="Route not found. Check Workspace and datastore",
                )
        raise_for_status(resp)

        resp = self.gs_dst.rest_client.put(
            f"/rest/layers/{layer_name}", json=layer_data
        )
        raise_for_status(resp)

    def copy_style(
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
