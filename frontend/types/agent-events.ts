/**
 * 与 docs/PLAN.md §6 SSE 事件协议对齐（前端消费）。
 */
export type AgentEvent =
  | { type: "message_start"; id: string }
  | { type: "message_delta"; id: string; content: string }
  | { type: "message_end"; id: string }
  | { type: "tool_call_start"; id: string; name: string; args: Record<string, unknown> }
  | { type: "tool_call_end"; id: string; result: Record<string, unknown> }
  | { type: "state_change"; patch: Record<string, unknown> }
  | { type: "dice_roll"; faces: number; result: number; label: string }
  | { type: "error"; message: string }
