import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function PatientDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/auth/login') }

  return (
    <div className="dashboard-page">
      <div className="dashboard-card">
        <div className="dashboard-icon">🧑‍⚕️</div>
        <div className="dashboard-role-badge">Patient</div>
        <h1 className="dashboard-title">Patient Dashboard</h1>
        <p className="dashboard-sub">
          Welcome back, <strong>{user?.full_name || 'Patient'}</strong>!<br/>
          Book appointments, view prescriptions & health records.
        </p>
        <button
          className="btn-primary"
          style={{maxWidth:'200px',margin:'24px auto 0'}}
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </div>
  )
}
