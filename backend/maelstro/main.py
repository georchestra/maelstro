"""
Main backend app setup
"""

from io import BytesIO
from typing import Annotated, Any
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    Header,
    Body,
)
from fastapi.responses import PlainTextResponse
from geonetwork import GnApi
from geonetwork.exceptions import GnException
from maelstro.config import ConfigError, app_config as config
from maelstro.metadata import Meta
from maelstro.core import CloneDataset
from maelstro.core.operations import gn_handler
from maelstro.common.models import SearchQuery
from maelstro.common.formatters import format_ES_error


app = FastAPI(root_path="/maelstro-backend")

app.state.health_countdown = 5


@app.head("/")
@app.get("/")
def root_page() -> dict[str, str]:
    """
    Hello world dummy route
    """
    return {"Hello": "World"}


@app.get("/user")
def user_page(
    sec_username: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_org: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_roles: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_external_authentication: Annotated[
        str | None, Header(include_in_schema=False)
    ] = None,
    sec_proxy: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_orgname: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> dict[str, str | None]:
    """
    Display user information provided by gateway
    """
    return {
        "username": sec_username,
        "org": sec_org,
        "roles": sec_roles,
        "external-authentication": sec_external_authentication,
        "proxy": sec_proxy,
        "orgname": sec_orgname,
    }


# pylint: disable=fixme
# TODO: deactivate for prod
@app.head("/debug")
@app.get("/debug")
@app.put("/debug")
@app.post("/debug")
@app.delete("/debug")
@app.options("/debug")
@app.patch("/debug")
def debug_page(request: Request) -> dict[str, Any]:
    """
    Display details of query including headers.
    This may be useful in development to check all the headers provided by the gateway.
    This entrypoint should be deactivated in prod.
    """
    return {
        **{
            k: request[k]
            for k in [
                "type",
                "asgi",
                "http_version",
                "server",
                "client",
                "scheme",
                "root_path",
            ]
        },
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "query_params": request.query_params.multi_items(),
    }


@app.get("/check_config")
def check_config(check_credentials: bool = True) -> dict[str, bool]:
    # TODO: implement check of all servers configured in the config file
    return {"test_conf.yaml": True, "check_credentials": check_credentials}


@app.get("/sources")
def get_sources() -> list[dict[str, str]]:
    return config.get_gn_sources()


@app.get("/destinations")
def get_destinations() -> list[dict[str, str]]:
    return config.get_destinations()


@app.post("/search/{src_name}")
def post_search(
    src_name: str, search_query: Annotated[SearchQuery, Body()]
) -> dict[str, Any]:
    src_info = config.get_access_info(
        is_src=True, is_geonetwork=True, instance_id=src_name
    )
    try:
        gn_handler.reset()
        gn = GnApi(src_info["url"], src_info["auth"])
        return gn.search(search_query.model_dump(by_alias=True, exclude_unset=True))
    except GnException as err:
        operations = gn_handler.pop_responses()
        raise HTTPException(
            err.code,
            {
                "msg": err.detail.message,
                "url": err.parent_response.url,
                "operations": operations,
                "content": format_ES_error(err.parent_response.json()),
            },
        ) from err


@app.get("/sources/{src_name}/data/{uuid}/layers")
def get_layers(src_name: str, uuid: str) -> list[dict[str, str]]:
    try:
        src_info = config.get_access_info(
            is_src=True, is_geonetwork=True, instance_id=src_name
        )
    except ConfigError as err:
        raise HTTPException(status_code=406, detail=err.args) from err

    gn = GnApi(src_info["url"], src_info["auth"])
    zipdata = gn.get_record_zip(uuid).read()
    meta = Meta(zipdata)
    return meta.get_ogc_geoserver_layers()


@app.put(
    "/copy",
    responses={
        200: {"content": {"text/plain": {}, "application/json": {}}},
        400: {"description": "should be 404, but 404 is rewritten by the gateway"},
    },
)
def put_dataset_copy(
    src_name: str,
    dst_name: str,
    metadataUuid: str,
    copy_meta: bool = True,
    copy_layers: bool = True,
    copy_styles: bool = True,
    dry_run: bool = False,
    accept: Annotated[str, Header()] = "text/plain",
) -> Any:
    if accept not in ["text/plain", "application/json"]:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {accept}. "
            'Accepts "text/plain" or "application/json"',
        )
    try:
        gn_handler.reset()
        clone_ds = CloneDataset(src_name, dst_name, metadataUuid, dry_run)
        clone_ds.clone_dataset(copy_meta, copy_layers, copy_styles, accept)
    except GnException as err:
        operations = gn_handler.pop_responses()
        raise HTTPException(
            err.code,
            {
                "msg": err.detail.message,
                "url": err.parent_request.url,
                "operations": operations,
                "content": err.parent_response.json() if err.parent_response else None,
            },
        ) from err
    if accept == "application/json":
        return gn_handler.pop_responses()
    return PlainTextResponse("\n".join(gn_handler.pop_formatted_responses()))


@app.post("/destinations/{dst_name}/data/{uuid}/layers/{layer_name}/copy")
def post_data_copy(dst_name: str, uuid: str, layer_name: str, src_name: str) -> Any:
    src_info = config.get_access_info(
        is_src=True, is_geonetwork=True, instance_id=src_name
    )
    gn = GnApi(src_info["url"], src_info["auth"])
    zipdata = gn.get_record_zip(uuid).read()

    print(f"Layer name {layer_name} currently unused, needed for cloning geoserver")

    dst_info = config.get_access_info(
        is_src=False, is_geonetwork=True, instance_id=dst_name
    )
    return GnApi(dst_info["url"], dst_info["auth"]).put_record_zip(BytesIO(zipdata))


@app.get("/health")
def health_check(
    response: Response,
    sec_username: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> dict[str, str | None]:
    """
    Health check to make sure the server is up and running
    For test purposes, the server is reported healthy only from the 5th request onwards
    """
    health_status: str = "healthy"
    if app.state.health_countdown > 0:
        app.state.health_countdown -= 1
        response.status_code = 404
        health_status = "unhealthy"
    return {"status": health_status, "user": sec_username}
