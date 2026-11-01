from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api import files as file_api
from app.api.schemas.files import (
    FileCategoryCreate,
    FileCategoryUpdate,
    FileCreate,
    FileSetCreate,
    FileSetUpdate,
    FileUpdate,
)


def _resource(resource_id: int, **values):
    return SimpleNamespace(id=resource_id, **values)


@pytest.mark.anyio
async def test_create_file_category_calls_service():
    request = FileCategoryCreate(name="documents")
    category = _resource(1, name=request.name)
    with patch.object(file_api.file_service, "create_file_category", new_callable=AsyncMock) as create:
        create.return_value = category

        result = await file_api.create_file_category(request, object())

    assert result is category
    create.assert_awaited_once_with(ANY, request)


@pytest.mark.anyio
async def test_list_file_categories_calls_repository():
    categories = [_resource(1, name="documents")]
    with patch.object(file_api.file_repository, "list_file_categories", new_callable=AsyncMock) as list_categories:
        list_categories.return_value = categories

        result = await file_api.list_file_categories(object())

    assert result == categories


@pytest.mark.anyio
async def test_get_file_category_returns_category():
    category = _resource(1, name="documents")
    with patch.object(file_api.file_repository, "get_file_category", new_callable=AsyncMock) as get_category:
        get_category.return_value = category

        result = await file_api.get_file_category(1, object())

    assert result is category
    get_category.assert_awaited_once_with(ANY, 1)


@pytest.mark.anyio
async def test_get_file_category_raises_404_when_missing():
    with patch.object(file_api.file_repository, "get_file_category", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as error:
            await file_api.get_file_category(1, object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_update_file_category_calls_service():
    request = FileCategoryUpdate(name="updated")
    category = _resource(1, name=request.name)
    with patch.object(file_api.file_service, "update_file_category", new_callable=AsyncMock, return_value=category) as update:
        result = await file_api.update_file_category(1, request, object())

    assert result is category
    update.assert_awaited_once_with(ANY, 1, request)


@pytest.mark.anyio
async def test_update_file_category_raises_404_when_missing():
    with patch.object(file_api.file_service, "update_file_category", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as error:
            await file_api.update_file_category(1, FileCategoryUpdate(), object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_delete_file_category_returns_204():
    with patch.object(file_api.file_repository, "delete_file_category", new_callable=AsyncMock, return_value=True) as delete:
        result = await file_api.delete_file_category(1, object())

    assert result.status_code == 204
    delete.assert_awaited_once_with(ANY, 1)


@pytest.mark.anyio
async def test_delete_file_category_raises_404_when_missing():
    with patch.object(file_api.file_repository, "delete_file_category", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as error:
            await file_api.delete_file_category(1, object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_create_file_calls_service():
    request = FileCreate(category_id=2, url="https://example.com/a.txt", size=10)
    file = _resource(1, category_id=2, url=request.url, size=10)
    with patch.object(file_api.file_service, "create_file", new_callable=AsyncMock, return_value=file) as create:
        result = await file_api.create_file(request, object())

    assert result is file
    create.assert_awaited_once_with(ANY, request)


@pytest.mark.anyio
async def test_list_and_get_file():
    file = _resource(1, category_id=2, url="https://example.com/a.txt", size=10)
    with patch.object(file_api.file_repository, "list_files", new_callable=AsyncMock, return_value=[file]), patch.object(file_api.file_repository, "get_file", new_callable=AsyncMock, return_value=file) as get_file:
        assert await file_api.list_files(object()) == [file]
        assert await file_api.get_file(1, object()) is file

    get_file.assert_awaited_once_with(ANY, 1)


@pytest.mark.anyio
async def test_get_file_raises_404_when_missing():
    with patch.object(file_api.file_repository, "get_file", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as error:
            await file_api.get_file(1, object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_update_and_delete_file():
    request = FileUpdate(size=20)
    file = _resource(1, category_id=2, url="https://example.com/a.txt", size=20)
    with patch.object(file_api.file_service, "update_file", new_callable=AsyncMock, return_value=file) as update, patch.object(file_api.file_repository, "delete_file", new_callable=AsyncMock, return_value=True) as delete:
        assert await file_api.update_file(1, request, object()) is file
        assert (await file_api.delete_file(1, object())).status_code == 204

    update.assert_awaited_once_with(ANY, 1, request)
    delete.assert_awaited_once_with(ANY, 1)


@pytest.mark.anyio
async def test_update_file_raises_404_when_missing():
    with patch.object(file_api.file_service, "update_file", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as error:
            await file_api.update_file(1, FileUpdate(), object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_delete_file_raises_404_when_missing():
    with patch.object(file_api.file_repository, "delete_file", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as error:
            await file_api.delete_file(1, object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_create_list_get_update_and_delete_file_set():
    request = FileSetCreate(name="important")
    update_request = FileSetUpdate(name="updated")
    file_set = _resource(1, name="important")
    updated = _resource(1, name="updated")
    with patch.object(file_api.file_service, "create_file_set", new_callable=AsyncMock, return_value=file_set) as create, patch.object(file_api.file_repository, "list_file_sets", new_callable=AsyncMock, return_value=[file_set]), patch.object(file_api.file_repository, "get_file_set", new_callable=AsyncMock, return_value=file_set), patch.object(file_api.file_service, "update_file_set", new_callable=AsyncMock, return_value=updated) as update, patch.object(file_api.file_repository, "delete_file_set", new_callable=AsyncMock, return_value=True) as delete:
        assert await file_api.create_file_set(request, object()) is file_set
        assert await file_api.list_file_sets(object()) == [file_set]
        assert await file_api.get_file_set(1, object()) is file_set
        assert await file_api.update_file_set(1, update_request, object()) is updated
        assert (await file_api.delete_file_set(1, object())).status_code == 204

    create.assert_awaited_once_with(ANY, request)
    update.assert_awaited_once_with(ANY, 1, update_request)
    delete.assert_awaited_once_with(ANY, 1)


@pytest.mark.anyio
async def test_get_and_update_file_set_raise_404_when_missing():
    with patch.object(file_api.file_repository, "get_file_set", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as get_error:
            await file_api.get_file_set(1, object())
    with patch.object(file_api.file_service, "update_file_set", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as update_error:
            await file_api.update_file_set(1, FileSetUpdate(), object())

    assert get_error.value.status_code == 404
    assert update_error.value.status_code == 404


@pytest.mark.anyio
async def test_delete_file_set_raises_404_when_missing():
    with patch.object(file_api.file_repository, "delete_file_set", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as error:
            await file_api.delete_file_set(1, object())

    assert error.value.status_code == 404


@pytest.mark.anyio
async def test_file_set_file_relationship_endpoints():
    file_set = _resource(1, name="important")
    file = _resource(2, category_id=3, url="https://example.com/a.txt", size=10)
    with patch.object(file_api.file_repository, "get_file_set", new_callable=AsyncMock, return_value=file_set), patch.object(file_api.file_repository, "get_file", new_callable=AsyncMock, return_value=file), patch.object(file_api.file_service, "list_files_in_file_set", new_callable=AsyncMock, return_value=[file]), patch.object(file_api.file_service, "attach_file_to_file_set", new_callable=AsyncMock) as attach, patch.object(file_api.file_service, "detach_file_from_file_set", new_callable=AsyncMock, return_value=True) as detach:
        assert await file_api.list_files_in_file_set(1, object()) == [file]
        assert (await file_api.attach_file_to_file_set(1, 2, object())).status_code == 204
        assert (await file_api.detach_file_from_file_set(1, 2, object())).status_code == 204

    attach.assert_awaited_once_with(ANY, file_set_id=1, file_id=2)
    detach.assert_awaited_once_with(ANY, 1, 2)


@pytest.mark.anyio
async def test_file_set_relationship_endpoints_raise_404_when_resource_missing():
    with patch.object(file_api.file_repository, "get_file_set", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as list_error:
            await file_api.list_files_in_file_set(1, object())
    with patch.object(file_api.file_repository, "get_file_set", new_callable=AsyncMock, return_value=None), patch.object(file_api.file_repository, "get_file", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as attach_error:
            await file_api.attach_file_to_file_set(1, 2, object())
        with pytest.raises(HTTPException) as detach_error:
            await file_api.detach_file_from_file_set(1, 2, object())

    assert list_error.value.status_code == 404
    assert attach_error.value.status_code == 404
    assert detach_error.value.status_code == 404
