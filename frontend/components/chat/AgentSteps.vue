<template>
  <n-card title="事件流（调试）" size="small" embedded>
    <n-scrollbar style="max-height: 240px">
      <n-timeline>
        <n-timeline-item
          v-for="(ev, i) in events"
          :key="i"
          :title="ev.type"
          :content="format(ev)"
          line-type="dashed"
        />
      </n-timeline>
    </n-scrollbar>
  </n-card>
</template>

<script setup lang="ts">
import { NCard, NScrollbar, NTimeline, NTimelineItem } from "naive-ui"
import type { AgentEvent } from "~/types/agent-events"

defineProps<{ events: AgentEvent[] }>()

function format(ev: AgentEvent): string {
  try {
    return JSON.stringify(ev)
  } catch {
    return String(ev)
  }
}
</script>
