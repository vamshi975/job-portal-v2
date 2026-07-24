// In dev, Vite proxies /api → http://localhost:8000 (see vite.config.js).
// In production, set VITE_API_BASE to your Render backend URL.
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`${res.status}: ${text || res.statusText}`)
  }
  return res.json()
}

export const api = {
  getJobs(params = {}) {
    const q = new URLSearchParams()
    for (const [k, v] of Object.entries(params)) {
      if (v !== '' && v !== null && v !== undefined) q.set(k, v)
    }
    return req(`/jobs?${q}`)
  },

  getJob: (id) => req(`/jobs/${id}`),

  patchStatus: (id, status, notes = null) =>
    req(`/jobs/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, ...(notes != null && { notes }) }),
    }),

  getDashboard: () => req('/dashboard'),
  getCountryStats: (country) => req(`/dashboard/country/${encodeURIComponent(country)}`),

  postDocs: (id, doc_type = 'both') =>
    req(`/jobs/${id}/documents`, {
      method: 'POST',
      body: JSON.stringify({ doc_type }),
    }),

  getDocs: (id) => req(`/jobs/${id}/documents`),

  // Returns a direct URL — use as href or fetch manually for download
  downloadUrl: (jobId, docId) => `${BASE}/jobs/${jobId}/documents/${docId}/download`,
}
