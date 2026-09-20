"""Health and readiness endpoints."""

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.dependencies import DatabaseSession


router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK, response_class=Response)
async def liveness() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/readyz",
    response_class=Response,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Database unavailable"
        }
    },
)
async def readiness(db: DatabaseSession) -> Response:
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(status_code=status.HTTP_200_OK)
