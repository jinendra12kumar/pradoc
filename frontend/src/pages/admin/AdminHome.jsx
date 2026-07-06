// src/pages/admin/AdminHome.jsx  — Stats dashboard
import { useState, useEffect } from 'react'
import { fetchAdminStats } from '../../api/admin'

const STATUS_COLORS = {
  pending:   '#f59e0b',
  confirmed: '#6366f1',
  completed: '#10b981',
  cancelled: '#ef4444',
  no_show:   '#64748b',
}

export default function AdminHome() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAdminStats()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="adm-loading">⏳ Loading dashboard…</div>
  if (!stats)  return <div className="adm-empty"><div className="icon">⚠️</div><div className="msg">Could not load statistics.</div></div>

  const totalAppts = Object.values(stats.appointment_status_breakdown || {}).reduce((s,v) => s+v, 0)

  const STAT_CARDS = [
    { icon: '👨‍⚕️', label: 'Total Doctors',          value: stats.total_doctors,          accent: '#6366f1', change: null },
    { icon: '🧑‍🤝‍🧑', label: 'Total Patients',         value: stats.total_patients,         accent: '#8b5cf6', change: null },
    { icon: '📅', label: "Today's Appointments",    value: stats.today_appointments,     accent: '#f59e0b', change: null },
    { icon: '💰', label: 'Total Revenue',            value: `₹${Number(stats.total_revenue).toLocaleString('en-IN', {maximumFractionDigits:0})}`, accent: '#10b981', change: null },
    { icon: '⏳', label: 'Pending Verifications',   value: stats.pending_verifications,  accent: '#ef4444', change: null },
    { icon: '📝', label: 'Total Articles',           value: stats.total_articles,         accent: '#3b82f6', change: null },
    { icon: '⭐', label: 'Total Reviews',            value: stats.total_reviews,          accent: '#f59e0b', change: null },
    { icon: '🗒️', label: 'Total Appointments',      value: totalAppts,                   accent: '#06b6d4', change: null },
  ]

  return (
    <>
      {/* Stat Cards */}
      <div className="adm-stats-grid">
        {STAT_CARDS.map(card => (
          <div key={card.label} className="adm-stat-card" style={{ '--card-accent': card.accent }}>
            <div className="adm-stat-top">
              <div className="adm-stat-icon" style={{ background: `${card.accent}22` }}>
                {card.icon}
              </div>
            </div>
            <div className="adm-stat-value">{card.value}</div>
            <div className="adm-stat-label">{card.label}</div>
          </div>
        ))}
      </div>

      {/* Appointment Status Breakdown */}
      <div className="adm-section-title">📊 Appointment Status Breakdown</div>
      <div className="adm-mini-card" style={{ marginBottom: 28 }}>
        <div style={{ padding: '20px 22px' }}>
          <div style={{ display: 'flex', gap: 4, marginBottom: 14, height: 12, borderRadius: 8, overflow: 'hidden' }}>
            {Object.entries(stats.appointment_status_breakdown || {}).map(([s, cnt]) => (
              <div key={s}
                style={{
                  width: totalAppts ? `${(cnt/totalAppts*100)}%` : 0,
                  background: STATUS_COLORS[s] || '#64748b',
                  transition: 'width 0.8s ease',
                  minWidth: cnt > 0 ? 4 : 0,
                }}
              />
            ))}
          </div>
          <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap' }}>
            {Object.entries(stats.appointment_status_breakdown || {}).map(([s, cnt]) => (
              <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem' }}>
                <span style={{ width: 10, height: 10, borderRadius: 3, background: STATUS_COLORS[s] || '#64748b', display: 'inline-block' }} />
                <span style={{ color: '#94a3b8', textTransform: 'capitalize' }}>{s.replace('_',' ')}</span>
                <span style={{ color: '#e2e8f0', fontWeight: 700 }}>{cnt}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="adm-section-title">⚡ Quick Actions</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
        {[
          { icon: '👨‍⚕️', label: 'Review pending doctor verifications', path: '/admin/doctors', accent: '#6366f1' },
          { icon: '📅', label: 'View today\'s appointments', path: '/admin/appointments', accent: '#f59e0b' },
          { icon: '📝', label: 'Publish a new health article', path: '/admin/articles', accent: '#10b981' },
          { icon: '⭐', label: 'Moderate patient reviews', path: '/admin/reviews', accent: '#8b5cf6' },
        ].map(q => (
          <a key={q.path} href={q.path}
            style={{
              display: 'flex', alignItems: 'center', gap: 12, padding: '16px 18px',
              background: 'var(--adm-card)', border: '1px solid var(--adm-border)',
              borderRadius: 14, textDecoration: 'none', transition: 'all 0.2s',
              borderLeft: `3px solid ${q.accent}`,
            }}
            onMouseEnter={e => e.currentTarget.style.transform='translateY(-2px)'}
            onMouseLeave={e => e.currentTarget.style.transform=''}
          >
            <span style={{ fontSize: '1.4rem' }}>{q.icon}</span>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', lineHeight: 1.4 }}>{q.label}</span>
          </a>
        ))}
      </div>
    </>
  )
}
