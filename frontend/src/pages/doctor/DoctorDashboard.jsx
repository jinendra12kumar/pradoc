import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { doctorApi } from '../../api/doctorApi'
import './doctor-onboarding.css'

const SCORE_LABELS = {
  registration_number: 'Registration Number',
  qualification: 'Qualification Added',
  registration_certificate: 'Registration Certificate',
  degree_certificate: 'Degree Certificate',
  clinic_information: 'Clinic Information',
}

const SCORE_MAX = {
  registration_number: 20,
  qualification: 20,
  registration_certificate: 30,
  degree_certificate: 20,
  clinic_information: 10,
}

export default function DoctorDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [dash, setDash] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await doctorApi.getDashboard()
        setDash(res.data)
        // If profile not complete, redirect to onboarding
        if (!res.data.is_profile_complete && res.data.verification_status === 'PENDING') {
          navigate('/doctor/onboarding')
          return
        }
      } catch (e) {
        console.error(e)
        navigate('/doctor/onboarding')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [navigate])

  const handleLogout = () => { logout(); navigate('/auth/login') }

  if (loading) {
    return <div className="loading-page"><div className="loading-spinner" /></div>
  }

  if (!dash) return null

  const pct = dash.profile_completion_pct
  const circumference = 2 * Math.PI * 34
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="doc-dashboard">
      <div className="doc-dashboard-container">
        <div className="doc-dashboard-header">
          <h1>👨‍⚕️ Doctor Dashboard</h1>
          <button className="dash-logout-btn" onClick={handleLogout}>Logout</button>
        </div>

        {/* Stats */}
        <div className="dash-stats">
          <div className="dash-stat-card">
            <div className="completion-ring-wrap">
              <div className="completion-ring">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle className="ring-bg" cx="40" cy="40" r="34" />
                  <circle className="ring-fill" cx="40" cy="40" r="34"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset} />
                </svg>
                <span className="ring-text">{pct}%</span>
              </div>
            </div>
            <div className="stat-label">Profile Complete</div>
          </div>

          <div className="dash-stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{dash.verification_score}</div>
            <div className="stat-label">Verification Score</div>
          </div>

          <div className="dash-stat-card">
            <div className="stat-icon">
              {dash.verification_status === 'APPROVED' ? '✅' :
               dash.verification_status === 'REJECTED' ? '❌' :
               dash.verification_status === 'UNDER_REVIEW' ? '🔍' : '⏳'}
            </div>
            <span className={`status-badge ${dash.verification_status}`}>
              {dash.verification_status.replace('_', ' ')}
            </span>
            <div className="stat-label">Status</div>
          </div>
        </div>

        {/* Score Breakdown */}
        {dash.score_breakdown && (
          <div className="dash-section">
            <h3>Verification Score Breakdown</h3>
            <div className="score-breakdown">
              {Object.entries(dash.score_breakdown).map(([key, val]) => (
                <div className="score-row" key={key}>
                  <span className="score-row-label">{SCORE_LABELS[key] || key}</span>
                  <div className="score-row-bar">
                    <div className="score-row-fill"
                      style={{ width: `${(val / (SCORE_MAX[key] || 30)) * 100}%` }} />
                  </div>
                  <span className="score-row-value">+{val}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Missing Fields */}
        {dash.missing_fields?.length > 0 && (
          <div className="dash-section">
            <h3>⚠️ Missing Fields</h3>
            <ul className="missing-list">
              {dash.missing_fields.map(f => (
                <li key={f}><span className="missing-dot" /> {f}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Missing Documents */}
        {dash.missing_documents?.length > 0 && (
          <div className="dash-section">
            <h3>📎 Missing Documents</h3>
            <ul className="missing-list">
              {dash.missing_documents.map(d => (
                <li key={d}><span className="missing-dot" /> {d}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Flags */}
        {dash.flags?.length > 0 && (
          <div className="dash-section">
            <h3>🚩 Verification Flags</h3>
            <ul className="missing-list">
              {dash.flags.map(f => (
                <li key={f.id}>
                  <span className="missing-dot" style={{background: f.severity === 'CRITICAL' ? 'var(--error)' : '#ed8936'}} />
                  <span><strong>[{f.severity}]</strong> {f.description}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action buttons */}
        <div style={{display: 'flex', gap: 12, marginTop: 20}}>
          <button className="btn-next" onClick={() => navigate('/doctor/onboarding')}>
            ✏️ Edit Profile
          </button>
          {dash.verification_status === 'PENDING' && (
            <button className="btn-submit" onClick={async () => {
              try {
                await doctorApi.submitForVerification()
                const res = await doctorApi.getDashboard()
                setDash(res.data)
              } catch (e) {
                alert(e.response?.data?.detail || 'Submission failed.')
              }
            }}>
              🚀 Submit for Verification
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
