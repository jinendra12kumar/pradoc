// src/pages/patient/MyAppointments.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchMyAppointments, cancelAppointment } from '../../api/appointments'
import AppointmentCard from '../../components/appointments/AppointmentCard'
import '../../appointments.css'

const TABS = [
  { key: '', label: 'All' },
  { key: 'pending',   label: 'Pending' },
  { key: 'confirmed', label: 'Confirmed' },
  { key: 'completed', label: 'Completed' },
  { key: 'cancelled', label: 'Cancelled' },
]

export default function MyAppointments() {
  const navigate = useNavigate()
  const [tab, setTab]       = useState('')
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage]     = useState(1)

  const load = (t = tab, p = page) => {
    setLoading(true)
    fetchMyAppointments(t, p)
      .then(setData)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(tab, 1); setPage(1) }, [tab])
  useEffect(() => { load(tab, page) }, [page])

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return
    await cancelAppointment(id)
    load()
  }

  const totalPages = data ? Math.ceil(data.total / 10) : 1

  return (
    <div style={{ padding: '28px 24px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e293b' }}>📋 My Appointments</h1>
        <button className="btn-primary" onClick={() => navigate('/patient/doctors')}>+ Book New</button>
      </div>

      {/* Tab filter */}
      <div className="tab-pills">
        {TABS.map(t => (
          <button key={t.key} className={`tab-pill ${tab === t.key ? 'active' : ''}`}
            onClick={() => setTab(t.key)}>
            {t.label}
            {data && t.key === tab && <span style={{ marginLeft: 6, background: 'rgba(255,255,255,0.3)', padding: '1px 7px', borderRadius: 10 }}>{data.total}</span>}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 48, color: '#94a3b8' }}>Loading appointments…</div>
      ) : !data?.items?.length ? (
        <div className="empty-state">
          <div className="emoji">📭</div>
          <div>No {tab || ''} appointments found.</div>
          <button className="btn-primary" style={{ marginTop: 12 }} onClick={() => navigate('/patient/doctors')}>
            Book Your First Appointment
          </button>
        </div>
      ) : (
        <>
          <div style={{ display: 'grid', gap: 14 }}>
            {data.items.map(appt => (
              <div key={appt.id}>
                <AppointmentCard appt={appt} role="patient" onCancel={handleCancel} />
                {appt.status === 'confirmed' && appt.consultation_type === 'online' && (
                  <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      className="btn-primary"
                      style={{
                        background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                        display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem',
                        padding: '9px 20px', borderRadius: 10,
                      }}
                      onClick={() => navigate(`/consultation/${appt.id}`)}
                    >
                      🎥 Join Video Consultation
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: 10, marginTop: 28 }}>
              <button className="btn-outline btn-sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>← Prev</button>
              <span style={{ lineHeight: '34px', fontSize: '0.85rem', color: '#64748b' }}>Page {page} of {totalPages}</span>
              <button className="btn-outline btn-sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
