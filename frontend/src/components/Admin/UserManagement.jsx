import { useState, useEffect } from 'react';
import client from '../../api/client';
import { FiPlus, FiEdit2, FiTrash2, FiShield, FiUser } from 'react-icons/fi';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ username: '', password: '', full_name: '', role: 'doctor' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      const res = await client.get('/users');
      setUsers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        const updateData = { full_name: form.full_name, role: form.role };
        if (form.password) updateData.password = form.password;
        await client.put(`/users/${editing}`, updateData);
      } else {
        await client.post('/users', form);
      }
      setShowForm(false);
      setEditing(null);
      setForm({ username: '', password: '', full_name: '', role: 'doctor' });
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Thao tác thất bại');
    }
  };

  const handleDelete = async (userId) => {
    if (!confirm('Xác nhận vô hiệu hóa tài khoản?')) return;
    try {
      await client.delete(`/users/${userId}`);
      fetchUsers();
    } catch (err) {
      console.error(err);
    }
  };

  const startEdit = (user) => {
    setEditing(user.user_id);
    setForm({ username: user.username, password: '', full_name: user.full_name || '', role: user.role });
    setShowForm(true);
  };

  if (loading) return <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h3 style={{ fontSize: 18, fontWeight: 600 }}>Quản lý Tài khoản</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>{users.length} tài khoản</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ username: '', password: '', full_name: '', role: 'doctor' }); }}>
          <FiPlus /> Thêm User
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: 20, animation: 'scaleIn 0.2s ease' }}>
          <div className="card-title" style={{ marginBottom: 16 }}>{editing ? 'Cập nhật User' : 'Tạo User mới'}</div>
          {error && <div className="login-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Username</label>
                <input className="form-input" value={form.username} disabled={!!editing}
                  onChange={(e) => setForm({...form, username: e.target.value})} required={!editing} />
              </div>
              <div className="form-group">
                <label className="form-label">{editing ? 'Mật khẩu mới (để trống = giữ nguyên)' : 'Mật khẩu'}</label>
                <input className="form-input" type="password" value={form.password}
                  onChange={(e) => setForm({...form, password: e.target.value})} required={!editing} />
              </div>
              <div className="form-group">
                <label className="form-label">Họ tên</label>
                <input className="form-input" value={form.full_name}
                  onChange={(e) => setForm({...form, full_name: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="form-label">Vai trò</label>
                <select className="form-select" value={form.role}
                  onChange={(e) => setForm({...form, role: e.target.value})}>
                  <option value="doctor">Doctor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" type="submit">{editing ? 'Cập nhật' : 'Tạo'}</button>
              <button className="btn btn-secondary" type="button" onClick={() => { setShowForm(false); setEditing(null); }}>Hủy</button>
            </div>
          </form>
        </div>
      )}

      {/* User List */}
      <div className="card">
        <table className="data-table">
          <thead>
            <tr><th>ID</th><th>Username</th><th>Họ tên</th><th>Vai trò</th><th>Trạng thái</th><th>Ngày tạo</th><th>Thao tác</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.user_id}>
                <td>{u.user_id}</td>
                <td style={{ fontWeight: 600 }}>{u.username}</td>
                <td>{u.full_name || '—'}</td>
                <td>
                  <span className={`badge ${u.role === 'admin' ? 'badge-high' : 'badge-info'}`}>
                    {u.role === 'admin' ? <><FiShield /> Admin</> : <><FiUser /> Doctor</>}
                  </span>
                </td>
                <td><span className={`badge ${u.is_active ? 'badge-low' : 'badge-high'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                <td style={{ fontSize: 13 }}>{u.created_at ? new Date(u.created_at).toLocaleDateString('vi-VN') : '—'}</td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-sm btn-secondary btn-icon" onClick={() => startEdit(u)} title="Sửa"><FiEdit2 /></button>
                    <button className="btn btn-sm btn-danger btn-icon" onClick={() => handleDelete(u.user_id)} title="Vô hiệu hóa"><FiTrash2 /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
