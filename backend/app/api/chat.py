import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.config import Settings, get_settings
from app.llm.deepseek import stream_chat_completion
from app.schemas.chat import ChatStreamRequest

router = APIRouter()


def _format_sse(data: dict[str, object]) -> dict[str, str]:
    return {"data": json.dumps(data, ensure_ascii=False)}


async def _chat_stream(
    body: ChatStreamRequest,
    settings: Settings,
) -> AsyncIterator[dict[str, str]]:
    msg_id = str(uuid.uuid4())
    yield _format_sse({"type": "message_start", "id": msg_id})

    if not settings.deepseek_api_key:
        yield _format_sse(
            {"type": "error", "message": "服务器未配置 DEEPSEEK_API_KEY，请在 backend/.env 中设置。"}
        )
        yield _format_sse({"type": "message_end", "id": msg_id})
        return

    api_messages = [{"role": m.role, "content": m.content} for m in body.messages]
    try:
        async for delta in stream_chat_completion(settings, api_messages):
            if delta:
                yield _format_sse({"type": "message_delta", "id": msg_id, "content": delta})
    except Exception as e:  # noqa: BLE001 — 流式端点需将错误写入 SSE
        yield _format_sse({"type": "error", "message": str(e)})

    yield _format_sse({"type": "message_end", "id": msg_id})


@router.post("/stream")
async def chat_stream(
    body: ChatStreamRequest,
    settings: Settings = Depends(get_settings),
) -> EventSourceResponse:
    return EventSourceResponse(_chat_stream(body, settings))
