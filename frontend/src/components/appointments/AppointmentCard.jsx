// src/components/appointments/AppointmentCard.jsx
import StatusBadge from './StatusBadge'

const fmtDate = (d) => new Date(d).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
const fmtTime = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hr = parseInt(h)
  return `${hr > 12 ? hr - 12 : hr || 12}:${m} ${hr >= 12 ? 'PM' : 'AM'}`
}

export default function AppointmentCard({ appt, role = 'patient', onConfirm, onComplete, onCancel, onNoShow, onPrescribe, onViewPatient }) {
  const doctorName  = appt.doctor?.full_name  || 'Doctor'
  const patientName = appt.patient?.full_name || 'Patient'
  const clinicName  = appt.clinic?.clinic_name || 'Clinic'
  const photo       = appt.doctor?.profile_photo

  return (
    <div className="appt-card">
      <div className="appt-card-header">
        <div className="appt-doctor-info">
          <div className="appt-avatar">
            {photo ? <img src={photo} alt={doctorName} /> : '👨‍⚕️'}
          </div>
          <div>
            <div className="appt-doctor-name">
              {role === 'patient' ? `Dr. ${doctorName}` : patientName}
            </div>
            <div className="appt-spec">
              {role === 'patient'
                ? (appt.doctor?.primary_specialization || 'General Physician')
                : (appt.patient?.mobile || '')}
            </div>
          </div>
        </div>
        <StatusBadge status={appt.status} />
      </div>

      <div className="appt-meta">
        <div className="appt-meta-item">
          <span>📅</span>
          <span>{fmtDate(appt.appointment_date)}</span>
        </div>
        <div className="appt-meta-item">
          <span>🕐</span>
          <span>{fmtTime(appt.slot_start_time)} – {fmtTime(appt.slot_end_time)}</span>
        </div>
        <div className="appt-meta-item">
          <span>🏥</span>
          <span>{clinicName}</span>
        </div>
        <div className="appt-meta-item">
          <span>{appt.consultation_type === 'online' ? '💻' : '🚶'}</span>
          <span>{appt.consultation_type === 'online' ? 'Online' : 'In-Clinic'}</span>
        </div>
        {appt.fee_charged && (
          <div className="appt-meta-item">
            <span>💰</span>
            <span>₹{appt.fee_charged}</span>
          </div>
        )}
      </div>

      {appt.patient_notes && (
        <div style={{ fontSize: '0.8rem', color: '#64748b', background: '#f8fafc', padding: '8px 12px', borderRadius: '8px' }}>
          📝 {appt.patient_notes}
        </div>
      )}

      {appt.prescription && (
        <div style={{ fontSize: '0.8rem', color: '#065f46', background: '#d1fae5', padding: '6px 12px', borderRadius: '8px' }}>
          💊 Prescription available
        </div>
      )}

      {/* Actions */}
      <div className="appt-actions">
        {role === 'doctor' && appt.status === 'pending' && (
          <button className="btn-success btn-sm" onClick={() => onConfirm?.(appt.id)}>✅ Confirm</button>
        )}
        {role === 'doctor' && appt.status === 'confirmed' && (
          <button className="btn-primary btn-sm" onClick={() => onComplete?.(appt.id)}>🏁 Complete</button>
        )}
        {role === 'doctor' && (appt.status === 'confirmed' || appt.status === 'pending') && (
          <button className="btn-outline btn-sm" onClick={() => onNoShow?.(appt.id)}>👻 No Show</button>
        )}
        {role === 'doctor' && appt.status === 'completed' && !appt.prescription && (
          <button className="btn-primary btn-sm" onClick={() => onPrescribe?.(appt)}>💊 Prescribe</button>
        )}
        {role === 'doctor' && (
          <button className="btn-outline btn-sm" onClick={() => onViewPatient?.(appt.patient_id)}>👤 Patient</button>
        )}
        {role === 'patient' && (appt.status === 'pending' || appt.status === 'confirmed') && (
          <button className="btn-danger btn-sm" onClick={() => onCancel?.(appt.id)}>❌ Cancel</button>
        )}
      </div>
    </div>
  )
}
