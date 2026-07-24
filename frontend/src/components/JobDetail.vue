<script setup>
import { computed, watch } from 'vue'
import { useJobsStore } from '../stores/jobs'
import { useDocsStore } from '../stores/docs'
import { api } from '../api/client'
import ScoreRing from './ScoreRing.vue'
import StatusPill from './StatusPill.vue'

const jobsStore = useJobsStore()
const docsStore = useDocsStore()

const job = computed(() => jobsStore.selected)
const docEntry = computed(() => job.value ? docsStore.get(job.value.uuid) : null)

// Load existing docs whenever the selected job changes
watch(() => job.value?.uuid, id => { if (id) docsStore.fetchDocs(id) }, { immediate: true })

function scoreColor(s) {
  if (!s && s !== 0) return 'var(--td)'
  if (s >= 8.5) return 'var(--succ)'
  if (s >= 6.5) return 'var(--acc)'
  if (s >= 5)   return 'var(--warn)'
  return 'var(--danger)'
}

async function setStatus(status) {
  if (!job.value) return
  await jobsStore.updateStatus(job.value.uuid, status)
}

async function genDocs() {
  if (!job.value) return
  await docsStore.generate(job.value.uuid, 'both')
}

const tags = computed(() => {
  if (!job.value) return []
  return [
    job.value.search_term,
    job.value.site,
    job.value.city,
    job.value.date_posted ? `Posted ${job.value.date_posted}` : null,
  ].filter(Boolean)
})

const genLabel = computed(() => {
  const s = docEntry.value?.state
  if (s === 'generating') return 'Generating…'
  if (s === 'done' && docEntry.value.docs.length) return '↺ Regenerate'
  return '⊕ Create documents'
})
</script>

<template>
  <div class="detail-pane">
    <!-- Empty state -->
    <div v-if="!job" class="d-empty">
      <div class="d-empty-icon">⊟</div>
      <p>Select a job to see details</p>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="d-head">
        <div class="d-title">{{ job.title }}</div>
        <div class="d-co">{{ job.company }} · {{ job.country }}</div>
        <div class="d-tags">
          <span v-for="t in tags" :key="t" class="tag">{{ t }}</span>
        </div>
        <div class="d-score-row">
          <ScoreRing :score="job.relevance_score ?? 0" :size="32" />
          <div>
            <div class="score-num" :style="{ color: scoreColor(job.relevance_score) }">
              {{ (job.relevance_score ?? 0).toFixed(1) }}
            </div>
            <div class="score-sub">relevance / 10</div>
          </div>
          <StatusPill :status="job.status || 'new'" style="margin-left: 8px" />
          <a
            v-if="job.job_url" :href="job.job_url"
            target="_blank" rel="noopener" class="ext-link"
          >Open ↗</a>
        </div>
      </div>

      <!-- Actions -->
      <div class="d-actions">
        <button
          v-if="job.status === 'new'"
          class="btn warn" @click="setStatus('interesting')"
        >★ Interesting</button>
        <button
          v-if="job.status !== 'applied'"
          class="btn succ" @click="setStatus('applied')"
        >✓ Applied</button>
        <button
          v-if="job.status !== 'new'"
          class="btn" @click="setStatus('new')"
        >↩ Reset</button>
        <button
          class="btn primary"
          :disabled="docEntry?.state === 'generating'"
          @click="genDocs"
        >
          <span v-if="docEntry?.state === 'generating'" class="spin" />
          {{ genLabel }}
        </button>
      </div>

      <!-- Body -->
      <div class="d-body">
        <!-- Doc generation status -->
        <div v-if="docEntry?.state === 'generating'" class="doc-status">
          <span class="spin" />
          Building cover letter + CV for {{ job.country }} locale…
        </div>
        <div v-if="docEntry?.state === 'error'" class="doc-status err">
          {{ docEntry.error }}
        </div>

        <!-- Doc download links -->
        <div v-if="docEntry?.docs?.length" class="doc-section">
          <div class="sec-lbl">Documents</div>
          <div class="doc-links">
            <a
              v-for="doc in docEntry.docs"
              :key="doc.id"
              :href="api.downloadUrl(job.uuid, doc.id)"
              class="doc-dl"
              download
            >⬇ {{ doc.doc_type }}_{{ job.uuid.slice(0, 8) }}.docx</a>
          </div>
          <div class="doc-meta">
            {{ job.country }} style · {{ docEntry.docs[0]?.created_at?.slice(0, 16) }}
          </div>
        </div>

        <!-- Description -->
        <div v-if="job.description">
          <div class="sec-lbl">Description</div>
          <div class="desc-text">{{ job.description }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-pane {
  flex: 1; display: flex; flex-direction: column;
  overflow: hidden; background: var(--s1);
}
.d-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 6px; color: var(--tm);
}
.d-empty-icon { font-size: 26px; opacity: 0.4; }
.d-empty p { font-size: 12px; }

.d-head {
  padding: 14px 16px 10px; flex-shrink: 0;
  border-bottom: 0.5px solid var(--bdr); background: var(--s2);
}
.d-title  { font-size: 15px; font-weight: 600; letter-spacing: -0.3px; color: var(--tp); line-height: 1.3; }
.d-co     { font-size: 12px; color: var(--ts); margin-top: 2px; }
.d-tags   { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.tag {
  font-size: 10px; background: var(--s1); color: var(--ts);
  padding: 2px 7px; border-radius: 4px; border: 0.5px solid var(--bdr);
}
.d-score-row { display: flex; align-items: center; gap: 8px; margin-top: 9px; }
.score-num {
  font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums;
  font-family: var(--mono); letter-spacing: -0.5px;
}
.score-sub { font-size: 9.5px; color: var(--tm); }
.ext-link {
  margin-left: auto; font-size: 11px; color: var(--acc);
  border: 0.5px solid var(--bdr); padding: 3px 8px; border-radius: var(--r);
}
.ext-link:hover { border-color: var(--acc); }

.d-actions {
  padding: 8px 16px; flex-shrink: 0;
  border-bottom: 0.5px solid var(--bdr);
  display: flex; gap: 5px; flex-wrap: wrap; background: var(--s2);
}
.d-body {
  flex: 1; overflow-y: auto; padding: 14px 16px;
  display: flex; flex-direction: column; gap: 14px;
}
.sec-lbl {
  font-size: 9px; font-weight: 600; letter-spacing: 0.8px;
  text-transform: uppercase; color: var(--tm); margin-bottom: 5px;
}
.doc-status { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--ts); }
.doc-status.err { color: var(--danger); }
.doc-section { display: flex; flex-direction: column; gap: 5px; }
.doc-links   { display: flex; gap: 6px; flex-wrap: wrap; }
.doc-dl {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px; background: var(--s2); border: 0.5px solid var(--bdr);
  border-radius: var(--r); font-size: 11px; font-weight: 500; color: var(--tp);
}
.doc-dl:hover { border-color: var(--acc); color: var(--acc); }
.doc-meta  { font-size: 10px; color: var(--td); }
.desc-text { font-size: 12px; line-height: 1.65; color: var(--ts); white-space: pre-line; }
</style>
