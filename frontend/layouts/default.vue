<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <n-layout content-style="min-height: 100vh; padding: 24px;">
        <slot />
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme, NConfigProvider, NLayout, NMessageProvider } from "naive-ui"
</script>
