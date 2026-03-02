import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/upload', component: () => import('../views/UploadView.vue') },
  { path: '/gallery', component: () => import('../views/GalleryView.vue') },
  { path: '/carousel', component: () => import('../views/CarouselView.vue') },
  {
    path: '/admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAdmin) {
    const auth = useAuthStore()
    if (!auth.isAdmin) return '/upload'
  }
})

export default router
