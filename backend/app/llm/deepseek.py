from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import Settings


def _client(settings: Settings) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


async def list_deepseek_models(settings: Settings) -> list[dict[str, str]]:
    if not settings.deepseek_api_key:
        return []
    client = _client(settings)
    page = await client.models.list()
    out: list[dict[str, str]] = []
    for m in page.data:
        ob = getattr(m, "owned_by", None) or ""
        out.append({"id": m.id, "owned_by": ob})
    out.sort(key=lambda x: x["id"])
    return out


async def stream_chat_completion(
    settings: Settings,
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
) -> AsyncIterator[str]:
    if not settings.deepseek_api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY")

    use_model = (model or "").strip() or settings.deepseek_model
    client = _client(settings)
    stream = await client.chat.completions.create(
        model=use_model,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        choice = chunk.choices[0]
        delta = choice.delta
        content = getattr(delta, "content", None)
        if content:
            yield content
        # finish_reason == "stop" 时仍可能没有最后的空 delta；由调用方发 message_end
