import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import get_settings


@pytest.mark.e2e
async def test_service_info_available(app_client: AsyncClient) -> None:
    response = await app_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == "FastAPI Microservice Template"


@pytest.mark.e2e
async def test_openapi_docs_available(app_client: AsyncClient) -> None:
    response = await app_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.e2e
async def test_openapi_schema_available(app_client: AsyncClient) -> None:
    response = await app_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "FastAPI Microservice Template"
    schemas = data["components"]["schemas"]
    assert "ErrorEnvelope" in schemas
    assert "TaskListResponse" in schemas
    assert (
        data["paths"]["/api/v1/tasks/"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/TaskListResponse"
    )


@pytest.mark.e2e
async def test_docs_available_when_rate_limit_storage_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OTEL_ENABLED", "false")
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("REDIS_PORT", "1")
    get_settings.cache_clear()

    from app.main import create_app

    app = create_app()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as rate_limited_client:
            docs_response = await rate_limited_client.get("/docs")
            root_response = await rate_limited_client.get("/")
    finally:
        get_settings.cache_clear()

    assert docs_response.status_code == 200
    assert root_response.status_code == 200
