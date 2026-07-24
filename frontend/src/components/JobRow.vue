<script setup>
import ScoreRing from './ScoreRing.vue'
import StatusPill from './StatusPill.vue'

defineProps({ job: Object, selected: Boolean })
defineEmits(['select'])

const SITE_COLORS = {
  linkedin: '#0A66C2', indeed: '#003A9B', naukri: '#FF6600',
}

function fmtDate(d) {
  return d ? d.slice(5).replace('-', '/') : ''
}
</script>

<template>
  <div class="jrow" :class="{ sel: selected }" @click="$emit('select', job.uuid)">
    <div class="sel-bar" v-if="selected" />
    <ScoreRing :score="job.relevance_score ?? 0" :size="30" />
    <div class="jmain">
      <div class="jtitle">{{ job.title }}</div>
      <div class="jmeta">
        <span
          class="site-dot"
          :style="{ background: SITE_COLORS[job.site] ?? '#888' }"
          :title="job.site"
        />
        {{ job.company }} · {{ job.city || job.country }}
      </div>
    </div>
    <div class="jright">
      <StatusPill :status="job.status || 'new'" />
      <span class="jdate">{{ fmtDate(job.date_posted) }}</span>
    </div>
  </div>
</template>

<style scoped>
.jrow {
  display: grid;
  grid-template-columns: 34px 1fr auto;
  gap: 7px; align-items: center;
  padding: 8px 10px; border-bottom: 0.5px solid var(--bdr);
  cursor: pointer; position: relative;
}
.jrow:hover { background: var(--s2); }
.jrow.sel   { background: var(--accBg); }
.sel-bar {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 2.5px; background: var(--acc); border-radius: 0 2px 2px 0;
}
.jmain { min-width: 0; }
.jtitle {
  font-size: 12px; font-weight: 500; color: var(--tp);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.jmeta {
  font-size: 10px; color: var(--ts); margin-top: 1px;
  display: flex; align-items: center; gap: 3px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.site-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; display: inline-block; }
.jright  { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex-shrink: 0; }
.jdate   { font-size: 10px; color: var(--td); font-variant-numeric: tabular-nums; }
</style>
