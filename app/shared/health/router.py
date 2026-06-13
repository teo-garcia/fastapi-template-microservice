from typing import Any

import structlog
from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.engine import get_db
from app.shared.messaging.nats_client import NatsJetStreamService, get_nats
from app.shared.redis.client import get_redis

router = APIRouter(tags=["health"])
logger = structlog.get_logger("health")


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    nats: NatsJetStreamService = Depends(get_nats),
) -> dict[str, Any]:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="database")
        checks["database"] = "error"

    try:
        await redis.ping()  # type: ignore[misc]
        checks["redis"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="redis")
        checks["redis"] = "error"

    if await nats.is_healthy():
        checks["nats"] = "ok"
    else:
        checks["nats"] = "error"

    is_healthy = all(v == "ok" for v in checks.values())
    response.status_code = 200 if is_healthy else 503
    return {
        "status": "ok" if is_healthy else "error",
        "checks": checks,
    }


@router.get("/health")
async def health(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    nats: NatsJetStreamService = Depends(get_nats),
) -> dict[str, Any]:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="database")
        checks["database"] = "error"

    try:
        await redis.ping()  # type: ignore[misc]
        checks["redis"] = "ok"
    except Exception:
        await logger.awarning("health_check_failed", service="redis")
        checks["redis"] = "error"

    if await nats.is_healthy():
        checks["nats"] = "ok"
    else:
        checks["nats"] = "error"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    response.status_code = 200 if overall == "ok" else 503
    return {"status": overall, "checks": checks}
