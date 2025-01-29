import re
import logging
import json
from requests.exceptions import HTTPError
from fastapi import HTTPException
from geonetwork import GnApi
from geoservercloud.services import RestService as GeoServerService
from maelstro.metadata import Meta
from maelstro.config import ConfigError, app_config as config
from .operations import OpLogger


logger = logging.getLogger()

# module to be converted to class structure
op_logger = OpLogger()
resource_urls = []


class MaelstroException(HTTPException):
    def __init__(self, err_dict):
        if not isinstance(err_dict, dict):
            err_dict = {"data": err_dict}
        super().__init__(err_dict.get("status_code", 500), err_dict)


class AuthError(MaelstroException):
    def __init__(self, err_dict):
        super().__init__({**err_dict, "status_code": 401})


class UrlError(MaelstroException):
    def __init__(self, err_dict):
        super().__init__({**err_dict, "status_code": 404})


class ParamError(MaelstroException):
    def __init__(self, err_dict):
        super().__init__({**err_dict, "status_code": 406})


def clone_uuid(
        src_name: str,
        dst_name: str,
        uuid: str,
        copy_meta: bool,
        copy_layers: bool,
        copy_styles: bool
):
    gn = get_gn_service(src_name, True)
    zipdata = gn.get_record_zip(uuid).read()
    meta = Meta(zipdata)

    if copy_layers or copy_styles:
        clone_layers(src_name, dst_name, meta, copy_layers, copy_styles)

    if copy_meta:
        gn_dst = get_gn_service(dst_name, False)
        mapping = {
            "sources": config.get_gs_sources(),
            "destinations": [
                src["gs_url"]
                for src in config.get_destinations()
            ],
        }
        meta.update_geoverver_urls(mapping)
        gn_dst.put_record_zip(meta.xml_bytes)

    return op_logger.format_operations()
    return op_logger.get_operations()
    dst_info = config.get_access_info(
        is_src=False, is_geonetwork=True, instance_id=dst_name
    )
    return GnApi(dst_info["url"], dst_info["auth"]).put_record_zip(zipdata)


def clone_layers(
        src_name: str,
        dst_name: str,
        meta,
        copy_layers: bool,
        copy_styles: bool
):
    layers = meta.get_ogc_geoserver_layers()
    server_layers = {
        url: set((l["name"] or "GAM:plan_b3_psc_02_captage_pct").split(":")[-1] for l in layers if url in l["server_url"])
        for url in config.get_gs_sources()
    }

    resource_urls.clear()
    gs_dst = get_gs_service(dst_name, False)
    for gs_url, layer_names in server_layers.items():
        if layer_names:
            gs_src = get_gs_service(gs_url, True)
            for layer_name in layer_names:
                resp = gs_src.rest_client.get(f"/rest/layers/{layer_name}.json")
                resp.raise_for_status()
                layer_data = resp.json()

                # resp = gs_dst.rest_client.put(f"/rest/layers/{layer_name}.json")

                # styles must be cloned first
                if copy_styles:
                    clone_styles(gs_src, gs_dst, layer_data)

                # styles must be available when cloning layers
                if copy_layers:
                    clone_layer(gs_src, gs_dst, layer_name, layer_data)


def clone_layer(gs_src, gs_dst, layer_name, layer_data):
    resource_url = layer_data["layer"]["resource"]["href"].replace(gs_src.url, "")
    if resource_url not in resource_urls:
        resource_urls.append(resource_url)
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
                    headers={"content-type": "application/xml"}
                )
            else:
                resp = gs_dst.rest_client.put(
                    resource_url.replace(".json", ".xml"),
                    data=resource.content,
                    headers={"content-type": "application/xml"}
                )
        else:
            resp = gs_dst.rest_client.post(
                resource_post_route,
                data=resource.content,
                headers={"content-type": "application/xml"}
            )
            if resp.status_code == 404:
                raise ParamError(
                    {
                        "context": "dst",
                        "key": resource_post_route,
                        "err": f"Route not found. Check Workspace and datastore"
                    }
                )
        resp.raise_for_status()

    resp = gs_dst.rest_client.put(f"/rest/layers/{layer_name}", json=layer_data)
    resp.raise_for_status()


def clone_styles(gs_src, gs_dst, layer_data):
    defaultStyle = layer_data["layer"]["defaultStyle"]
    additional_styles = layer_data["layer"].get("styles", {}).get("style", [])
    all_styles = {
        style["name"]: {
            "workspace": style.get("workspace"),
            "href": style.get("href"),
        }
        for style in [defaultStyle] + additional_styles
    }
    for style_name, style in all_styles.items():
        clone_style(gs_src, gs_dst, style_name, style)


def clone_style(gs_src, gs_dst, style_name, style):
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
            #dst_style.raise_for_status()

        dst_style_def = gs_dst.rest_client.put(
            style_def_route,
            data=style_def.content,
            headers={
                "content-type": style_def.headers['content-type']
            }
        )
        #dst_style_def.raise_for_status()


def get_service_info(url, is_source, is_geonetwork):
    try:
        service_info = config.get_access_info(
            is_src=is_source, is_geonetwork=is_geonetwork, instance_id=url
        )
    except ConfigError as err:
        logger.debug(
            "Key not found: %s\n Config:\n%s",
            url,
            json.dumps(config.config, indent=4)
        )
        raise ParamError(
            {
                "context": "src" if is_source else "dst",
                "key": url,
                "err": f"{'geonetwork' if is_geonetwork else 'geoserver'} not found"
            }
        ) from err
    return service_info


def get_gn_service(instance_name, is_source):
    gn_info = get_service_info(instance_name, is_source, True)
    return op_logger.add_gn_service(GnApi(gn_info["url"], gn_info["auth"]), gn_info["url"], is_source)


def get_gs_service(instance_name, is_source):
    gs_info = get_service_info(instance_name, is_source, False)
    gss = GeoServerService(gs_info["url"], gs_info["auth"])
    try:
        resp = gss.rest_client.get(f"/rest/about/version.json")
    except HTTPError as err:
        if err.response.status_code == 401:
            raise AuthError(
                {"server": gs_info["url"], "user": gs_info["auth"] and gs_info["auth"].login, "err": "Invalid credentials"}
            )
    print((resp.json()["about"]["resource"][0]["@name"], resp.json()["about"]["resource"][0]["Version"]))
    return op_logger.add_gs_service(gss, gs_info["url"], is_source)
