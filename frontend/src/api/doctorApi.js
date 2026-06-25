import api from './authApi'

// ── Doctor Onboarding API ─────────────────────────────────────────────────────

export const doctorApi = {
  // Reference data
  getReferenceData: () => api.get('/doctor/reference-data'),

  // Full profile
  getProfile: () => api.get('/doctor/profile'),

  // Step 1: Personal info
  savePersonalInfo: (data) => api.put('/doctor/profile/personal', data),

  // Step 2: Professional info
  saveProfessionalInfo: (data) => api.put('/doctor/profile/professional', data),

  // Step 3: Qualifications
  getQualifications: () => api.get('/doctor/profile/qualifications'),
  addQualification: (data) => api.post('/doctor/profile/qualifications', data),
  deleteQualification: (id) => api.delete(`/doctor/profile/qualifications/${id}`),

  // Step 4: Specializations
  saveSpecializations: (data) => api.put('/doctor/profile/specializations', data),

  // Step 5: Clinics
  createClinic: (data) => api.post('/doctor/profile/clinics', data),
  updateClinic: (id, data) => api.put(`/doctor/profile/clinics/${id}`, data),
  deleteClinic: (id) => api.delete(`/doctor/profile/clinics/${id}`),

  // Step 6: Documents
  uploadDocument: (documentType, file) => {
    const formData = new FormData()
    formData.append('document_type', documentType)
    formData.append('file', file)
    return api.post('/doctor/profile/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteDocument: (id) => api.delete(`/doctor/profile/documents/${id}`),

  // Profile photo
  uploadProfilePhoto: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/doctor/profile/photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Verification
  submitForVerification: () => api.post('/doctor/profile/submit'),

  // Dashboard
  getDashboard: () => api.get('/doctor/dashboard'),

  // Public profile
  getPublicProfile: (id) => api.get(`/doctor/public/${id}`),
}

// ── Patient Portal API ────────────────────────────────────────────────────────

export const patientApi = {
  // Homepage data (specializations, featured doctors, top clinics)
  getHomeData: () => api.get('/patient/home'),

  // Search doctors with filters
  searchDoctors: (params) => api.get('/patient/doctors/search', { params }),

  // Doctor detail
  getDoctorDetail: (id) => api.get(`/patient/doctors/${id}`),
}

export default doctorApi

