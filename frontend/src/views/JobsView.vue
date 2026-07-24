<script setup>
import { ref } from 'vue'
import JobList from '../components/JobList.vue'
import JobDetail from '../components/JobDetail.vue'

const listWidth = ref(374)
const MIN = 200
const MAX = 640
const dragging = ref(false)

function startResize(e) {
  e.preventDefault()
  dragging.value = true
  const startX = e.clientX
  const startW = listWidth.value

  function onMove(e) {
    listWidth.value = Math.min(MAX, Math.max(MIN, startW + e.clientX - startX))
  }
  function onUp() {
    dragging.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function resetWidth() {
  listWidth.value = 374
}
</script>

<template>
  <div class="jobs-view" :class="{ dragging }">
    <JobList :style="{ width: listWidth + 'px' }" />
    <div
      class="resize-handle"
      @mousedown="startResize"
      @dblclick="resetWidth"
      title="Drag to resize · Double-click to reset"
    >
      <div class="handle-grip" />
    </div>
    <JobDetail />
  </div>
</template>

<style scoped>
.jobs-view { display: flex; flex: 1; overflow: hidden; }
.jobs-view.dragging { cursor: col-resize; user-select: none; }

.resize-handle {
  width: 6px;
  flex-shrink: 0;
  background: var(--bdr);
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  position: relative;
}
.resize-handle:hover,
.jobs-view.dragging .resize-handle {
  background: var(--acc);
}

.handle-grip {
  width: 2px;
  height: 24px;
  border-radius: 2px;
  background: var(--bdrS);
  transition: background 0.15s;
}
.resize-handle:hover .handle-grip,
.jobs-view.dragging .handle-grip {
  background: #fff6;
}
</style>
