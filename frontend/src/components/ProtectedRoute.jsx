import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const ROLE_ROUTES = {
  patient: '/patient/home',
  doctor: '/doctor/dashboard',
  admin: '/admin/dashboard',
}

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to correct dashboard
    const correct = ROLE_ROUTES[role] || '/auth/login'
    return <Navigate to={correct} replace />
  }

  return children
}
