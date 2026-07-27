# APIの処理を定義する

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import insert_api_log
from app.schema import AddRequest, AddResponse
from app.stream_logger import info_log

async def calc_add(
    request: AddRequest,
    db: AsyncSession
) -> AddResponse:
    info_log("start.")
    result = request.a + request.b
    await insert_api_log(db, api="add", phase="post", result="success", message=f"Adding {request.a} and {request.b} is {result}")
    info_log("end.")
    return AddResponse(result=result)
