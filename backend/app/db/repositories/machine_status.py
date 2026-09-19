"""Persistence operations for machine status."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MachineStatus


async def init_db_data(db: AsyncSession) -> None:
    """Insert the default machine status when it does not exist."""
    stmt = select(MachineStatus).where(
        MachineStatus.module == "ModuleA",
        MachineStatus.unit == "Unit1",
    )
    existing_record = await db.scalar(stmt)
    if existing_record is None:
        db.add(MachineStatus(module="ModuleA", unit="Unit1", status=1))
        await db.commit()
