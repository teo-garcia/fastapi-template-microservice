from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import TaskStatus
from app.modules.tasks.schemas import CreateTaskSchema, PaginationMeta, TaskListResponse, TaskResponse, UpdateTaskSchema
from app.modules.tasks.service import TasksService
from app.shared.database.engine import get_db
from app.shared.exceptions.schemas import ErrorEnvelope

router = APIRouter(prefix="/tasks", tags=["tasks"])

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorEnvelope},
    422: {"model": ErrorEnvelope},
}


def _get_service(db: AsyncSession = Depends(get_db)) -> TasksService:
    return TasksService(db)


@router.get("/", response_model=TaskListResponse, responses={422: {"model": ErrorEnvelope}})
async def list_tasks(
    status: TaskStatus | None = None,
    priority: int | None = Query(default=None, ge=0, le=10),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    service: TasksService = Depends(_get_service),
) -> TaskListResponse:
    tasks, total = await service.find_all(status=status, priority=priority, page=page, page_size=page_size)
    return TaskListResponse(
        data=[TaskResponse.model_validate(t) for t in tasks],
        meta=PaginationMeta(total=total, page=page, page_size=page_size),
    )


@router.get("/{task_id}", response_model=TaskResponse, responses=ERROR_RESPONSES)
async def get_task(task_id: str, service: TasksService = Depends(_get_service)) -> TaskResponse:
    task = await service.find_one(task_id)
    return TaskResponse.model_validate(task)


@router.post(
    "/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, responses={422: {"model": ErrorEnvelope}}
)
async def create_task(data: CreateTaskSchema, service: TasksService = Depends(_get_service)) -> TaskResponse:
    task = await service.create(data)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse, responses=ERROR_RESPONSES)
async def update_task(
    task_id: str, data: UpdateTaskSchema, service: TasksService = Depends(_get_service)
) -> TaskResponse:
    task = await service.update(task_id, data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorEnvelope}})
async def delete_task(task_id: str, service: TasksService = Depends(_get_service)) -> None:
    await service.delete(task_id)
