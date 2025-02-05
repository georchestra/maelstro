from typing import Any, Optional
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: Optional[dict[str, Any]] = {"query_string": {"query": "*"}}
    source_: Optional[list[str]] = Field([], alias="_source")
    from_: Optional[int] = Field(0, alias="from")
    size: Optional[int] = 20
