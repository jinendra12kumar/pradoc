// src/components/medical/MedicalRecordUploader.jsx
// Drag-and-drop + click to upload medical records
import { useState, useRef } from 'react'

const RECORD_TYPES = [
  { value: 'lab_report',   label: '🧪 Lab Report' },
  { value: 'xray',         label: '📷 X-Ray' },
  { value: 'scan',         label: '🩻 Scan (CT/MRI)' },
  { value: 'prescription', label: '💊 Prescription' },
  { value: 'discharge',    label: '🏥 Discharge Summary' },
  { value: 'other',        label: '📁 Other' },
]

function FileIcon({ ext }) {
  const icons = { pdf: '📄', jpg: '🖼️', jpeg: '🖼️', png: '🖼️' }
  return <span style={{ fontSize: 28 }}>{icons[ext] || '📎'}</span>
}

export default function MedicalRecordUploader({ onSuccess }) {
  const [dragging, setDragging]   = useState(false)
  const [file, setFile]           = useState(null)
  const [title, setTitle]         = useState('')
  const [recordType, setType]     = useState('other')
  const [description, setDesc]    = useState('')
  const [recordDate, setDate]     = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError]         = useState('')
  const [preview, setPreview]     = useState(null)
  const inputRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) selectFile(f)
  }

  const selectFile = (f) => {
    setFile(f)
    setError('')
    if (!title) setTitle(f.name.replace(/\.[^/.]+$/, ''))
    if (f.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = e => setPreview(e.target.result)
      reader.readAsDataURL(f)
    } else {
      setPreview(null)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) { setError('Please select a file.'); return }
    if (!title.trim()) { setError('Please enter a title.'); return }

    const fd = new FormData()
    fd.append('file', file)
    fd.append('title', title)
    fd.append('record_type', recordType)
    fd.append('description', description)
    fd.append('record_date', recordDate)

    setUploading(true); setError('')
    try {
      const res = await fetch('/api/v1/files/medical-records/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        body: fd,
      }).then(r => r.json())

      if (res.record_id) {
        setFile(null); setTitle(''); setDesc(''); setDate(''); setPreview(null); setType('other')
        onSuccess?.(res)
      } else {
        setError(res.detail || 'Upload failed.')
      }
    } catch { setError('Network error.') }
    finally { setUploading(false) }
  }

  const ext = file?.name?.split('.').pop().toLowerCase()
  const sizeMB = file ? (file.size / 1024 / 1024).toFixed(2) : null

  return (
    <form onSubmit={handleUpload}>
      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
        style={{
          border: `2px dashed ${dragging ? '#6366f1' : file ? '#10b981' : '#e2e8f0'}`,
          background: dragging ? '#eef2ff' : file ? '#f0fdf4' : '#f8fafc',
          borderRadius: 14, padding: 32, textAlign: 'center', cursor: 'pointer',
          transition: 'all 0.2s', marginBottom: 16,
        }}>
        <input ref={inputRef} type="file" style={{ display: 'none' }}
          accept=".pdf,.jpg,.jpeg,.png" onChange={e => selectFile(e.target.files[0])} />

        {file ? (
          <div>
            {preview
              ? <img src={preview} alt="preview" style={{ maxHeight: 80, borderRadius: 8, marginBottom: 8 }} />
              : <FileIcon ext={ext} />
            }
            <div style={{ fontWeight: 700, color: '#1e293b', marginTop: 6 }}>{file.name}</div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: 2 }}>
              {sizeMB} MB · {ext?.toUpperCase()}
            </div>
            <button type="button" onClick={e => { e.stopPropagation(); setFile(null); setPreview(null) }}
              style={{ marginTop: 10, fontSize: '0.75rem', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
              ✕ Remove
            </button>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 40, marginBottom: 8 }}>📎</div>
            <div style={{ fontWeight: 700, color: '#1e293b', fontSize: '0.95rem' }}>
              {dragging ? 'Drop your file here' : 'Click or drag file to upload'}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: 4 }}>
              PDF, JPG, PNG — max 5MB
            </div>
          </div>
        )}
      </div>

      {/* Fields */}
      <div style={{ display: 'grid', gap: 12 }}>
        <div>
          <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Title *</label>
          <input value={title} onChange={e => setTitle(e.target.value)} required placeholder="e.g. Blood Test Report July 2026"
            style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.9rem' }} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Record Type</label>
            <select value={recordType} onChange={e => setType(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.88rem' }}>
              {RECORD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Record Date</label>
            <input type="date" value={recordDate} onChange={e => setDate(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.88rem' }} />
          </div>
        </div>

        <div>
          <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>Description (optional)</label>
          <textarea value={description} onChange={e => setDesc(e.target.value)} rows={2}
            placeholder="e.g. CBC test ordered by Dr. Smith"
            style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.88rem', resize: 'vertical' }} />
        </div>
      </div>

      {error && <div style={{ color: '#ef4444', fontSize: '0.82rem', marginTop: 10 }}>⚠️ {error}</div>}

      <button type="submit" disabled={uploading || !file}
        style={{
          marginTop: 16, width: '100%', padding: '12px', borderRadius: 12,
          background: uploading ? '#94a3b8' : 'linear-gradient(135deg,#6366f1,#4338ca)',
          color: '#fff', border: 'none', fontWeight: 800, fontSize: '0.95rem',
          cursor: uploading ? 'not-allowed' : 'pointer',
        }}>
        {uploading ? '⏳ Uploading…' : '📤 Upload Record'}
      </button>
    </form>
  )
}
