import { setup } from "@css-render/vue3-ssr"
import { defineNuxtPlugin } from "#app"

export default defineNuxtPlugin((nuxtApp) => {
  if (!import.meta.server) {
    return
  }
  const { collect } = setup(nuxtApp.vueApp)
  const ssr = nuxtApp.ssrContext
  if (!ssr) {
    return
  }
  const original = ssr.renderMeta
  ssr.renderMeta = () => {
    const resolved = original?.() ?? {}
    const merge = (meta: Record<string, unknown>) => ({
      ...meta,
      headTags: `${meta.headTags ?? ""}${collect()}`,
    })
    if (resolved && typeof (resolved as Promise<unknown>).then === "function") {
      return (resolved as Promise<Record<string, unknown>>).then(merge)
    }
    return merge(resolved as Record<string, unknown>)
  }
})
