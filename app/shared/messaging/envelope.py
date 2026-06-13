from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class JetStreamEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    source: str
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_version: str = Field(alias="dataVersion", default="1")
    data: Any
