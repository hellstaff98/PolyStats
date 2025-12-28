import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import main_app
from core.models import Base, db_helper

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

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
async def auth_headers(client: AsyncClient):
    user_data = {
        "email": "test_user@example.com",
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