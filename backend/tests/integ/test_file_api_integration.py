from uuid import uuid4

import pytest


@pytest.mark.anyio
async def test_file_api_create_update_attach_and_delete(client):
    """Complete the file registration and file-set management business flow."""
    suffix = uuid4().hex
    category_name = f"pytest category {suffix}"
    file_url = f"https://example.com/files/{suffix}.txt"
    file_set_name = f"pytest file set {suffix}"

    category_response = await client.post(
        "/file-categories", json={"name": category_name}
    )
    assert category_response.status_code == 201
    category = category_response.json()
    assert category["name"] == category_name
    category_id = category["id"]

    file_response = await client.post(
        "/files",
        json={"category_id": category_id, "url": file_url, "size": 128},
    )
    assert file_response.status_code == 201
    file = file_response.json()
    assert file["category_id"] == category_id
    assert file["url"] == file_url
    file_id = file["id"]

    file_set_response = await client.post(
        "/file-sets", json={"name": file_set_name}
    )
    assert file_set_response.status_code == 201
    file_set = file_set_response.json()
    assert file_set["name"] == file_set_name
    file_set_id = file_set["id"]

    try:
        assert (await client.get(f"/file-categories/{category_id}")).json() == category
        assert (await client.get(f"/files/{file_id}")).json() == file
        assert (await client.get(f"/file-sets/{file_set_id}")).json() == file_set

        attach_response = await client.put(
            f"/file-sets/{file_set_id}/files/{file_id}"
        )
        assert attach_response.status_code == 204

        files_in_set_response = await client.get(
            f"/file-sets/{file_set_id}/files"
        )
        assert files_in_set_response.status_code == 200
        assert files_in_set_response.json() == [file]

        assert category in (await client.get("/file-categories")).json()
        assert file in (await client.get("/files")).json()
        assert file_set in (await client.get("/file-sets")).json()

        update_category_response = await client.patch(
            f"/file-categories/{category_id}",
            json={"name": f"updated {category_name}"},
        )
        assert update_category_response.status_code == 200
        assert update_category_response.json()["name"] == f"updated {category_name}"

        update_file_response = await client.patch(
            f"/files/{file_id}", json={"size": 256}
        )
        assert update_file_response.status_code == 200
        assert update_file_response.json()["size"] == 256

        update_file_set_response = await client.patch(
            f"/file-sets/{file_set_id}",
            json={"name": f"updated {file_set_name}"},
        )
        assert update_file_set_response.status_code == 200
        assert update_file_set_response.json()["name"] == f"updated {file_set_name}"

        detach_response = await client.delete(
            f"/file-sets/{file_set_id}/files/{file_id}"
        )
        assert detach_response.status_code == 204
        assert (await client.get(f"/file-sets/{file_set_id}/files")).json() == []
    finally:
        await client.delete(f"/file-sets/{file_set_id}")
        await client.delete(f"/files/{file_id}")
        await client.delete(f"/file-categories/{category_id}")

