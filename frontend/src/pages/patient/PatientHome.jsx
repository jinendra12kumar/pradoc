import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { patientApi } from '../../api/doctorApi'

export default function PatientHome() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    patientApi.getHomeData()
      .then(res => setData(res.data))
      .catch(err => console.error('Failed to load home data:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    navigate(`/patient/doctors?q=${encodeURIComponent(search.trim())}`)
  }

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner" />
        <p className="loading-text">Loading...</p>
      </div>
    )
  }

  const specs = data?.specializations || []
  const featured = data?.featured_doctors || []
  const clinics = data?.top_clinics || []

  return (
    <>
      {/* ── Hero Section ─────────────────────────────────────────── */}
      <section className="hero-section">
        <h1 className="hero-title">
          Your Health, <span>Our Priority</span>
        </h1>
        <p className="hero-subtitle">
          Find and book appointments with the best doctors near you.
          Search by specialization, experience, or availability.
        </p>
        <form className="hero-search" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search doctors, specializations, clinics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="hero-search-btn">
            Search
          </button>
        </form>
      </section>

      {/* ── Specializations ──────────────────────────────────────── */}
      {specs.length > 0 && (
        <section className="section">
          <div className="section-header">
            <div>
              <h2 className="section-title">
                Consult <span>Top Doctors</span> Online
              </h2>
              <p className="section-subtitle">
                Book appointments for any health concern
              </p>
            </div>
            <Link to="/patient/doctors" className="section-link">
              View All →
            </Link>
          </div>
          <div className="spec-grid">
            {specs.map(spec => (
              <Link
                key={spec.name}
                to={`/patient/doctors?specialization=${encodeURIComponent(spec.name)}`}
                className="spec-card"
              >
                <span className="spec-icon">{spec.icon}</span>
                <span className="spec-name">{spec.name}</span>
                <span className="spec-count">
                  {spec.count} Doctor{spec.count !== 1 ? 's' : ''}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ── Featured Doctors ─────────────────────────────────────── */}
      {featured.length > 0 && (
        <section className="section" style={{ background: 'var(--white)' }}>
          <div className="section-header">
            <div>
              <h2 className="section-title">
                <span>Featured</span> Doctors
              </h2>
              <p className="section-subtitle">
                Top-rated doctors based on experience and reviews
              </p>
            </div>
            <Link to="/patient/doctors" className="section-link">
              See All →
            </Link>
          </div>
          <div className="doctors-grid">
            {featured.map(doc => (
              <DoctorCard key={doc.id} doctor={doc} />
            ))}
          </div>
        </section>
      )}

      {/* ── Top Clinics ──────────────────────────────────────────── */}
      {clinics.length > 0 && (
        <section className="section">
          <div className="section-header">
            <div>
              <h2 className="section-title">
                Book at <span>Top Clinics</span>
              </h2>
              <p className="section-subtitle">
                Trusted clinics with verified doctors
              </p>
            </div>
          </div>
          <div className="clinics-grid">
            {clinics.map((clinic, i) => (
              <div key={i} className="clinic-card">
                <div className="clinic-card-icon">🏥</div>
                <div className="clinic-card-name">{clinic.clinic_name}</div>
                <div className="clinic-card-city">
                  📍 {clinic.city}, {clinic.state}
                </div>
                <div className="clinic-card-stats">
                  <span className="clinic-card-stat">
                    👨‍⚕️ {clinic.doctor_count} Doctor{clinic.doctor_count !== 1 ? 's' : ''}
                  </span>
                  {clinic.specializations.slice(0, 2).map((s, j) => (
                    <span key={j} className="clinic-card-stat">{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Show empty state if no data at all */}
      {specs.length === 0 && featured.length === 0 && clinics.length === 0 && (
        <div className="no-results" style={{ margin: '40px' }}>
          <div className="no-results-icon">🏥</div>
          <h3 className="no-results-title">No Doctors Available Yet</h3>
          <p className="no-results-text">
            Verified doctors will appear here once they complete their profiles.
          </p>
        </div>
      )}
    </>
  )
}

/* ── Reusable Doctor Card ──────────────────────────────────────────────────── */
function DoctorCard({ doctor }) {
  const navigate = useNavigate()

  return (
    <div
      className="doctor-card"
      onClick={() => navigate(`/patient/doctors/${doctor.id}`)}
    >
      <div className="doctor-card-photo">
        {doctor.profile_photo
          ? <img src={`/${doctor.profile_photo}`} alt={doctor.full_name} />
          : '👨‍⚕️'
        }
      </div>
      <div className="doctor-card-info">
        <div className="doctor-card-name">{doctor.full_name}</div>
        <div className="doctor-card-spec">
          {doctor.primary_specialization || 'General Physician'}
        </div>
        <div className="doctor-card-meta">
          {doctor.years_of_experience != null && (
            <span className="doctor-card-tag">
              {doctor.years_of_experience}+ yrs exp
            </span>
          )}
          {doctor.qualifications?.slice(0, 2).map((q, i) => (
            <span key={i} className="doctor-card-tag">{q.split(' - ')[0]}</span>
          ))}
          {doctor.online_consultation && (
            <span className="doctor-card-tag online">● Online</span>
          )}
        </div>
        <div className="doctor-card-bottom">
          <div className="doctor-card-fee">
            {doctor.consultation_fee
              ? <>₹{Number(doctor.consultation_fee).toLocaleString()} <small>consultation</small></>
              : <small>Fee not listed</small>
            }
          </div>
          <button className="doctor-card-btn">View Profile</button>
        </div>
      </div>
    </div>
  )
}

export { DoctorCard }
