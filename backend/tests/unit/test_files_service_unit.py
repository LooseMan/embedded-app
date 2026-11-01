from types import SimpleNamespace
from unittest.mock import AsyncMock, ANY, patch

import pytest

from app.api.schemas.files import (
    FileCategoryCreate,
    FileCategoryUpdate,
    FileCreate,
    FileSetCreate,
    FileSetUpdate,
    FileUpdate,
)
from app.services import files as file_service


def _resource(resource_id: int):
    return SimpleNamespace(id=resource_id)


@pytest.mark.anyio
async def test_create_file_category_delegates_name():
    request = FileCategoryCreate(name="documents")
    category = _resource(1)
    with patch.object(file_service.file_repository, "create_file_category", new_callable=AsyncMock, return_value=category) as create:
        result = await file_service.create_file_category(object(), request)

    assert result is category
    create.assert_awaited_once_with(ANY, name="documents")


@pytest.mark.anyio
async def test_update_file_category_delegates_request():
    request = FileCategoryUpdate(name="updated")
    with patch.object(file_service.file_repository, "update_file_category", new_callable=AsyncMock) as update:
        await file_service.update_file_category(object(), 1, request)

    update.assert_awaited_once_with(ANY, 1, name="updated")


@pytest.mark.anyio
async def test_create_and_update_file_delegate_all_fields():
    create_request = FileCreate(category_id=2, url="https://example.com/a", size=10)
    update_request = FileUpdate(category_id=3, url="https://example.com/b", size=20)
    with patch.object(file_service.file_repository, "create_file", new_callable=AsyncMock) as create, patch.object(file_service.file_repository, "update_file", new_callable=AsyncMock) as update:
        await file_service.create_file(object(), create_request)
        await file_service.update_file(object(), 4, update_request)

    create.assert_awaited_once_with(ANY, category_id=2, url=create_request.url, size=10)
    update.assert_awaited_once_with(ANY, 4, category_id=3, url=update_request.url, size=20)


@pytest.mark.anyio
async def test_create_and_update_file_set_delegate_name():
    create_request = FileSetCreate(name="important")
    update_request = FileSetUpdate(name="updated")
    with patch.object(file_service.file_repository, "create_file_set", new_callable=AsyncMock) as create, patch.object(file_service.file_repository, "update_file_set", new_callable=AsyncMock) as update:
        await file_service.create_file_set(object(), create_request)
        await file_service.update_file_set(object(), 5, update_request)

    create.assert_awaited_once_with(ANY, name="important")
    update.assert_awaited_once_with(ANY, 5, name="updated")


@pytest.mark.anyio
async def test_file_set_file_operations_delegate_to_repository():
    with patch.object(file_service.file_repository, "list_files_in_file_set", new_callable=AsyncMock) as list_files, patch.object(file_service.file_repository, "attach_file_to_file_set", new_callable=AsyncMock) as attach, patch.object(file_service.file_repository, "delete_file_set_relation", new_callable=AsyncMock) as detach:
        await file_service.list_files_in_file_set(object(), 5)
        await file_service.attach_file_to_file_set(object(), file_set_id=5, file_id=6)
        await file_service.detach_file_from_file_set(object(), 5, 6)

    list_files.assert_awaited_once_with(ANY, 5)
    attach.assert_awaited_once_with(ANY, file_set_id=5, file_id=6)
    detach.assert_awaited_once_with(ANY, 5, 6)
