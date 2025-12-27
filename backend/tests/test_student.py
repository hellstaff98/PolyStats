import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_student_full_auth_and_progress_scenario(client: AsyncClient):
    """
    Сценарий: Регистрация -> Авторизация -> Нахождение предмета -> Обновление прогресса
    """

    # --- 1. РЕГИСТРАЦИЯ ---
    # Данные соответствуют твоей схеме UserCreate
    user_data = {
        "email": "student@poly.edu",
        "password": "strongpassword123",
        "group_name": "5130904/30105"  # Обязательное поле из твоего UserCreate
    }

    # settings.api.v1.auth обычно разворачивается в /api/v1/auth
    # Путь регистрации в FastAPI Users по умолчанию /register
    reg_response = await client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201

    # --- 2. ВХОД (АВТОРИЗАЦИЯ) ---
    # FastAPI Users по умолчанию использует OAuth2 Password Request Form (x-www-form-urlencoded)
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200

    # Получаем токен (если используется JWT)
    # Если ты используешь Cookie транспорт, клиент httpx сам сохранит их
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # --- 3. НАХОЖДЕНИЕ/СОЗДАНИЕ ПРЕДМЕТА ---
    # Создаем предмет от лица этого пользователя
    sub_res = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Физика"},
        headers=headers
    )
    assert sub_res.status_code == 201
    subject_id = sub_res.json()["id"]

    # --- 4. ДОБАВЛЕНИЕ ЛАБОРАТОРНОЙ И ОТМЕТКА ---
    # Добавляем активность
    act_res = await client.post(
        f"/api/v1/subjects/{subject_id}/activity-add",
        json={"name": "Лабораторные", "max_progress": 10, "current_progress": 0},
        headers=headers
    )
    activity_id = act_res.json()["id"]

    # Отмечаем выполнение (Плюс)
    update_res = await client.patch(
        f"/api/v1/subjects/activities/{activity_id}/plus",
        headers=headers
    )
    assert update_res.status_code == 200

    # --- 5. ПРОВЕРКА ПРОГРЕССА И МОТИВАЦИЯ ---
    list_res = await client.get("/api/v1/subjects/list", headers=headers)
    subjects = list_res.json()
    physics = next(s for s in subjects if s["id"] == subject_id)

    # Проверяем, что прогресс изменился
    assert physics["activities"][0]["current_progress"] == 1
    # Если у тебя есть расчет процентов:
    # assert physics["total_progress"] > 0