from datetime import datetime
from typing import Any, Optional, Annotated
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: Optional[dict[str, Any]] = {"query_string": {"query": "*"}}
    source_: Optional[list[str]] = Field([], alias="_source")
    from_: Optional[int] = Field(0, alias="from")
    size: Optional[int] = 20


user_response_description = """
User related x-Headers:
- username: User name
- org: User organization
- roles: User roles
- external-authentication: External authentication
- proxy: Proxy
- orgname: Organization name
"""


class UserResponse(BaseModel):
    """
    User related x-Headers:
    - sec_username: User name
    - sec_org: User organization
    - sec_roles: User roles
    - sec_external_authentication: External authentication
    - sec_proxy: Proxy
    - sec_orgname: Organization name
    """

    username: Optional[str]
    org: Optional[str]
    roles: Optional[str]
    external_authentication: Annotated[
        Optional[str], Field(None, serialization_alias="external-authentication")
    ]
    proxy: Optional[str]
    orgname: Optional[str]


class SourcesResponseElement(BaseModel):
    name: str
    url: str


class DestinationsResponseElement(BaseModel):
    name: str
    gn_url: str
    gs_url: str


class RegisteredTransformation(BaseModel):
    xsl_path: str
    description: str


class TransformationResponse(BaseModel):
    registered_transformations: Annotated[
        dict[str, RegisteredTransformation],
        Field({}, serialization_alias="Registered transformations"),
    ]
    transformation_paths: Annotated[
        Optional[dict[str, list[RegisteredTransformation]]],
        Field({}, serialization_alias="Transformation paths"),
    ]


class Metadata(BaseModel):
    title: str
    iso_standard: Optional[str] = ""


class LinkedLayer(BaseModel):
    server_url: str
    name: str
    description: str
    protocol: str


class PreviewGN(BaseModel):
    src: str
    dst: str
    metadata: list[Metadata]


class PreviewGS(BaseModel):
    src: str
    dst: str
    layers: list[str]
    styles: list[str]


class CopyPreview(BaseModel):
    geonetwork_resources: list[PreviewGN]
    geoserver_resources: list[PreviewGS]


class OperationsRecord(BaseModel):
    def string_format(self) -> str:
        return "Generic Record"


class ApiRecord(OperationsRecord):
    type: str
    method: str
    status_code: int
    url: str

    def string_format(self) -> str:
        return ""


class GnApiRecord(ApiRecord):
    type: str = "gn_api"


class GsApiRecord(ApiRecord):
    type: str = "gs_api"


class InfoRecord(OperationsRecord):
    message: str
    detail: dict[str, Any]


class DetailedResponse(BaseModel):
    summary: str
    info: dict[str, Any] = {}
    operations: list[OperationsRecord]


class ExceptionDetail(BaseModel):
    err: str
    status_code: int = 500
    context: str = "src"
    server: str | None = None
    key: str | None = None
    user: str | None = None
    operations: list[dict[str, Any]] = Field(default_factory=lambda: [])


class JsonLogRecord(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    first_name: str
    last_name: str
    status_code: int
    dataset_uuid: str
    src_name: str
    dst_name: str
    src_title: str
    dst_title: str
    copy_meta: bool
    copy_layers: bool
    copy_styles: bool
    details: Optional[list[dict[str, Any]]] = Field(default_factory=lambda: [])


sample_json_log_records = [
    {
        "id": 97,
        "start_time": "2025-02-07T17:00:48.232023",
        "end_time": "2025-02-07T17:00:49.537302",
        "first_name": "",
        "last_name": "",
        "status_code": 200,
        "dataset_uuid": "4d6318d8-de30-4af5-8f37-971c486a0280",
        "src_name": "GeonetworkRennes",
        "dst_name": "CompoLocale",
        "src_title": "Schéma Directeur Vélo Métropolitain de Rennes Métropole",
        "dst_title": "Schéma Directeur Vélo Métropolitain de Rennes Métropole",
        "copy_meta": True,
        "copy_layers": False,
        "copy_styles": False,
        "details": [],
    },
]
