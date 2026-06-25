import { useState } from 'react'
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function PatientLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [search, setSearch] = useState('')

  const handleLogout = () => { logout(); navigate('/auth/login') }

  const handleSearch = (e) => {
    e.preventDefault()
    if (search.trim()) {
      navigate(`/patient/doctors?q=${encodeURIComponent(search.trim())}`)
    }
  }

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link'

  return (
    <div className="patient-layout">
      <nav className="patient-nav">
        <Link to="/patient/home" className="nav-logo">
          Pra<span>Doc</span>
        </Link>
        <div className="nav-links">
          <Link to="/patient/home" className={isActive('/patient/home')}>Home</Link>
          <Link to="/patient/doctors" className={isActive('/patient/doctors')}>Find Doctors</Link>
        </div>
        <form className="nav-search" onSubmit={handleSearch}>
          <span className="nav-search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search doctors, specializations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>
        <div className="nav-user">
          <span className="nav-user-name">{user?.full_name || 'Patient'}</span>
          <button className="nav-logout" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
