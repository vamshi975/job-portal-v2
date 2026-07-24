<script setup>
import { ref, computed, onMounted } from 'vue'
import { useJobsStore } from '../stores/jobs'
import JobRow from './JobRow.vue'

const store = useJobsStore()

const COUNTRIES = [
  'Germany', 'Netherlands', 'Belgium', 'India',
  'United States', 'Canada', 'Denmark', 'Sweden',
]
const FLAGS = {
  Germany: '🇩🇪', Netherlands: '🇳🇱', Belgium: '🇧🇪', India: '🇮🇳',
  'United States': '🇺🇸', Canada: '🇨🇦', Denmark: '🇩🇰', Sweden: '🇸🇪',
}
const SITES = [
  { value: 'linkedin', label: '🔵 LinkedIn' },
  { value: 'indeed',   label: '🔷 Indeed'   },
  { value: 'naukri',   label: '🟠 Naukri'   },
]

// Derive unique cities from current job results for the city dropdown
const availableCities = computed(() => {
  const cities = store.jobs
    .map(j => j.city)
    .filter(Boolean)
  return [...new Set(cities)].sort()
})

const q = ref('')
let searchTimer = null

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    store.filters.q = q.value
    store.filters.page = 1
    store.fetchJobs()
  }, 300)
}

function onFilterChange() {
  // Reset city when country changes since cities are country-specific
  store.filters.page = 1
  store.fetchJobs()
}

function onCountryChange() {
  store.filters.city = ''
  store.filters.page = 1
  store.fetchJobs()
}

onMounted(() => store.fetchJobs())
</script>

<template>
  <div class="list-pane">
    <div class="filters">
      <!-- Row 1: search + country + status -->
      <div class="filter-row">
        <div class="s-wrap">
          <span class="s-icon">⌕</span>
          <input
            class="f-input" v-model="q" @input="onSearch"
            placeholder="Search jobs…"
          />
        </div>
        <select class="f-select" v-model="store.filters.country" @change="onCountryChange">
          <option value="">All countries</option>
          <option v-for="c in COUNTRIES" :key="c" :value="c">{{ FLAGS[c] }} {{ c }}</option>
        </select>
        <select class="f-select" v-model="store.filters.status" @change="onFilterChange">
          <option value="">All status</option>
          <option value="new">New</option>
          <option value="interesting">Interesting</option>
          <option value="applied">Applied</option>
        </select>
      </div>

      <!-- Row 2: city + site -->
      <div class="filter-row">
        <select class="f-select grow" v-model="store.filters.city" @change="onFilterChange">
          <option value="">All cities</option>
          <option v-for="c in availableCities" :key="c" :value="c">{{ c }}</option>
        </select>
        <select class="f-select grow" v-model="store.filters.site" @change="onFilterChange">
          <option value="">All sites</option>
          <option v-for="s in SITES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>

      <!-- Row 3: min score -->
      <div class="score-row">
        <span>Min score</span>
        <input
          type="range" min="0" max="10" step="0.5"
          v-model.number="store.filters.min_score"
          @change="onFilterChange"
        />
        <span class="score-val">{{ store.filters.min_score.toFixed(1) }}</span>
        <span class="count-lbl">{{ store.total }} shown</span>
      </div>
    </div>

    <div class="job-list">
      <div v-if="store.loading" class="list-msg">Loading…</div>
      <div v-else-if="store.error" class="list-msg err">{{ store.error }}</div>
      <div v-else-if="!store.jobs.length" class="list-msg">No jobs match these filters</div>
      <template v-else>
        <JobRow
          v-for="job in store.jobs"
          :key="job.uuid"
          :job="job"
          :selected="job.uuid === store.selectedId"
          @select="store.selectJob"
        />
      </template>
    </div>
  </div>
</template>

<style scoped>
.list-pane {
  min-width: 200px; flex-shrink: 0;
  border-right: none;
  display: flex; flex-direction: column; overflow: hidden;
  background: var(--s1);
}
.filters {
  padding: 8px 10px; border-bottom: 0.5px solid var(--bdr);
  display: flex; flex-direction: column; gap: 5px; background: var(--s2);
  flex-shrink: 0;
}
.filter-row { display: flex; gap: 4px; }
.s-wrap { flex: 1; position: relative; }
.s-icon {
  position: absolute; left: 7px; top: 50%; transform: translateY(-50%);
  font-size: 11px; color: var(--tm); pointer-events: none;
}
.f-input {
  width: 100%; height: 27px; padding: 0 7px 0 23px;
  background: var(--s1); border: 0.5px solid var(--bdr); border-radius: var(--r);
  font-size: 12px; font-family: var(--font); color: var(--tp); outline: none;
}
.f-input:focus { border-color: var(--acc); }
.f-select {
  height: 27px; padding: 0 5px; flex-shrink: 0;
  background: var(--s1); border: 0.5px solid var(--bdr); border-radius: var(--r);
  font-size: 11px; font-family: var(--font); color: var(--tp);
  outline: none; cursor: pointer;
}
.f-select.grow { flex: 1; min-width: 0; }
.f-select:focus { border-color: var(--acc); }
.score-row {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--tm);
}
.score-row input[type=range] { flex: 1; accent-color: var(--acc); }
.score-val { font-variant-numeric: tabular-nums; font-weight: 600; color: var(--acc); min-width: 24px; }
.count-lbl { font-size: 10px; color: var(--td); margin-left: auto; }
.job-list { flex: 1; overflow-y: auto; }
.list-msg { padding: 36px 16px; text-align: center; color: var(--tm); font-size: 12px; }
.list-msg.err { color: var(--danger); }
</style>
