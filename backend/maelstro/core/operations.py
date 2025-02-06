from typing import Any
import logging
from logging import Handler
from requests import Response
from requests.exceptions import RequestException
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from geonetwork.gn_logger import logger as gn_logger
from geoservercloud.services.restlogger import gs_logger as gs_logger  # type: ignore
from geonetwork.exceptions import GnException
from maelstro.logging.psql_logger import log_request_to_db


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def handle_fastapi_exception(request: Request, err: HTTPException) -> Any:
        if "/copy/" in str(request.url):
            log_request_to_db(
                err.status_code,
                request,
                log_handler.properties,
                log_handler.get_json_responses(),
            )
        return await http_exception_handler(request, err)

    @app.exception_handler(GnException)
    def handle_gn_exception(request: Request, err: GnException) -> None:
        raise HTTPException(
            # 404 not found on lib level will rather be a bad request here
            # error 400 is not truncated by the gateway, whereas 404 is
            err.code if err.code != 404 else 400,
            {
                "msg": err.detail.message,
                "url": err.parent_response.url,
                "operations": log_handler.get_json_responses(),
                "content": err.detail.info,
            },
        ) from err

    @app.exception_handler(RequestException)
    def handle_gs_exception(request: Request, err: RequestException) -> None:
        gs_logger.debug(
            "[%s] %s: %s",
            request.method,
            str(request.url),
            err.__class__.__name__,
            extra={"response": request},
        )
        raise HTTPException(
            status_code=504,
            detail={
                "message": f"HTTP error {err.__class__.__name__} at {request.url}",
                "operations": log_handler.get_json_responses(),
                "info": str(err),
            },
        ) from err


def raise_for_status(response: Response) -> None:
    if 400 <= response.status_code < 600:
        raise HTTPException(
            response.status_code if response.status_code != 404 else 400,
            {
                "message": f"HTTP error in [{response.request.method}] {response.url}",
                "operations": log_handler.get_json_responses(),
                "info": response.text,
            },
        )


class LogCollectionHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.responses: list[Response | None | dict[str, Any]] = []
        self.valid = False
        self.properties: dict[str, Any] = {}

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # The response attribute of the record has been added via the `extra` parameter
            # type checking skipped for simplicity
            self.responses.append(record.response)  # type: ignore
        except AttributeError:
            self.responses.append(None)

    def format_response(self, resp: Response | dict[str, Any]) -> str:
        if isinstance(resp, Response):
            return f"[{resp.request.method}] - ({resp.status_code}) : {resp.url}"
        return " - ".join(f"{k}: {v}" for k, v in resp.items() if k != "detail")

    def json_response(self, resp: Response | dict[str, Any]) -> dict[str, Any]:
        if isinstance(resp, Response):
            return {
                "method": resp.request.method,
                "status_code": resp.status_code,
                "url": resp.url,
            }
        return resp

    def get_formatted_responses(self) -> list[str]:
        return [self.format_response(r) for r in self.responses if r is not None]

    def get_json_responses(self) -> list[dict[str, Any]]:
        return [self.json_response(r) for r in self.responses if r is not None]


# must use a global variable so that log_handler is accessible from inside exception
log_handler = LogCollectionHandler()
gn_logger.addHandler(log_handler)
gs_logger.addHandler(log_handler)
