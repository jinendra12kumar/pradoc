// src/api/admin.js — Admin Panel API helpers

const BASE = '/api/v1/admin'

const authHeader = () => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json',
})

// ── Stats ─────────────────────────────────────────────────────────────────────
export const fetchAdminStats = () =>
  fetch(`${BASE}/stats`, { headers: authHeader() }).then(r => r.json())

// ── Doctors ───────────────────────────────────────────────────────────────────
export const fetchAdminDoctors = (page = 1, search = '') => {
  const params = new URLSearchParams({ page, page_size: 20 })
  if (search) params.append('search', search)
  return fetch(`${BASE}/doctors?${params}`, { headers: authHeader() }).then(r => r.json())
}

export const verifyDoctor = (doctorProfileId, status, reason = '') => {
  const params = new URLSearchParams({ status })
  if (reason) params.append('reason', reason)
  return fetch(`${BASE}/doctors/${doctorProfileId}/verify?${params}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())
}

export const toggleDoctorActive = (doctorProfileId, isActive) =>
  fetch(`${BASE}/doctors/${doctorProfileId}/toggle-active?is_active=${isActive}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

// ── Patients ──────────────────────────────────────────────────────────────────
export const fetchAdminPatients = (page = 1, search = '') => {
  const params = new URLSearchParams({ page, page_size: 20 })
  if (search) params.append('search', search)
  return fetch(`${BASE}/patients?${params}`, { headers: authHeader() }).then(r => r.json())
}

export const togglePatientActive = (userId, isActive) =>
  fetch(`${BASE}/patients/${userId}/toggle-active?is_active=${isActive}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

// ── Appointments ──────────────────────────────────────────────────────────────
export const fetchAdminAppointments = (page = 1, status = '', dateFilter = '') => {
  const params = new URLSearchParams({ page, page_size: 20 })
  if (status) params.append('status', status)
  if (dateFilter) params.append('date_filter', dateFilter)
  return fetch(`${BASE}/appointments?${params}`, { headers: authHeader() }).then(r => r.json())
}

export const updateAppointmentStatus = (appointmentId, status) =>
  fetch(`${BASE}/appointments/${appointmentId}/status?status=${status}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

// ── Reviews ───────────────────────────────────────────────────────────────────
export const fetchAdminReviews = (page = 1) =>
  fetch(`${BASE}/reviews?page=${page}`, { headers: authHeader() }).then(r => r.json())

export const adminDeleteReview = (reviewId) =>
  fetch(`${BASE}/reviews/${reviewId}`, {
    method: 'DELETE', headers: authHeader(),
  }).then(r => r.json())

export const adminUpdateReviewStatus = (reviewId, status) =>
  fetch(`${BASE}/reviews/${reviewId}/status?status=${status}`, {
    method: 'PUT', headers: authHeader(),
  }).then(r => r.json())

// ── Articles ──────────────────────────────────────────────────────────────────
export const fetchAdminArticles = (page = 1) =>
  fetch(`${BASE}/articles?page=${page}`, { headers: authHeader() }).then(r => r.json())

export const fetchArticleById = (id) =>
  fetch(`${BASE}/articles/${id}`, { headers: authHeader() }).then(r => r.json())

export const createArticle = (payload) =>
  fetch(`${BASE}/articles`, {
    method: 'POST', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const updateArticle = (id, payload) =>
  fetch(`${BASE}/articles/${id}`, {
    method: 'PUT', headers: authHeader(), body: JSON.stringify(payload),
  }).then(r => r.json())

export const deleteArticle = (id) =>
  fetch(`${BASE}/articles/${id}`, {
    method: 'DELETE', headers: authHeader(),
  }).then(r => r.json())
