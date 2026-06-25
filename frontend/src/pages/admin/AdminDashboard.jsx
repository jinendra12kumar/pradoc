import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/auth/login') }

  return (
    <div className="dashboard-page">
      <div className="dashboard-card">
        <div className="dashboard-icon">🛡️</div>
        <div className="dashboard-role-badge" style={{background:'#fff5f5',color:'#c53030'}}>Admin</div>
        <h1 className="dashboard-title">Admin Dashboard</h1>
        <p className="dashboard-sub">
          Welcome, <strong>{user?.full_name || 'Administrator'}</strong>.<br/>
          Manage users, doctors, appointments & system settings.
        </p>
        <button
          className="btn-primary"
          style={{maxWidth:'200px',margin:'24px auto 0',background:'linear-gradient(135deg,#e53e3e,#c53030)'}}
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </div>
  )
}
