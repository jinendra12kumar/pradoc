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
import AdminDashboard   from './pages/admin/AdminDashboard'

import './patient-portal.css'
import './appointments.css'

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

          {/* Protected — Admin */}
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/auth/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
