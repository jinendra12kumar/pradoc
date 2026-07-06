// src/pages/admin/AdminLayout.jsx
import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import '../../admin.css'

const NAV = [
  { section: 'Overview' },
  { key: '/admin/home',         icon: '🏠', label: 'Dashboard' },
  { section: 'Management' },
  { key: '/admin/doctors',      icon: '👨‍⚕️', label: 'Doctors' },
  { key: '/admin/patients',     icon: '🧑‍🤝‍🧑', label: 'Patients' },
  { key: '/admin/appointments', icon: '📅', label: 'Appointments' },
  { key: '/admin/articles',     icon: '📝', label: 'Articles' },
  { key: '/admin/reviews',      icon: '⭐', label: 'Reviews' },
]

const PAGE_TITLES = {
  '/admin/home':         '🏠 Dashboard',
  '/admin/doctors':      '👨‍⚕️ Manage Doctors',
  '/admin/patients':     '🧑‍🤝‍🧑 Manage Patients',
  '/admin/appointments': '📅 Manage Appointments',
  '/admin/articles':     '📝 Manage Articles',
  '/admin/reviews':      '⭐ Manage Reviews',
}

export default function AdminLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()

  const handleLogout = () => { logout(); navigate('/auth/login') }
  const currentPath = location.pathname
  const title = PAGE_TITLES[currentPath] || '🛡️ Admin Panel'

  return (
    <div className="admin-shell">
      {/* Sidebar */}
      <aside className="admin-sidebar">
        <div className="adm-brand">
          <div className="adm-brand-logo">🩺 PraDoc</div>
          <div className="adm-brand-sub">Admin Control Panel</div>
        </div>

        <nav className="adm-nav">
          {NAV.map((item, i) =>
            item.section ? (
              <div key={i} className="adm-nav-section">{item.section}</div>
            ) : (
              <div
                key={item.key}
                className={`adm-nav-item ${currentPath === item.key ? 'active' : ''}`}
                onClick={() => navigate(item.key)}
              >
                <span className="adm-nav-icon">{item.icon}</span>
                {item.label}
              </div>
            )
          )}
        </nav>

        <div className="adm-sidebar-footer">
          <div className="adm-user-chip">
            <div className="adm-avatar">{user?.full_name?.[0] || 'A'}</div>
            <div>
              <div className="adm-user-name">{user?.full_name || 'Admin'}</div>
              <div className="adm-user-role">Administrator</div>
            </div>
          </div>
          <button className="btn-adm-logout" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main Area */}
      <div className="admin-main">
        <div className="admin-topbar">
          <h1>{title}</h1>
          <div className="admin-topbar-actions">
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
            </span>
          </div>
        </div>
        <div className="admin-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
