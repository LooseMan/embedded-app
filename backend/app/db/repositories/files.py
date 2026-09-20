"""Persistence operations for file-related models."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import File, FileCategory, FileSet, FileSetRel


async def list_file_categories(db: AsyncSession) -> list[FileCategory]:
    return list(
        (await db.scalars(select(FileCategory).order_by(FileCategory.id))).all()
    )


async def get_file_category(db: AsyncSession, category_id: int) -> FileCategory | None:
    return await db.get(FileCategory, category_id)


async def create_file_category(db: AsyncSession, *, name: str) -> FileCategory:
    category = FileCategory(name=name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_file_category(
    db: AsyncSession, category_id: int, *, name: str | None
) -> FileCategory | None:
    category = await get_file_category(db, category_id)
    if category is None:
        return None
    if name is not None:
        category.name = name
    await db.commit()
    await db.refresh(category)
    return category


async def delete_file_category(db: AsyncSession, category_id: int) -> bool:
    category = await get_file_category(db, category_id)
    if category is None:
        return False
    await db.delete(category)
    await db.commit()
    return True


async def list_files(db: AsyncSession) -> list[File]:
    return list((await db.scalars(select(File).order_by(File.id))).all())


async def get_file(db: AsyncSession, file_id: int) -> File | None:
    return await db.get(File, file_id)


async def create_file(
    db: AsyncSession, *, category_id: int, url: str, size: int
) -> File:
    file = File(category_id=category_id, url=url, size=size)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def update_file(
    db: AsyncSession,
    file_id: int,
    *,
    category_id: int | None,
    url: str | None,
    size: int | None,
) -> File | None:
    file = await get_file(db, file_id)
    if file is None:
        return None
    if category_id is not None:
        file.category_id = category_id
    if url is not None:
        file.url = url
    if size is not None:
        file.size = size
    await db.commit()
    await db.refresh(file)
    return file


async def delete_file(db: AsyncSession, file_id: int) -> bool:
    file = await get_file(db, file_id)
    if file is None:
        return False
    await db.delete(file)
    await db.commit()
    return True


async def list_file_sets(db: AsyncSession) -> list[FileSet]:
    return list((await db.scalars(select(FileSet).order_by(FileSet.id))).all())


async def get_file_set(db: AsyncSession, file_set_id: int) -> FileSet | None:
    return await db.get(FileSet, file_set_id)


async def create_file_set(db: AsyncSession, *, name: str) -> FileSet:
    file_set = FileSet(name=name)
    db.add(file_set)
    await db.commit()
    await db.refresh(file_set)
    return file_set


async def update_file_set(
    db: AsyncSession, file_set_id: int, *, name: str | None
) -> FileSet | None:
    file_set = await get_file_set(db, file_set_id)
    if file_set is None:
        return None
    if name is not None:
        file_set.name = name
    await db.commit()
    await db.refresh(file_set)
    return file_set


async def delete_file_set(db: AsyncSession, file_set_id: int) -> bool:
    file_set = await get_file_set(db, file_set_id)
    if file_set is None:
        return False
    await db.delete(file_set)
    await db.commit()
    return True


async def list_files_in_file_set(
    db: AsyncSession, file_set_id: int
) -> list[File]:
    stmt = (
        select(File)
        .join(FileSetRel, FileSetRel.file_id == File.id)
        .where(FileSetRel.file_set_id == file_set_id)
        .order_by(File.id)
    )
    return list((await db.scalars(stmt)).all())


async def list_file_set_relations(db: AsyncSession) -> list[FileSetRel]:
    return list(
        (
            await db.scalars(
                select(FileSetRel).order_by(
                    FileSetRel.file_set_id, FileSetRel.file_id
                )
            )
        ).all()
    )


async def get_file_set_relation(
    db: AsyncSession, file_set_id: int, file_id: int
) -> FileSetRel | None:
    return await db.get(FileSetRel, (file_set_id, file_id))


async def create_file_set_relation(
    db: AsyncSession, *, file_set_id: int, file_id: int
) -> FileSetRel:
    relation = FileSetRel(file_set_id=file_set_id, file_id=file_id)
    db.add(relation)
    await db.commit()
    await db.refresh(relation)
    return relation


async def attach_file_to_file_set(
    db: AsyncSession, *, file_set_id: int, file_id: int
) -> bool:
    relation = await get_file_set_relation(db, file_set_id, file_id)
    if relation is not None:
        return False
    db.add(FileSetRel(file_set_id=file_set_id, file_id=file_id))
    await db.commit()
    return True


async def delete_file_set_relation(
    db: AsyncSession, file_set_id: int, file_id: int
) -> bool:
    relation = await get_file_set_relation(db, file_set_id, file_id)
    if relation is None:
        return False
    await db.execute(
        delete(FileSetRel).where(
            FileSetRel.file_set_id == file_set_id,
            FileSetRel.file_id == file_id,
        )
    )
    await db.commit()
    return True
