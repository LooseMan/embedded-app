"""HTTP router aggregation."""

from fastapi import APIRouter

from app.api import files, health


router = APIRouter()
router.include_router(health.router)
router.include_router(files.router)
