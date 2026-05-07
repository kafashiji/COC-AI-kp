import type { AgentEvent } from "~/types/agent-events"

export type ChatRole = "user" | "assistant" | "system"

export interface ChatTurn {
  role: ChatRole
  content: string
}

function parseSseBlock(block: string): string | null {
  for (const line of block.split("\n")) {
    if (line.startsWith("data:")) {
      return line.slice(5).trimStart()
    }
  }
  return null
}

/**
 * POST /api/chat/stream，按 SSE 解析 PLAN §6 事件（fetch + ReadableStream，非 GET EventSource）。
 */
export async function streamAgentChat(
  apiBase: string,
  messages: ChatTurn[],
  onEvent: (event: AgentEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const url = `${apiBase.replace(/\/$/, "")}/api/chat/stream`
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(text || `HTTP ${res.status}`)
  }
  const reader = res.body?.getReader()
  if (!reader) {
    throw new Error("响应无正文流")
  }
  const decoder = new TextDecoder()
  let buffer = ""
  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }
    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split("\n\n")
    buffer = chunks.pop() ?? ""
    for (const raw of chunks) {
      const payload = parseSseBlock(raw)
      if (!payload) {
        continue
      }
      try {
        onEvent(JSON.parse(payload) as AgentEvent)
      } catch {
        onEvent({ type: "error", message: "无法解析 SSE 数据帧" })
      }
    }
  }
}
