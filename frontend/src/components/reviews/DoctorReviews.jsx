// src/components/reviews/DoctorReviews.jsx
// Displays rating summary + review list + submit form
import { useState, useEffect } from 'react'

const BASE = '/api/v1/reviews'
const authHeader = () => ({ Authorization: `Bearer ${localStorage.getItem('access_token')}`, 'Content-Type': 'application/json' })

const StarRating = ({ value, onChange, size = 28 }) => (
  <div style={{ display: 'flex', gap: 4 }}>
    {[1, 2, 3, 4, 5].map(n => (
      <span key={n}
        onClick={() => onChange && onChange(n)}
        style={{ fontSize: size, cursor: onChange ? 'pointer' : 'default', color: n <= value ? '#f59e0b' : '#e2e8f0', transition: 'color 0.15s' }}
      >★</span>
    ))}
  </div>
)

const RatingBar = ({ label, count, total }) => {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
      <span style={{ fontSize: '0.78rem', color: '#64748b', minWidth: 32 }}>{label}★</span>
      <div style={{ flex: 1, height: 8, background: '#f1f5f9', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: '#f59e0b', borderRadius: 4, transition: 'width 0.4s' }} />
      </div>
      <span style={{ fontSize: '0.75rem', color: '#94a3b8', minWidth: 24 }}>{count}</span>
    </div>
  )
}

export default function DoctorReviews({ doctorProfileId, canReview = false }) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [rating, setRating]   = useState(5)
  const [comment, setComment] = useState('')
  const [anon, setAnon]       = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError]     = useState('')
  const [success, setSuccess] = useState(false)

  const load = () => {
    setLoading(true)
    fetch(`${BASE}/doctor/${doctorProfileId}`)
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false))
  }

  useEffect(() => { if (doctorProfileId) load() }, [doctorProfileId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true); setError('')
    const res = await fetch(`${BASE}/`, {
      method: 'POST', headers: authHeader(),
      body: JSON.stringify({ doctor_profile_id: doctorProfileId, rating, comment, is_anonymous: anon }),
    }).then(r => r.json())
    if (res.review_id) { setSuccess(true); setShowForm(false); load() }
    else setError(res.detail || 'Failed to submit review.')
    setSubmitting(false)
  }

  if (loading) return <div style={{ color: '#94a3b8', padding: 16 }}>Loading reviews…</div>

  const avg = data?.average_rating || 0
  const total = data?.total_reviews || 0
  const breakdown = data?.rating_breakdown || {}

  return (
    <div>
      {/* Summary */}
      <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap' }}>
        {/* Big number */}
        <div style={{ textAlign: 'center', minWidth: 90 }}>
          <div style={{ fontSize: '3rem', fontWeight: 900, color: '#1e293b', lineHeight: 1 }}>{avg.toFixed(1)}</div>
          <StarRating value={Math.round(avg)} size={18} />
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 4 }}>{total} review{total !== 1 ? 's' : ''}</div>
        </div>
        {/* Bars */}
        <div style={{ flex: 1, minWidth: 200 }}>
          {[5, 4, 3, 2, 1].map(n => (
            <RatingBar key={n} label={n} count={breakdown[n] || 0} total={total} />
          ))}
        </div>
      </div>

      {/* Review CTA */}
      {canReview && !success && (
        <div style={{ marginBottom: 20 }}>
          {!showForm ? (
            <button
              onClick={() => setShowForm(true)}
              style={{ padding: '10px 20px', background: '#eef2ff', color: '#4338ca', border: '2px solid #c7d2fe', borderRadius: 10, fontWeight: 700, cursor: 'pointer', fontSize: '0.88rem' }}>
              ✍️ Write a Review
            </button>
          ) : (
            <form onSubmit={handleSubmit}
              style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 14, padding: 20 }}>
              <div style={{ fontWeight: 700, marginBottom: 14 }}>Rate Dr.</div>
              <StarRating value={rating} onChange={setRating} size={34} />
              <textarea
                value={comment} onChange={e => setComment(e.target.value)} rows={3}
                placeholder="Share your experience (optional)…"
                style={{ width: '100%', marginTop: 14, padding: '10px 12px', borderRadius: 10, border: '2px solid #e2e8f0', fontSize: '0.9rem', resize: 'vertical' }}
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10, fontSize: '0.84rem', color: '#64748b', cursor: 'pointer' }}>
                <input type="checkbox" checked={anon} onChange={e => setAnon(e.target.checked)} />
                Post anonymously
              </label>
              {error && <div style={{ color: '#ef4444', fontSize: '0.82rem', marginTop: 8 }}>⚠️ {error}</div>}
              <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                <button type="button" onClick={() => setShowForm(false)}
                  style={{ padding: '9px 18px', borderRadius: 9, border: '2px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                  Cancel
                </button>
                <button type="submit" disabled={submitting}
                  style={{ padding: '9px 18px', borderRadius: 9, background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 700, fontSize: '0.85rem' }}>
                  {submitting ? '⏳ Posting…' : '⭐ Submit Review'}
                </button>
              </div>
            </form>
          )}
        </div>
      )}
      {success && <div style={{ color: '#065f46', background: '#d1fae5', padding: '10px 14px', borderRadius: 10, marginBottom: 16, fontWeight: 600 }}>✅ Review submitted!</div>}

      {/* Review list */}
      {!data?.reviews?.length ? (
        <div style={{ textAlign: 'center', color: '#94a3b8', padding: '20px 0', fontSize: '0.88rem' }}>
          No reviews yet. Be the first to review!
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 14 }}>
          {data.reviews.map((r) => (
            <div key={r.id} style={{ background: '#fff', border: '1px solid #f1f5f9', borderRadius: 12, padding: '14px 18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#1e293b' }}>
                    {r.is_anonymous ? '👤 Anonymous' : (r.patient_name || 'Patient')}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: 2 }}>
                    {new Date(r.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </div>
                </div>
                <StarRating value={r.rating} size={16} />
              </div>
              {r.comment && <p style={{ margin: 0, fontSize: '0.85rem', color: '#475569', lineHeight: 1.5 }}>{r.comment}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
