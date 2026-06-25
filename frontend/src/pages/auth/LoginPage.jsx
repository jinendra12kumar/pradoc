import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const ROLE_REDIRECT = {
  patient: '/patient/dashboard',
  doctor:  '/doctor/dashboard',
  admin:   '/admin/dashboard',
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [form, setForm] = useState({ identifier: '', password: '' })
  const [showPw, setShowPw]   = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.identifier || !form.password) {
      setError('Please fill in all fields.')
      return
    }
    setLoading(true)
    try {
      const role = await login(form.identifier, form.password)
      navigate(ROLE_REDIRECT[role] || '/')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Login failed. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {/* Left illustration */}
      <div className="auth-left">
        <a href="/" className="auth-brand">
          <span className="auth-brand-logo">•PraDoc•</span>
        </a>
        <svg viewBox="0 0 400 360" className="auth-illustration" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="200" cy="280" rx="160" ry="30" fill="rgba(0,200,180,0.12)" />
          <circle cx="200" cy="170" r="120" fill="url(#globe)" />
          <defs>
            <radialGradient id="globe" cx="40%" cy="35%">
              <stop offset="0%" stopColor="#4dd9c7"/>
              <stop offset="100%" stopColor="#00a896"/>
            </radialGradient>
          </defs>
          <ellipse cx="200" cy="260" rx="150" ry="25" fill="rgba(150,80,200,0.35)" />
          {/* Medical cross */}
          <rect x="182" y="145" width="36" height="10" rx="5" fill="white" opacity="0.9"/>
          <rect x="195" y="132" width="10" height="36" rx="5" fill="white" opacity="0.9"/>
          {/* Floating cards */}
          <rect x="60" y="80" width="70" height="50" rx="8" fill="white" opacity="0.9"/>
          <text x="95" y="112" textAnchor="middle" fontSize="22">💊</text>
          <rect x="270" y="60" width="70" height="50" rx="8" fill="white" opacity="0.9"/>
          <text x="305" y="92" textAnchor="middle" fontSize="22">🩺</text>
          <rect x="290" y="175" width="60" height="45" rx="8" fill="white" opacity="0.9"/>
          <text x="320" y="204" textAnchor="middle" fontSize="20">❤️</text>
          <rect x="55" y="175" width="60" height="45" rx="8" fill="white" opacity="0.9"/>
          <text x="85" y="204" textAnchor="middle" fontSize="20">🏥</text>
        </svg>
        <div className="auth-left-tagline">
          <h2>Your Health, Our Priority</h2>
          <p>Book appointments, manage records,<br />and connect with top doctors.</p>
        </div>
      </div>

      {/* Right panel */}
      <div className="auth-right">
        {/* Tabs */}
        <div className="auth-tabs">
          <button className="auth-tab active">Login</button>
          <button className="auth-tab" onClick={() => navigate('/auth/register')}>Register</button>
        </div>

        <h1 className="form-title">Welcome back 👋</h1>
        <p className="form-subtitle">Sign in to access your health dashboard</p>

        {error && <div className="alert alert-error">⚠️ {error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="identifier">Mobile Number / Email ID</label>
            <input
              id="identifier"
              name="identifier"
              type="text"
              className="form-input"
              placeholder="Mobile Number / Email ID"
              value={form.identifier}
              onChange={handleChange}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="password-wrapper">
              <input
                id="password"
                name="password"
                type={showPw ? 'text' : 'password'}
                className="form-input"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                autoComplete="current-password"
                style={{ paddingRight: '44px' }}
              />
              <button type="button" className="password-toggle" onClick={() => setShowPw(!showPw)}>
                {showPw ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'20px' }}>
            <div className="check-group" style={{marginBottom:0}}>
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember me for 30 days</label>
            </div>
            <button type="button" className="auth-link" onClick={() => alert('Forgot password coming soon!')}>
              Forgot password?
            </button>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading && <span className="spinner" />}
            {loading ? 'Signing in…' : 'Login'}
          </button>
        </form>

        <div className="auth-footer" style={{marginTop:'24px'}}>
          Don't have an account?{' '}
          <Link to="/auth/register" className="auth-link">Register</Link>
        </div>
      </div>
    </div>
  )
}
