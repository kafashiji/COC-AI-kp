<template>
  <div style="max-width: 840px; margin: 0 auto">
    <n-h1>COC AI Keeper</n-h1>
    <n-p depth="3">阶段一 Week 1：DeepSeek 流式对话（SSE 事件协议）</n-p>

    <n-card title="对话" style="margin-top: 16px">
      <n-space vertical size="large">
        <div
          style="
            min-height: 200px;
            white-space: pre-wrap;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
          "
        >
          {{ assistantText || "（助手回复将出现在此处）" }}
        </div>

        <n-input
          v-model:value="userInput"
          type="textarea"
          placeholder="输入消息…"
          :autosize="{ minRows: 3, maxRows: 8 }"
          :disabled="streaming"
        />

        <n-space>
          <n-button type="primary" :loading="streaming" @click="send">发送</n-button>
          <n-button secondary :disabled="!streaming" @click="abort">停止</n-button>
        </n-space>

        <ChatAgentSteps v-if="steps.length" :events="steps" />
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import {
  NButton,
  NCard,
  NH1,
  NP,
  NInput,
  NSpace,
  useMessage,
} from "naive-ui"
import { ref } from "vue"
import { streamAgentChat } from "~/composables/useAgentStream"
import type { AgentEvent } from "~/types/agent-events"

const config = useRuntimeConfig()
const message = useMessage()

const userInput = ref("你好，用一两句话自我介绍。")
const assistantText = ref("")
const streaming = ref(false)
const steps = ref<AgentEvent[]>([])
let controller: AbortController | null = null

async function send() {
  const content = userInput.value.trim()
  if (!content || streaming.value) {
    return
  }
  assistantText.value = ""
  steps.value = []
  streaming.value = true
  controller = new AbortController()
  const apiBase = config.public.apiBase as string

  try {
    await streamAgentChat(
      apiBase,
      [{ role: "user", content }],
      (ev) => {
        steps.value.push(ev)
        if (ev.type === "message_delta") {
          assistantText.value += ev.content
        }
        if (ev.type === "error") {
          message.error(ev.message)
        }
      },
      controller.signal,
    )
  } catch (e) {
    message.error(e instanceof Error ? e.message : String(e))
  } finally {
    streaming.value = false
    controller = null
  }
}

function abort() {
  controller?.abort()
}
</script>
