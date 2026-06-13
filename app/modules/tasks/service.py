from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import Task, TaskStatus
from app.modules.tasks.schemas import CreateTaskSchema, UpdateTaskSchema

type TaskListResult = tuple[list[Task], int]


class TasksService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_all(
        self,
        status: TaskStatus | None = None,
        priority: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TaskListResult:
        query = select(Task)
        count_query = select(func.count()).select_from(Task)

        if status is not None:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)

        if priority is not None:
            query = query.where(Task.priority >= priority)
            count_query = count_query.where(Task.priority >= priority)

        total_result = await self.db.execute(count_query)
        total = int(total_result.scalar_one())
        result = await self.db.execute(
            query.order_by(Task.priority.desc(), Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def find_one(self, task_id: str) -> Task:
        task = await self.db.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    async def create(self, data: CreateTaskSchema) -> Task:
        task = Task(**data.model_dump())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: str, data: UpdateTaskSchema) -> Task:
        task = await self.find_one(task_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: str) -> None:
        task = await self.find_one(task_id)
        await self.db.delete(task)
        await self.db.commit()
