<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 },
  size: { type: Number, default: 30 },
})

const r = computed(() => (props.size - 4) / 2)
const C = computed(() => 2 * Math.PI * r.value)
const fill = computed(() => (Math.min(10, Math.max(0, props.score)) / 10) * C.value)
const gap = computed(() => C.value - fill.value)
const color = computed(() => {
  const s = props.score
  if (s >= 8.5) return 'var(--succ)'
  if (s >= 6.5) return 'var(--acc)'
  if (s >= 5)   return 'var(--warn)'
  return 'var(--danger)'
})
const cx = computed(() => props.size / 2)
const fs = computed(() => Math.round(props.size * 0.27))
const ty = computed(() => props.size / 2 + props.size * 0.145)
</script>

<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
    <circle :cx="cx" :cy="cx" :r="r" fill="none" stroke="var(--bdrS)" stroke-width="2.5" />
    <circle
      :cx="cx" :cy="cx" :r="r"
      fill="none" :stroke="color" stroke-width="2.5"
      :stroke-dasharray="`${fill.toFixed(1)} ${gap.toFixed(1)}`"
      stroke-linecap="round"
      :transform="`rotate(-90 ${cx} ${cx})`"
    />
    <text
      :x="cx" :y="ty"
      text-anchor="middle" :fill="color"
      :font-size="fs" font-weight="600"
      font-family="ui-monospace,monospace"
    >{{ score.toFixed(1) }}</text>
  </svg>
</template>
