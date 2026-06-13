from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config.settings import get_settings
from app.modules.tasks.router import router as tasks_router
from app.shared.database.engine import dispose_engine
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.health.router import router as health_router
from app.shared.logging.config import configure_logging
from app.shared.messaging.nats_client import nats_service
from app.shared.metrics.middleware import MetricsMiddleware
from app.shared.metrics.router import router as metrics_router
from app.shared.middleware.logging_mw import LoggingMiddleware
from app.shared.middleware.request_id import RequestIdMiddleware
from app.shared.middleware.security_headers import SecurityHeadersMiddleware
from app.shared.redis.client import redis_client
from app.shared.telemetry import configure_telemetry, shutdown_telemetry

logger = structlog.get_logger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_output=settings.log_json)
    await logger.ainfo("starting", app=settings.app_name, version=settings.app_version)
    yield
    await logger.ainfo("shutting_down")
    await nats_service.close()
    await redis_client.aclose()
    await dispose_engine()
    shutdown_telemetry()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    configure_telemetry(settings, app)

    # Middleware stack (last added = first executed)
    if settings.metrics_enabled:
        app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.cors_origin],
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_credentials=True,
            allow_headers=["*"],
        )

    # Rate limiting
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.throttle_limit],
        storage_uri=settings.redis_url,
        in_memory_fallback_enabled=True,
        swallow_errors=True,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Exception handlers
    register_exception_handlers(app)

    @app.get("/")
    async def service_info() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "status": "ok",
            "version": settings.app_version,
        }

    # Routers (health and metrics are outside the API prefix)
    app.include_router(health_router)
    if settings.metrics_enabled:
        app.include_router(metrics_router)
    app.include_router(tasks_router, prefix=settings.api_prefix)

    return app


app = create_app()
