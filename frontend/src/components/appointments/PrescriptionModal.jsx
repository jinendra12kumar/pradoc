// src/components/appointments/PrescriptionModal.jsx
import { useState } from 'react'
import { createPrescription } from '../../api/appointments'

const emptyMed = () => ({ name: '', dosage: '', frequency: '', duration: '', notes: '' })

export default function PrescriptionModal({ appointment, onClose, onSuccess }) {
  const [diagnosis, setDiagnosis]     = useState('')
  const [medicines, setMedicines]     = useState([emptyMed()])
  const [instructions, setInstructions] = useState('')
  const [followUp, setFollowUp]       = useState('')
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState('')

  const updateMed = (i, field, val) => {
    setMedicines(prev => prev.map((m, idx) => idx === i ? { ...m, [field]: val } : m))
  }
  const addMed    = () => setMedicines(prev => [...prev, emptyMed()])
  const removeMed = (i) => setMedicines(prev => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!diagnosis.trim()) { setError('Diagnosis is required.'); return }
    setLoading(true); setError('')
    try {
      const res = await createPrescription({
        appointment_id: appointment.id,
        diagnosis,
        medicines: medicines.filter(m => m.name.trim()),
        instructions: instructions || null,
        follow_up_date: followUp || null,
      })
      if (res.prescription_id) onSuccess?.()
      else setError(res.detail || 'Failed to create prescription.')
    } catch { setError('Network error.') }
    finally { setLoading(false) }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div className="modal-header">
          <h3>💊 Write Prescription</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: 16 }}>
          Patient: <strong>{appointment.patient?.full_name || 'Patient'}</strong> &nbsp;|&nbsp;
          Date: <strong>{appointment.appointment_date}</strong>
        </div>

        <form onSubmit={handleSubmit}>
          <label style={{ fontWeight: 700, fontSize: '0.85rem', display: 'block', marginBottom: 6 }}>Diagnosis *</label>
          <textarea
            value={diagnosis} onChange={e => setDiagnosis(e.target.value)}
            rows={2} required
            style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.9rem', resize: 'vertical', marginBottom: 16 }}
            placeholder="e.g. Viral fever, Upper respiratory infection"
          />

          <div style={{ fontWeight: 700, fontSize: '0.85rem', marginBottom: 10 }}>Medicines</div>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1.2fr auto', gap: 8, marginBottom: 6, paddingLeft: 4 }}>
            <span>Medicine Name</span><span>Dosage</span><span>Frequency</span><span>Duration</span><span></span>
          </div>
          {medicines.map((med, i) => (
            <div key={i} className="medicine-row">
              <input placeholder="e.g. Paracetamol" value={med.name} onChange={e => updateMed(i, 'name', e.target.value)}
                style={{ padding: '8px 10px', borderRadius: 8, border: '1px solid #e2e8f0', fontSize: '0.83rem' }} />
              <input placeholder="500mg" value={med.dosage} onChange={e => updateMed(i, 'dosage', e.target.value)}
                style={{ padding: '8px 10px', borderRadius: 8, border: '1px solid #e2e8f0', fontSize: '0.83rem' }} />
              <select value={med.frequency} onChange={e => updateMed(i, 'frequency', e.target.value)}
                style={{ padding: '8px 10px', borderRadius: 8, border: '1px solid #e2e8f0', fontSize: '0.83rem' }}>
                <option value="">Freq</option>
                <option>OD</option><option>BD</option><option>TDS</option><option>QID</option><option>SOS</option>
              </select>
              <input placeholder="5 days" value={med.duration} onChange={e => updateMed(i, 'duration', e.target.value)}
                style={{ padding: '8px 10px', borderRadius: 8, border: '1px solid #e2e8f0', fontSize: '0.83rem' }} />
              <button type="button" onClick={() => removeMed(i)}
                style={{ background: '#fee2e2', color: '#ef4444', border: 'none', borderRadius: 8, padding: '8px 10px', cursor: 'pointer', fontWeight: 700 }}>✕</button>
            </div>
          ))}
          <button type="button" onClick={addMed}
            style={{ marginBottom: 16, marginTop: 6, fontSize: '0.8rem', color: '#6366f1', background: '#eef2ff', border: 'none', borderRadius: 8, padding: '7px 14px', cursor: 'pointer', fontWeight: 600 }}>
            + Add Medicine
          </button>

          <label style={{ fontWeight: 700, fontSize: '0.85rem', display: 'block', marginBottom: 6 }}>Instructions</label>
          <textarea value={instructions} onChange={e => setInstructions(e.target.value)} rows={2}
            placeholder="e.g. Take after food, avoid cold drinks..."
            style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.88rem', resize: 'vertical', marginBottom: 14 }} />

          <label style={{ fontWeight: 700, fontSize: '0.85rem', display: 'block', marginBottom: 6 }}>Follow-up Date</label>
          <input type="date" value={followUp} onChange={e => setFollowUp(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            style={{ padding: '9px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.88rem', marginBottom: 16 }} />

          {error && <div style={{ color: '#ef4444', fontSize: '0.82rem', marginBottom: 12 }}>⚠️ {error}</div>}

          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button type="button" className="btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? '⏳ Saving...' : '💊 Save Prescription'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
