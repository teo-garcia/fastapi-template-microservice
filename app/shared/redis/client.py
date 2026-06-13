from redis.asyncio import Redis

from app.config.settings import get_settings

settings = get_settings()

redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password or None,
    decode_responses=True,
)


def get_redis() -> Redis:
    return redis_client
