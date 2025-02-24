from typing import Any
from fastapi import HTTPException
from dataclasses import dataclass, asdict, field


@dataclass
class MaelstroDetail:
    err: str
    status_code: int = 500
    context: str = "src"
    server: str | None = None
    key: str | None = None
    user: str | None = None
    operations: list[dict[str, Any]] = field(default_factory=lambda: [])

    def asdict(self) -> dict[str, str | int | None]:
        return asdict(self)


class MaelstroException(HTTPException):
    def __init__(self, err_detail: MaelstroDetail):
        super().__init__(err_detail.status_code, err_detail.asdict())


class AuthError(MaelstroException):
    def __init__(self, err_detail: MaelstroDetail):
        err_detail.status_code = 401
        super().__init__(err_detail)


class UrlError(MaelstroException):
    def __init__(self, err_detail: MaelstroDetail):
        err_detail.status_code = 404
        super().__init__(err_detail)


class ParamError(MaelstroException):
    def __init__(self, err_detail: MaelstroDetail):
        err_detail.status_code = 400
        super().__init__(err_detail)
