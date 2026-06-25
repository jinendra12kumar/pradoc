import { useState } from 'react'
import { doctorApi } from '../../../api/doctorApi'

const QUAL_TYPES = ['MBBS','BDS','BHMS','BAMS','MD','MS','DM','MCh','DNB','OTHER']

const emptyQual = () => ({
  qualification_type: '',
  college_name: '',
  university_name: '',
  graduation_year: '',
})

export default function QualificationsStep({ profile, onNext, onBack, onReload, setSaving, setError }) {
  const existing = profile?.qualifications || []
  const [newQuals, setNewQuals] = useState(existing.length === 0 ? [emptyQual()] : [])

  const updateNew = (i, k, v) => {
    setNewQuals(prev => prev.map((q, idx) => idx === i ? { ...q, [k]: v } : q))
  }

  const addNew = () => setNewQuals([...newQuals, emptyQual()])

  const removeNew = (i) => setNewQuals(newQuals.filter((_, idx) => idx !== i))

  const deleteExisting = async (id) => {
    try {
      await doctorApi.deleteQualification(id)
      await onReload()
    } catch (e) {
      setError('Failed to remove qualification.')
    }
  }

  const handleSave = async () => {
    setError('')
    // Validate new qualifications
    for (const q of newQuals) {
      if (!q.qualification_type || !q.college_name || !q.university_name || !q.graduation_year) {
        setError('Please fill all fields for each qualification.')
        return
      }
    }
    if (existing.length === 0 && newQuals.length === 0) {
      setError('Please add at least one qualification.')
      return
    }

    setSaving(true)
    try {
      for (const q of newQuals) {
        await doctorApi.addQualification({
          ...q,
          graduation_year: parseInt(q.graduation_year),
        })
      }
      setNewQuals([])
      await onReload()
      onNext()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save qualifications.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Education & Qualifications</h2>
      <p className="step-card-subtitle">Add your medical qualifications</p>

      <div className="dynamic-cards">
        {/* Existing qualifications */}
        {existing.map((q) => (
          <div className="dynamic-card" key={q.id}>
            <div className="dynamic-card-header">
              <span className="dynamic-card-title">
                {q.qualification_type} — {q.college_name}
              </span>
              <button className="dynamic-card-remove" onClick={() => deleteExisting(q.id)}>
                Remove
              </button>
            </div>
            <div className="form-row three">
              <div className="form-group">
                <label className="form-label">Type</label>
                <input className="form-input readonly" value={q.qualification_type} readOnly />
              </div>
              <div className="form-group">
                <label className="form-label">University</label>
                <input className="form-input readonly" value={q.university_name} readOnly />
              </div>
              <div className="form-group">
                <label className="form-label">Year</label>
                <input className="form-input readonly" value={q.graduation_year} readOnly />
              </div>
            </div>
          </div>
        ))}

        {/* New qualifications */}
        {newQuals.map((q, i) => (
          <div className="dynamic-card" key={`new-${i}`}>
            <div className="dynamic-card-header">
              <span className="dynamic-card-title">New Qualification #{i + 1}</span>
              {(newQuals.length > 1 || existing.length > 0) && (
                <button className="dynamic-card-remove" onClick={() => removeNew(i)}>Remove</button>
              )}
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Qualification Type *</label>
                <select className="form-select" value={q.qualification_type}
                  onChange={e => updateNew(i, 'qualification_type', e.target.value)}>
                  <option value="">Select</option>
                  {QUAL_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Graduation Year *</label>
                <input className="form-input" type="number" value={q.graduation_year}
                  onChange={e => updateNew(i, 'graduation_year', e.target.value)}
                  min="1950" max={new Date().getFullYear()} placeholder="e.g. 2015" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Medical College *</label>
                <input className="form-input" value={q.college_name}
                  onChange={e => updateNew(i, 'college_name', e.target.value)}
                  placeholder="e.g. AIIMS Delhi" />
              </div>
              <div className="form-group">
                <label className="form-label">University *</label>
                <input className="form-input" value={q.university_name}
                  onChange={e => updateNew(i, 'university_name', e.target.value)}
                  placeholder="e.g. Delhi University" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="add-card-btn" onClick={addNew}>+ Add Another Qualification</button>

      <div className="step-nav">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-next" onClick={handleSave}>Save & Continue →</button>
      </div>
    </div>
  )
}
