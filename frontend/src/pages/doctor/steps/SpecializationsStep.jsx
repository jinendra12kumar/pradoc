import { useState } from 'react'
import { doctorApi } from '../../../api/doctorApi'

export default function SpecializationsStep({ profile, refData, onNext, onBack, onReload, setSaving, setError }) {
  const existing = profile?.specializations || []
  const allSpecs = refData?.specializations || []

  const [primary, setPrimary] = useState(
    existing.find(s => s.is_primary)?.specialization_name || ''
  )
  const [secondary, setSecondary] = useState(
    existing.filter(s => !s.is_primary).map(s => s.specialization_name)
  )

  const toggleSecondary = (name) => {
    if (name === primary) return
    setSecondary(prev =>
      prev.includes(name) ? prev.filter(s => s !== name) : [...prev, name]
    )
  }

  const setPrimarySpec = (name) => {
    setPrimary(name)
    setSecondary(prev => prev.filter(s => s !== name))
  }

  const handleSave = async () => {
    setError('')
    if (!primary) {
      setError('Please select a primary specialization.')
      return
    }
    setSaving(true)
    try {
      const specs = [
        { specialization_name: primary, is_primary: true },
        ...secondary.map(s => ({ specialization_name: s, is_primary: false })),
      ]
      await doctorApi.saveSpecializations({ specializations: specs })
      await onReload()
      onNext()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save specializations.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Specialization</h2>
      <p className="step-card-subtitle">Select your primary and secondary specializations</p>

      <div className="form-group">
        <label className="form-label">Primary Specialization * <span style={{fontSize: 12, color: 'var(--text-light)'}}>(click to set as primary)</span></label>
        <div className="spec-grid">
          {allSpecs.map(s => (
            <button
              key={s}
              type="button"
              className={`spec-chip ${s === primary ? 'primary' : ''}`}
              onClick={() => setPrimarySpec(s)}
            >
              {s === primary && '★ '}{s}
            </button>
          ))}
        </div>
      </div>

      {primary && (
        <div className="form-group" style={{marginTop: 20}}>
          <label className="form-label">Secondary Specializations <span style={{fontSize: 12, color: 'var(--text-light)'}}>(optional, click to toggle)</span></label>
          <div className="spec-grid">
            {allSpecs.filter(s => s !== primary).map(s => (
              <button
                key={s}
                type="button"
                className={`spec-chip ${secondary.includes(s) ? 'selected' : ''}`}
                onClick={() => toggleSecondary(s)}
              >
                {secondary.includes(s) && '✓ '}{s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="step-nav">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-next" onClick={handleSave}>Save & Continue →</button>
      </div>
    </div>
  )
}
