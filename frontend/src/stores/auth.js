import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index.js'
import { hashPassword } from '../api/crypto.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => !!user.value?.is_admin)
  const isSuperAdmin = computed(() => !!user.value?.is_super_admin)

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password: hashPassword(password) })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
  }

  async function register(username, password) {
    return api.post('/auth/register', { username, password: hashPassword(password) })
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { user, token, isAuthenticated, isAdmin, isSuperAdmin, login, register, logout }
})
