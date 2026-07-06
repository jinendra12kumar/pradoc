// src/pages/doctor/DoctorDashboard.jsx — Full doctor dashboard with sidebar
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  fetchDoctorDashboard, fetchDoctorAppointments,
  confirmAppointment, completeAppointment, markNoShow,
  fetchPatientHistory,
} from '../../api/appointments'
import AppointmentCard from '../../components/appointments/AppointmentCard'
import PrescriptionModal from '../../components/appointments/PrescriptionModal'
import '../../appointments.css'

const NAV = [
  { key: 'overview',  icon: '📊', label: 'Overview' },
  { key: 'today',     icon: '📅', label: "Today's" },
  { key: 'upcoming',  icon: '🗓️', label: 'Upcoming' },
  { key: 'history',   icon: '📋', label: 'History' },
]

export default function DoctorDashboard() {
  const navigate  = useNavigate()
  const [section, setSection]   = useState('overview')
  const [summary, setSummary]   = useState(null)
  const [appts, setAppts]       = useState(null)
  const [loading, setLoading]   = useState(true)
  const [prescAppt, setPrescAppt] = useState(null)
  const [patientView, setPatientView] = useState(null)
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const loadSummary = () =>
    fetchDoctorDashboard().then(setSummary)

  const loadAppts = (dateFilter = '') => {
    setLoading(true)
    fetchDoctorAppointments(dateFilter)
      .then(setAppts)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadSummary()
    loadAppts()
  }, [])

  useEffect(() => {
    if (section === 'overview') return
    const map = { today: 'today', upcoming: 'upcoming', history: 'past' }
    loadAppts(map[section] || '')
  }, [section])

  const refresh = () => { loadSummary(); loadAppts(section === 'overview' ? '' : section) }

  const handleConfirm  = async (id) => { await confirmAppointment(id);  refresh() }
  const handleComplete = async (id) => { await completeAppointment(id); refresh() }
  const handleNoShow   = async (id) => { await markNoShow(id);          refresh() }

  const handleViewPatient = async (patientId) => {
    const res = await fetchPatientHistory(patientId)
    setPatientView({ id: patientId, ...res })
  }

  return (
    <div className="doctor-dash">
      {/* Sidebar */}
      <aside className="doctor-sidebar">
        <div className="brand">🩺 PraDoc</div>
        {NAV.map(n => (
          <div key={n.key} className={`sidebar-item ${section === n.key ? 'active' : ''}`} onClick={() => setSection(n.key)}>
            {n.icon} {n.label}
          </div>
        ))}
        <div style={{ marginTop: 'auto', paddingTop: 24 }}>
          <div style={{ padding: '10px 14px', color: 'rgba(255,255,255,0.5)', fontSize: '0.78rem' }}>
            Dr. {user.full_name}
          </div>
          <div className="sidebar-item" onClick={() => { localStorage.clear(); navigate('/auth/login') }}>
            🚪 Logout
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="doctor-content">

        {/* ── Overview ── */}
        {section === 'overview' && (
          <>
            <div style={{ marginBottom: 28 }}>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b' }}>
                Good {new Date().getHours() < 12 ? 'Morning' : 'Afternoon'}, Dr. {user.full_name?.split(' ')[0]} 👋
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>{new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
            </div>

            <div className="stat-cards">
              {[
                { icon: '📅', value: summary?.today_count ?? 0,     label: "Today's",  color: '#6366f1' },
                { icon: '🗓️', value: summary?.upcoming_count ?? 0,  label: 'Upcoming', color: '#f59e0b' },
                { icon: '✅', value: summary?.completed_count ?? 0, label: 'Completed',color: '#10b981' },
                { icon: '⏳', value: summary?.pending_count ?? 0,   label: 'Pending',  color: '#ef4444' },
              ].map(s => (
                <div key={s.label} className="stat-card" style={{ borderTop: `3px solid ${s.color}`, cursor: 'pointer' }}
                  onClick={() => setSection(s.label === "Today's" ? 'today' : s.label.toLowerCase())}>
                  <div className="stat-icon">{s.icon}</div>
                  <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
                  <div className="stat-label">{s.label}</div>
                </div>
              ))}
            </div>

            <div className="section-title">📅 Today's Schedule</div>
            {!summary?.today_appointments?.length ? (
              <div className="empty-state"><div className="emoji">☀️</div><div>No appointments today.</div></div>
            ) : (
            <div style={{ display: 'grid', gap: 14 }}>
                {summary.today_appointments.map(appt => (
                  <div key={appt.id}>
                    <AppointmentCard appt={appt} role="doctor"
                      onConfirm={handleConfirm} onComplete={handleComplete}
                      onNoShow={handleNoShow} onPrescribe={setPrescAppt}
                      onViewPatient={handleViewPatient} />
                    {appt.status === 'confirmed' && appt.consultation_type === 'online' && (
                      <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}>
                        <button
                          style={{
                            display: 'flex', alignItems: 'center', gap: 8,
                            padding: '9px 20px', background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                            color: 'white', border: 'none', borderRadius: 10,
                            fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer',
                            boxShadow: '0 4px 14px rgba(99,102,241,0.35)',
                          }}
                          onClick={() => navigate(`/consultation/${appt.id}`)}
                        >
                          🚀 Start Video Consultation
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Appointments list (today/upcoming/history) ── */}
        {section !== 'overview' && (
          <>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e293b', marginBottom: 24 }}>
              {NAV.find(n => n.key === section)?.icon} {NAV.find(n => n.key === section)?.label} Appointments
            </h1>
            {loading ? (
              <div style={{ textAlign: 'center', padding: 48, color: '#94a3b8' }}>Loading…</div>
            ) : !appts?.items?.length ? (
              <div className="empty-state"><div className="emoji">📭</div><div>No appointments found.</div></div>
            ) : (
              <div style={{ display: 'grid', gap: 14 }}>
                {appts.items.map(appt => (
                  <div key={appt.id}>
                    <AppointmentCard appt={appt} role="doctor"
                      onConfirm={handleConfirm} onComplete={handleComplete}
                      onNoShow={handleNoShow} onPrescribe={setPrescAppt}
                      onViewPatient={handleViewPatient} />
                    {appt.status === 'confirmed' && appt.consultation_type === 'online' && (
                      <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}>
                        <button
                          style={{
                            display: 'flex', alignItems: 'center', gap: 8,
                            padding: '9px 20px', background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                            color: 'white', border: 'none', borderRadius: 10,
                            fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer',
                            boxShadow: '0 4px 14px rgba(99,102,241,0.35)',
                          }}
                          onClick={() => navigate(`/consultation/${appt.id}`)}
                        >
                          🚀 Start Video Consultation
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>

      {/* Prescription Modal */}
      {prescAppt && (
        <PrescriptionModal
          appointment={prescAppt}
          onClose={() => setPrescAppt(null)}
          onSuccess={() => { setPrescAppt(null); refresh() }}
        />
      )}

      {/* Patient History Drawer */}
      {patientView && (
        <div className="modal-overlay" onClick={() => setPatientView(null)}>
          <div className="modal-box" style={{ maxWidth: 700 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>👤 Patient History</h3>
              <button className="modal-close" onClick={() => setPatientView(null)}>✕</button>
            </div>
            <div className="section-title" style={{ marginTop: 8 }}>Appointments ({patientView.appointments?.length || 0})</div>
            {patientView.appointments?.slice(0, 5).map(a => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#f8fafc', borderRadius: 10, marginBottom: 8, fontSize: '0.85rem' }}>
                <span>{a.appointment_date} · {a.slot_start_time}</span>
                <span className={`badge badge-${a.status}`} style={{ textTransform: 'capitalize' }}>{a.status}</span>
              </div>
            ))}
            <div className="section-title" style={{ marginTop: 20 }}>Prescriptions ({patientView.prescriptions?.length || 0})</div>
            {patientView.prescriptions?.slice(0, 3).map(rx => (
              <div key={rx.id} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: '12px 14px', marginBottom: 8 }}>
                <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{rx.diagnosis}</div>
                <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 4 }}>
                  {rx.medicines?.map(m => `${m.name} ${m.dosage}`).join(' · ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
