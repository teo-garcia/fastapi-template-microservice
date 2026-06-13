from functools import lru_cache
from urllib.parse import quote

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "FastAPI Microservice Template"
    app_version: str = "1"
    debug: bool = False
    port: int = 8000
    api_prefix: str = "/api/v1"
    shutdown_timeout: int = 10

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_microservice"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_ttl: int = 3600

    # NATS JetStream
    nats_url: str = "nats://localhost:4222"
    nats_client_name: str = "fastapi-template-microservice"
    nats_subject_prefix: str = "templates"
    nats_stream_prefix: str = "template"
    nats_timeout: float = 5.0
    nats_ack_wait_seconds: float = 30.0
    nats_max_messages: int = 10_000
    nats_max_deliver: int = 3
    nats_max_reconnect_attempts: int = 10
    nats_reconnect_time_wait: float = 2.0

    # Logging
    log_level: str = "info"
    log_json: bool = True

    # CORS
    cors_enabled: bool = True
    cors_origin: str = "http://localhost:3000"

    # Rate limiting
    throttle_limit: str = "100/minute"

    # Metrics
    metrics_enabled: bool = True

    # Tracing
    otel_enabled: bool = True
    otel_service_name: str = "fastapi-template-microservice"
    otel_exporter_otlp_traces_endpoint: str = "http://localhost:4318/v1/traces"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations (replaces asyncpg with psycopg)."""
        return self.database_url.replace("+asyncpg", "")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        """Redis URL shared by app clients and rate-limit storage."""
        password = f":{quote(self.redis_password, safe='')}@" if self.redis_password else ""
        return f"redis://{password}{self.redis_host}:{self.redis_port}/0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
