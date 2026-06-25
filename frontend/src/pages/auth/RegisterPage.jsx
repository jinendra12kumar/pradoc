import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../../api/authApi'

function getStrength(pw) {
  let score = 0
  if (pw.length >= 8) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  return score
}

const STRENGTH_LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong']
const STRENGTH_COLORS = ['', '#e53e3e', '#dd6b20', '#d69e2e', '#38a169']

export default function RegisterPage() {
  const navigate = useNavigate()
  const [role, setRole]     = useState('patient')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState('')

  const [form, setForm] = useState({
    full_name: '', email: '', mobile: '',
    password: '', confirm_password: '',
  })
  const [fieldErrors, setFieldErrors] = useState({})

  const strength = getStrength(form.password)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setFieldErrors({ ...fieldErrors, [e.target.name]: '' })
    setError('')
  }

  const validate = () => {
    const errs = {}
    if (!form.full_name.trim()) errs.full_name = 'Full name is required'
    if (!form.email.trim()) errs.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Invalid email'
    if (!form.mobile.trim()) errs.mobile = 'Mobile is required'
    else if (!/^[6-9]\d{9}$/.test(form.mobile)) errs.mobile = 'Enter valid 10-digit Indian mobile'
    if (!form.password) errs.password = 'Password is required'
    else if (strength < 2) errs.password = 'Password is too weak'
    if (form.password !== form.confirm_password) errs.confirm_password = 'Passwords do not match'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setFieldErrors(errs); return }

    setLoading(true)
    try {
      await authApi.register({ ...form, role })
      navigate('/auth/verify-otp', { state: { email: form.email, role } })
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Registration failed. Please try again.'
      setError(Array.isArray(msg) ? msg.map(m => m.msg).join(', ') : msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {/* Left */}
      <div className="auth-left">
        <a href="/" className="auth-brand">
          <span className="auth-brand-logo">•PraDoc•</span>
        </a>
        <svg viewBox="0 0 400 360" className="auth-illustration" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="200" cy="280" rx="160" ry="30" fill="rgba(0,200,180,0.12)" />
          <circle cx="200" cy="170" r="120" fill="url(#globe2)" />
          <defs>
            <radialGradient id="globe2" cx="40%" cy="35%">
              <stop offset="0%" stopColor="#4dd9c7"/>
              <stop offset="100%" stopColor="#00a896"/>
            </radialGradient>
          </defs>
          <ellipse cx="200" cy="260" rx="150" ry="25" fill="rgba(150,80,200,0.35)" />
          <rect x="182" y="145" width="36" height="10" rx="5" fill="white" opacity="0.9"/>
          <rect x="195" y="132" width="10" height="36" rx="5" fill="white" opacity="0.9"/>
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
          <h2>{role === 'doctor' ? 'Join 125,000+ Doctors' : 'Join 10M+ Patients'}</h2>
          <p>{role === 'doctor'
            ? 'Manage appointments, consult online,\nand grow your practice.'
            : 'Book appointments, manage prescriptions,\nand stay healthy.'}
          </p>
        </div>
      </div>

      {/* Right */}
      <div className="auth-right">
        <div className="auth-tabs">
          <button className="auth-tab" onClick={() => navigate('/auth/login')}>Login</button>
          <button className="auth-tab active">Register</button>
        </div>

        {/* Role Switcher */}
        <div className="role-switcher">
          <button
            type="button"
            className={`role-btn ${role === 'patient' ? 'active' : ''}`}
            onClick={() => setRole('patient')}
            id="role-patient"
          >
            🧑‍⚕️ I'm a Patient
          </button>
          <button
            type="button"
            className={`role-btn ${role === 'doctor' ? 'active' : ''}`}
            onClick={() => setRole('doctor')}
            id="role-doctor"
          >
            👨‍⚕️ I'm a Doctor
          </button>
        </div>

        <h1 className="form-title">
          {role === 'doctor' ? 'Doctor Registration' : 'Patient Registration'}
        </h1>
        <p className="form-subtitle">
          {role === 'doctor'
            ? 'Join as a Doctor — OTP will be sent to your email'
            : 'Create your patient account — OTP will be sent to your email'}
        </p>

        {error && <div className="alert alert-error">⚠️ {error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          {/* Full Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="full_name">Full Name</label>
            <input
              id="full_name" name="full_name" type="text"
              className={`form-input ${fieldErrors.full_name ? 'error' : ''}`}
              placeholder={role === 'doctor' ? 'Dr. Full Name' : 'Your full name'}
              value={form.full_name} onChange={handleChange}
            />
            {fieldErrors.full_name && <p className="field-error">⚠ {fieldErrors.full_name}</p>}
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              id="email" name="email" type="email"
              className={`form-input ${fieldErrors.email ? 'error' : ''}`}
              placeholder="email@example.com"
              value={form.email} onChange={handleChange}
            />
            {fieldErrors.email && <p className="field-error">⚠ {fieldErrors.email}</p>}
          </div>

          {/* Mobile */}
          <div className="form-group">
            <label className="form-label" htmlFor="mobile">Mobile Number</label>
            <div className="mobile-group">
              <span className="mobile-prefix">+91 (IND)</span>
              <input
                id="mobile" name="mobile" type="tel"
                className={`form-input mobile-input ${fieldErrors.mobile ? 'error' : ''}`}
                placeholder="10-digit mobile number"
                value={form.mobile} onChange={handleChange} maxLength={10}
              />
            </div>
            {fieldErrors.mobile && <p className="field-error">⚠ {fieldErrors.mobile}</p>}
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">Create Password</label>
            <div className="password-wrapper">
              <input
                id="password" name="password"
                type={showPw ? 'text' : 'password'}
                className={`form-input ${fieldErrors.password ? 'error' : ''}`}
                placeholder="Min 8 chars, 1 uppercase, 1 number"
                value={form.password} onChange={handleChange}
                style={{ paddingRight: '44px' }}
              />
              <button type="button" className="password-toggle" onClick={() => setShowPw(!showPw)}>
                {showPw ? '🙈' : '👁️'}
              </button>
            </div>
            {form.password && (
              <div className="pw-strength">
                <div className="pw-strength-bar">
                  <div className="pw-strength-fill" style={{
                    width: `${(strength / 4) * 100}%`,
                    background: STRENGTH_COLORS[strength],
                  }} />
                </div>
                <span className="pw-strength-label" style={{ color: STRENGTH_COLORS[strength] }}>
                  Password Strength: <strong>{STRENGTH_LABELS[strength]}</strong>
                </span>
              </div>
            )}
            {fieldErrors.password && <p className="field-error">⚠ {fieldErrors.password}</p>}
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="confirm_password">Re-enter Password</label>
            <input
              id="confirm_password" name="confirm_password"
              type={showPw ? 'text' : 'password'}
              className={`form-input ${fieldErrors.confirm_password ? 'error' : ''}`}
              placeholder="Confirm your password"
              value={form.confirm_password} onChange={handleChange}
            />
            {fieldErrors.confirm_password && <p className="field-error">⚠ {fieldErrors.confirm_password}</p>}
          </div>

          <div className="check-group">
            <input type="checkbox" id="terms" required />
            <label htmlFor="terms">
              By signing up, I agree to the <button type="button" className="auth-link">terms & conditions</button>
            </label>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading && <span className="spinner" />}
            {loading ? 'Sending OTP…' : 'Send OTP'}
          </button>
        </form>

        <div className="auth-footer" style={{marginTop:'20px'}}>
          Already have an account?{' '}
          <Link to="/auth/login" className="auth-link">Login</Link>
        </div>
      </div>
    </div>
  )
}
