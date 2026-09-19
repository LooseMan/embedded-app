"""Persistence operations for API logs."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APILog


async def insert_api_log(
    db: AsyncSession,
    *,
    api: str,
    phase: str,
    result: str,
    message: str,
) -> None:
    db.add(APILog(api_name=api, phase=phase, result=result, message=message))
    await db.commit()
