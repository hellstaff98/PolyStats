import pytest
from httpx import AsyncClient

@pytest.fixture
async def auth_headers(client: AsyncClient):
    user_data = {
        "email": "test_subject_user@example.com",
        "password": "password123",
        "group_name": "5130904/30105"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_add_subject_authorized(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Математика"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Математика"

@pytest.mark.asyncio
async def test_activity_lifecycle(client: AsyncClient, auth_headers):

    sub_res = await client.post("/api/v1/subjects/add", json={"name": "Физика"}, headers=auth_headers)
    subject_id = sub_res.json()["id"]

    act_data = {"name": "Лаба №1", "max_progress": 1}
    act_res = await client.post(f"/api/v1/subjects/{subject_id}/activity-add", json=act_data, headers=auth_headers)
    act_id = act_res.json()["id"]
    assert act_res.json()["current_progress"] == 0

    plus_res = await client.patch(f"/api/v1/subjects/activities/{act_id}/plus", headers=auth_headers)
    assert plus_res.json()["current_progress"] == 1

    over_plus = await client.patch(f"/api/v1/subjects/activities/{act_id}/plus", headers=auth_headers)
    assert over_plus.json()["current_progress"] == 1

    minus_res = await client.patch(f"/api/v1/subjects/activities/{act_id}/minus", headers=auth_headers)
    assert minus_res.json()["current_progress"] == 0