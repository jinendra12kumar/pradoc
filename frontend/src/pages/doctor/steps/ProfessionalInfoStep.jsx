import { useState } from 'react'
import { doctorApi } from '../../../api/doctorApi'

export default function ProfessionalInfoStep({ profile, refData, onNext, onBack, onReload, setSaving, setError }) {
  const p = profile?.professional || {}
  const [form, setForm] = useState({
    medical_registration_number: p.medical_registration_number || '',
    medical_council: p.medical_council || '',
    registration_year: p.registration_year || '',
    years_of_experience: p.years_of_experience ?? '',
    current_hospital: p.current_hospital || '',
  })
  const [prevHospitals, setPrevHospitals] = useState(p.previous_hospitals || [])
  const [hospInput, setHospInput] = useState('')

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const addHosp = () => {
    const h = hospInput.trim()
    if (h && !prevHospitals.includes(h)) setPrevHospitals([...prevHospitals, h])
    setHospInput('')
  }

  const handleSave = async () => {
    setError('')
    if (!form.medical_registration_number || !form.medical_council || !form.registration_year || form.years_of_experience === '') {
      setError('Please fill all required fields.')
      return
    }
    setSaving(true)
    try {
      await doctorApi.saveProfessionalInfo({
        ...form,
        registration_year: parseInt(form.registration_year),
        years_of_experience: parseInt(form.years_of_experience),
        previous_hospitals: prevHospitals.length > 0 ? prevHospitals : null,
      })
      await onReload()
      onNext()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save professional info.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Professional Information</h2>
      <p className="step-card-subtitle">Your medical registration details</p>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Medical Registration Number *</label>
          <input className="form-input" value={form.medical_registration_number}
            onChange={e => update('medical_registration_number', e.target.value)}
            placeholder="e.g. KMC-12345" />
        </div>
        <div className="form-group">
          <label className="form-label">Medical Council *</label>
          <select className="form-select" value={form.medical_council}
            onChange={e => update('medical_council', e.target.value)}>
            <option value="">Select Council</option>
            {(refData?.medical_councils || []).map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Registration Year *</label>
          <input className="form-input" type="number" value={form.registration_year}
            onChange={e => update('registration_year', e.target.value)}
            min="1950" max={new Date().getFullYear()} placeholder="e.g. 2015" />
        </div>
        <div className="form-group">
          <label className="form-label">Years of Experience *</label>
          <input className="form-input" type="number" value={form.years_of_experience}
            onChange={e => update('years_of_experience', e.target.value)}
            min="0" max="70" placeholder="e.g. 10" />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Current Hospital / Organization</label>
        <input className="form-input" value={form.current_hospital}
          onChange={e => update('current_hospital', e.target.value)}
          placeholder="e.g. Apollo Hospitals" />
      </div>

      <div className="form-group">
        <label className="form-label">Previous Hospitals (optional)</label>
        <div className="tags-container">
          {prevHospitals.map(h => (
            <span className="tag" key={h}>
              {h} <button className="tag-remove" onClick={() => setPrevHospitals(prevHospitals.filter(x => x !== h))}>×</button>
            </span>
          ))}
        </div>
        <div className="tag-input-row">
          <input className="form-input" value={hospInput} placeholder="Hospital name"
            onChange={e => setHospInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addHosp())} />
          <button className="tag-add-btn" type="button" onClick={addHosp}>Add</button>
        </div>
      </div>

      <div className="step-nav">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-next" onClick={handleSave}>Save & Continue →</button>
      </div>
    </div>
  )
}
