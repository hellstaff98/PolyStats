import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_student_full_auth_and_progress_scenario(client: AsyncClient):



    user_data = {
        "email": "student@poly.edu",
        "password": "strongpassword123",
        "group_name": "5130904/30105"
    }


    reg_response = await client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201


    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200


    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}


    sub_res = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Физика"},
        headers=headers
    )
    assert sub_res.status_code == 201
    subject_id = sub_res.json()["id"]


    act_res = await client.post(
        f"/api/v1/subjects/{subject_id}/activity-add",
        json={"name": "Лабораторные", "max_progress": 10, "current_progress": 0},
        headers=headers
    )
    activity_id = act_res.json()["id"]

    update_res = await client.patch(
        f"/api/v1/subjects/activities/{activity_id}/plus",
        headers=headers
    )
    assert update_res.status_code == 200

    list_res = await client.get("/api/v1/subjects/list", headers=headers)
    subjects = list_res.json()
    physics = next(s for s in subjects if s["id"] == subject_id)

    assert physics["activities"][0]["current_progress"] == 1
