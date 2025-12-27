import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import main_app
from core.models import Base, db_helper
from core.authentication.fastapi_users import current_active_user

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def override_current_active_user():
    class MockUser:
        id = 1
        email = "test@example.com"
        is_active = True

    return MockUser()


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    main_app.dependency_overrides[db_helper.session_getter] = override_get_async_session

    async with AsyncClient(app=main_app, base_url="http://test") as ac:
        yield ac

    main_app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(client):
    main_app.dependency_overrides[current_active_user] = override_current_active_user
    yield client
    if current_active_user in main_app.dependency_overrides:
        del main_app.dependency_overrides[current_active_user]