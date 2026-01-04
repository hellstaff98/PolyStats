from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api import router as api_router
from core.config import settings
from core.models import db_helper, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()

main_app = FastAPI(
    lifespan=lifespan,
    title="PolyStats API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path=settings.api.prefix
)
main_app.include_router(api_router)

@main_app.get('/')
def root():
    return {"message": "приветик", "version": settings.api.v1.prefix}

if __name__ == '__main__':
    uvicorn.run("main:main_app",
                host=settings.run.host,
                port=settings.run.port,
                reload=True)
