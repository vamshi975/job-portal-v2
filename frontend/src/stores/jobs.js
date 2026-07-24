import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { api } from '../api/client'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref(null)
  const selectedId = ref(null)
  const selectedDetail = ref(null)
  const dashboard = ref(null)

  const filters = reactive({
    q: '',
    country: '',
    city: '',
    site: '',
    status: '',
    min_score: 6.0,
    page: 1,
    page_size: 50,
  })

  const countryStats = ref(null)

  const selected = computed(() => selectedDetail.value)

  async function fetchJobs() {
    loading.value = true
    error.value = null
    try {
      const data = await api.getJobs({
        search: filters.q || undefined,
        country: filters.country || undefined,
        city: filters.city || undefined,
        site: filters.site || undefined,
        status: filters.status || undefined,
        min_score: filters.min_score,
        page: filters.page,
        page_size: filters.page_size,
      })
      jobs.value = data.jobs
      total.value = data.total
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function selectJob(id) {
    selectedId.value = id
    selectedDetail.value = null
    try {
      selectedDetail.value = await api.getJob(id)
    } catch (e) {
      error.value = e.message
    }
  }

  async function updateStatus(id, status) {
    const updated = await api.patchStatus(id, status)
    // Reflect in list without a full refetch
    const idx = jobs.value.findIndex(j => j.uuid === id)
    if (idx >= 0) jobs.value[idx] = { ...jobs.value[idx], status }
    if (selectedDetail.value?.uuid === id) {
      selectedDetail.value = { ...selectedDetail.value, status }
    }
    return updated
  }

  async function fetchDashboard() {
    try {
      dashboard.value = await api.getDashboard()
    } catch (e) {
      error.value = e.message
    }
  }

  async function fetchCountryStats(country) {
    countryStats.value = null
    try {
      countryStats.value = await api.getCountryStats(country)
    } catch (e) {
      error.value = e.message
    }
  }

  return {
    jobs, total, loading, error, selectedId, selected, filters,
    dashboard, countryStats,
    fetchJobs, selectJob, updateStatus, fetchDashboard, fetchCountryStats,
  }
})
