"""SSE 事件载荷（与 docs/PLAN.md §6 对齐）。"""

from typing import Literal, TypeAlias, TypedDict, Union


class MessageStart(TypedDict):
    type: Literal["message_start"]
    id: str


class MessageDelta(TypedDict):
    type: Literal["message_delta"]
    id: str
    content: str


class MessageEnd(TypedDict):
    type: Literal["message_end"]
    id: str


class ToolCallStart(TypedDict):
    type: Literal["tool_call_start"]
    id: str
    name: str
    args: dict[str, object]


class ToolCallEnd(TypedDict):
    type: Literal["tool_call_end"]
    id: str
    result: dict[str, object]


class StateChange(TypedDict):
    type: Literal["state_change"]
    patch: dict[str, object]


class DiceRoll(TypedDict):
    type: Literal["dice_roll"]
    faces: int
    result: int
    label: str


class ErrorEvent(TypedDict):
    type: Literal["error"]
    message: str


AgentEvent: TypeAlias = Union[
    MessageStart,
    MessageDelta,
    MessageEnd,
    ToolCallStart,
    ToolCallEnd,
    StateChange,
    DiceRoll,
    ErrorEvent,
]
