// src/pages/admin/AdminDashboard.jsx  — Entry redirect
import { Navigate } from 'react-router-dom'

// /admin/dashboard → redirect into the full admin panel
export default function AdminDashboard() {
  return <Navigate to="/admin/home" replace />
}
