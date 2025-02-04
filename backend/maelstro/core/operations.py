from typing import Any, Callable
import logging
from logging import Handler
from requests import Response
from requests.exceptions import RequestException
from fastapi import HTTPException
from geonetwork.gn_logger import logger as gn_logger
from geonetwork.exceptions import GnException


gs_logger = logging.getLogger("GeoOperations")
gs_logger.addHandler(logging.StreamHandler())
gs_logger.setLevel(logging.DEBUG)


class ResponseHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.responses: list[Response | None | dict[str, Any]] = []
        self.valid = False

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


def add_gn_handling(app_function: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped_function(self, *args, **kwargs):  # type: ignore
        try:
            result = app_function(self, *args, **kwargs)
            return result
        except GnException as err:
            raise HTTPException(
                err.code,
                {
                    "msg": err.detail.message,
                    "url": err.parent_response.url,
                    "operations": self.response_handler.get_json_responses(),
                    "content": err.detail.info,
                },
            ) from err

    return wrapped_function


def add_gs_handling(app_function: Callable[..., Any]) -> Callable[..., Any]:
    METHODS_TO_LOG = ["get", "post", "put", "delete"]

    if app_function.__name__ in METHODS_TO_LOG:

        def wrapped_function(path, *args, **kwargs):  # type: ignore
            try:
                result = app_function(path, *args, **kwargs)

                gs_logger.debug(
                    "[%s] %s: %s",
                    app_function.__name__,
                    result.status_code,
                    path,
                    extra={"response": result},
                )
                return result
            except RequestException as err:
                gs_logger.debug(
                    "[%s] %s: %s",
                    app_function.__name__,
                    path,
                    err.__class__.__name__,
                    extra={"response": err.request},
                )
                raise HTTPException(
                    status_code=504,
                    detail={
                        "message": f"HTTP error {err.__class__.__name__} at {path}",
                        "info": err,
                    },
                ) from err

        return wrapped_function
    return app_function


class LoggedRequests:
    def __init__(self) -> None:
        self.handler = ResponseHandler()

    def __enter__(self) -> ResponseHandler:
        gn_logger.addHandler(self.handler)
        gs_logger.addHandler(self.handler)
        self.handler.valid = True
        return self.handler

    def __exit__(self, *args: Any) -> None:
        self.handler.valid = False
        gn_logger.removeHandler(self.handler)
        gs_logger.removeHandler(self.handler)
