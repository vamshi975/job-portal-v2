<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useJobsStore } from '../stores/jobs'

const store = useJobsStore()
onMounted(() => store.fetchDashboard())

const dash = computed(() => store.dashboard)
const cs   = computed(() => store.countryStats)

const COUNTRIES = [
  'Germany', 'Netherlands', 'Belgium', 'India',
  'United States', 'Canada', 'Denmark', 'Sweden',
]
const FLAGS = {
  Germany: '🇩🇪', Netherlands: '🇳🇱', Belgium: '🇧🇪', India: '🇮🇳',
  'United States': '🇺🇸', Canada: '🇨🇦', Denmark: '🇩🇰', Sweden: '🇸🇪',
}
const SITE_COLORS = {
  linkedin: '#0A66C2', indeed: '#003A9B', naukri: '#FF6600',
}

const selectedCountry = ref('')
watch(selectedCountry, c => { if (c) store.fetchCountryStats(c) })

function pct(n, total) {
  return total ? Math.round((n / total) * 100) : 0
}

// ── helpers ──────────────────────────────────────────────
const maxCountry = computed(() => {
  if (!dash.value?.jobs_by_country?.length) return 1
  return Math.max(...dash.value.jobs_by_country.map(d => d.count))
})

function maxCount(items) {
  return items?.length ? Math.max(...items.map(i => i.count)) : 1
}

const lineChart = computed(() => {
  const data = dash.value?.jobs_over_time ?? []
  if (!data.length) return null
  const W = 280, H = 68, p = 8
  const maxN = Math.max(...data.map(d => d.count), 1)
  const pts = data.map((d, i) => ({
    x: p + Math.round((i / Math.max(data.length - 1, 1)) * (W - p * 2)),
    y: p + Math.round((1 - d.count / maxN) * (H - p * 2)),
    label: d.date.slice(5),
  }))
  const linePath = pts.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' ')
  const areaPath = `${linePath} L${pts.at(-1).x},${H} L${pts[0].x},${H} Z`
  const step = Math.max(1, Math.ceil(pts.length / 5))
  return { W, H, pts, linePath, areaPath, labels: pts.filter((_, i) => i % step === 0) }
})
</script>

<template>
  <div class="dash">
    <div v-if="!dash" class="loading">Loading dashboard…</div>
    <template v-else>

      <!-- ── Stat cards ───────────────────────────────── -->
      <div class="stats-grid">
        <div class="stat">
          <div class="stat-lbl">Total jobs</div>
          <div class="stat-val">{{ dash.total_jobs }}</div>
          <div class="stat-sub">across all countries</div>
        </div>
        <div class="stat">
          <div class="stat-lbl">New</div>
          <div class="stat-val">{{ dash.application_funnel.new }}</div>
          <div class="stat-sub">unreviewed</div>
        </div>
        <div class="stat">
          <div class="stat-lbl">Interesting</div>
          <div class="stat-val warn">{{ dash.application_funnel.interesting }}</div>
          <div class="stat-sub">to review</div>
        </div>
        <div class="stat">
          <div class="stat-lbl">Applied</div>
          <div class="stat-val succ">{{ dash.application_funnel.applied }}</div>
          <div class="stat-sub">in progress</div>
        </div>
      </div>

      <!-- ── Global charts ────────────────────────────── -->
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-title">Jobs by country</div>
          <div class="bar-chart">
            <div v-for="item in dash.jobs_by_country.slice(0, 8)" :key="item.label" class="bar-row">
              <span class="bar-lbl">{{ FLAGS[item.label] || '' }} {{ item.label }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: Math.round((item.count / maxCountry) * 100) + '%' }" />
              </div>
              <span class="bar-cnt">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-title">Application funnel</div>
          <div class="funnel">
            <div class="fn-row">
              <div class="fn-lbl-g"><span class="fn-dot" style="background:var(--tm)" /><span class="fn-lbl">New</span></div>
              <div class="fn-track"><div class="fn-fill tm" :style="{ width: pct(dash.application_funnel.new, dash.total_jobs) + '%' }">{{ dash.application_funnel.new }}</div></div>
              <span class="fn-pct">{{ pct(dash.application_funnel.new, dash.total_jobs) }}%</span>
            </div>
            <div class="fn-row">
              <div class="fn-lbl-g"><span class="fn-dot" style="background:var(--warn)" /><span class="fn-lbl">Interesting</span></div>
              <div class="fn-track"><div class="fn-fill warn" :style="{ width: pct(dash.application_funnel.interesting, dash.total_jobs) + '%' }">{{ dash.application_funnel.interesting }}</div></div>
              <span class="fn-pct">{{ pct(dash.application_funnel.interesting, dash.total_jobs) }}%</span>
            </div>
            <div class="fn-row">
              <div class="fn-lbl-g"><span class="fn-dot" style="background:var(--succ)" /><span class="fn-lbl">Applied</span></div>
              <div class="fn-track"><div class="fn-fill succ" :style="{ width: pct(dash.application_funnel.applied, dash.total_jobs) + '%' }">{{ dash.application_funnel.applied }}</div></div>
              <span class="fn-pct">{{ pct(dash.application_funnel.applied, dash.total_jobs) }}%</span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-title">Jobs over time</div>
          <div v-if="lineChart" class="line-wrap">
            <svg :viewBox="`0 0 ${lineChart.W} ${lineChart.H + 16}`" style="width:100%;overflow:visible">
              <path :d="lineChart.areaPath" fill="var(--acc)" opacity="0.12" />
              <path :d="lineChart.linePath" fill="none" stroke="var(--acc)" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" />
              <circle :cx="lineChart.pts.at(-1).x" :cy="lineChart.pts.at(-1).y" r="3" fill="var(--acc)" />
              <text v-for="p in lineChart.labels" :key="p.label" :x="p.x" :y="lineChart.H + 13" text-anchor="middle" font-size="8" fill="var(--td)" font-family="ui-monospace,monospace">{{ p.label }}</text>
            </svg>
          </div>
          <div v-else class="chart-empty">No time-series data yet</div>
        </div>

        <div class="chart-card">
          <div class="chart-title">Top companies</div>
          <div class="co-list">
            <div v-for="(item, i) in dash.top_companies.slice(0, 8)" :key="item.label" class="co-row">
              <span class="co-rank">{{ i + 1 }}</span>
              <span class="co-name">{{ item.label }}</span>
              <span class="co-cnt">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Country drill-down ────────────────────────── -->
      <div class="drilldown-header">
        <div class="drilldown-title">Regional breakdown</div>
        <select class="country-sel" v-model="selectedCountry">
          <option value="">Select a country…</option>
          <option v-for="c in COUNTRIES" :key="c" :value="c">{{ FLAGS[c] }} {{ c }}</option>
        </select>
      </div>

      <div v-if="selectedCountry && !cs" class="loading">Loading…</div>

      <template v-if="cs">
        <!-- KPI row -->
        <div class="kpi-row">
          <div class="kpi">
            <div class="kpi-val">{{ cs.total_jobs }}</div>
            <div class="kpi-lbl">Total jobs</div>
          </div>
          <div class="kpi">
            <div class="kpi-val acc">{{ cs.jobs_by_city.length }}</div>
            <div class="kpi-lbl">Cities</div>
          </div>
          <div class="kpi">
            <div class="kpi-val warn">{{ cs.jobs_by_role.length }}</div>
            <div class="kpi-lbl">Role types</div>
          </div>
          <div class="kpi">
            <div class="kpi-val succ">{{ cs.jobs_by_site.length }}</div>
            <div class="kpi-lbl">Job sites</div>
          </div>
        </div>

        <!-- Drill-down charts -->
        <div class="charts-grid">

          <!-- Jobs by city -->
          <div class="chart-card">
            <div class="chart-title">Jobs by city <span class="chart-sub">in {{ cs.country }}</span></div>
            <div class="bar-chart">
              <div v-for="item in cs.jobs_by_city.slice(0, 12)" :key="item.label" class="bar-row">
                <span class="bar-lbl">{{ item.label }}</span>
                <div class="bar-track">
                  <div class="bar-fill city" :style="{ width: Math.round((item.count / maxCount(cs.jobs_by_city)) * 100) + '%' }" />
                </div>
                <span class="bar-cnt">{{ item.count }}</span>
              </div>
            </div>
            <div v-if="!cs.jobs_by_city.length" class="chart-empty">No city data</div>
          </div>

          <!-- Jobs by skill / role -->
          <div class="chart-card">
            <div class="chart-title">Jobs by skill / role <span class="chart-sub">in {{ cs.country }}</span></div>
            <div class="bar-chart">
              <div v-for="item in cs.jobs_by_role.slice(0, 12)" :key="item.label" class="bar-row">
                <span class="bar-lbl">{{ item.label }}</span>
                <div class="bar-track">
                  <div class="bar-fill role" :style="{ width: Math.round((item.count / maxCount(cs.jobs_by_role)) * 100) + '%' }" />
                </div>
                <span class="bar-cnt">{{ item.count }}</span>
              </div>
            </div>
            <div v-if="!cs.jobs_by_role.length" class="chart-empty">No role data</div>
          </div>

          <!-- Jobs by site -->
          <div class="chart-card">
            <div class="chart-title">Jobs by site <span class="chart-sub">in {{ cs.country }}</span></div>
            <div class="site-bars">
              <div v-for="item in cs.jobs_by_site" :key="item.label" class="site-row">
                <span class="site-dot-l" :style="{ background: SITE_COLORS[item.label] ?? '#888' }" />
                <span class="bar-lbl">{{ item.label }}</span>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{
                      width: Math.round((item.count / maxCount(cs.jobs_by_site)) * 100) + '%',
                      background: SITE_COLORS[item.label] ?? 'var(--acc)',
                    }"
                  />
                </div>
                <span class="bar-cnt">{{ item.count }}</span>
              </div>
            </div>
            <div v-if="!cs.jobs_by_site.length" class="chart-empty">No site data</div>
          </div>

          <!-- Top companies in country -->
          <div class="chart-card">
            <div class="chart-title">Top companies <span class="chart-sub">in {{ cs.country }}</span></div>
            <div class="co-list">
              <div v-for="(item, i) in cs.top_companies" :key="item.label" class="co-row">
                <span class="co-rank">{{ i + 1 }}</span>
                <span class="co-name">{{ item.label }}</span>
                <span class="co-cnt">{{ item.count }}</span>
              </div>
            </div>
            <div v-if="!cs.top_companies.length" class="chart-empty">No data</div>
          </div>

        </div>
      </template>

      <div v-if="!selectedCountry" class="drilldown-empty">
        ↑ Select a country above to see city, skill, and site breakdowns
      </div>

    </template>
  </div>
</template>

<style scoped>
.dash { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 12px; }
.loading { padding: 40px; text-align: center; color: var(--tm); }

/* Stat cards */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.stat { background: var(--s1); border: 0.5px solid var(--bdr); border-radius: 8px; padding: 12px 14px; }
.stat-lbl { font-size: 9.5px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--tm); margin-bottom: 4px; }
.stat-val { font-size: 24px; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -1px; color: var(--tp); line-height: 1; }
.stat-val.warn { color: var(--warn); }
.stat-val.succ { color: var(--succ); }
.stat-sub { font-size: 10px; color: var(--td); margin-top: 2px; }

/* Charts */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.chart-card { background: var(--s1); border: 0.5px solid var(--bdr); border-radius: 8px; padding: 12px 14px; }
.chart-title { font-size: 11px; font-weight: 600; color: var(--tp); margin-bottom: 10px; }
.chart-sub { font-weight: 400; color: var(--tm); margin-left: 4px; }
.chart-empty { font-size: 11px; color: var(--tm); }

/* Bar chart */
.bar-chart { display: flex; flex-direction: column; gap: 6px; }
.bar-row { display: grid; grid-template-columns: 90px 1fr 26px; align-items: center; gap: 7px; }
.bar-lbl { font-size: 10px; color: var(--ts); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-track { height: 6px; background: var(--s3); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; background: var(--acc); }
.bar-fill.city { background: var(--warn); }
.bar-fill.role { background: var(--succ); }
.bar-cnt { font-size: 10px; font-variant-numeric: tabular-nums; color: var(--tm); text-align: right; }

/* Funnel */
.funnel { display: flex; flex-direction: column; gap: 8px; }
.fn-row { display: flex; align-items: center; gap: 8px; }
.fn-lbl-g { width: 72px; display: flex; align-items: center; gap: 5px; flex-shrink: 0; }
.fn-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.fn-lbl { font-size: 10px; color: var(--ts); }
.fn-track { flex: 1; height: 20px; background: var(--s3); border-radius: 4px; overflow: hidden; }
.fn-fill { height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 7px; font-size: 10px; font-weight: 600; font-variant-numeric: tabular-nums; color: #fff; white-space: nowrap; min-width: 20px; }
.fn-fill.tm   { background: var(--tm); }
.fn-fill.warn { background: var(--warn); }
.fn-fill.succ { background: var(--succ); }
.fn-pct { font-size: 9.5px; color: var(--tm); min-width: 30px; text-align: right; }

/* Line */
.line-wrap { overflow: hidden; }

/* Companies */
.co-list { display: flex; flex-direction: column; gap: 5px; }
.co-row  { display: flex; align-items: center; gap: 7px; }
.co-rank { font-size: 9px; color: var(--td); font-variant-numeric: tabular-nums; width: 12px; text-align: right; flex-shrink: 0; }
.co-name { font-size: 11px; color: var(--tp); flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.co-cnt  { font-size: 10px; font-variant-numeric: tabular-nums; font-weight: 600; color: var(--ts); background: var(--s2); padding: 2px 6px; border-radius: 10px; border: 0.5px solid var(--bdr); flex-shrink: 0; }

/* ── Country drill-down ───────────────────────────────── */
.drilldown-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; background: var(--s1);
  border: 0.5px solid var(--bdr); border-radius: 8px;
}
.drilldown-title { font-size: 12px; font-weight: 600; color: var(--tp); flex: 1; }
.country-sel {
  height: 28px; padding: 0 8px;
  background: var(--s1); border: 0.5px solid var(--bdrS);
  border-radius: var(--r); font-size: 12px; font-family: var(--font);
  color: var(--tp); outline: none; cursor: pointer; min-width: 180px;
}
.country-sel:focus { border-color: var(--acc); }

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.kpi {
  background: var(--s1); border: 0.5px solid var(--bdr); border-radius: 8px;
  padding: 10px 14px; text-align: center;
}
.kpi-val {
  font-size: 22px; font-weight: 600; font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px; color: var(--tp); line-height: 1;
}
.kpi-val.acc  { color: var(--acc); }
.kpi-val.warn { color: var(--warn); }
.kpi-val.succ { color: var(--succ); }
.kpi-lbl { font-size: 10px; color: var(--tm); margin-top: 3px; }

/* Site bars with colored dots */
.site-bars { display: flex; flex-direction: column; gap: 8px; }
.site-row { display: grid; grid-template-columns: 8px 70px 1fr 26px; align-items: center; gap: 7px; }
.site-dot-l { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.drilldown-empty {
  text-align: center; font-size: 11px; color: var(--td);
  padding: 20px; border: 0.5px dashed var(--bdr); border-radius: 8px;
}
</style>
