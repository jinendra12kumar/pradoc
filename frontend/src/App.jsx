import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import PatientLayout from './components/PatientLayout'

import LoginPage       from './pages/auth/LoginPage'
import RegisterPage    from './pages/auth/RegisterPage'
import OTPVerifyPage   from './pages/auth/OTPVerifyPage'
import PatientHome     from './pages/patient/PatientHome'
import DoctorSearch    from './pages/patient/DoctorSearch'
import DoctorDetail    from './pages/patient/DoctorDetail'
import BookAppointment from './pages/patient/BookAppointment'
import PatientDashboard from './pages/patient/PatientDashboard'
import MyAppointments  from './pages/patient/MyAppointments'
import PatientProfile  from './pages/patient/PatientProfile'
import DoctorDashboard from './pages/doctor/DoctorDashboard'
import DoctorOnboarding from './pages/doctor/DoctorOnboarding'

// Video Consultation
import VideoConsultation from './pages/consultation/VideoConsultation'

// Admin Panel
import AdminLayout        from './pages/admin/AdminLayout'
import AdminHome          from './pages/admin/AdminHome'
import ManageDoctors      from './pages/admin/ManageDoctors'
import ManagePatients     from './pages/admin/ManagePatients'
import ManageAppointments from './pages/admin/ManageAppointments'
import ManageArticles     from './pages/admin/ManageArticles'
import ManageReviews      from './pages/admin/ManageReviews'

import './patient-portal.css'
import './appointments.css'
import './admin.css'
import './consultation.css'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/"                  element={<Navigate to="/auth/login" replace />} />
          <Route path="/auth/login"        element={<LoginPage />} />
          <Route path="/auth/register"     element={<RegisterPage />} />
          <Route path="/auth/verify-otp"   element={<OTPVerifyPage />} />

          {/* Protected — Patient (with shared layout) */}
          <Route
            path="/patient"
            element={
              <ProtectedRoute allowedRoles={['patient']}>
                <PatientLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/patient/home" replace />} />
            <Route path="home"            element={<PatientHome />} />
            <Route path="dashboard"       element={<PatientDashboard />} />
            <Route path="my-appointments" element={<MyAppointments />} />
            <Route path="profile"         element={<PatientProfile />} />
            <Route path="doctors"         element={<DoctorSearch />} />
            <Route path="doctors/:id"     element={<DoctorDetail />} />
            <Route path="book/:doctorId"  element={<BookAppointment />} />
          </Route>

          {/* Video Consultation (patient OR doctor) */}
          <Route
            path="/consultation/:appointmentId"
            element={
              <ProtectedRoute allowedRoles={['patient', 'doctor']}>
                <VideoConsultation />
              </ProtectedRoute>
            }
          />

          {/* Protected — Doctor */}
          <Route
            path="/doctor/dashboard"
            element={
              <ProtectedRoute allowedRoles={['doctor']}>
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/doctor/onboarding"
            element={
              <ProtectedRoute allowedRoles={['doctor']}>
                <DoctorOnboarding />
              </ProtectedRoute>
            }
          />

          {/* Protected — Admin (nested routes via AdminLayout) */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index                    element={<Navigate to="/admin/home" replace />} />
            <Route path="home"              element={<AdminHome />} />
            <Route path="doctors"           element={<ManageDoctors />} />
            <Route path="patients"          element={<ManagePatients />} />
            <Route path="appointments"      element={<ManageAppointments />} />
            <Route path="articles"          element={<ManageArticles />} />
            <Route path="reviews"           element={<ManageReviews />} />
            {/* Legacy redirect */}
            <Route path="dashboard"         element={<Navigate to="/admin/home" replace />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/auth/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
