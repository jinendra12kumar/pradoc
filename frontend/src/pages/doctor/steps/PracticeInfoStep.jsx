import { useState } from 'react'
import { doctorApi } from '../../../api/doctorApi'

const DAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN']
const DAY_LABELS = { MON:'Mon', TUE:'Tue', WED:'Wed', THU:'Thu', FRI:'Fri', SAT:'Sat', SUN:'Sun' }

const emptySlot = (day) => ({ day_of_week: day, start_time: '09:00', end_time: '17:00', is_active: true })

export default function PracticeInfoStep({ profile, refData, onNext, onBack, onReload, setSaving, setError }) {
  const existingClinics = profile?.clinics || []
  const states = refData?.indian_states || []

  const [form, setForm] = useState({
    clinic_name: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    consultation_fee: '',
    online_consultation: false,
    online_consultation_fee: '',
  })
  const [slots, setSlots] = useState([emptySlot('MON'), emptySlot('TUE'), emptySlot('WED'), emptySlot('THU'), emptySlot('FRI')])
  const [showForm, setShowForm] = useState(existingClinics.length === 0)

  const update = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const updateSlot = (i, k, v) => setSlots(prev => prev.map((s, idx) => idx === i ? { ...s, [k]: v } : s))

  const addSlot = () => {
    const usedDays = slots.map(s => s.day_of_week)
    const next = DAYS.find(d => !usedDays.includes(d))
    if (next) setSlots([...slots, emptySlot(next)])
  }

  const removeSlot = (i) => setSlots(slots.filter((_, idx) => idx !== i))

  const deleteClinic = async (id) => {
    try {
      await doctorApi.deleteClinic(id)
      await onReload()
    } catch (e) {
      setError('Failed to remove clinic.')
    }
  }

  const handleSave = async () => {
    setError('')
    if (existingClinics.length === 0 && !showForm) {
      setError('Please add at least one clinic.')
      return
    }
    if (showForm) {
      if (!form.clinic_name || !form.address || !form.city || !form.state || !form.pincode || !form.consultation_fee) {
        setError('Please fill all required clinic fields.')
        return
      }
      setSaving(true)
      try {
        await doctorApi.createClinic({
          ...form,
          consultation_fee: parseFloat(form.consultation_fee),
          online_consultation_fee: form.online_consultation && form.online_consultation_fee
            ? parseFloat(form.online_consultation_fee) : null,
          availability: slots.filter(s => s.is_active).map(s => ({
            day_of_week: s.day_of_week,
            start_time: s.start_time + ':00',
            end_time: s.end_time + ':00',
            is_active: true,
          })),
        })
        await onReload()
        setShowForm(false)
        onNext()
      } catch (e) {
        setError(e.response?.data?.detail || 'Failed to save clinic.')
      } finally {
        setSaving(false)
      }
    } else {
      onNext()
    }
  }

  return (
    <div className="step-card">
      <h2 className="step-card-title">Practice Information</h2>
      <p className="step-card-subtitle">Add your clinic details and availability</p>

      {/* Existing clinics */}
      {existingClinics.length > 0 && (
        <div className="dynamic-cards" style={{marginBottom: 20}}>
          {existingClinics.map(c => (
            <div className="dynamic-card" key={c.id}>
              <div className="dynamic-card-header">
                <span className="dynamic-card-title">{c.clinic_name} — {c.city}</span>
                <button className="dynamic-card-remove" onClick={() => deleteClinic(c.id)}>Remove</button>
              </div>
              <p style={{fontSize: 13, color: 'var(--text-mid)'}}>
                ₹{c.consultation_fee} | {c.address}, {c.state} {c.pincode}
                {c.online_consultation && ` | Online: ₹${c.online_consultation_fee}`}
              </p>
              {c.availability_slots?.length > 0 && (
                <div className="tags-container" style={{marginTop: 8}}>
                  {c.availability_slots.map(s => (
                    <span className="tag" key={s.id}>{DAY_LABELS[s.day_of_week]} {s.start_time?.slice(0,5)}-{s.end_time?.slice(0,5)}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!showForm && (
        <button className="add-card-btn" onClick={() => setShowForm(true)} style={{marginBottom: 20}}>
          + Add {existingClinics.length > 0 ? 'Another' : 'a'} Clinic
        </button>
      )}

      {showForm && (
        <>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Clinic Name *</label>
              <input className="form-input" value={form.clinic_name}
                onChange={e => update('clinic_name', e.target.value)} placeholder="Clinic name" />
            </div>
            <div className="form-group">
              <label className="form-label">Consultation Fee (₹) *</label>
              <input className="form-input" type="number" value={form.consultation_fee}
                onChange={e => update('consultation_fee', e.target.value)} placeholder="e.g. 500" min="0" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Clinic Address *</label>
            <textarea className="form-textarea" value={form.address}
              onChange={e => update('address', e.target.value)} placeholder="Full address"
              style={{minHeight: 60}} />
          </div>

          <div className="form-row three">
            <div className="form-group">
              <label className="form-label">City *</label>
              <input className="form-input" value={form.city}
                onChange={e => update('city', e.target.value)} placeholder="City" />
            </div>
            <div className="form-group">
              <label className="form-label">State *</label>
              <select className="form-select" value={form.state} onChange={e => update('state', e.target.value)}>
                <option value="">Select</option>
                {states.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Pincode *</label>
              <input className="form-input" value={form.pincode}
                onChange={e => update('pincode', e.target.value)} placeholder="6 digits" maxLength={6} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" style={{display: 'flex', alignItems: 'center', gap: 8}}>
                <input type="checkbox" checked={form.online_consultation}
                  onChange={e => update('online_consultation', e.target.checked)}
                  style={{accentColor: 'var(--teal)', width: 16, height: 16}} />
                Online Consultation Available
              </label>
            </div>
            {form.online_consultation && (
              <div className="form-group">
                <label className="form-label">Online Fee (₹)</label>
                <input className="form-input" type="number" value={form.online_consultation_fee}
                  onChange={e => update('online_consultation_fee', e.target.value)} placeholder="e.g. 300" min="0" />
              </div>
            )}
          </div>

          {/* Availability */}
          <div className="form-group" style={{marginTop: 12}}>
            <label className="form-label">Availability Schedule</label>
            <div className="avail-grid">
              {slots.map((s, i) => (
                <div className="avail-row" key={i}>
                  <select className="form-select" value={s.day_of_week}
                    onChange={e => updateSlot(i, 'day_of_week', e.target.value)}
                    style={{padding: '8px 10px', fontSize: 13}}>
                    {DAYS.map(d => <option key={d} value={d}>{DAY_LABELS[d]}</option>)}
                  </select>
                  <input type="time" className="form-input" value={s.start_time}
                    onChange={e => updateSlot(i, 'start_time', e.target.value)} />
                  <input type="time" className="form-input" value={s.end_time}
                    onChange={e => updateSlot(i, 'end_time', e.target.value)} />
                  <button className="avail-remove" onClick={() => removeSlot(i)}>✕</button>
                </div>
              ))}
            </div>
            {slots.length < 7 && (
              <button className="add-card-btn" onClick={addSlot} style={{marginTop: 8, padding: 10, fontSize: 13}}>
                + Add Day
              </button>
            )}
          </div>
        </>
      )}

      <div className="step-nav">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-next" onClick={handleSave}>
          {showForm ? 'Save & Continue →' : 'Continue →'}
        </button>
      </div>
    </div>
  )
}
