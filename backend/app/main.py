"""FastAPI application assembly."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan hook; schema changes are managed by Alembic."""
    yield

app = FastAPI(
    title="Embedded App API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
