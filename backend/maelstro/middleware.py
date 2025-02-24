from fastapi import FastAPI
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException
from geonetwork.exceptions import GnException
from geoservercloud.services.restlogger import gs_logger as gs_logger  # type: ignore
from maelstro.logging.psql_logger import log_request_to_db
from maelstro.core.georchestra import get_georchestra_handler
from maelstro.common.exceptions import MaelstroException


def setup_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def exception_wrapper(request, call_next):
        with get_georchestra_handler() as geo_hnd:
            try:
                request.state.geo_handler = geo_hnd
                return await call_next(request)
            except (MaelstroException, GnException, RequestException) as err:
                response = {}
                status_code = 400
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
                    status_code = 504
                response["operations"] = geo_hnd.log_handler.pop_json_responses()
                if "/copy" in str(request.url):
                    log_request_to_db(
                        status_code,
                        request,
                        geo_hnd.log_handler.pop_properties(),
                        response["operations"],
                    )
                return JSONResponse(response, status_code=status_code)
