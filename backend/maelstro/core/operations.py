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
    def __init__(self, hnd_id: None | str = None) -> None:
        super().__init__()
        self._id = hnd_id
        self.responses: dict[str, list[OperationsRecord]] = {}
        self.properties: dict[str, dict[str, Any]] = {}

    @property
    def valid(self) -> bool:
        return self.id in self.responses

    @property
    def id(self) -> str:
        return self._id or str(threading.current_thread().ident) or "0"

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # The response attribute of the record has been added via the `extra` parameter
            # type checking skipped for simplicity
            response = record.response  # type: ignore
            api_record = ApiRecord(
                type="response",
                method=response.request.method,
                status_code=response.status_code,
                url=response.url,
            )
            self.responses[self.id].append(api_record)
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
        self.properties[self.id] = {"start_time": datetime.now()}

    def log_info(self, info: InfoRecord) -> None:
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


def format_response(record: OperationsRecord) -> str:
    if isinstance(record, ApiRecord):
        return f"[{record.method}] - ({record.status_code}) : {record.url}"
    elif isinstance(record, InfoRecord):
        return f"{record.message}: {' - '.join(f'{k}: {v}' for k, v in record.detail.items())}"
        # return " - ".join(f"{k}: {v}" for k, v in record.items() if k != "detail")
    return ""


def format_responses(responses: list[OperationsRecord]) -> list[str]:
    return [format_response(r) for r in responses]


# must use a global variable so that log_handler is accessible from inside exception
# log_handler = LogCollectionHandler()
# gn_logger.addHandler(log_handler)
# gs_logger.addHandler(log_handler)
