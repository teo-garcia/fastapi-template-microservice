import asyncio
import sys

from sqlalchemy import delete

from app.modules.tasks.models import Task, TaskStatus
from app.shared.database.engine import async_session_factory, dispose_engine

SEED_TASKS = [
    {
        "title": "Review onboarding checklist",
        "description": "Confirm the template health, docs, metrics, and task APIs.",
        "status": TaskStatus.PENDING,
        "priority": 3,
    },
    {
        "title": "Ship API contract polish",
        "description": "Validate pagination, errors, and OpenAPI schema examples.",
        "status": TaskStatus.IN_PROGRESS,
        "priority": 7,
    },
    {
        "title": "Archive completed setup",
        "description": "Keep a completed task available for filtering examples.",
        "status": TaskStatus.COMPLETED,
        "priority": 1,
    },
]


async def seed() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(Task))
        session.add_all(Task(**task) for task in SEED_TASKS)
        await session.commit()


async def main() -> None:
    try:
        await seed()
        sys.stdout.write(f"Seeded {len(SEED_TASKS)} tasks\n")
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
