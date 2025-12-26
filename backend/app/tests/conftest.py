import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import main_app
@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр event loop для всей тестовой сессии."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def ac():
    """
    Асинхронный клиент для тестов.
    Использует ASGITransport для прямого взаимодействия с FastAPI без реальных сетевых запросов.
    """
    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test"
    ) as client:
        yield client

# Если захочешь очищать базу между тестами, можно добавить это:
# @pytest.fixture(scope="function", autouse=True)
# async def clear_db():
#     yield
#     # Здесь можно добавить логику очистки конкретных таблиц после каждого теста
#     # Например: await session.execute(text("DELETE FROM subjects"))
