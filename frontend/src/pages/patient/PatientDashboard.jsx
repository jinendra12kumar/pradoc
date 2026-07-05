// src/pages/patient/PatientDashboard.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchPatientDashboard, fetchNotifications, markNotificationRead, cancelAppointment } from '../../api/appointments'
import AppointmentCard from '../../components/appointments/AppointmentCard'
import '../../appointments.css'

export default function PatientDashboard() {
  const navigate = useNavigate()
  const [data, setData]     = useState(null)
  const [notifs, setNotifs] = useState([])
  const [loading, setLoading] = useState(true)
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const load = () => {
    setLoading(true)
    Promise.all([fetchPatientDashboard(), fetchNotifications()])
      .then(([dash, n]) => { setData(dash); setNotifs(Array.isArray(n) ? n : []) })
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleCancel = async (id) => {
    if (!window.confirm('Cancel this appointment?')) return
    await cancelAppointment(id)
    load()
  }

  const handleNotifClick = async (n) => {
    if (!n.is_read) await markNotificationRead(n.id)
    setNotifs(prev => prev.map(x => x.id === n.id ? { ...x, is_read: true } : x))
  }

  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>Loading dashboard…</div>

  const stats = [
    { icon: '📅', value: data?.upcoming_count ?? 0, label: 'Upcoming',  color: '#6366f1' },
    { icon: '✅', value: data?.past_count ?? 0,      label: 'Past',      color: '#10b981' },
    { icon: '❌', value: data?.cancelled_count ?? 0, label: 'Cancelled', color: '#ef4444' },
    { icon: '🔔', value: data?.unread_notifications ?? 0, label: 'Notifications', color: '#f59e0b' },
  ]

  return (
    <div style={{ padding: '28px 24px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b', marginBottom: 4 }}>
            👋 Hello, {user.full_name?.split(' ')[0] || 'Patient'}
          </h1>
          <p style={{ fontSize: '0.88rem', color: '#64748b' }}>Here's your health overview</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/patient/doctors')}>🔍 Find Doctor</button>
      </div>

      <div className="stat-cards">
        {stats.map(s => (
          <div key={s.label} className="stat-card" style={{ borderTop: `3px solid ${s.color}` }}>
            <div className="stat-icon">{s.icon}</div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 32, flexWrap: 'wrap' }}>
        {[
          { icon: '📋', label: 'My Appointments', path: '/patient/my-appointments' },
          { icon: '👤', label: 'My Profile',      path: '/patient/profile' },
          { icon: '🔍', label: 'Search Doctors',  path: '/patient/doctors' },
        ].map(a => (
          <button key={a.label} onClick={() => navigate(a.path)}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 18px', borderRadius: 12, background: '#fff', border: '1px solid #e2e8f0', cursor: 'pointer', fontWeight: 600, fontSize: '0.88rem', color: '#334155' }}>
            {a.icon} {a.label}
          </button>
        ))}
      </div>

      <div className="section-title">📅 Upcoming Appointments</div>
      {!data?.upcoming_appointments?.length ? (
        <div className="empty-state" style={{ marginBottom: 32 }}>
          <div className="emoji">📅</div>
          <div>No upcoming appointments.</div>
          <button className="btn-primary" style={{ marginTop: 12 }} onClick={() => navigate('/patient/doctors')}>Book Now</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 14, marginBottom: 32 }}>
          {data.upcoming_appointments.map(appt => (
            <AppointmentCard key={appt.id} appt={appt} role="patient" onCancel={handleCancel} />
          ))}
        </div>
      )}

      {data?.recent_prescriptions?.length > 0 && (
        <>
          <div className="section-title">💊 Recent Prescriptions</div>
          <div style={{ display: 'grid', gap: 12, marginBottom: 32 }}>
            {data.recent_prescriptions.map(rx => (
              <div key={rx.id} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: '16px 20px' }}>
                <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>📋 {rx.diagnosis}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 8 }}>
                  {new Date(rx.created_at).toLocaleDateString('en-IN')}
                  {rx.follow_up_date && <span> · Follow-up: {rx.follow_up_date}</span>}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {rx.medicines?.slice(0, 3).map((m, i) => (
                    <span key={i} style={{ fontSize: '0.78rem', padding: '3px 10px', background: '#dbeafe', color: '#1e40af', borderRadius: 20, fontWeight: 600 }}>
                      {m.name} {m.dosage}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {notifs.length > 0 && (
        <>
          <div className="section-title">🔔 Notifications</div>
          <div style={{ display: 'grid', gap: 10 }}>
            {notifs.slice(0, 5).map(n => (
              <div key={n.id} onClick={() => handleNotifClick(n)}
                style={{ background: n.is_read ? '#fff' : '#fefce8', border: `1px solid ${n.is_read ? '#e2e8f0' : '#fde68a'}`, borderRadius: 12, padding: '12px 16px', cursor: 'pointer' }}>
                <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#1e293b' }}>{n.title}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: 3 }}>{n.message}</div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: 6 }}>{new Date(n.created_at).toLocaleString('en-IN')}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
