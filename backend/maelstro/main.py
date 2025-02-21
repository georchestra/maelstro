"""
Main backend app setup
"""

from typing import Annotated, Any
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Path,
    Query,
    Request,
    Header,
    Body,
)
from fastapi.responses import PlainTextResponse
from maelstro.core.georchestra import get_georchestra_handler
from maelstro.config import app_config as config
from maelstro.metadata import Meta
from maelstro.core import CopyManager
from maelstro.core.operations import log_handler, setup_exception_handlers
from maelstro.logging.psql_logger import (
    setup_db_logging,
    log_request_to_db,
    get_raw_logs,
    format_logs,
    DbNotSetup,
)
from maelstro.common.models import (
    SearchQuery,
    UserResponse,
    user_response_description,
    SourcesResponseElement,
    DestinationsResponseElement,
    RegisteredTransformation,
    LinkedLayer,
    CopyPreview,
    JsonLogRecord,
    sample_json_log_records,
)


app = FastAPI(root_path="/maelstro-backend")
setup_exception_handlers(app)
setup_db_logging()


@app.head("/")
@app.get(
    "/",
    response_description="Hello world dict",
)
def root_page() -> dict[str, str]:
    """
    Hello world dummy route
    """
    return {"Hello": "World"}


@app.get(
    "/user",
    response_description=user_response_description,
)
def user_page(
    sec_username: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_org: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_roles: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_external_authentication: Annotated[
        str | None, Header(include_in_schema=False)
    ] = None,
    sec_proxy: Annotated[str | None, Header(include_in_schema=False)] = None,
    sec_orgname: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> UserResponse:
    """
    Display user information provided by gateway
    """
    return UserResponse(
        username=sec_username,
        org=sec_org,
        roles=sec_roles,
        external_authentication=sec_external_authentication,
        proxy=sec_proxy,
        orgname=sec_orgname,
    )


debug_response_description = """
Contents of query including headers, data, query_params
"""


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
def check_config(
    check_credentials: Annotated[
        bool,
        Query(
            description=(
                "if true, all configured credentials are confirmed to be valid via "
                "a test connection to each server"
            )
        ),
    ] = True
) -> dict[str, bool]:
    """
    This entrypoint is meant to validate the configuration.
    - path of the config file (tbc. security issue ??)
    - check that the format is correct
    - check that all mandatory information is given
    - tell which default values are used
    To be implemented
    """
    # TODO: implement check of all servers configured in the config file
    return {"test_conf.yaml": True, "check_credentials": check_credentials}


@app.get(
    "/sources",
    response_description="A list of each server with the name defined in the config file and the API URL",
)
def get_sources() -> list[SourcesResponseElement]:
    """
    List all the geonetwork source servers registered in the config file
    """
    return config.get_gn_sources()


@app.get(
    "/destinations",
    response_description="A list of destinations with name, URL of geonetwork server and URL of geoserver for each",
)
def get_destinations() -> list[DestinationsResponseElement]:
    """
    List all the geonetwork/geoserver combinations registered in the config file
    """
    return config.get_destinations()


@app.get("/transformations")
def get_transformations() -> dict[str, RegisteredTransformation]:
    """
    List all XSL transformations registered in the config file with their descriptions
    """
    return config.get_transformations()


@app.get("/transformation_pairs")
def get_transformation_pairs() -> dict[str, list[RegisteredTransformation]]:
    """
    List all the transformations registered for each src/dst geonetwork pair
    """
    return config.get_all_transformation_pairs()


@app.post("/search/{src_name}")
def post_search(
    src_name: Annotated[
        str, Path(description="Name of the source Geonetwork to be used for the search")
    ],
    search_query: Annotated[SearchQuery, Body()],
) -> dict[str, Any]:
    """
    Transmit search query to selected Geonetwork server select among the sources
    """
    with get_georchestra_handler() as geo_hnd:
        gn = geo_hnd.get_gn_service(src_name, True)
        return gn.search(search_query.model_dump(by_alias=True, exclude_unset=True))


@app.get("/sources/{src_name}/data/{uuid}/layers")
def get_layers(
    src_name: Annotated[
        str, Path(description="Name of the source Geonetwork to be used for the search")
    ],
    uuid: Annotated[str, Path(description="UUID which references the dataset")],
) -> list[LinkedLayer]:
    """
    Extract linked layers from a dataset on the source Geonetwork server
    """
    with get_georchestra_handler() as geo_hnd:
        gn = geo_hnd.get_gn_service(src_name, True)
        zipdata = gn.get_record_zip(uuid).read()
        meta = Meta(zipdata)
        return meta.get_ogc_geoserver_layers()


@app.get(
    "/copy_preview",
    responses={
        200: {
            "content": {
                "application/json": {},
            }
        },
        400: {"description": "400 may also be an uuid which is not found, see details"},
    },
)
def get_copy_preview(
    src_name: Annotated[
        str,
        Query(
            description="Name of the source Geonetwork to be used for the copy operation"
        ),
    ],
    dst_name: Annotated[
        str,
        Query(
            description="Name of the destination Geonetwork to be used for the copy operation"
        ),
    ],
    metadataUuid: Annotated[
        str, Query(description="UUID which references the dataset")
    ],
    copy_meta: Annotated[
        bool, Query(description="Enable copying metadata to destination Geonetwork")
    ] = True,
    copy_layers: Annotated[
        bool, Query(description="Enable copying linked layers to destination Geoserver")
    ] = True,
    copy_styles: Annotated[
        bool,
        Query(
            description="Enable copying styles of linked layers to destination Geoserver"
        ),
    ] = True,
) -> CopyPreview:
    copy_mgr = CopyManager(src_name, dst_name, metadataUuid)
    return copy_mgr.copy_preview(copy_meta, copy_layers, copy_styles)


@app.put(
    "/copy",
    responses={
        200: {
            "content": {
                "text/plain": {"example": ["string"]},
                "application/json": {"example": [{}]},
            }
        },
        400: {"description": "400 may also be an uuid which is not found, see details"},
    },
)
def put_dataset_copy(
    request: Request,
    src_name: Annotated[
        str,
        Query(
            description="Name of the source Geonetwork to be used for the copy operation"
        ),
    ],
    dst_name: Annotated[
        str,
        Query(
            description="Name of the destination Geonetwork to be used for the copy operation"
        ),
    ],
    metadataUuid: Annotated[
        str, Query(description="UUID which references the dataset")
    ],
    copy_meta: Annotated[
        bool, Query(description="Enable copying metadata to destination Geonetwork")
    ] = True,
    copy_layers: Annotated[
        bool, Query(description="Enable copying linked layers to destination Geoserver")
    ] = True,
    copy_styles: Annotated[
        bool,
        Query(
            description="Enable copying styles of linked layers to destination Geoserver"
        ),
    ] = True,
    accept: Annotated[str, Header(include_in_schema=False)] = "text/plain",
) -> Any:
    """
    Complex operation: copy source dataset to destination including:
    - metadata (if copy_meta == true)
    - all linked geoserver layers (if copy_layers == true)
    - all styles of linked layers (if copy_styles == true)
    """
    if accept not in ["text/plain", "application/json"]:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {accept}. "
            'Accepts "text/plain" or "application/json"',
        )
    copy_mgr = CopyManager(src_name, dst_name, metadataUuid)
    operations = copy_mgr.copy_dataset(copy_meta, copy_layers, copy_styles, accept)
    log_request_to_db(
        200, request, log_handler.pop_properties(), log_handler.pop_json_responses()
    )
    if accept == "application/json":
        return operations
    return PlainTextResponse("\n".join(operations))


@app.get(
    "/logs",
    responses={
        200: {
            "content": {
                "text/plain": {"example": "OP1\nOP2"},
                "application/json": {"example": sample_json_log_records},
            }
        },
        500: {},
    },
)
def get_logs(
    size: Annotated[int, Query(description="Number of log record to retrieve")] = 5,
    offset: Annotated[
        int, Query(description="Offset of first log record to retrieve")
    ] = 0,
    get_details: Annotated[
        bool,
        Query(
            description="Retrieve an additional field with the elementary operations (API calls)"
        ),
    ] = False,
    accept: Annotated[str, Header(include_in_schema=False)] = "text/plain",
) -> str | list[JsonLogRecord]:
    """
    Get a defined number of log records in json or plain text format
    """
    try:
        if accept == "application/json":
            return get_raw_logs(size, offset, get_details)
        return PlainTextResponse("\n".join(format_logs(size, offset)))  # type: ignore
    except DbNotSetup as err:
        raise HTTPException(500, "DB logging not configured") from err


@app.get("/health")
def health_check(
    sec_username: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> dict[str, str | None]:
    """
    Health check to make sure the server is up and running
    For test purposes, the server is reported healthy only from the 5th request onwards
    """
    health_status: str = "healthy"
    return {"status": health_status, "user": sec_username}
