// src/pages/admin/ManageReviews.jsx
import { useState, useEffect } from 'react'
import { fetchAdminReviews, adminDeleteReview, adminUpdateReviewStatus } from '../../api/admin'

const STATUS_BADGE = {
  active:   'adm-badge-success',
  hidden:   'adm-badge-muted',
  reported: 'adm-badge-danger',
}

function Stars({ n }) {
  return <span className="stars">{'★'.repeat(n)}{'☆'.repeat(5 - n)}</span>
}

export default function ManageReviews() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage]       = useState(1)
  const [busy, setBusy]       = useState(null)

  const load = (p = page) => {
    setLoading(true)
    fetchAdminReviews(p).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this review? This cannot be undone.')) return
    setBusy(id)
    await adminDeleteReview(id)
    load(); setBusy(null)
  }

  const handleStatus = async (id, newStatus) => {
    setBusy(id)
    await adminUpdateReviewStatus(id, newStatus)
    load(); setBusy(null)
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 1

  return (
    <div className="adm-table-wrap">
      <div className="adm-table-header">
        <div className="adm-section-title" style={{ margin: 0 }}>⭐ All Reviews</div>
        <div style={{ fontSize: '0.82rem', color: '#64748b' }}>{data?.total ?? 0} reviews</div>
      </div>

      {loading ? <div className="adm-loading">Loading…</div>
      : !data?.items?.length ? (
        <div className="adm-empty"><div className="icon">⭐</div><div className="msg">No reviews yet.</div></div>
      ) : (
        <table className="adm-table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Rating</th>
              <th>Comment</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(rv => (
              <tr key={rv.id}>
                <td style={{ fontWeight: 500 }}>{rv.is_anonymous ? '🕵️ Anonymous' : rv.patient_name}</td>
                <td style={{ color: '#94a3b8' }}>{rv.doctor_name}</td>
                <td><Stars n={rv.rating} /></td>
                <td style={{ maxWidth: 240, color: '#94a3b8', fontSize: '0.8rem' }}>
                  {rv.comment ? rv.comment.slice(0, 100) + (rv.comment.length > 100 ? '…' : '') : '—'}
                </td>
                <td>
                  <span className={`adm-badge ${STATUS_BADGE[rv.status] || 'adm-badge-muted'}`}>
                    {rv.status}
                  </span>
                </td>
                <td style={{ color: '#64748b', fontSize: '0.78rem' }}>
                  {rv.created_at ? new Date(rv.created_at).toLocaleDateString('en-IN') : '—'}
                </td>
                <td>
                  <div className="adm-action-group">
                    {rv.status === 'active' && (
                      <button className="btn-adm-warning" disabled={busy===rv.id}
                        onClick={() => handleStatus(rv.id, 'hidden')}>🙈 Hide</button>
                    )}
                    {rv.status === 'hidden' && (
                      <button className="btn-adm-success" disabled={busy===rv.id}
                        onClick={() => handleStatus(rv.id, 'active')}>👁️ Show</button>
                    )}
                    <button className="btn-adm-danger" disabled={busy===rv.id}
                      onClick={() => handleDelete(rv.id)}>🗑️ Delete</button>
                  </div>
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
