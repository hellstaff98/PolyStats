import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_access_denied(client: AsyncClient):
    response = await client.get("/api/v1/subjects/list")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_list_subjects(client: AsyncClient, auth_headers):
    subject_name = "Высшая математика"

    add_resp = await client.post(
        "/api/v1/subjects/add",
        json={"name": subject_name},
        headers=auth_headers
    )
    assert add_resp.status_code == 201

    list_resp = await client.get("/api/v1/subjects/list", headers=auth_headers)
    assert list_resp.status_code == 200

    data = list_resp.json()

    names = [item["name"] for item in data]
    assert subject_name in names, f"Предмет {subject_name} не найден в списке {names}"


@pytest.mark.asyncio
async def test_delete_subject_cascade(client: AsyncClient, auth_headers):

    sub = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Физика на удаление"},
        headers=auth_headers
    )
    sub_id = sub.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/subjects/{sub_id}",
        headers=auth_headers
    )
    assert delete_resp.status_code == 204

    list_resp = await client.get("/api/v1/subjects/list", headers=auth_headers)
    names = [item["name"] for item in list_resp.json()]
    assert "Физика на удаление" not in names