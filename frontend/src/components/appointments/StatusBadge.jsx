// src/components/appointments/StatusBadge.jsx
export default function StatusBadge({ status }) {
  const map = {
    pending:   { label: 'Pending',   cls: 'badge-pending',   icon: '⏳' },
    confirmed: { label: 'Confirmed', cls: 'badge-confirmed', icon: '✅' },
    completed: { label: 'Completed', cls: 'badge-completed', icon: '🏁' },
    cancelled: { label: 'Cancelled', cls: 'badge-cancelled', icon: '❌' },
    no_show:   { label: 'No Show',   cls: 'badge-no_show',   icon: '👻' },
  }
  const s = map[status] || { label: status, cls: 'badge-pending', icon: '•' }
  return <span className={`badge ${s.cls}`}>{s.icon} {s.label}</span>
}
