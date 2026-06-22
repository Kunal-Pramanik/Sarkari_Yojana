const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
export async function signUp(email: string, password: string, full_name: string) {
  const res = await fetch(`${API_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name })
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Signup failed')
  }
  return res.json()
}

export async function signIn(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/signin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Sign in failed')
  }
  const data = await res.json()
  // Save token and user info to localStorage
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('user_id', data.user_id)
  localStorage.setItem('user_email', data.email)
  localStorage.setItem('user_name', data.full_name)
  return data
}

export function signOut() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('user_email')
  localStorage.removeItem('user_name')
  window.location.href = '/login'
}

export function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export function getUser() {
  return {
    user_id: localStorage.getItem('user_id'),
    email: localStorage.getItem('user_email'),
    full_name: localStorage.getItem('user_name')
  }
}

export function isLoggedIn(): boolean {
  return !!localStorage.getItem('access_token')
}