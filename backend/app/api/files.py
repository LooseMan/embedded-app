"""File-related CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Response, status

from app.api.dependencies import DatabaseSession
from app.api.schemas.files import (
    FileCategoryCreate,
    FileCategoryResponse,
    FileCategoryUpdate,
    FileCreate,
    FileResponse,
    FileSetCreate,
    FileSetResponse,
    FileSetUpdate,
    FileUpdate,
)
from app.db.repositories import files as file_repository
from app.services import files as file_service


router = APIRouter(prefix="", tags=["files"])


@router.post(
    "/file-categories",
    response_model=FileCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_file_category(
    request: FileCategoryCreate, db: DatabaseSession
) -> FileCategoryResponse:
    return await file_service.create_file_category(db, request)


@router.get("/file-categories", response_model=list[FileCategoryResponse])
async def list_file_categories(db: DatabaseSession) -> list[FileCategoryResponse]:
    return await file_repository.list_file_categories(db)


@router.get(
    "/file-categories/{category_id}", response_model=FileCategoryResponse
)
async def get_file_category(
    category_id: int, db: DatabaseSession
) -> FileCategoryResponse:
    category = await file_repository.get_file_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File category not found",
        )
    return category


@router.patch(
    "/file-categories/{category_id}", response_model=FileCategoryResponse
)
async def update_file_category(
    category_id: int, request: FileCategoryUpdate, db: DatabaseSession
) -> FileCategoryResponse:
    category = await file_service.update_file_category(db, category_id, request)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File category not found",
        )
    return category


@router.delete(
    "/file-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_file_category(category_id: int, db: DatabaseSession) -> Response:
    deleted = await file_repository.delete_file_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File category not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/files",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_file(request: FileCreate, db: DatabaseSession) -> FileResponse:
    return await file_service.create_file(db, request)


@router.get("/files", response_model=list[FileResponse])
async def list_files(db: DatabaseSession) -> list[FileResponse]:
    return await file_repository.list_files(db)


@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: DatabaseSession) -> FileResponse:
    file = await file_repository.get_file(db, file_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return file


@router.patch("/files/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int, request: FileUpdate, db: DatabaseSession
) -> FileResponse:
    file = await file_service.update_file(db, file_id, request)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return file


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, db: DatabaseSession) -> Response:
    deleted = await file_repository.delete_file(db, file_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/file-sets",
    response_model=FileSetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_file_set(
    request: FileSetCreate, db: DatabaseSession
) -> FileSetResponse:
    return await file_service.create_file_set(db, request)


@router.get("/file-sets", response_model=list[FileSetResponse])
async def list_file_sets(db: DatabaseSession) -> list[FileSetResponse]:
    return await file_repository.list_file_sets(db)


@router.get("/file-sets/{file_set_id}", response_model=FileSetResponse)
async def get_file_set(file_set_id: int, db: DatabaseSession) -> FileSetResponse:
    file_set = await file_repository.get_file_set(db, file_set_id)
    if file_set is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File set not found"
        )
    return file_set


@router.patch("/file-sets/{file_set_id}", response_model=FileSetResponse)
async def update_file_set(
    file_set_id: int, request: FileSetUpdate, db: DatabaseSession
) -> FileSetResponse:
    file_set = await file_service.update_file_set(db, file_set_id, request)
    if file_set is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File set not found"
        )
    return file_set


@router.delete("/file-sets/{file_set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_set(file_set_id: int, db: DatabaseSession) -> Response:
    deleted = await file_repository.delete_file_set(db, file_set_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File set not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/file-sets/{file_set_id}/files", response_model=list[FileResponse])
async def list_files_in_file_set(
    file_set_id: int, db: DatabaseSession
) -> list[FileResponse]:
    file_set = await file_repository.get_file_set(db, file_set_id)
    if file_set is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File set not found",
        )
    return await file_service.list_files_in_file_set(db, file_set_id)


@router.delete(
    "/file-sets/{file_set_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def detach_file_from_file_set(
    file_set_id: int, file_id: int, db: DatabaseSession
) -> Response:
    file_set = await file_repository.get_file_set(db, file_set_id)
    file = await file_repository.get_file(db, file_id)
    if file_set is None or file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File set or file not found",
        )
    deleted = await file_service.detach_file_from_file_set(
        db, file_set_id, file_id
    )
    if not deleted:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/file-sets/{file_set_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def attach_file_to_file_set(
    file_set_id: int, file_id: int, db: DatabaseSession
) -> Response:
    file_set = await file_repository.get_file_set(db, file_set_id)
    file = await file_repository.get_file(db, file_id)
    if file_set is None or file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File set or file not found",
        )
    await file_service.attach_file_to_file_set(
        db, file_set_id=file_set_id, file_id=file_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
