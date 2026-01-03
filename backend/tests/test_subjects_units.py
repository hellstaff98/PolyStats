import pytest
from httpx import AsyncClient

@pytest.fixture
async def auth_headers(client: AsyncClient):

    user_data = {
        "email": "unit_test_user@example.com",
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
async def test_subject_lifecycle(client: AsyncClient, auth_headers):

    add_res = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Алгоритмы"},
        headers=auth_headers
    )
    assert add_res.status_code == 201
    subject_id = add_res.json()["id"]
    assert add_res.json()["name"] == "Алгоритмы"

    del_res = await client.delete(f"/api/v1/subjects/{subject_id}", headers=auth_headers)
    assert del_res.status_code == 204

    check_res = await client.get(f"/api/v1/subjects/{subject_id}", headers=auth_headers)
    assert check_res.status_code == 404

@pytest.mark.asyncio
async def test_activity_management(client: AsyncClient, auth_headers):

    sub = await client.post("/api/v1/subjects/add", json={"name": "БД"}, headers=auth_headers)
    s_id = sub.json()["id"]

    act_res = await client.post(
        f"/api/v1/subjects/{s_id}/activity-add",
        json={"name": "Курсовая", "max_progress": 1},
        headers=auth_headers
    )
    assert act_res.status_code == 200
    activity_id = act_res.json()["id"]
    assert act_res.json()["name"] == "Курсовая"

    del_act = await client.delete(f"/api/v1/subjects/activities/{activity_id}", headers=auth_headers)
    assert del_act.status_code == 204

    sub_details = await client.get(f"/api/v1/subjects/{s_id}", headers=auth_headers)
    assert len(sub_details.json()["activities"]) == 0

@pytest.mark.asyncio
async def test_progress_increment_decrement(client: AsyncClient, auth_headers):
    sub = await client.post("/api/v1/subjects/add", json={"name": "Тест Прогресса"}, headers=auth_headers)
    s_id = sub.json()["id"]
    act = await client.post(f"/api/v1/subjects/{s_id}/activity-add",
                           json={"name": "Лабы", "max_progress": 3}, headers=auth_headers)
    a_id = act.json()["id"]

    await client.patch(f"/api/v1/subjects/activities/{a_id}/plus", headers=auth_headers)
    res = await client.patch(f"/api/v1/subjects/activities/{a_id}/plus", headers=auth_headers)
    assert res.json()["current_progress"] == 2

    res = await client.patch(f"/api/v1/subjects/activities/{a_id}/minus", headers=auth_headers)
    assert res.json()["current_progress"] == 1

@pytest.mark.asyncio
async def test_progress_boundaries(client: AsyncClient, auth_headers):
    sub = await client.post("/api/v1/subjects/add", json={"name": "Границы"}, headers=auth_headers)
    s_id = sub.json()["id"]
    act = await client.post(f"/api/v1/subjects/{s_id}/activity-add",
                           json={"name": "Тест", "max_progress": 1}, headers=auth_headers)
    a_id = act.json()["id"]

    await client.patch(f"/api/v1/subjects/activities/{a_id}/minus", headers=auth_headers)
    res_min = await client.get(f"/api/v1/subjects/{s_id}", headers=auth_headers)
    assert res_min.json()["activities"][0]["current_progress"] == 0

    await client.patch(f"/api/v1/subjects/activities/{a_id}/plus", headers=auth_headers)
    await client.patch(f"/api/v1/subjects/activities/{a_id}/plus", headers=auth_headers)
    res_max = await client.get(f"/api/v1/subjects/{s_id}", headers=auth_headers)
    assert res_max.json()["activities"][0]["current_progress"] == 1