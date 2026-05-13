import { useLocation } from 'react-router-dom';
import { FiBell } from 'react-icons/fi';

const pageTitles = {
  '/': 'Dashboard',
  '/patients': 'Quản lý Bệnh nhân',
  '/predictions': 'Dự đoán Tái nhập viện',
  '/predictions/history': 'Lịch sử Dự đoán',
  '/admin/users': 'Quản lý Users',
  '/admin/models': 'Quản lý ML Models',
  '/admin/monitoring': 'Monitoring & Metrics',
};

export default function Header() {
  const location = useLocation();
  
  const getTitle = () => {
    for (const [path, title] of Object.entries(pageTitles)) {
      if (location.pathname === path) return title;
    }
    if (location.pathname.startsWith('/patients/')) return 'Chi tiết Bệnh nhân';
    if (location.pathname.startsWith('/predictions/') && location.pathname !== '/predictions/history') return 'Kết quả Dự đoán';
    return 'MedPredict AI';
  };

  return (
    <header className="header">
      <h2 className="header-title">{getTitle()}</h2>
      <div className="header-actions">
        <button className="btn btn-icon btn-secondary" title="Notifications">
          <FiBell />
        </button>
      </div>
    </header>
  );
}
