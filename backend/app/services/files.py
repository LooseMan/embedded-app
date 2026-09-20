"""Use cases for file-related resources."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.files import (
    FileCategoryCreate,
    FileCategoryUpdate,
    FileCreate,
    FileSetCreate,
    FileSetUpdate,
    FileUpdate,
)
from app.db.repositories import files as file_repository


async def create_file_category(db: AsyncSession, request: FileCategoryCreate):
    return await file_repository.create_file_category(db, name=request.name)


async def update_file_category(
    db: AsyncSession, category_id: int, request: FileCategoryUpdate
):
    return await file_repository.update_file_category(
        db, category_id, name=request.name
    )


async def create_file(db: AsyncSession, request: FileCreate):
    return await file_repository.create_file(
        db,
        category_id=request.category_id,
        url=request.url,
        size=request.size,
    )


async def update_file(db: AsyncSession, file_id: int, request: FileUpdate):
    return await file_repository.update_file(
        db,
        file_id,
        category_id=request.category_id,
        url=request.url,
        size=request.size,
    )


async def create_file_set(db: AsyncSession, request: FileSetCreate):
    return await file_repository.create_file_set(db, name=request.name)


async def update_file_set(
    db: AsyncSession, file_set_id: int, request: FileSetUpdate
):
    return await file_repository.update_file_set(
        db, file_set_id, name=request.name
    )


async def list_files_in_file_set(db: AsyncSession, file_set_id: int):
    return await file_repository.list_files_in_file_set(db, file_set_id)


async def attach_file_to_file_set(
    db: AsyncSession, *, file_set_id: int, file_id: int
):
    return await file_repository.attach_file_to_file_set(
        db, file_set_id=file_set_id, file_id=file_id
    )


async def detach_file_from_file_set(
    db: AsyncSession, file_set_id: int, file_id: int
):
    return await file_repository.delete_file_set_relation(db, file_set_id, file_id)
