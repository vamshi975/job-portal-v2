import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api/client'

// Per-job entry: { state: 'idle'|'generating'|'done'|'error', docs: [], error: null }
export const useDocsStore = defineStore('docs', () => {
  const map = ref({})

  function _entry(jobId) {
    if (!map.value[jobId]) {
      map.value[jobId] = { state: 'idle', docs: [], error: null }
    }
    return map.value[jobId]
  }

  function get(jobId) {
    return map.value[jobId] ?? { state: 'idle', docs: [], error: null }
  }

  async function generate(jobId, doc_type = 'both') {
    const entry = _entry(jobId)
    entry.state = 'generating'
    entry.error = null
    try {
      await api.postDocs(jobId, doc_type)
      // Poll until the background task writes the files
      for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 3000))
        const res = await api.getDocs(jobId)
        if (res.documents?.length) {
          entry.docs = res.documents
          entry.state = 'done'
          return
        }
      }
      // Timed out — show whatever exists
      const res = await api.getDocs(jobId)
      entry.docs = res.documents ?? []
      entry.state = 'done'
    } catch (e) {
      entry.state = 'error'
      entry.error = e.message
    }
  }

  async function fetchDocs(jobId) {
    const entry = _entry(jobId)
    try {
      const res = await api.getDocs(jobId)
      entry.docs = res.documents ?? []
      if (entry.docs.length && entry.state === 'idle') entry.state = 'done'
    } catch {
      // silently ignore — doc list is non-critical
    }
  }

  return { map, get, generate, fetchDocs }
})
