import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { authApi } from '../../api/authApi'
import { useAuth } from '../../context/AuthContext'

const RESEND_TIMEOUT = 60

export default function OTPVerifyPage() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const { saveSession } = useAuth()

  const email = location.state?.email || ''
  const role  = location.state?.role  || 'patient'

  const [otp, setOtp]         = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [success, setSuccess] = useState('')
  const [timer, setTimer]     = useState(RESEND_TIMEOUT)
  const [resending, setResending] = useState(false)

  const inputRefs = useRef([])

  // Countdown timer
  useEffect(() => {
    if (timer <= 0) return
    const id = setInterval(() => setTimer(t => t - 1), 1000)
    return () => clearInterval(id)
  }, [timer])

  // Redirect if no email passed
  useEffect(() => {
    if (!email) navigate('/auth/register')
  }, [email, navigate])

  const handleOtpChange = (index, value) => {
    if (!/^\d?$/.test(value)) return
    const updated = [...otp]
    updated[index] = value
    setOtp(updated)
    setError('')
    if (value && index < 5) inputRefs.current[index + 1]?.focus()
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (pasted.length === 6) {
      setOtp(pasted.split(''))
      inputRefs.current[5]?.focus()
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    const otpStr = otp.join('')
    if (otpStr.length !== 6) { setError('Please enter the complete 6-digit OTP.'); return }

    setLoading(true)
    setError('')
    try {
      const res = await authApi.verifyOtp({ email, otp: otpStr })
      saveSession(res.data)
      setSuccess('Email verified! Redirecting to your dashboard…')
      const ROUTES = { patient: '/patient/dashboard', doctor: '/doctor/dashboard', admin: '/admin/dashboard' }
      setTimeout(() => navigate(ROUTES[res.data.role] || '/'), 1500)
    } catch (err) {
      const msg = err?.response?.data?.detail || 'OTP verification failed.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (timer > 0 || resending) return
    setResending(true)
    setError('')
    try {
      await authApi.resendOtp(email)
      setSuccess('A new OTP has been sent to your email.')
      setTimer(RESEND_TIMEOUT)
      setOtp(['', '', '', '', '', ''])
      inputRefs.current[0]?.focus()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to resend OTP.')
    } finally {
      setResending(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-left">
        <a href="/" className="auth-brand"><span className="auth-brand-logo">•PraDoc•</span></a>
        <svg viewBox="0 0 300 260" className="auth-illustration" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="40" width="200" height="180" rx="20" fill="#e6faf8" stroke="#00c8b4" strokeWidth="2"/>
          <rect x="80" y="80" width="140" height="16" rx="8" fill="#00c8b4" opacity="0.4"/>
          <rect x="80" y="108" width="100" height="12" rx="6" fill="#00c8b4" opacity="0.25"/>
          {/* OTP boxes */}
          <rect x="65" y="140" width="30" height="35" rx="6" fill="white" stroke="#00c8b4" strokeWidth="2"/>
          <rect x="103" y="140" width="30" height="35" rx="6" fill="white" stroke="#00c8b4" strokeWidth="2"/>
          <rect x="141" y="140" width="30" height="35" rx="6" fill="white" stroke="#00c8b4" strokeWidth="2"/>
          <rect x="179" y="140" width="30" height="35" rx="6" fill="white" stroke="#00c8b4" strokeWidth="2"/>
          <text x="80" y="165" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#00c8b4">3</text>
          <text x="118" y="165" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#00c8b4">8</text>
          <text x="156" y="165" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#00c8b4">•</text>
          <text x="194" y="165" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#00c8b4">•</text>
          <circle cx="245" cy="55" r="30" fill="url(#email-grad)"/>
          <text x="245" y="63" textAnchor="middle" fontSize="22">✉️</text>
          <defs>
            <radialGradient id="email-grad"><stop offset="0%" stopColor="#4dd9c7"/><stop offset="100%" stopColor="#00a896"/></radialGradient>
          </defs>
        </svg>
        <div className="auth-left-tagline">
          <h2>Check Your Email</h2>
          <p>We sent a 6-digit verification code<br/>to your registered email.</p>
        </div>
      </div>

      <div className="auth-right" style={{justifyContent:'center'}}>
        <h1 className="form-title">Verify Your Email ✉️</h1>
        <p className="form-subtitle">
          Enter the OTP sent to <strong>{email}</strong><br/>
          <span style={{color:'var(--text-light)',fontSize:'12px'}}>
            {role === 'doctor' ? 'Doctor' : 'Patient'} registration — code valid for 5 minutes
          </span>
        </p>

        {error   && <div className="alert alert-error">⚠️ {error}</div>}
        {success && <div className="alert alert-success">✅ {success}</div>}

        <form onSubmit={handleVerify}>
          <div className="otp-container" onPaste={handlePaste}>
            {otp.map((digit, i) => (
              <input
                key={i}
                ref={el => inputRefs.current[i] = el}
                type="text"
                inputMode="numeric"
                maxLength={1}
                className={`otp-box ${digit ? 'filled' : ''}`}
                value={digit}
                onChange={e => handleOtpChange(i, e.target.value)}
                onKeyDown={e => handleKeyDown(i, e)}
                id={`otp-box-${i}`}
              />
            ))}
          </div>

          <button type="submit" className="btn-primary" disabled={loading || !!success}>
            {loading && <span className="spinner" />}
            {loading ? 'Verifying…' : 'Verify OTP'}
          </button>
        </form>

        <div className="resend-timer" style={{marginTop:'20px'}}>
          {timer > 0
            ? <>Resend OTP in <strong style={{color:'var(--teal)'}}>{timer}s</strong></>
            : (
              <button
                type="button"
                className="auth-link"
                onClick={handleResend}
                disabled={resending}
              >
                {resending ? 'Resending…' : 'Resend OTP'}
              </button>
            )
          }
        </div>

        <div className="auth-footer" style={{marginTop:'16px'}}>
          <Link to="/auth/register" className="auth-link">← Back to Register</Link>
        </div>
      </div>
    </div>
  )
}
