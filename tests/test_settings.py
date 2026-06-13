from app.config.settings import Settings


def test_redis_url_encodes_password() -> None:
    redis_password = "p@ss/word"  # noqa: S105
    settings = Settings(redis_host="redis", redis_password=redis_password)

    assert settings.redis_url == "redis://:p%40ss%2Fword@redis:6379/0"
