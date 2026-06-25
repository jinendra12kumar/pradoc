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
import DoctorDashboard from './pages/doctor/DoctorDashboard'
import DoctorOnboarding from './pages/doctor/DoctorOnboarding'
import AdminDashboard   from './pages/admin/AdminDashboard'

import './patient-portal.css'

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
            <Route path="home" element={<PatientHome />} />
            <Route path="dashboard" element={<Navigate to="/patient/home" replace />} />
            <Route path="doctors" element={<DoctorSearch />} />
            <Route path="doctors/:id" element={<DoctorDetail />} />
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
