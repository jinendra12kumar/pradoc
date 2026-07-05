// src/components/appointments/SlotPicker.jsx
// Two modes: pick_time (grid) | next_available (pre-filtered free slots)
import { useState } from 'react'

const fmtTime = (t) => {
  if (!t) return ''
  const [h, m] = String(t).split(':')
  const hr = parseInt(h)
  return `${hr > 12 ? hr - 12 : hr || 12}:${m} ${hr >= 12 ? 'PM' : 'AM'}`
}

export default function SlotPicker({ slots = [], nextAvailableSlots = [], value, onChange }) {
  const [mode, setMode] = useState('pick_time')
  const displaySlots = mode === 'next_available' ? nextAvailableSlots : slots

  return (
    <div>
      {/* Mode toggle */}
      <div className="slot-mode-toggle">
        <button
          className={`slot-mode-btn ${mode === 'pick_time' ? 'active' : ''}`}
          onClick={() => setMode('pick_time')}
        >
          🕐 Pick a Time
        </button>
        <button
          className={`slot-mode-btn ${mode === 'next_available' ? 'active' : ''}`}
          onClick={() => setMode('next_available')}
        >
          ⚡ Next Available
        </button>
      </div>

      {mode === 'next_available' && nextAvailableSlots.length === 0 && (
        <div className="empty-state">
          <div className="emoji">😔</div>
          <div>No available slots for this date</div>
        </div>
      )}

      {mode === 'pick_time' && slots.length === 0 && (
        <div className="empty-state">
          <div className="emoji">📅</div>
          <div>No schedule found for this day</div>
        </div>
      )}

      {displaySlots.length > 0 && (
        <div className="slots-grid">
          {displaySlots.map((slot) => {
            const key = slot.start_time
            const isSelected = value === key
            const isBooked   = !slot.is_available
            return (
              <div
                key={key}
                className={`slot-chip ${isSelected ? 'selected' : ''} ${isBooked ? 'booked' : ''}`}
                onClick={() => !isBooked && onChange(slot)}
                title={isBooked ? 'Already booked' : slot.slot_label}
              >
                {fmtTime(slot.start_time)}
                {isBooked && <span className="slot-tag">Booked</span>}
                {mode === 'next_available' && !isBooked && (
                  <span className="slot-tag" style={{ color: '#10b981' }}>Free</span>
                )}
              </div>
            )
          })}
        </div>
      )}

      {value && (
        <div style={{ marginTop: 14, padding: '10px 14px', background: '#eef2ff', borderRadius: 10, fontSize: '0.85rem', color: '#4338ca', fontWeight: 600 }}>
          ✅ Selected: {fmtTime(value)}
        </div>
      )}
    </div>
  )
}
