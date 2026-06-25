import { createContext, useContext, useState, useCallback } from 'react'
import { authApi } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const saveSession = useCallback((tokens) => {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    localStorage.setItem('user_role', tokens.role)
  }, [])

  const login = useCallback(async (identifier, password) => {
    const res = await authApi.login({ identifier, password })
    saveSession(res.data)
    const me = await authApi.getMe()
    setUser(me.data)
    localStorage.setItem('user', JSON.stringify(me.data))
    return res.data.role
  }, [saveSession])

  const logout = useCallback(() => {
    localStorage.clear()
    setUser(null)
  }, [])

  const isAuthenticated = !!localStorage.getItem('access_token')
  const role = localStorage.getItem('user_role')

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, role, saveSession }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
