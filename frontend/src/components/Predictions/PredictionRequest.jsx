import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { FiActivity, FiUser, FiSend } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PredictionRequest() {
  const [searchParams] = useSearchParams();
  const [subjectId, setSubjectId] = useState(searchParams.get('subject_id') || '');
  const [hadmId, setHadmId] = useState(searchParams.get('hadm_id') || '');
  const [admissions, setAdmissions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (subjectId) fetchAdmissions();
  }, [subjectId]);

  const fetchAdmissions = async () => {
    try {
      const res = await client.get(`/patients/${subjectId}/admissions`);
      setAdmissions(res.data);
    } catch {
      setAdmissions([]);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!subjectId || !hadmId) { setError('Vui lòng điền đầy đủ thông tin'); return; }
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const res = await client.post('/predictions/request', {
        subject_id: parseInt(subjectId),
        hadm_id: parseInt(hadmId)
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Dự đoán thất bại');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    const colors = { HIGH: '#f43f5e', MEDIUM: '#f59e0b', LOW: '#10b981' };
    return colors[level] || '#6b7280';
  };

  return (
    <div>
      <div className="grid-2">
        {/* Request Form */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title"><FiActivity style={{ verticalAlign: 'middle', marginRight: 8 }} />Yêu cầu Dự đoán</div>
              <div className="card-subtitle">Dự đoán nguy cơ tái nhập viện 30 ngày</div>
            </div>
          </div>
          {error && <div className="login-error">{error}</div>}
          <form onSubmit={handlePredict}>
            <div className="form-group">
              <label className="form-label"><FiUser style={{ marginRight: 4 }} /> Subject ID</label>
              <input className="form-input" type="number" value={subjectId} 
                onChange={(e) => { setSubjectId(e.target.value); setHadmId(''); }}
                placeholder="Nhập Subject ID..." required />
            </div>
            <div className="form-group">
              <label className="form-label">Admission (hadm_id)</label>
              {admissions.length > 0 ? (
                <select className="form-select" value={hadmId} onChange={(e) => setHadmId(e.target.value)} required>
                  <option value="">-- Chọn lượt nhập viện --</option>
                  {admissions.map((a) => (
                    <option key={a.hadm_id} value={a.hadm_id}>
                      #{a.hadm_id} — {a.admission_type} ({a.admittime ? new Date(a.admittime).toLocaleDateString('vi-VN') : '?'})
                    </option>
                  ))}
                </select>
              ) : (
                <input className="form-input" type="number" value={hadmId}
                  onChange={(e) => setHadmId(e.target.value)}
                  placeholder="Nhập Admission ID..." required />
              )}
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
              {loading ? <><span className="spinner" style={{ width: 16, height: 16 }}></span> Đang xử lý...</> : <><FiSend /> Chạy Dự đoán</>}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Kết quả Dự đoán</div>
          </div>
          {result ? (
            <div>
              {/* Risk Gauge */}
              <div className="risk-gauge">
                <div className={`gauge-circle ${result.risk_level?.toLowerCase()}`} 
                  style={{ '--gauge-pct': `${Math.round(result.probability * 100)}%` }}>
                  <div className="gauge-inner">
                    <div className="gauge-value" style={{ color: getRiskColor(result.risk_level) }}>
                      {(result.probability * 100).toFixed(1)}%
                    </div>
                    <div className="gauge-label">Xác suất tái nhập viện</div>
                  </div>
                </div>
                <span className={`badge badge-${result.risk_level?.toLowerCase()}`} style={{ fontSize: 16, padding: '6px 20px' }}>
                  {result.risk_level === 'HIGH' ? '⚠️ NGUY CƠ CAO' : result.risk_level === 'MEDIUM' ? '⚡ NGUY CƠ TRUNG BÌNH' : '✅ NGUY CƠ THẤP'}
                </span>
              </div>

              {/* Top Features */}
              {result.top_features?.length > 0 && (
                <div style={{ marginTop: 20 }}>
                  <h4 style={{ marginBottom: 12, color: 'var(--text-secondary)' }}>Yếu tố ảnh hưởng chính</h4>
                  <div style={{ height: 250 }}>
                    <ResponsiveContainer>
                      <BarChart data={result.top_features.slice(0, 6)} layout="vertical" margin={{ left: 100 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.3)" />
                        <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                        <YAxis type="category" dataKey="feature" tick={{ fill: '#9ca3af', fontSize: 11 }} width={100} />
                        <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid rgba(55,65,81,0.5)', borderRadius: 8 }} />
                        <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              <div style={{ marginTop: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                Model: {result.model_name} {result.model_version} | Prediction #{result.prediction_id}
              </div>
            </div>
          ) : (
            <div className="loading-spinner" style={{ minHeight: 300 }}>
              <FiActivity style={{ fontSize: 48, opacity: 0.15 }} />
              <span style={{ color: 'var(--text-muted)' }}>Chọn bệnh nhân và chạy dự đoán</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
