from typing import Any
import logging
import threading
from datetime import datetime
from logging import Handler
from requests import Response
from pydantic import BaseModel
# from requests.exceptions import RequestException
from fastapi import FastAPI, HTTPException, Request
# from fastapi.exception_handlers import http_exception_handler
from geonetwork.gn_logger import logger as gn_logger
from geoservercloud.services.restlogger import gs_logger as gs_logger  # type: ignore
# from geonetwork.exceptions import GnException
# from maelstro.logging.psql_logger import log_request_to_db
# from maelstro.common.models import OperationsRecord


# def setup_exception_handlers(app: FastAPI) -> None:
#     @app.exception_handler(HTTPException)
#     async def handle_fastapi_exception(request: Request, err: HTTPException) -> Any:
#         operations = log_handler.pop_json_responses()
#         err.detail["operations"] = operations
#         if "/copy" in str(request.url):
#             log_request_to_db(
#                 err.status_code,
#                 request,
#                 log_handler.pop_properties(),
#                 operations,
#             )
#         return await http_exception_handler(request, err)

#     @app.exception_handler(GnException)
#     def handle_gn_exception(request: Request, err: GnException) -> None:
#         raise HTTPException(
#             # 404 not found on lib level will rather be a bad request here
#             # error 400 is not truncated by the gateway, whereas 404 is
#             err.code if err.code != 404 else 400,
#             {
#                 "msg": err.detail.message,
#                 "url": err.parent_request.url,
#                 "content": err.detail.info,
#             },
#         ) from err

#     @app.exception_handler(RequestException)
#     def handle_gs_exception(request: Request, err: RequestException) -> None:
#         gs_logger.debug(
#             "[%s] %s: %s",
#             request.method,
#             str(request.url),
#             err.__class__.__name__,
#             extra={"response": request},
#         )
#         raise HTTPException(
#             status_code=504,
#             detail={
#                 "message": f"HTTP error {err.__class__.__name__} at {request.url}",
#                 "info": str(err),
#             },
#         ) from err


def raise_for_status(response: Response) -> None:
    if 400 <= response.status_code < 600:
        raise HTTPException(
            response.status_code if response.status_code != 404 else 400,
            {
                "message": f"HTTP error in [{response.request.method}] {response.url}",
                "operations": log_handler.pop_json_responses(),
                "info": response.text,
            },
        )


class LogCollectionHandler(Handler):
    def __init__(self, id=None) -> None:
        super().__init__()
        self._id = id
        self.responses: dict[int, list[Response | None | dict[str, Any]]] = {}
        self.properties: dict[str, Any] = {}

    @property
    def valid(self):
        return self.id in self.responses

    @property
    def id(self):
        return self._id or threading.current_thread().ident

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # The response attribute of the record has been added via the `extra` parameter
            # type checking skipped for simplicity
            self.responses[self.id].append(record.response)  # type: ignore
        except AttributeError:
            self.responses[self.id].append(None)

    def init_thread(self) -> None:
        self.clear_current_thread()
        self.responses[self.id] = []
        self.properties[self.id] = {
            "start_time": datetime.now()
        }

    def log_info(self, info: dict[str, Any]) -> None:
        self.responses[self.id].append(info)

    def set_property(self, key: str, value: Any) -> None:
        self.properties[self.id][key] = value

    def pop_properties(self) -> dict[str, Any]:
        return self.properties.get(self.id, {})

    def clear_current_thread(self) -> None:
        self.responses.pop(self.id, None)
        self.properties.pop(self.id, None)

    def json_response(self, resp: Response | dict[str, Any]) -> dict[str, Any]:
        if isinstance(resp, Response):
            return {
                "method": resp.request.method,
                "status_code": resp.status_code,
                "url": resp.url,
            }
        if isinstance(resp, BaseModel):
            return resp.dict()
        return resp

    def pop_json_responses(self) -> list[dict[str, Any]]:
        responses = self.responses.pop(self.id, [])
        return [self.json_response(r) for r in responses if r is not None]


def format_response(self, resp: Response | dict[str, Any]) -> str:
    if isinstance(resp, Response):
        return f"[{resp.request.method}] - ({resp.status_code}) : {resp.url}"
    return " - ".join(f"{k}: {v}" for k, v in resp.items() if k != "detail")


def format_responses(responses: list[dict[str, Any]]) -> list[str]:
    return [format_response(r) for r in responses]


# must use a global variable so that log_handler is accessible from inside exception
# log_handler = LogCollectionHandler()
# gn_logger.addHandler(log_handler)
# gs_logger.addHandler(log_handler)
