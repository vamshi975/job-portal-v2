import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/JobsView.vue') },
    { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
  ],
})
