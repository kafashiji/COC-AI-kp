from collections.abc import AsyncIterator
from openai import AsyncOpenAI

from app.config import Settings


async def stream_chat_completion(
    settings: Settings,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    if not settings.deepseek_api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY")

    client = AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
    stream = await client.chat.completions.create(
        model=settings.deepseek_model,
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
