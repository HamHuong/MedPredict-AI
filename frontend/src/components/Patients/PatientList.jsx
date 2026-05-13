import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { FiSearch, FiChevronLeft, FiChevronRight } from 'react-icons/fi';

export default function PatientList() {
  const [patients, setPatients] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [gender, setGender] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const perPage = 20;

  useEffect(() => { fetchPatients(); }, [page, gender]);

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const params = { page, per_page: perPage };
      if (search) params.search = search;
      if (gender) params.gender = gender;
      const res = await client.get('/patients', { params });
      setPatients(res.data.patients);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Failed to load patients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchPatients();
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      {/* Search Bar */}
      <div className="search-bar">
        <form onSubmit={handleSearch} className="search-input-wrapper">
          <FiSearch className="search-icon" />
          <input
            id="patient-search"
            className="form-input"
            type="text"
            placeholder="Tìm kiếm theo Subject ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>
        <select 
          className="form-select" 
          style={{ width: 150 }}
          value={gender}
          onChange={(e) => { setGender(e.target.value); setPage(1); }}
        >
          <option value="">Tất cả giới</option>
          <option value="M">Nam (M)</option>
          <option value="F">Nữ (F)</option>
        </select>
        <button className="btn btn-primary" onClick={handleSearch}>Tìm</button>
      </div>

      {/* Patient Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Danh sách Bệnh nhân</div>
            <div className="card-subtitle">Tổng: {total} bệnh nhân</div>
          </div>
        </div>

        {loading ? (
          <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Subject ID</th>
                  <th>Giới tính</th>
                  <th>Tuổi (anchor)</th>
                  <th>Năm (anchor)</th>
                  <th>Nhóm năm</th>
                  <th>Tử vong</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((p) => (
                  <tr key={p.subject_id} onClick={() => navigate(`/patients/${p.subject_id}`)}>
                    <td style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>{p.subject_id}</td>
                    <td>
                      <span className={`badge ${p.gender === 'M' ? 'badge-info' : 'badge-medium'}`}>
                        {p.gender === 'M' ? 'Nam' : 'Nữ'}
                      </span>
                    </td>
                    <td>{p.anchor_age}</td>
                    <td>{p.anchor_year}</td>
                    <td>{p.anchor_year_group}</td>
                    <td>{p.dod ? new Date(p.dod).toLocaleDateString('vi-VN') : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                  <FiChevronLeft />
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  const p = page <= 3 ? i + 1 : page + i - 2;
                  if (p > totalPages) return null;
                  return (
                    <button key={p} className={page === p ? 'active' : ''} onClick={() => setPage(p)}>
                      {p}
                    </button>
                  );
                })}
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                  <FiChevronRight />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
