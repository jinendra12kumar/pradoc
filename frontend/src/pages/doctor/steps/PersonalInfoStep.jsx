import { useState, useRef } from 'react'
import { doctorApi } from '../../../api/doctorApi'

const COMMON_LANGUAGES = [
  'English',
  'Hindi',
  'Kannada',
  'Telugu',
  'Tamil',
  'Malayalam',
  'Marathi',
  'Bengali',
  'Gujarati',
  'Punjabi',
  'Odia',
  'Urdu',
  'Sanskrit',
  'Spanish',
  'French',
  'German',
  'Assamese',
  'Maithili',
  'Santali',
  'Kashmiri',
  'Nepali',
  'Sindhi',
  'Konkani',
  'Dogri',
  'Manipuri'
]

export default function PersonalInfoStep({ profile, onNext, onReload, setSaving, setError }) {
  const p = profile?.personal || {}
  const [form, setForm] = useState({
    full_name: p.full_name || '',
    gender: p.gender || '',
    date_of_birth: p.date_of_birth || '',
    bio: p.bio || '',
  })
  const [languages, setLanguages] = useState(p.languages_spoken || [])
  const [langInput, setLangInput] = useState('')
  const [photoPreview, setPhotoPreview] = useState(
    p.profile_photo ? `/uploads/${p.profile_photo}` : null
  )
  const fileRef = useRef()

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const addLang = () => {
    const l = langInput.trim()
    if (l && !languages.includes(l)) setLanguages([...languages, l])
    setLangInput('')
  }

  const removeLang = (l) => setLanguages(languages.filter(x => x !== l))

  const handlePhoto = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setPhotoPreview(URL.createObjectURL(file))
    try {
      await doctorApi.uploadProfilePhoto(file)
      await onReload()
    } catch (err) {
      setError('Photo upload failed.')
    }
  }

  const handleSave = async () => {
    setError('')
    if (!form.full_name || !form.gender || !form.date_of_birth) {
      setError('Please fill all required fields.')
      return
    }
    if (languages.length === 0) {
      setError('Please add at least one language.')
      return
    }
    setSaving(true)
    try {
      await doctorApi.savePersonalInfo({
        ...form,
        languages_spoken: languages,
      })
      await onReload()
      onNext()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save personal info.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Personal Information</h2>
      <p className="step-card-subtitle">Tell us about yourself</p>

      <div className="photo-upload-area">
        <div className={`photo-preview ${photoPreview ? 'has-photo' : ''}`}>
          {photoPreview
            ? <img src={photoPreview} alt="Profile" />
            : <span className="photo-preview-placeholder">👤</span>}
        </div>
        <div>
          <button className="photo-upload-btn" onClick={() => fileRef.current?.click()}>
            Upload Photo
          </button>
          <input ref={fileRef} type="file" accept="image/*" hidden onChange={handlePhoto} />
          <p style={{fontSize: 12, color: 'var(--text-light)', marginTop: 6}}>JPG, PNG (max 5MB)</p>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Full Name *</label>
          <input className="form-input" value={form.full_name}
            onChange={e => update('full_name', e.target.value)} placeholder="Dr. Full Name" />
        </div>
        <div className="form-group">
          <label className="form-label">Gender *</label>
          <select className="form-select" value={form.gender} onChange={e => update('gender', e.target.value)}>
            <option value="">Select Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Date of Birth *</label>
          <input className="form-input" type="date" value={form.date_of_birth}
            onChange={e => update('date_of_birth', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Email</label>
          <input className="form-input readonly" value={p.email || ''} readOnly />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Mobile</label>
          <input className="form-input readonly" value={p.mobile || ''} readOnly />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Languages Spoken *</label>
        <div className="tags-container">
          {languages.map(l => (
            <span className="tag" key={l}>
              {l} <button className="tag-remove" onClick={() => removeLang(l)}>×</button>
            </span>
          ))}
        </div>
        <div className="tag-input-row">
          <input className="form-input" value={langInput} placeholder="e.g. English"
            list="languages-list"
            onChange={e => setLangInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addLang())} />
          <datalist id="languages-list">
            {COMMON_LANGUAGES.filter(lang => !languages.includes(lang)).map(lang => (
              <option key={lang} value={lang} />
            ))}
          </datalist>
          <button className="tag-add-btn" type="button" onClick={addLang}>Add</button>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Professional Bio</label>
        <textarea className="form-textarea" value={form.bio} placeholder="Brief professional summary..."
          onChange={e => update('bio', e.target.value)} maxLength={2000} />
      </div>

      <div className="step-nav">
        <div />
        <button className="btn-next" onClick={handleSave}>Save & Continue →</button>
      </div>
    </div>
  )
}
