// src/pages/admin/ManageDoctors.jsx
import { useState, useEffect } from 'react'
import { fetchAdminDoctors, verifyDoctor, toggleDoctorActive } from '../../api/admin'

const VERIF_BADGE = {
  APPROVED:    { cls: 'adm-badge-success', label: '✅ Approved' },
  PENDING:     { cls: 'adm-badge-warning', label: '⏳ Pending' },
  UNDER_REVIEW:{ cls: 'adm-badge-info',    label: '🔍 Reviewing' },
  REJECTED:    { cls: 'adm-badge-danger',  label: '❌ Rejected' },
  SUSPENDED:   { cls: 'adm-badge-muted',   label: '🚫 Suspended' },
}

export default function ManageDoctors() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage]     = useState(1)
  const [search, setSearch] = useState('')
  const [rejModal, setRejModal] = useState(null) // { id }
  const [rejReason, setRejReason] = useState('')
  const [busy, setBusy]     = useState(false)

  const load = (p = page, s = search) => {
    setLoading(true)
    fetchAdminDoctors(p, s).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(1, search); setPage(1) }, [search])
  useEffect(() => { load(page, search) }, [page])

  const handleVerify = async (id, status, reason = '') => {
    setBusy(true)
    await verifyDoctor(id, status, reason)
    load(); setBusy(false); setRejModal(null)
  }

  const handleToggle = async (id, current) => {
    setBusy(true)
    await toggleDoctorActive(id, !current)
    load(); setBusy(false)
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 1

  return (
    <>
      <div className="adm-table-wrap">
        <div className="adm-table-header">
          <div className="adm-search">
            🔍 <input placeholder="Search doctors…" value={search}
              onChange={e => setSearch(e.target.value)} />
          </div>
          <div style={{ fontSize: '0.82rem', color: '#64748b' }}>
            {data?.total ?? 0} doctors total
          </div>
        </div>

        {loading ? <div className="adm-loading">Loading…</div>
        : !data?.items?.length ? (
          <div className="adm-empty"><div className="icon">👨‍⚕️</div><div className="msg">No doctors found.</div></div>
        ) : (
          <table className="adm-table">
            <thead>
              <tr>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Experience</th>
                <th>Profile</th>
                <th>Verification</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map(doc => {
                const vb = VERIF_BADGE[doc.verification_status] || VERIF_BADGE.PENDING
                return (
                  <tr key={doc.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: '#e2e8f0' }}>Dr. {doc.full_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.email}</div>
                    </td>
                    <td style={{ color: '#94a3b8' }}>{doc.primary_specialization || '—'}</td>
                    <td style={{ color: '#94a3b8' }}>{doc.years_of_experience ? `${doc.years_of_experience} yrs` : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ width: 60, height: 5, background: '#1e2235', borderRadius: 4, overflow: 'hidden' }}>
                          <div style={{ width: `${doc.profile_completion_pct}%`, height: '100%', background: '#6366f1', borderRadius: 4 }} />
                        </div>
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.profile_completion_pct}%</span>
                      </div>
                    </td>
                    <td><span className={`adm-badge ${vb.cls}`}>{vb.label}</span></td>
                    <td>
                      <span className={`adm-badge ${doc.is_active ? 'adm-badge-success' : 'adm-badge-danger'}`}>
                        {doc.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="adm-action-group">
                        {doc.verification_status !== 'APPROVED' && (
                          <button className="btn-adm-success" disabled={busy}
                            onClick={() => handleVerify(doc.id, 'APPROVED')}>✅ Approve</button>
                        )}
                        {doc.verification_status !== 'REJECTED' && (
                          <button className="btn-adm-danger" disabled={busy}
                            onClick={() => setRejModal({ id: doc.id })}>❌ Reject</button>
                        )}
                        <button className="btn-adm-ghost" disabled={busy}
                          onClick={() => handleToggle(doc.id, doc.is_active)}>
                          {doc.is_active ? '🚫 Disable' : '✅ Enable'}
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}

        {totalPages > 1 && (
          <div className="adm-pagination">
            <button className="btn-adm-ghost" onClick={() => setPage(p => Math.max(1, p-1))} disabled={page===1}>← Prev</button>
            <span>Page {page} of {totalPages}</span>
            <button className="btn-adm-ghost" onClick={() => setPage(p => Math.min(totalPages, p+1))} disabled={page===totalPages}>Next →</button>
          </div>
        )}
      </div>

      {/* Reject Modal */}
      {rejModal && (
        <div className="adm-modal-overlay" onClick={() => setRejModal(null)}>
          <div className="adm-modal" onClick={e => e.stopPropagation()}>
            <h2>❌ Reject Doctor</h2>
            <div className="adm-form-group">
              <label>Reason for rejection</label>
              <textarea placeholder="Provide a clear reason…"
                value={rejReason} onChange={e => setRejReason(e.target.value)} />
            </div>
            <div className="adm-modal-actions">
              <button className="btn-adm-ghost" onClick={() => setRejModal(null)}>Cancel</button>
              <button className="btn-adm-danger" disabled={busy}
                onClick={() => handleVerify(rejModal.id, 'REJECTED', rejReason)}>
                Reject Doctor
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
