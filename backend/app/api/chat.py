import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.config import Settings, get_settings
from app.llm.deepseek import list_deepseek_models, stream_chat_completion
from app.schemas.chat import ChatModelsResponse, ChatStreamRequest, ListedModel

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
            {
                "type": "error",
                "message": "服务器未配置 DEEPSEEK_API_KEY，请在仓库根目录或 backend/.env 中设置（参见 .env.example）。",
            }
        )
        yield _format_sse({"type": "message_end", "id": msg_id})
        return

    api_messages = [{"role": m.role, "content": m.content} for m in body.messages]
    chosen = (body.model or "").strip() or settings.deepseek_model
    try:
        async for delta in stream_chat_completion(settings, api_messages, model=chosen):
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


@router.get("/models", response_model=ChatModelsResponse)
async def chat_models(settings: Settings = Depends(get_settings)) -> ChatModelsResponse:
    default = settings.deepseek_model
    if not settings.deepseek_api_key:
        return ChatModelsResponse(
            default_model=default,
            models=[],
            api_configured=False,
        )
    try:
        raw = await list_deepseek_models(settings)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"拉取模型列表失败: {e}") from e
    return ChatModelsResponse(
        default_model=default,
        models=[ListedModel(id=m["id"], owned_by=m.get("owned_by", "")) for m in raw],
        api_configured=True,
    )
