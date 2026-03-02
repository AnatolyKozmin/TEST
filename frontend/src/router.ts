import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from './pages/LandingPage.vue'
import RegisterPage from './pages/RegisterPage.vue'
import AdminPage from './pages/AdminPage.vue'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: LandingPage },
    { path: '/register', component: RegisterPage },
    { path: '/admin', component: AdminPage },
  ],
})

