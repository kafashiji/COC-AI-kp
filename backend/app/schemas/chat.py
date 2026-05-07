from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1, max_length=32000)


class ChatStreamRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
