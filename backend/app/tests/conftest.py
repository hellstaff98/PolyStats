import pytest
import asyncio
import os
import sys
import importlib
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from fastapi import FastAPI

# Гарантируем, что /app в путях
sys.path.insert(0, '/app')


def get_application() -> FastAPI:
    """Динамический импорт приложения."""
    try:
        # Попробуем несколько путей импорта
        try:
            mod = importlib.import_module("main")
            app = getattr(mod, "main_app", None)
            if isinstance(app, FastAPI):
                return app
        except ImportError:
            pass

        try:
            mod = importlib.import_module("core.main")
            for attr in dir(mod):
                instance = getattr(mod, attr)
                if isinstance(instance, FastAPI):
                    return instance
        except ImportError:
            pass

        # Если не нашли, создаем пустое приложение
        return FastAPI()
    except Exception as e:
        print(f"✗ Error loading app: {e}")
        return FastAPI()


fastapi_app = get_application()

# --- Настройка БД ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@test_db:5432/app"
)
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# --- Фикстуры ---
@pytest.fixture(scope="session")
def event_loop():
    """Управление циклом событий."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Сессия БД для теста."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def ac(db_session):
    """Асинхронный клиент с подменой авторизации."""

    # Пробуем импортировать зависимости
    try:
        from core.database import get_db
        get_db_func = get_db
    except ImportError:
        async def get_db_func():
            yield db_session

    try:
        from api.deps import get_current_user
        get_current_user_func = get_current_user
    except ImportError:
        async def get_current_user_func():
            # Возвращаем тестового пользователя
            return {"id": 1, "username": "test_user", "is_active": True}

    # Подменяем зависимости
    fastapi_app.dependency_overrides[get_db_func] = lambda: db_session
    fastapi_app.dependency_overrides[get_current_user_func] = get_current_user_func

    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client

    # Очищаем подмены после теста
    fastapi_app.dependency_overrides.clear()