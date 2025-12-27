import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "приветик"}


@pytest.mark.asyncio
async def test_add_subject(client):
    # Создание предмета
    response = await client.post(
        "/api/v1/subjects/add",
        json={"name": "Математика"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Математика"


@pytest.mark.asyncio
async def test_get_subjects_list(client):
    # Добавим предмет и проверим список
    await client.post("/api/v1/subjects/add", json={"name": "Программирование"})

    response = await client.get("/api/v1/subjects/list")
    assert response.status_code == 200
    data = response.json()
    assert any(s["name"] == "Программирование" for s in data)


@pytest.mark.asyncio
async def test_delete_subject(client):
    # Создаем предмет
    create_res = await client.post("/api/v1/subjects/add", json={"name": "На удаление"})
    subject_id = create_res.json()["id"]

    # Удаляем
    del_res = await client.get(f"/api/v1/subjects/{subject_id}")  # Сначала проверим наличие
    assert del_res.status_code == 200

    response = await client.delete(f"/api/v1/subjects/{subject_id}")
    assert response.status_code == 204