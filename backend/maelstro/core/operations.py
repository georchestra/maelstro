from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator
import logging
from uuid import UUID, uuid4
from datetime import datetime
from logging import Handler
from requests import Response
from maelstro.common.models import (
    OperationsRecord,
    ApiRecord,
    GnApiRecord,
    GsApiRecord,
    InfoRecord,
    context_type,
)
from maelstro.common.exceptions import MaelstroException


def raise_for_status(response: Response) -> None:
    if 400 <= response.status_code < 600:
        raise MaelstroException(
            err=f"HTTP error in [{response.request.method}] {response.url}",
            status_code=response.status_code,
            context=response.text,
        )


logger_uuid: ContextVar[UUID] = ContextVar("logger_uuid")


class LogCollectionHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.responses: list[OperationsRecord] = []
        self.properties: dict[str, Any] = {"start_time": datetime.now()}
        self.context: context_type = "General"
        self.id = uuid4()
        logger_uuid.set(self.id)

    @contextmanager
    def logger_context(self, new_context: context_type) -> Iterator[Any]:
        old_context = self.context
        self.context = new_context
        yield self
        self.context = old_context

    def emit(self, record: logging.LogRecord) -> None:
        current_uuid = logger_uuid.get()
        if current_uuid != self.id:
            # Discard log message from different context / thread /request
            return
        try:
            # The response attribute of the record has been added via the `extra` parameter
            # type checking skipped for simplicity
            response = record.response  # type: ignore
            #                           # AttributeError if record has no response
            record_class = ApiRecord
            if record.name == "GN Session":
                record_class = GnApiRecord
            elif record.name == "GS Session":
                record_class = GsApiRecord

            api_record = record_class(
                method=response.request.method,
                status_code=response.status_code,
                url=response.url,
                data_type=self.context,
            )
            self.responses.append(api_record)
        except AttributeError:
            self.responses.append(
                InfoRecord(
                    message=record.message,
                    detail={"src": "generic logger"},
                )
            )

    def log_info(self, info: InfoRecord) -> None:
        info.data_type = self.context
        self.responses.append(info)

    def set_property(self, key: str, value: Any) -> None:
        self.properties[key] = value

    def get_properties(self) -> dict[str, Any]:
        return self.properties

    def get_json_responses(self) -> list[dict[str, Any]]:
        return [
            r.model_dump() if isinstance(r, OperationsRecord) else r
            for r in self.responses
        ]
