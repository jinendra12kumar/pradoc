// src/pages/patient/BookAppointment.jsx
// 4-step booking wizard: Clinic → Date → Slot → Confirm
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import SlotPicker from '../../components/appointments/SlotPicker'
import { fetchSlots, bookAppointment } from '../../api/appointments'
import '../../appointments.css'

const steps = ['Select Clinic', 'Select Date', 'Select Slot', 'Confirm']

function StepBar({ current }) {
  return (
    <div className="wizard-steps" style={{ gap: 40 }}>
      {steps.map((label, i) => {
        const idx = i + 1
        const cls = idx < current ? 'done' : idx === current ? 'active' : ''
        return (
          <div key={label} className={`wizard-step ${cls}`}>
            <div className="step-circle">{idx < current ? '✓' : idx}</div>
            <div className="step-label">{label}</div>
          </div>
        )
      })}
    </div>
  )
}

export default function BookAppointment() {
  const { doctorId } = useParams()
  const navigate     = useNavigate()

  const [doctorData, setDoctorData]   = useState(null)
  const [step, setStep]               = useState(1)
  const [selectedClinic, setClinic]   = useState(null)
  const [selectedDate, setDate]       = useState('')
  const [slotsData, setSlotsData]     = useState(null)
  const [selectedSlot, setSlot]       = useState(null)
  const [consultType, setConsultType] = useState('in_clinic')
  const [notes, setNotes]             = useState('')
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState('')
  const [success, setSuccess]         = useState(false)

  // Fetch doctor profile
  useEffect(() => {
    fetch(`/api/v1/patient/doctors/${doctorId}`)
      .then(r => r.json())
      .then(setDoctorData)
      .catch(() => setError('Failed to load doctor details.'))
  }, [doctorId])

  // Fetch slots when date + clinic selected
  useEffect(() => {
    if (!selectedClinic || !selectedDate) return
    setLoading(true)
    fetchSlots(selectedClinic.id, doctorId, selectedDate)
      .then(setSlotsData)
      .finally(() => setLoading(false))
  }, [selectedClinic, selectedDate])

  const today = new Date().toISOString().split('T')[0]
  const maxDate = new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0]

  const handleBook = async () => {
    if (!selectedSlot) { setError('Please select a slot.'); return }
    setLoading(true); setError('')
    try {
      const payload = {
        doctor_profile_id: doctorId,
        clinic_id: selectedClinic.id,
        appointment_date: selectedDate,
        slot_start_time: selectedSlot.start_time,
        slot_end_time: selectedSlot.end_time,
        consultation_type: consultType,
        patient_notes: notes || null,
      }
      const res = await bookAppointment(payload)
      if (res.appointment_id) setSuccess(true)
      else setError(res.detail || 'Booking failed.')
    } catch { setError('Network error.') }
    finally { setLoading(false) }
  }

  if (success) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <div style={{ fontSize: 64 }}>🎉</div>
        <h2 style={{ color: '#065f46', marginTop: 12 }}>Appointment Booked!</h2>
        <p style={{ color: '#64748b', marginBottom: 24 }}>
          Your appointment is <strong>pending confirmation</strong> from the doctor.
        </p>
        <button className="btn-primary" onClick={() => navigate('/patient/my-appointments')}>
          View My Appointments
        </button>
      </div>
    )
  }

  return (
    <div style={{ padding: '28px 16px', maxWidth: 800, margin: '0 auto' }}>
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: '#6366f1', fontWeight: 700, cursor: 'pointer', marginBottom: 16, fontSize: '0.9rem' }}>
        ← Back
      </button>
      <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e293b', marginBottom: 24 }}>
        Book Appointment
        {doctorData && <span style={{ fontWeight: 400, fontSize: '1rem', color: '#64748b' }}> with Dr. {doctorData.full_name}</span>}
      </h1>

      <StepBar current={step} />

      {/* ── Step 1: Clinic ── */}
      {step === 1 && (
        <div>
          <h3 className="section-title">🏥 Select Clinic</h3>
          {!doctorData && <p style={{ color: '#94a3b8' }}>Loading clinics…</p>}
          {doctorData?.clinics?.length === 0 && <div className="empty-state"><div className="emoji">🏥</div>No clinics available.</div>}
          <div style={{ display: 'grid', gap: 14 }}>
            {doctorData?.clinics?.map(clinic => {
              const isOnline  = clinic.online_consultation
              const selected  = selectedClinic?.id === clinic.id
              return (
                <div key={clinic.id}
                  onClick={() => setClinic(clinic)}
                  style={{
                    border: `2px solid ${selected ? '#6366f1' : '#e2e8f0'}`,
                    background: selected ? '#eef2ff' : '#fff',
                    borderRadius: 14, padding: '16px 20px', cursor: 'pointer', transition: 'all 0.2s',
                  }}>
                  <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>{clinic.clinic_name}</div>
                  <div style={{ fontSize: '0.82rem', color: '#64748b' }}>{clinic.address}, {clinic.city}</div>
                  <div style={{ display: 'flex', gap: 14, marginTop: 10, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.82rem', color: '#0f766e', fontWeight: 600 }}>₹{clinic.consultation_fee} In-Clinic</span>
                    {isOnline && (
                      <span style={{ fontSize: '0.82rem', color: '#6366f1', fontWeight: 600 }}>
                        💻 Online ₹{clinic.online_consultation_fee || clinic.consultation_fee}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {selectedClinic?.online_consultation && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontWeight: 700, marginBottom: 10, fontSize: '0.9rem' }}>Consultation Type</div>
              <div style={{ display: 'flex', gap: 12 }}>
                {['in_clinic', 'online'].map(t => (
                  <button key={t} onClick={() => setConsultType(t)}
                    className={`slot-mode-btn ${consultType === t ? 'active' : ''}`}
                    style={{ flex: 'none', width: 'auto', padding: '9px 20px' }}>
                    {t === 'online' ? '💻 Video Call' : '🚶 In-Clinic'}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <button className="btn-primary" onClick={() => selectedClinic && setStep(2)} disabled={!selectedClinic}>
              Next →
            </button>
          </div>
        </div>
      )}

      {/* ── Step 2: Date ── */}
      {step === 2 && (
        <div>
          <h3 className="section-title">📅 Select Date</h3>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: 16 }}>Pick an appointment date within the next 30 days.</p>
          <input
            type="date" value={selectedDate} min={today} max={maxDate}
            onChange={e => { setDate(e.target.value); setSlot(null) }}
            style={{ padding: '12px 16px', borderRadius: 12, border: '2px solid #e2e8f0', fontSize: '1rem', width: '100%', maxWidth: 280 }}
          />
          <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
            <button className="btn-outline" onClick={() => setStep(1)}>← Back</button>
            <button className="btn-primary" onClick={() => selectedDate && setStep(3)} disabled={!selectedDate}>Next →</button>
          </div>
        </div>
      )}

      {/* ── Step 3: Slot ── */}
      {step === 3 && (
        <div>
          <h3 className="section-title">🕐 Select Time Slot</h3>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: 16 }}>
            <strong>⚡ Next Available</strong> shows you the first free slots. <strong>🕐 Pick a Time</strong> shows the full day grid.
          </p>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 30, color: '#94a3b8' }}>Loading slots…</div>
          ) : (
            <SlotPicker
              slots={slotsData?.slots || []}
              nextAvailableSlots={slotsData?.next_available_slots || []}
              value={selectedSlot?.start_time}
              onChange={setSlot}
            />
          )}
          <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
            <button className="btn-outline" onClick={() => setStep(2)}>← Back</button>
            <button className="btn-primary" onClick={() => selectedSlot && setStep(4)} disabled={!selectedSlot}>Next →</button>
          </div>
        </div>
      )}

      {/* ── Step 4: Confirm ── */}
      {step === 4 && (
        <div>
          <h3 className="section-title">✅ Confirm Appointment</h3>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: 20, marginBottom: 20 }}>
            <Row label="Doctor"   value={`Dr. ${doctorData?.full_name}`} />
            <Row label="Clinic"   value={`${selectedClinic?.clinic_name}, ${selectedClinic?.city}`} />
            <Row label="Date"     value={selectedDate} />
            <Row label="Time"     value={`${selectedSlot?.slot_label}`} />
            <Row label="Type"     value={consultType === 'online' ? '💻 Online Video' : '🚶 In-Clinic'} />
            <Row label="Fee"      value={`₹${consultType === 'online' ? (selectedClinic?.online_consultation_fee || selectedClinic?.consultation_fee) : selectedClinic?.consultation_fee}`} />
          </div>

          <label style={{ fontWeight: 700, fontSize: '0.88rem', display: 'block', marginBottom: 6 }}>
            Reason for visit (optional)
          </label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3}
            placeholder="Describe your symptoms or reason for visit..."
            style={{ width: '100%', padding: '10px 12px', borderRadius: 12, border: '2px solid #e2e8f0', fontSize: '0.9rem', resize: 'vertical', marginBottom: 20 }} />

          {error && <div style={{ color: '#ef4444', marginBottom: 12 }}>⚠️ {error}</div>}

          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn-outline" onClick={() => setStep(3)}>← Back</button>
            <button className="btn-primary" onClick={handleBook} disabled={loading}>
              {loading ? '⏳ Booking…' : '🗓️ Confirm Booking'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f5f9', fontSize: '0.88rem' }}>
      <span style={{ color: '#64748b' }}>{label}</span>
      <span style={{ fontWeight: 700, color: '#1e293b' }}>{value}</span>
    </div>
  )
}
