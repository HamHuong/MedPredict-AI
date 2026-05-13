import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  FiGrid, FiUsers, FiActivity, FiClock, 
  FiSettings, FiCpu, FiBarChart2, FiLogOut,
  FiShield
} from 'react-icons/fi';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { section: 'Main', items: [
      { path: '/', icon: <FiGrid />, label: 'Dashboard' },
      { path: '/patients', icon: <FiUsers />, label: 'Bệnh nhân' },
      { path: '/predictions', icon: <FiActivity />, label: 'Dự đoán' },
      { path: '/predictions/history', icon: <FiClock />, label: 'Lịch sử dự đoán' },
    ]},
    ...(user?.role === 'admin' ? [{ section: 'Admin', items: [
      { path: '/admin/users', icon: <FiShield />, label: 'Quản lý Users' },
      { path: '/admin/models', icon: <FiCpu />, label: 'Quản lý Models' },
      { path: '/admin/monitoring', icon: <FiBarChart2 />, label: 'Monitoring' },
    ]}] : []),
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🏥</div>
        <div>
          <h1>MedPredict AI</h1>
          <div className="logo-subtitle">Clinical Prediction</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((section) => (
          <div key={section.section} className="nav-section">
            <div className="nav-section-title">{section.section}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile" onClick={logout}>
          <div className="user-avatar">
            {user?.full_name?.[0] || user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.full_name || user?.username}</div>
            <div className="user-role">{user?.role}</div>
          </div>
          <FiLogOut style={{ color: 'var(--text-muted)' }} />
        </div>
      </div>
    </aside>
  );
}
