from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tasks.models import TaskStatus


class CreateTaskSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=0, ge=0, le=10)


class UpdateTaskSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(None, ge=0, le=10)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., alias="pageSize", ge=1, le=100)


class TaskListResponse(BaseModel):
    data: list[TaskResponse]
    meta: PaginationMeta
