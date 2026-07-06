// src/pages/admin/ManageAppointments.jsx
import { useState, useEffect } from 'react'
import { fetchAdminAppointments, updateAppointmentStatus } from '../../api/admin'

const STATUS_OPTS = ['', 'pending', 'confirmed', 'completed', 'cancelled', 'no_show']
const DATE_OPTS   = [
  { value: '',         label: 'All Dates' },
  { value: 'today',    label: 'Today' },
  { value: 'upcoming', label: 'Upcoming' },
  { value: 'past',     label: 'Past' },
]
const STATUS_BADGE = {
  pending:   'adm-badge-warning',
  confirmed: 'adm-badge-info',
  completed: 'adm-badge-success',
  cancelled: 'adm-badge-danger',
  no_show:   'adm-badge-muted',
}

export default function ManageAppointments() {
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(true)
  const [page, setPage]         = useState(1)
  const [status, setStatus]     = useState('')
  const [dateF, setDateF]       = useState('')
  const [busy, setBusy]         = useState(null)

  const load = (p = page) => {
    setLoading(true)
    fetchAdminAppointments(p, status, dateF).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(1); setPage(1) }, [status, dateF])
  useEffect(() => { load(page) }, [page])

  const handleStatus = async (id, newStatus) => {
    setBusy(id)
    await updateAppointmentStatus(id, newStatus)
    load(); setBusy(null)
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 1

  return (
    <div className="adm-table-wrap">
      <div className="adm-table-header">
        <div className="adm-filters">
          <select className="adm-filter-select" value={status} onChange={e => setStatus(e.target.value)}>
            {STATUS_OPTS.map(s => (
              <option key={s} value={s}>{s ? s.replace('_',' ') : 'All Statuses'}</option>
            ))}
          </select>
          <select className="adm-filter-select" value={dateF} onChange={e => setDateF(e.target.value)}>
            {DATE_OPTS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
          </select>
        </div>
        <div style={{ fontSize: '0.82rem', color: '#64748b' }}>{data?.total ?? 0} appointments</div>
      </div>

      {loading ? <div className="adm-loading">Loading…</div>
      : !data?.items?.length ? (
        <div className="adm-empty"><div className="icon">📅</div><div className="msg">No appointments found.</div></div>
      ) : (
        <table className="adm-table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date &amp; Time</th>
              <th>Type</th>
              <th>Status</th>
              <th>Fee</th>
              <th>Override Status</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(a => (
              <tr key={a.id}>
                <td style={{ fontWeight: 500 }}>{a.patient_name}</td>
                <td style={{ color: '#94a3b8' }}>{a.doctor_name}</td>
                <td>
                  <div style={{ fontWeight: 500 }}>{a.appointment_date}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.slot_start_time?.slice(0,5)}</div>
                </td>
                <td>
                  <span className={`adm-badge ${a.consultation_type === 'online' ? 'adm-badge-info' : 'adm-badge-muted'}`}>
                    {a.consultation_type === 'online' ? '🎥 Online' : '🏥 In-Clinic'}
                  </span>
                </td>
                <td>
                  <span className={`adm-badge ${STATUS_BADGE[a.status] || 'adm-badge-muted'}`} style={{ textTransform: 'capitalize' }}>
                    {a.status.replace('_',' ')}
                  </span>
                </td>
                <td style={{ color: '#10b981', fontWeight: 600 }}>
                  {a.fee_charged ? `₹${a.fee_charged}` : '—'}
                </td>
                <td>
                  <select className="adm-filter-select" style={{ fontSize: '0.76rem' }}
                    disabled={busy === a.id}
                    value={a.status}
                    onChange={e => handleStatus(a.id, e.target.value)}>
                    {['pending','confirmed','completed','cancelled','no_show'].map(s => (
                      <option key={s} value={s}>{s.replace('_',' ')}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {totalPages > 1 && (
        <div className="adm-pagination">
          <button className="btn-adm-ghost" onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1}>← Prev</button>
          <span>Page {page} of {totalPages}</span>
          <button className="btn-adm-ghost" onClick={() => setPage(p => Math.min(totalPages,p+1))} disabled={page===totalPages}>Next →</button>
        </div>
      )}
    </div>
  )
}
