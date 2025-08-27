from typing import Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException
from geonetwork.exceptions import GnException
from geoservercloud.services.restlogger import gs_logger as gs_logger  # type: ignore
from maelstro.logging.psql_logger import log_request_to_db
from maelstro.core.georchestra import get_georchestra_handler
from maelstro.common.models import DetailedResponse
from maelstro.common.exceptions import MaelstroException


def setup_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def exception_wrapper(request: Any, call_next: Any) -> Any:
        with get_georchestra_handler() as geo_hnd:
            try:
                request.state.geo_handler = geo_hnd
                return await call_next(request)
            except (MaelstroException, GnException, RequestException) as err:
                response: dict[str, Any] = {}
                status_code = 400
                if isinstance(err, MaelstroException):
                    if err.details.status_code not in [400, 404]:
                        status_code = 500
                    response["summary"] = "MaelstroException"
                    response["info"] = err.details.dict()
                if isinstance(err, GnException):
                    response["summary"] = "HTTPException"
                    response["info"] = {
                        "msg": err.detail.message,
                        "url": err.parent_request.url,
                        "content": err.detail.info,
                    }
                    if err.code != 404:
                        status_code = err.code
                elif isinstance(err, RequestException):
                    response["summary"] = "RequestException"
                    gs_logger.debug(
                        "[%s] %s: %s",
                        request.method,
                        str(request.url),
                        err.__class__.__name__,
                        extra={"response": request},
                    )
                    response["info"] = {
                        "message": f"HTTP error {err.__class__.__name__} at {request.url}",
                        "info": str(err),
                    }
                    status_code = 500
                response["operations"] = geo_hnd.log_handler.get_json_responses()
                if "/copy" in str(request.url):
                    log_request_to_db(
                        status_code,
                        request,
                        geo_hnd.log_handler.get_properties(),
                        response["operations"],
                    )
                return JSONResponse(
                    DetailedResponse(**response).dict(), status_code=status_code
                )
