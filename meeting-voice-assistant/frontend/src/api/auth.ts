const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const authApi = {
  async login(username: string, password: string) {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (!res.ok) throw new Error('Login failed')
    return res.json()
  },

  async register(username: string, email: string, password: string) {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })
    if (!res.ok) throw new Error('Register failed')
    return res.json()
  }
}