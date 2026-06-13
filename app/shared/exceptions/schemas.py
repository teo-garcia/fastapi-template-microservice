from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    request_id: str = Field(..., alias="requestId")


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: Literal[False] = False
    status_code: int = Field(..., alias="statusCode", ge=400)
    timestamp: str
    path: str
    method: str
    message: str | list[str]
    error: str
    errors: Any | None = None
    meta: ErrorMeta | None = None
