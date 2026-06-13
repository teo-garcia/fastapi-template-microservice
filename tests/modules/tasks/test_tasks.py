import pytest
from httpx import AsyncClient

API_PREFIX = "/api/v1"


def assert_error_envelope(data: dict[str, object], status_code: int, method: str) -> None:
    assert data["success"] is False
    assert data["statusCode"] == status_code
    assert data["method"] == method
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["path"], str)
    assert isinstance(data["message"], str)
    assert isinstance(data["error"], str)
    meta = data["meta"]
    assert isinstance(meta, dict)
    assert isinstance(meta["requestId"], str)


@pytest.mark.e2e
class TestTasksCRUD:
    async def test_create_task(self, client: AsyncClient) -> None:
        response = await client.post(
            f"{API_PREFIX}/tasks/",
            json={"title": "Test task", "description": "A test task", "priority": 3},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test task"
        assert data["description"] == "A test task"
        assert data["status"] == "PENDING"
        assert data["priority"] == 3
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_list_tasks(self, client: AsyncClient) -> None:
        await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task for listing"})
        response = await client.get(f"{API_PREFIX}/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        assert data["meta"]["total"] >= 1
        assert data["meta"]["page"] == 1
        assert data["meta"]["pageSize"] == 20

    async def test_list_tasks_paginates_results(self, client: AsyncClient) -> None:
        await client.post(f"{API_PREFIX}/tasks/", json={"title": "First", "priority": 1})
        await client.post(f"{API_PREFIX}/tasks/", json={"title": "Second", "priority": 2})

        response = await client.get(f"{API_PREFIX}/tasks/?page=1&pageSize=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["meta"] == {"total": 2, "page": 1, "pageSize": 1}

    async def test_list_tasks_supports_status_and_priority_filters(self, client: AsyncClient) -> None:
        await client.post(
            f"{API_PREFIX}/tasks/",
            json={"title": "Low pending", "priority": 1, "status": "PENDING"},
        )
        await client.post(
            f"{API_PREFIX}/tasks/",
            json={"title": "High in progress", "priority": 5, "status": "IN_PROGRESS"},
        )

        response = await client.get(f"{API_PREFIX}/tasks/?status=IN_PROGRESS&priority=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["status"] == "IN_PROGRESS"
        assert data["data"][0]["priority"] >= 5

    async def test_get_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to get"})
        task_id = create_resp.json()["id"]

        response = await client.get(f"{API_PREFIX}/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Task to get"

    async def test_update_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to update"})
        task_id = create_resp.json()["id"]

        response = await client.patch(
            f"{API_PREFIX}/tasks/{task_id}",
            json={"title": "Updated title", "status": "IN_PROGRESS"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["status"] == "IN_PROGRESS"

    async def test_delete_task(self, client: AsyncClient) -> None:
        create_resp = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Task to delete"})
        task_id = create_resp.json()["id"]

        response = await client.delete(f"{API_PREFIX}/tasks/{task_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"{API_PREFIX}/tasks/{task_id}")
        assert get_resp.status_code == 404


@pytest.mark.e2e
class TestTasksValidation:
    async def test_create_task_empty_title_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": ""})
        assert response.status_code == 422
        assert_error_envelope(response.json(), 422, "POST")

    async def test_create_task_missing_title_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"description": "no title"})
        assert response.status_code == 422

    async def test_create_task_invalid_priority_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Bad priority", "priority": 99})
        assert response.status_code == 422

    async def test_create_task_invalid_status_rejected(self, client: AsyncClient) -> None:
        response = await client.post(f"{API_PREFIX}/tasks/", json={"title": "Bad status", "status": "INVALID"})
        assert response.status_code == 422


@pytest.mark.e2e
class TestTasksNotFound:
    async def test_get_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.get(f"{API_PREFIX}/tasks/nonexistent-id")
        assert response.status_code == 404
        assert_error_envelope(response.json(), 404, "GET")

    async def test_update_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.patch(f"{API_PREFIX}/tasks/nonexistent-id", json={"title": "nope"})
        assert response.status_code == 404

    async def test_delete_nonexistent_task(self, client: AsyncClient) -> None:
        response = await client.delete(f"{API_PREFIX}/tasks/nonexistent-id")
        assert response.status_code == 404
