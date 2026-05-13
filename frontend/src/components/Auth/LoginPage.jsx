import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { FiUser, FiLock } from 'react-icons/fi';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">🏥</div>
          <h2>MedPredict AI</h2>
          <p>Hệ thống Dự đoán Tái nhập viện</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              <FiUser style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Tên đăng nhập
            </label>
            <input
              id="login-username"
              className="form-input"
              type="text"
              placeholder="Nhập username..."
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label className="form-label">
              <FiLock style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Mật khẩu
            </label>
            <input
              id="login-password"
              className="form-input"
              type="password"
              placeholder="Nhập mật khẩu..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button 
            id="login-submit"
            className="btn btn-primary" 
            type="submit" 
            disabled={loading}
          >
            {loading ? (
              <><span className="spinner" style={{ width: 16, height: 16 }}></span> Đang đăng nhập...</>
            ) : (
              'Đăng nhập'
            )}
          </button>
        </form>

        <div style={{ marginTop: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 12 }}>
          <p>Demo: admin/admin123 hoặc doctor/doctor123</p>
        </div>
      </div>
    </div>
  );
}
