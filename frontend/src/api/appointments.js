// src/api/appointments.js — All appointment-related API calls

const BASE = '/api/v1/appointments'
const REVIEW_BASE = '/api/v1/reviews'
const FILES_BASE  = '/api/v1/files'

const authHeader = () => {
  const token = localStorage.getItem('access_token')
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}
const authHeaderNoContentType = () => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
})

// ── Slots ─────────────────────────────────────────────────────────────────────
export const fetchSlots = (clinicId, doctorProfileId, date) =>
  fetch(`${BASE}/slots?clinic_id=${clinicId}&doctor_profile_id=${doctorProfileId}&date=${date}`, {
    headers: authHeader(),
  }).then(r => r.json())

// ── Booking ───────────────────────────────────────────────────────────────────
export const bookAppointment = (payload) =>
  fetch(`${BASE}/book`, {
    method: 'POST', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

// ── Patient appointments ───────────────────────────────────────────────────────
export const fetchMyAppointments = (status = '', page = 1) => {
  const params = new URLSearchParams({ page, page_size: 10 })
  if (status) params.append('status', status)
  return fetch(`${BASE}/my?${params}`, { headers: authHeader() }).then(r => r.json())
}

export const fetchPatientDashboard = () =>
  fetch(`${BASE}/dashboard/patient`, { headers: authHeader() }).then(r => r.json())

export const cancelAppointment = (id, reason = '') =>
  fetch(`${BASE}/${id}/cancel?reason=${encodeURIComponent(reason)}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

// ── Doctor endpoints ──────────────────────────────────────────────────────────
export const fetchDoctorDashboard = () =>
  fetch(`${BASE}/dashboard/doctor`, { headers: authHeader() }).then(r => r.json())

export const fetchDoctorAppointments = (dateFilter = '', status = '', page = 1) => {
  const params = new URLSearchParams({ page, page_size: 10 })
  if (dateFilter) params.append('date_filter', dateFilter)
  if (status) params.append('status', status)
  return fetch(`${BASE}/doctor/list?${params}`, { headers: authHeader() }).then(r => r.json())
}

export const confirmAppointment  = (id) =>
  fetch(`${BASE}/${id}/confirm`,  { method: 'PUT', headers: authHeader() }).then(r => r.json())

export const completeAppointment = (id) =>
  fetch(`${BASE}/${id}/complete`, { method: 'PUT', headers: authHeader() }).then(r => r.json())

export const markNoShow = (id) =>
  fetch(`${BASE}/${id}/no-show`,  { method: 'PUT', headers: authHeader() }).then(r => r.json())

export const createPrescription = (payload) =>
  fetch(`${BASE}/prescription`, {
    method: 'POST', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const fetchPatientHistory = (patientProfileId) =>
  fetch(`${BASE}/patients/${patientProfileId}/history`, { headers: authHeader() }).then(r => r.json())

// ── Notifications ─────────────────────────────────────────────────────────────
export const fetchNotifications = (unreadOnly = false) =>
  fetch(`${BASE}/notifications?unread_only=${unreadOnly}`, { headers: authHeader() }).then(r => r.json())

export const markNotificationRead = (id) =>
  fetch(`${BASE}/notifications/${id}/read`, { method: 'PUT', headers: authHeader() }).then(r => r.json())

// ── Patient Profile & Records ─────────────────────────────────────────────────
export const fetchPatientProfile = () =>
  fetch(`${BASE}/profile/me`, { headers: authHeader() }).then(r => r.json())

export const updatePatientProfile = (payload) =>
  fetch(`${BASE}/profile/me`, {
    method: 'PUT', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const fetchMedicalRecords = () =>
  fetch(`${BASE}/medical-records`, { headers: authHeader() }).then(r => r.json())

export const addMedicalRecord = (payload) =>
  fetch(`${BASE}/medical-records`, {
    method: 'POST', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const fetchMyPrescriptions = () =>
  fetch(`${BASE}/prescriptions/my`, { headers: authHeader() }).then(r => r.json())

// ── Reviews ───────────────────────────────────────────────────────────────────
export const fetchDoctorReviews = (doctorProfileId) =>
  fetch(`${REVIEW_BASE}/doctor/${doctorProfileId}`).then(r => r.json())

export const submitReview = (payload) =>
  fetch(`${REVIEW_BASE}/`, {
    method: 'POST', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const updateReview = (reviewId, rating, comment) =>
  fetch(`${REVIEW_BASE}/${reviewId}?rating=${rating}&comment=${encodeURIComponent(comment || '')}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

export const deleteReview = (reviewId) =>
  fetch(`${REVIEW_BASE}/${reviewId}`, {
    method: 'DELETE', headers: authHeader(),
  }).then(r => r.json())

export const fetchMyReviews = () =>
  fetch(`${REVIEW_BASE}/my`, { headers: authHeader() }).then(r => r.json())

// ── Prescription PDF Download ─────────────────────────────────────────────────
export const downloadPrescriptionPDF = async (prescriptionId) => {
  const res = await fetch(`${FILES_BASE}/prescription/${prescriptionId}/download`, {
    headers: authHeaderNoContentType(),
  })
  if (!res.ok) throw new Error('Download failed')
  const cd  = res.headers.get('content-disposition') || ''
  const fn  = cd.match(/filename="(.+)"/)?.[1] || `prescription_${prescriptionId.slice(0,8)}.pdf`
  const blob = await res.blob()
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = fn; a.click()
  URL.revokeObjectURL(url)
}

// ── Medical Record File Upload ────────────────────────────────────────────────
export const uploadMedicalRecord = (formData) =>
  fetch(`${FILES_BASE}/medical-records/upload`, {
    method: 'POST', headers: authHeaderNoContentType(), body: formData,
  }).then(r => r.json())

export const viewMedicalRecordFile = (recordId) => {
  const token = localStorage.getItem('access_token')
  window.open(`${FILES_BASE}/medical-records/${recordId}/view?token=${token}`, '_blank')
}

