from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1, max_length=32000)


class ChatStreamRequest(BaseModel):
    """model 不传则使用服务端 DEEPSEEK_MODEL。"""

    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
    model: str | None = Field(default=None, max_length=128)


class ListedModel(BaseModel):
    id: str
    owned_by: str = ""


class ChatModelsResponse(BaseModel):
    default_model: str
    models: list[ListedModel]
    api_configured: bool
