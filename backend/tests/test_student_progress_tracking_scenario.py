import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Проверка доступности API"""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "приветик"}


@pytest.mark.asyncio
async def test_add_subject(client: AsyncClient):
    """Проверка создания предмета"""
    response = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Математика"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Математика"


@pytest.mark.asyncio
async def test_get_subjects_list(client: AsyncClient):
    """Проверка получения списка предметов"""
    await client.post("/api/v1/subjects/add", json={"name": "Программирование"})

    response = await client.get("/api/v1/subjects/list")
    assert response.status_code == 200
    data = response.json()
    assert any(s["name"] == "Программирование" for s in data)


@pytest.mark.asyncio
async def test_delete_subject(client: AsyncClient):
    """Проверка удаления предмета"""
    # Создаем
    create_res = await client.post("/api/v1/subjects/add", json={"name": "На удаление"})
    subject_id = create_res.json()["id"]

    # Удаляем
    response = await client.delete(f"/api/v1/subjects/{subject_id}")
    assert response.status_code == 204

    # Проверяем, что больше не существует
    check_res = await client.get(f"/api/v1/subjects/{subject_id}")
    assert check_res.status_code == 404


@pytest.mark.asyncio
async def test_student_progress_tracking_scenario(client: AsyncClient):
    """
    Сценарий 2: Ежедневное обновление прогресса.
    Проверяет цепочку: Создание предмета -> Добавление активности -> Инкремент прогресса.
    """
    # 1. Студент добавляет предмет
    subject_res = await client.post("/api/v1/subjects/add", json={"name": "Экономика"})
    subject_id = subject_res.json()["id"]

    # 2. Студент добавляет активность (например, Лабораторные, всего 3)
    activity_data = {
        "name": "Лабораторные",
        "max_progress": 3,
        "current_progress": 0
    }
    act_res = await client.post(f"/api/v1/subjects/{subject_id}/activity-add", json=activity_data)
    activity_id = act_res.json()["id"]

    # 3. Студент отмечает выполнение одной работы (нажимает "Плюс")
    update_res = await client.patch(f"/api/v1/subjects/activities/{activity_id}/plus")
    assert update_res.status_code == 200

    # 4. Проверка: прогресс увеличился
    updated_data = update_res.json()
    assert updated_data["current_progress"] == 1

    # 5. Проверка: прогресс отображается в общем списке
    list_res = await client.get("/api/v1/subjects/list")
    subjects = list_res.json()
    economy = next(s for s in subjects if s["id"] == subject_id)
    assert economy["activities"][0]["current_progress"] == 1