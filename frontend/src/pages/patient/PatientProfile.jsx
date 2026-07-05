// src/pages/patient/PatientProfile.jsx  — with file upload + prescription download
import { useState, useEffect } from 'react'
import {
  fetchPatientProfile, updatePatientProfile,
  fetchMedicalRecords, fetchMyPrescriptions,
} from '../../api/appointments'
import MedicalRecordUploader from '../../components/medical/MedicalRecordUploader'
import '../../appointments.css'

const TABS = ['Profile', 'Medical Records', 'Prescriptions']
const token = () => localStorage.getItem('access_token')

function downloadPrescription(rxId) {
  const link = document.createElement('a')
  link.href = `/api/v1/files/prescription/${rxId}/download`
  // attach auth via a small XHR fetch trick since <a> can't set headers
  fetch(link.href, { headers: { Authorization: `Bearer ${token()}` } })
    .then(r => {
      if (!r.ok) throw new Error('Download failed')
      const cd = r.headers.get('content-disposition') || ''
      const fn = cd.match(/filename="(.+)"/)?.[1] || `prescription_${rxId.slice(0,8)}.pdf`
      return r.blob().then(blob => ({ blob, fn }))
    })
    .then(({ blob, fn }) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = fn; a.click()
      URL.revokeObjectURL(url)
    })
    .catch(() => alert('Could not download prescription.'))
}

function viewRecord(recordId) {
  window.open(`/api/v1/files/medical-records/${recordId}/view?token=${token()}`, '_blank')
}

export default function PatientProfile() {
  const [tab, setTab]         = useState('Profile')
  const [profile, setProfile] = useState(null)
  const [records, setRecords] = useState([])
  const [prescriptions, setPrescriptions] = useState([])
  const [editing, setEditing] = useState(false)
  const [form, setForm]       = useState({})
  const [saving, setSaving]   = useState(false)
  const [msg, setMsg]         = useState('')
  const [showUploader, setShowUploader] = useState(false)

  const loadAll = () => {
    fetchPatientProfile().then(p => { setProfile(p); setForm(p) })
    fetchMedicalRecords().then(r => setRecords(Array.isArray(r) ? r : []))
    fetchMyPrescriptions().then(p => setPrescriptions(Array.isArray(p) ? p : []))
  }
  useEffect(loadAll, [])

  const handleSave = async () => {
    setSaving(true)
    await updatePatientProfile(form)
    setMsg('Profile updated ✅'); setEditing(false); setSaving(false)
    setTimeout(() => setMsg(''), 3000)
  }

  const handleUploadSuccess = () => {
    setShowUploader(false)
    fetchMedicalRecords().then(r => setRecords(Array.isArray(r) ? r : []))
  }

  const f = (k) => ({ value: form[k] || '', onChange: e => setForm(p => ({ ...p, [k]: e.target.value })) })
  const inputStyle = (ed) => ({
    width: '100%', padding: '10px 12px', borderRadius: 10,
    border: `2px solid ${ed ? '#c7d2fe' : '#e2e8f0'}`,
    fontSize: '0.9rem', background: ed ? '#fff' : '#f8fafc',
  })

  const RECORD_TYPE_ICONS = { lab_report:'🧪', xray:'📷', scan:'🩻', prescription:'💊', discharge:'🏥', other:'📁' }

  return (
    <div style={{ padding: '28px 24px', maxWidth: 860, margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e293b', marginBottom: 24 }}>👤 My Profile</h1>

      {msg && (
        <div style={{ padding: '10px 16px', background: '#d1fae5', color: '#065f46', borderRadius: 10, marginBottom: 16, fontWeight: 600 }}>
          {msg}
        </div>
      )}

      <div className="tab-pills">
        {TABS.map(t => <button key={t} className={`tab-pill ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>{t}</button>)}
      </div>

      {/* ── Profile Tab ── */}
      {tab === 'Profile' && profile && (
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 16, padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#1e293b' }}>{profile.full_name}</div>
              <div style={{ fontSize: '0.83rem', color: '#64748b' }}>{profile.email} · {profile.mobile}</div>
            </div>
            {!editing
              ? <button className="btn-outline" onClick={() => setEditing(true)}>✏️ Edit</button>
              : <div style={{ display: 'flex', gap: 8 }}>
                  <button className="btn-outline btn-sm" onClick={() => setEditing(false)}>Cancel</button>
                  <button className="btn-primary btn-sm" onClick={handleSave} disabled={saving}>{saving ? '⏳' : 'Save'}</button>
                </div>
            }
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[
              { label: 'Date of Birth', key: 'date_of_birth', type: 'date' },
              { label: 'Gender', key: 'gender', type: 'select', opts: ['male', 'female', 'other'] },
              { label: 'Blood Group', key: 'blood_group', type: 'select', opts: ['A+','A-','B+','B-','AB+','AB-','O+','O-'] },
              { label: 'City', key: 'city' },
              { label: 'State', key: 'state' },
              { label: 'Pincode', key: 'pincode' },
              { label: 'Emergency Contact', key: 'emergency_contact_name' },
              { label: 'Emergency Phone', key: 'emergency_contact_phone' },
            ].map(({ label, key, type, opts }) => (
              <div key={key}>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>{label}</label>
                {type === 'select' ? (
                  <select {...f(key)} disabled={!editing} style={inputStyle(editing)}>
                    <option value="">Select</option>
                    {opts.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input type={type || 'text'} {...f(key)} disabled={!editing} style={inputStyle(editing)} />
                )}
              </div>
            ))}
          </div>
          <div style={{ marginTop: 16 }}>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Allergies</label>
            <textarea {...f('allergies')} disabled={!editing} rows={2} style={{ ...inputStyle(editing), resize: 'vertical' }} placeholder="e.g. Penicillin, dust..." />
          </div>
          <div style={{ marginTop: 12 }}>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Chronic Conditions</label>
            <textarea {...f('chronic_conditions')} disabled={!editing} rows={2} style={{ ...inputStyle(editing), resize: 'vertical' }} placeholder="e.g. Diabetes Type 2, Hypertension..." />
          </div>
        </div>
      )}

      {/* ── Medical Records Tab ── */}
      {tab === 'Medical Records' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ color: '#64748b', fontSize: '0.88rem' }}>{records.length} record(s)</div>
            <button className="btn-primary btn-sm" onClick={() => setShowUploader(v => !v)}>
              {showUploader ? '✕ Cancel' : '+ Upload Record'}
            </button>
          </div>

          {showUploader && (
            <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 16, padding: 24, marginBottom: 20 }}>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: 16 }}>📤 Upload Medical Record</div>
              <MedicalRecordUploader onSuccess={handleUploadSuccess} />
            </div>
          )}

          {!records.length ? (
            <div className="empty-state"><div className="emoji">🗂️</div><div>No medical records yet.</div></div>
          ) : (
            <div style={{ display: 'grid', gap: 12 }}>
              {records.map(r => (
                <div key={r.id} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: '14px 18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      <span style={{ fontSize: 28 }}>{RECORD_TYPE_ICONS[r.record_type] || '📁'}</span>
                      <div>
                        <div style={{ fontWeight: 700, color: '#1e293b' }}>{r.title}</div>
                        <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 2 }}>
                          {r.record_type?.replace('_', ' ')} {r.record_date && `· ${r.record_date}`}
                        </div>
                        {r.description && <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: 3 }}>{r.description}</div>}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                        {new Date(r.created_at).toLocaleDateString('en-IN')}
                      </div>
                      {r.file_path && (
                        <button onClick={() => viewRecord(r.id)}
                          style={{ fontSize: '0.78rem', padding: '5px 12px', borderRadius: 8, background: '#eef2ff', color: '#4338ca', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
                          👁️ View
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Prescriptions Tab ── */}
      {tab === 'Prescriptions' && (
        <div>
          {!prescriptions.length ? (
            <div className="empty-state"><div className="emoji">💊</div><div>No prescriptions yet.</div></div>
          ) : (
            <div style={{ display: 'grid', gap: 14 }}>
              {prescriptions.map(rx => (
                <div key={rx.id} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: '18px 20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                    <div>
                      <div style={{ fontWeight: 800, color: '#1e293b', fontSize: '0.95rem' }}>📋 {rx.diagnosis}</div>
                      <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: 3 }}>
                        {new Date(rx.created_at).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })}
                        {rx.follow_up_date && <span style={{ color: '#6366f1', marginLeft: 10 }}>🗓️ Follow-up: {rx.follow_up_date}</span>}
                      </div>
                    </div>
                    <button
                      onClick={() => downloadPrescription(rx.id)}
                      style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 9, background: 'linear-gradient(135deg,#6366f1,#4338ca)', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 700, fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
                      ⬇️ Download PDF
                    </button>
                  </div>
                  <div style={{ display: 'grid', gap: 6 }}>
                    {rx.medicines?.map((m, i) => (
                      <div key={i} style={{ display: 'flex', gap: 10, flexWrap: 'wrap', fontSize: '0.83rem', padding: '6px 10px', background: '#f8fafc', borderRadius: 8, alignItems: 'center' }}>
                        <strong style={{ color: '#1e293b' }}>{m.name}</strong>
                        <span style={{ color: '#64748b' }}>{m.dosage}</span>
                        <span style={{ color: '#6366f1', fontWeight: 600 }}>{m.frequency}</span>
                        <span style={{ color: '#0f766e' }}>{m.duration}</span>
                        {m.notes && <span style={{ color: '#94a3b8' }}>({m.notes})</span>}
                      </div>
                    ))}
                  </div>
                  {rx.instructions && (
                    <div style={{ marginTop: 10, padding: '8px 12px', background: '#fefce8', borderRadius: 8, fontSize: '0.82rem', color: '#92400e' }}>
                      📌 {rx.instructions}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
