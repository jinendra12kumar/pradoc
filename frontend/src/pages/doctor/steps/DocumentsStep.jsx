import { useRef } from 'react'
import { doctorApi } from '../../../api/doctorApi'

const DOC_CONFIGS = [
  { type: 'MEDICAL_REG_CERT', label: 'Medical Registration Certificate', icon: '📋', required: true },
  { type: 'DEGREE_CERT', label: 'Degree Certificate', icon: '🎓', required: true },
  { type: 'PROFILE_PHOTO', label: 'Profile Photo (Verification)', icon: '📸', required: true },
  { type: 'CLINIC_PROOF', label: 'Clinic Ownership Proof', icon: '🏥', required: false },
  { type: 'GST_CERT', label: 'GST Certificate', icon: '📄', required: false },
  { type: 'RENT_AGREEMENT', label: 'Rent Agreement', icon: '📝', required: false },
  { type: 'UTILITY_BILL', label: 'Utility Bill', icon: '💡', required: false },
]

export default function DocumentsStep({ profile, onBack, onSubmit, onReload, setSaving, setError, saving }) {
  const docs = profile?.documents || []
  const uploadedTypes = new Set(docs.map(d => d.document_type))
  const fileRefs = useRef({})

  const handleUpload = async (docType, e) => {
    const file = e.target.files[0]
    if (!file) return
    setError('')
    setSaving(true)
    try {
      await doctorApi.uploadDocument(docType, file)
      await onReload()
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed.'
      setError(msg)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (docId) => {
    setError('')
    try {
      await doctorApi.deleteDocument(docId)
      await onReload()
    } catch (err) {
      setError('Delete failed.')
    }
  }

  const getDoc = (type) => docs.find(d => d.document_type === type)

  const handleSave = () => {
    setError('')
    const missing = DOC_CONFIGS.filter(cfg => cfg.required && !uploadedTypes.has(cfg.type))
    if (missing.length > 0) {
      setError(`Please upload the following required documents: ${missing.map(m => m.label).join(', ')}`)
      return
    }
    onSubmit()
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Verification Documents</h2>
      <p className="step-card-subtitle">Upload documents to verify your profile</p>

      <div className="doc-grid">
        {DOC_CONFIGS.map(cfg => {
          const uploaded = uploadedTypes.has(cfg.type)
          const doc = getDoc(cfg.type)
          return (
            <div
              key={cfg.type}
              className={`doc-upload-card ${uploaded ? 'uploaded' : ''} ${cfg.required && !uploaded ? 'mandatory' : ''}`}
              onClick={() => !uploaded && fileRefs.current[cfg.type]?.click()}
            >
              {uploaded && (
                <button className="doc-remove-btn" onClick={(e) => {
                  e.stopPropagation()
                  handleDelete(doc.id)
                }}>✕</button>
              )}

              <span className="doc-badge {cfg.required ? 'required' : 'optional'}">
                {cfg.required ? 'Required' : 'Optional'}
              </span>

              <div className="doc-icon">{uploaded ? '✅' : cfg.icon}</div>
              <div className="doc-label">{cfg.label}</div>
              <div className={`doc-status ${uploaded ? 'uploaded' : ''}`}>
                {uploaded ? `${doc.original_filename}` : 'Click to upload'}
              </div>

              <input
                ref={el => fileRefs.current[cfg.type] = el}
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                hidden
                onChange={(e) => handleUpload(cfg.type, e)}
              />
            </div>
          )
        })}
      </div>

      <div className="step-nav" style={{marginTop: 32}}>
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-submit" onClick={handleSave} disabled={saving}>
          {saving ? 'Submitting...' : '🚀 Submit for Verification'}
        </button>
      </div>
    </div>
  )
}
