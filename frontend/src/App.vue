<script setup>
import { ref, onMounted } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'auto')

function applyTheme(t) {
  if (t === 'auto') document.documentElement.removeAttribute('data-theme')
  else document.documentElement.setAttribute('data-theme', t)
}

function toggleTheme() {
  const next = theme.value === 'dark' ? 'light' : 'dark'
  theme.value = next
  localStorage.setItem('theme', next)
  applyTheme(next)
}

onMounted(() => applyTheme(theme.value))
</script>

<template>
  <div class="app-shell">
    <nav class="nav">
      <div class="brand">
        <div class="brand-icon">💼</div>
        Job Portal v2
      </div>
      <div class="nav-tabs">
        <RouterLink to="/" class="tab-btn" active-class="on" exact>Jobs</RouterLink>
        <RouterLink to="/dashboard" class="tab-btn" active-class="on">Dashboard</RouterLink>
      </div>
      <div class="nav-r">
        <button
          class="icon-btn" @click="toggleTheme"
          :title="theme === 'dark' ? 'Switch to light' : 'Switch to dark'"
        >{{ theme === 'dark' ? '☾' : '☀' }}</button>
      </div>
    </nav>
    <div class="view-area">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app-shell { height: 100vh; display: flex; flex-direction: column; }
.nav {
  height: 46px; display: flex; align-items: center; padding: 0 14px; gap: 0;
  background: var(--s2); border-bottom: 0.5px solid var(--bdr); flex-shrink: 0;
}
.brand {
  display: flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 600; color: var(--tp); letter-spacing: -0.3px; margin-right: 16px;
}
.brand-icon {
  width: 22px; height: 22px; border-radius: 5px; background: var(--acc);
  display: flex; align-items: center; justify-content: center; font-size: 13px;
}
.nav-tabs { display: flex; gap: 2px; flex: 1; }
.tab-btn {
  padding: 5px 12px; border-radius: 5px; font-size: 12px; font-weight: 500;
  color: var(--tm); cursor: pointer; border: none; background: transparent;
  text-decoration: none; transition: all 0.1s;
}
.tab-btn:hover { background: var(--s3); color: var(--ts); }
.tab-btn.on    { background: var(--accBg); color: var(--acc); }
.nav-r { display: flex; align-items: center; gap: 7px; }
.icon-btn {
  width: 28px; height: 28px; border: 0.5px solid var(--bdr); background: var(--s1);
  color: var(--ts); border-radius: var(--r); cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.icon-btn:hover { border-color: var(--bdrS); color: var(--tp); }
.view-area { flex: 1; display: flex; overflow: hidden; }
</style>
