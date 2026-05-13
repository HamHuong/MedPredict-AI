import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { FiChevronLeft, FiChevronRight, FiFilter } from 'react-icons/fi';

export default function PredictionHistory() {
  const [predictions, setPredictions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const perPage = 20;

  useEffect(() => { fetchHistory(); }, [page, riskFilter]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = { page, per_page: perPage };
      if (riskFilter) params.risk_level = riskFilter;
      const res = await client.get('/predictions/history', { params });
      setPredictions(res.data.predictions);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      <div className="search-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <FiFilter style={{ color: 'var(--text-muted)' }} />
          <select className="form-select" style={{ width: 180 }} value={riskFilter}
            onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}>
            <option value="">Tất cả mức nguy cơ</option>
            <option value="HIGH">🔴 Cao</option>
            <option value="MEDIUM">🟡 Trung bình</option>
            <option value="LOW">🟢 Thấp</option>
          </select>
        </div>
        <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Tổng: {total} kết quả</span>
      </div>

      <div className="card">
        {loading ? (
          <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>
        ) : predictions.length === 0 ? (
          <div className="loading-spinner">Chưa có lịch sử dự đoán</div>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Bệnh nhân</th>
                  <th>Admission</th>
                  <th>Xác suất</th>
                  <th>Nguy cơ</th>
                  <th>Model</th>
                  <th>Thời gian</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => (
                  <tr key={p.prediction_id} onClick={() => navigate(`/predictions/${p.prediction_id}`)}>
                    <td style={{ fontWeight: 600 }}>#{p.prediction_id}</td>
                    <td>{p.subject_id}</td>
                    <td>{p.hadm_id}</td>
                    <td style={{ fontWeight: 600, color: 
                      p.probability > 0.7 ? 'var(--accent-rose)' : 
                      p.probability > 0.3 ? 'var(--accent-amber)' : 'var(--accent-emerald)' 
                    }}>
                      {(p.probability * 100).toFixed(1)}%
                    </td>
                    <td><span className={`badge badge-${p.risk_level?.toLowerCase()}`}>{p.risk_level}</span></td>
                    <td style={{ fontSize: 12 }}>{p.model_name} {p.model_version}</td>
                    <td style={{ fontSize: 13 }}>{p.predicted_at ? new Date(p.predicted_at).toLocaleString('vi-VN') : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 && (
              <div className="pagination">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}><FiChevronLeft /></button>
                <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Trang {page}/{totalPages}</span>
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}><FiChevronRight /></button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
