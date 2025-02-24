from typing import Any
import logging
import threading
from datetime import datetime
from logging import Handler
from requests import Response
from maelstro.common.models import OperationsRecord, ApiRecord, InfoRecord
from maelstro.common.exceptions import MaelstroException


def raise_for_status(response: Response) -> None:
    if 400 <= response.status_code < 600:
        raise MaelstroException(
            err=f"HTTP error in [{response.request.method}] {response.url}",
            status_code=response.status_code,
            context=response.text,
        )


class LogCollectionHandler(Handler):
    def __init__(self, id=None) -> None:
        super().__init__()
        self._id = id
        self.responses: dict[int, list[OperationsRecord]] = {}
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
            api_record = ApiRecord(
                type="response",
                method=record.response.request.method,
                status_code=record.response.status_code,
                url=record.response.url,
            )
            self.responses[self.id].append(api_record)  # type: ignore
        except AttributeError:
            self.responses[self.id].append(
                InfoRecord(
                    message=record.message,
                    detail={"src": "generic logger"},
                )
            )

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

    def pop_json_responses(self) -> list[dict[str, Any]]:
        responses = self.responses.pop(self.id, [])
        return [r.dict() for r in responses if r is not None]


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
