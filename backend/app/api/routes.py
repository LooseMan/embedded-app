"""HTTP route definitions."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AddRequest, AddResponse
from app.db.session import get_db
from app.services.calculation import calc_add


router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/healthz", status_code=status.HTTP_200_OK, response_class=Response)
async def liveness() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/readyz",
    response_class=Response,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"}},
)
async def readiness(db: DatabaseSession) -> Response:
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
    return await calc_add(request, db)
