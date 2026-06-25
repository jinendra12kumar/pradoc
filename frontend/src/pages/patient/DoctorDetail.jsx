import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { patientApi } from '../../api/doctorApi'

const DAY_NAMES = { MON: 'Monday', TUE: 'Tuesday', WED: 'Wednesday', THU: 'Thursday', FRI: 'Friday', SAT: 'Saturday', SUN: 'Sunday' }

const formatTime = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hr = parseInt(h)
  const ampm = hr >= 12 ? 'PM' : 'AM'
  return `${hr % 12 || 12}:${m} ${ampm}`
}

export default function DoctorDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doctor, setDoctor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    patientApi.getDoctorDetail(id)
      .then(res => setDoctor(res.data))
      .catch(() => setError('Doctor not found'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner" />
        <p className="loading-text">Loading doctor profile...</p>
      </div>
    )
  }

  if (error || !doctor) {
    return (
      <div className="detail-page">
        <div className="no-results">
          <div className="no-results-icon">😔</div>
          <h3 className="no-results-title">Doctor Not Found</h3>
          <p className="no-results-text">This profile may not be available.</p>
          <button className="back-btn" onClick={() => navigate('/patient/doctors')} style={{ marginTop: 20 }}>
            ← Back to Search
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="detail-page">
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

      {/* ── Hero Header ──────────────────────────────────────────── */}
      <div className="detail-hero">
        <div className="detail-photo">
          {doctor.profile_photo
            ? <img src={`/${doctor.profile_photo}`} alt={doctor.full_name} />
            : '👨‍⚕️'
          }
        </div>
        <div className="detail-hero-info">
          <h1 className="detail-name">{doctor.full_name}</h1>
          {doctor.primary_specialization && (
            <span className="detail-primary-spec">{doctor.primary_specialization}</span>
          )}
          <div className="detail-stats">
            {doctor.years_of_experience != null && (
              <div className="detail-stat">
                <span className="detail-stat-value">{doctor.years_of_experience}+</span>
                <span className="detail-stat-label">Years Experience</span>
              </div>
            )}
            {doctor.clinics?.length > 0 && (
              <div className="detail-stat">
                <span className="detail-stat-value">
                  ₹{Number(doctor.clinics[0].consultation_fee).toLocaleString()}
                </span>
                <span className="detail-stat-label">Consultation Fee</span>
              </div>
            )}
            {doctor.gender && (
              <div className="detail-stat">
                <span className="detail-stat-value" style={{ textTransform: 'capitalize' }}>
                  {doctor.gender}
                </span>
                <span className="detail-stat-label">Gender</span>
              </div>
            )}
            {doctor.clinics?.length > 0 && (
              <div className="detail-stat">
                <span className="detail-stat-value">{doctor.clinics.length}</span>
                <span className="detail-stat-label">Clinic{doctor.clinics.length > 1 ? 's' : ''}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── About ────────────────────────────────────────────────── */}
      {(doctor.bio || doctor.languages_spoken?.length > 0) && (
        <div className="detail-section">
          <h2 className="detail-section-title">📝 About</h2>
          {doctor.bio && <p className="detail-bio">{doctor.bio}</p>}
          {doctor.languages_spoken?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-dark)', marginRight: 8 }}>
                Languages:
              </span>
              <div className="detail-tags" style={{ display: 'inline-flex' }}>
                {doctor.languages_spoken.map((l, i) => (
                  <span key={i} className="detail-tag">{l}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Specializations ──────────────────────────────────────── */}
      {doctor.specializations?.length > 0 && (
        <div className="detail-section">
          <h2 className="detail-section-title">🎯 Specializations</h2>
          <div className="detail-tags">
            {doctor.specializations.map((s, i) => (
              <span
                key={i}
                className={`detail-tag ${s === doctor.primary_specialization ? 'primary' : ''}`}
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Education & Qualifications ───────────────────────────── */}
      {doctor.qualifications?.length > 0 && (
        <div className="detail-section">
          <h2 className="detail-section-title">🎓 Education & Qualifications</h2>
          <ul className="detail-qual-list">
            {doctor.qualifications.map((q, i) => (
              <li key={i} className="detail-qual-item">
                <div className="detail-qual-icon">🎓</div>
                <div className="detail-qual-text">
                  <div className="detail-qual-type">{q.qualification_type}</div>
                  <div className="detail-qual-college">
                    {q.college_name} • {q.university_name} • {q.graduation_year}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          {doctor.current_hospital && (
            <div style={{ marginTop: 16, padding: '12px 16px', background: 'var(--teal-light)', borderRadius: 10 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--teal-dark)' }}>
                🏥 Currently at: {doctor.current_hospital}
              </span>
            </div>
          )}
        </div>
      )}

      {/* ── Clinics & Availability ───────────────────────────────── */}
      {doctor.clinics?.length > 0 && (
        <div className="detail-section">
          <h2 className="detail-section-title">📍 Clinics & Availability</h2>
          {doctor.clinics.map((clinic, i) => (
            <div key={i} className="detail-clinic">
              <div className="detail-clinic-header">
                <div>
                  <div className="detail-clinic-name">{clinic.clinic_name}</div>
                  <div className="detail-clinic-address">
                    {clinic.address}, {clinic.city}, {clinic.state} - {clinic.pincode}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="detail-clinic-fee">
                    ₹{Number(clinic.consultation_fee).toLocaleString()}
                  </div>
                  {clinic.online_consultation && (
                    <span className="doctor-card-tag online" style={{ marginTop: 4, display: 'inline-block' }}>
                      ● Online Available
                      {clinic.online_consultation_fee && (
                        <> (₹{Number(clinic.online_consultation_fee).toLocaleString()})</>
                      )}
                    </span>
                  )}
                </div>
              </div>

              {/* Availability Grid */}
              {clinic.availability_slots?.length > 0 && (
                <div className="avail-grid">
                  {clinic.availability_slots.map((slot, j) => (
                    <div key={j} className={`avail-slot ${slot.is_active ? 'active' : ''}`}>
                      <div className="avail-day">{DAY_NAMES[slot.day_of_week] || slot.day_of_week}</div>
                      <div className="avail-time">
                        {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
