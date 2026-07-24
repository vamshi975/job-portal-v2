<script setup>
defineProps({ status: { type: String, default: 'new' } })
</script>

<template>
  <span class="pill" :class="status">{{ status }}</span>
</template>

<style scoped>
.pill {
  font-size: 9.5px; font-weight: 500; padding: 2px 6px;
  border-radius: 20px; white-space: nowrap; display: inline-block;
}
.pill.new        { color: var(--tm);   background: var(--s3);      border: 0.5px solid var(--bdr);     }
.pill.interesting { color: var(--warn); background: var(--warnBg);  border: 0.5px solid var(--warnBdr); }
.pill.applied    { color: var(--succ); background: var(--succBg);  border: 0.5px solid var(--succBdr); }
</style>
