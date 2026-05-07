import type { AgentEvent } from "~/types/agent-events"

export type ChatRole = "user" | "assistant" | "system"

export interface ChatTurn {
  role: ChatRole
  content: string
}

export interface ChatModelsPayload {
  default_model: string
  models: { id: string; owned_by: string }[]
  api_configured: boolean
}

export async function fetchChatModels(apiBase: string): Promise<ChatModelsPayload> {
  const url = `${apiBase.replace(/\/$/, "")}/api/chat/models`
  const res = await fetch(url)
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json() as Promise<ChatModelsPayload>
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
  opts?: { signal?: AbortSignal; model?: string },
): Promise<void> {
  const url = `${apiBase.replace(/\/$/, "")}/api/chat/stream`
  const body: Record<string, unknown> = { messages }
  const m = opts?.model?.trim()
  if (m) {
    body.model = m
  }
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: opts?.signal,
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
    // sse-starlette 以 \r\n 分隔行、以 \r\n\r\n 结束一帧；仅用 \n\n 分割会永远拆不开
    const normalized = buffer.replace(/\r\n/g, "\n")
    const chunks = normalized.split("\n\n")
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
