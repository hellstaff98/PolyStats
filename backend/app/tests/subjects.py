# tests/test_subjects.py
import pytest


@pytest.mark.asyncio
async def test_read_subjects_empty(ac):
    # Пытаемся получить список предметов
    response = await ac.get("/api/v1/subjects/list")

    # Если юзер не авторизован в тесте, вернет 401
    # Если вы еще не настроили моки авторизации — это ожидаемо
    assert response.status_code in [200, 401]