"""FastAPI application and HTTP endpoint definitions."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import engine, get_db
from app.model import Base
from app.schema import AddRequest, AddResponse
from app.service import calc_add


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Create application tables when the server starts."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Embedded App API",
    version="1.0.0",
    lifespan=lifespan,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

# OpenAPIの仕様書に表示しないようにする場合は、include_in_schema=Falseを指定します
@router.get(
    "/healthz",
    status_code=status.HTTP_200_OK,
    response_class=Response,
)
async def liveness() -> Response:
    """Return success when the API process is running."""
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/readyz",
    response_class=Response,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"}},
)
async def readiness(db: DatabaseSession) -> Response:
    """Return success only when the database accepts a query."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/add",
    response_model=AddResponse,
    status_code=status.HTTP_200_OK,
    tags=["calculation"],
    summary="Add two integers",
)
async def add(request: AddRequest, db: DatabaseSession) -> AddResponse:
    """Add two integers and record the request."""
    return await calc_add(request, db)


app.include_router(router)
