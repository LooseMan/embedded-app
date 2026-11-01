import json
import os

import pytest
from httpx import AsyncClient


def _decode_body(body: bytes):
    if not body:
        return None
    try:
        return json.loads(body)
    except (UnicodeDecodeError, ValueError):
        return body.decode("utf-8", errors="replace")


class RecordingAsyncClient(AsyncClient):
    """AsyncClient that keeps the most recent request/response pair for failures."""

    def __init__(self, *args, **kwargs):
        self.last_interaction = None
        super().__init__(*args, **kwargs)

    async def send(self, request, *args, **kwargs):
        self.last_interaction = {
            "method": request.method,
            "url": str(request.url),
            "req_headers": dict(request.headers),
            "req_body": _decode_body(request.content),
        }
        try:
            response = await super().send(request, *args, **kwargs)
            await response.aread()
        except Exception as error:
            self.last_interaction["error"] = repr(error)
            raise

        self.last_interaction.update(
            status_code=response.status_code,
            res_body=_decode_body(response.content),
        )
        return response


@pytest.fixture
async def client():
    async with RecordingAsyncClient(
        base_url=os.getenv("BACKEND_BASE_URL", "http://localhost:8000"),
    ) as test_client:
        yield test_client
