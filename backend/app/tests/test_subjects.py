import pytest


@pytest.mark.asyncio
async def test_read_subjects_minimal(ac):
    """
    Простейшая проверка эндпоинта:
    1. Эндпоинт существует.
    2. Он возвращает успешный статус (200) или требует авторизации (401).
    3. Ответ является валидным JSON-ом.
    """
    print("\n=== STARTING MINIMAL API TEST ===")

    # Делаем запрос к вашему API
    response = await ac.get("/api/v1/subjects/list")

    print(f"DEBUG: Status Code = {response.status_code}")
    print(f"DEBUG: Response JSON = {response.json()}")

    # Проверяем, что API вообще работает
    # Мы допускаем 401, если система защиты уже работает,
    # или 200, если доступ открыт или мок сработал.
    assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"

    # Если 200, проверяем, что вернулся список
    if response.status_code == 200:
        assert isinstance(response.json(), list)
        print("✓ API is up and returned a valid list")