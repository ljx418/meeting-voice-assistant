import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('auth_token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response = await authApi.login(username, password)
    token.value = response.access_token
    localStorage.setItem('auth_token', token.value)
    user.value = response.user
  }

  async function register(username: string, email: string, password: string) {
    await authApi.register(username, email, password)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return { token, user, isAuthenticated, login, register, logout }
})