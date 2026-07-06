// src/pages/admin/ManagePatients.jsx
import { useState, useEffect } from 'react'
import { fetchAdminPatients, togglePatientActive } from '../../api/admin'

export default function ManagePatients() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage]       = useState(1)
  const [search, setSearch]   = useState('')
  const [busy, setBusy]       = useState(false)

  const load = (p = page, s = search) => {
    setLoading(true)
    fetchAdminPatients(p, s).then(setData).finally(() => setLoading(false))
  }

  useEffect(() => { load(1, search); setPage(1) }, [search])
  useEffect(() => { load(page, search) }, [page])

  const handleToggle = async (userId, current) => {
    setBusy(true)
    await togglePatientActive(userId, !current)
    load(); setBusy(false)
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 1

  return (
    <div className="adm-table-wrap">
      <div className="adm-table-header">
        <div className="adm-search">
          🔍 <input placeholder="Search patients…" value={search}
            onChange={e => setSearch(e.target.value)} />
        </div>
        <div style={{ fontSize: '0.82rem', color: '#64748b' }}>{data?.total ?? 0} patients total</div>
      </div>

      {loading ? <div className="adm-loading">Loading…</div>
      : !data?.items?.length ? (
        <div className="adm-empty"><div className="icon">🧑‍🤝‍🧑</div><div className="msg">No patients found.</div></div>
      ) : (
        <table className="adm-table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Mobile</th>
              <th>Appointments</th>
              <th>Verified</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(pt => (
              <tr key={pt.id}>
                <td>
                  <div style={{ fontWeight: 600, color: '#e2e8f0' }}>{pt.full_name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{pt.email}</div>
                </td>
                <td style={{ color: '#94a3b8' }}>{pt.mobile}</td>
                <td>
                  <span className="adm-badge adm-badge-info">{pt.appointment_count} appts</span>
                </td>
                <td>
                  <span className={`adm-badge ${pt.is_verified ? 'adm-badge-success' : 'adm-badge-warning'}`}>
                    {pt.is_verified ? '✅ Yes' : '⏳ No'}
                  </span>
                </td>
                <td>
                  <span className={`adm-badge ${pt.is_active ? 'adm-badge-success' : 'adm-badge-danger'}`}>
                    {pt.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td style={{ color: '#64748b', fontSize: '0.78rem' }}>
                  {pt.created_at ? new Date(pt.created_at).toLocaleDateString('en-IN') : '—'}
                </td>
                <td>
                  <button className="btn-adm-ghost" disabled={busy}
                    onClick={() => handleToggle(pt.id, pt.is_active)}>
                    {pt.is_active ? '🚫 Disable' : '✅ Enable'}
                  </button>
                </td>
              </tr>
            ))}
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
  )
}
