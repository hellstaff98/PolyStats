import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_access_denied(client: AsyncClient):

    response = await client.get("/api/v1/subjects/list")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_list_subjects(auth_client: AsyncClient):

    add_resp = await auth_client.post(
        "/api/v1/subjects/add",
        json={"name": "Высшая математика"}
    )
    assert add_resp.status_code == 201

    list_resp = await auth_client.get("/api/v1/subjects/list")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert len(data) > 0
    assert data[0]["name"] == "Высшая математика"


@pytest.mark.asyncio
async def test_delete_subject_cascade(auth_client: AsyncClient):

    sub = await auth_client.post("/api/v1/subjects/add", json={"name": "Физика"})
    sub_id = sub.json()["id"]

    delete_resp = await auth_client.delete(f"/api/v1/subjects/{sub_id}")
    assert delete_resp.status_code == 204