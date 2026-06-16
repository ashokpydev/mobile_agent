from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Privacy-first mobile security assistant for Android risk analysis.",
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "version": settings.app_version, "status": "ready"}

