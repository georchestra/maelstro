"""
Main backend app setup
"""

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
from maelstro.core.georchestra import get_georchestra_handler
from maelstro.config import app_config as config
from maelstro.metadata import Meta
from maelstro.core import CloneDataset
from maelstro.core.operations import log_handler, setup_exception_handlers
from maelstro.logging.psql_logger import create_db_table, log_request_to_db, get_logs, format_logs
from maelstro.common.models import SearchQuery


app = FastAPI(root_path="/maelstro-backend")
setup_exception_handlers(app)
# this call is safe: by default sqlalchemy checks first if the table exists
create_db_table()

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
async def debug_page(request: Request) -> dict[str, Any]:
    """
    Display details of query including headers.
    This may be useful in development to check all the headers provided by the gateway.
    This entrypoint should be deactivated in prod.
    """
    return {
        **{
            k: str(request.get(k))
            for k in [
                "method",
                "type",
                "asgi",
                "http_version",
                "server",
                "client",
                "scheme",
                "url",
                "base_url",
                "root_path",
            ]
        },
        "data": await request.body(),
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
    with get_georchestra_handler() as geo_hnd:
        gn = geo_hnd.get_gn_service(src_name, True)
        return gn.search(search_query.model_dump(by_alias=True, exclude_unset=True))


@app.get("/sources/{src_name}/data/{uuid}/layers")
def get_layers(src_name: str, uuid: str) -> list[dict[str, str]]:
    with get_georchestra_handler() as geo_hnd:
        gn = geo_hnd.get_gn_service(src_name, True)
        zipdata = gn.get_record_zip(uuid).read()
        meta = Meta(zipdata)
        return meta.get_ogc_geoserver_layers()


@app.put(
    "/copy",
    responses={
        200: {"content": {"text/plain": {}, "application/json": {}}},
        400: {"description": "400 may also be an uuid which is not found, see details"},
    },
)
def put_dataset_copy(
    request: Request,
    src_name: str,
    dst_name: str,
    metadataUuid: str,
    copy_meta: bool = True,
    copy_layers: bool = True,
    copy_styles: bool = True,
    accept: Annotated[str, Header(include_in_schema=False)] = "text/plain",
) -> Any:
    if accept not in ["text/plain", "application/json"]:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {accept}. "
            'Accepts "text/plain" or "application/json"',
        )
    clone_ds = CloneDataset(src_name, dst_name, metadataUuid)
    operations = clone_ds.clone_dataset(copy_meta, copy_layers, copy_styles, accept)
    log_request_to_db(200, request, log_handler)
    if accept == "application/json":
        return operations
    return PlainTextResponse("\n".join(operations))


@app.get(
    "/logs",
    responses={
        200: {"content": {"text/plain": {}, "application/json": {}}},
    }
)
def get_user_logs(
        size: int = 5,
        offset: int = 0,
        get_details: bool = False,
        accept: Annotated[str, Header(include_in_schema=False)] = "text/plain"
):
    if accept == "application/json":
        return get_logs(size, offset, get_details)
    return PlainTextResponse("\n".join(format_logs(size, offset)))


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
