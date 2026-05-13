import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { 
  FiUsers, FiActivity, FiAlertTriangle, FiTrendingUp,
  FiCpu, FiCalendar
} from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const RISK_COLORS = { HIGH: '#f43f5e', MEDIUM: '#f59e0b', LOW: '#10b981' };

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await client.get('/admin/dashboard');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        Đang tải dữ liệu...
      </div>
    );
  }

  const riskData = [
    { name: 'Cao', value: stats?.high_risk_count || 0, color: RISK_COLORS.HIGH },
    { name: 'Trung bình', value: stats?.medium_risk_count || 0, color: RISK_COLORS.MEDIUM },
    { name: 'Thấp', value: stats?.low_risk_count || 0, color: RISK_COLORS.LOW },
  ];

  const modelMetrics = stats?.active_model?.metrics 
    ? Object.entries(stats.active_model.metrics).map(([key, val]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value: Math.round(val * 100)
      }))
    : [];

  return (
    <div>
      {/* Stat Cards */}
      <div className="stat-cards">
        <div className="stat-card emerald" onClick={() => navigate('/patients')} style={{ cursor: 'pointer' }}>
          <div className="stat-icon emerald"><FiUsers /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total_patients || 0}</div>
            <div className="stat-label">Tổng bệnh nhân</div>
          </div>
        </div>
        <div className="stat-card blue">
          <div className="stat-icon blue"><FiCalendar /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total_admissions || 0}</div>
            <div className="stat-label">Lượt nhập viện</div>
          </div>
        </div>
        <div className="stat-card amber" onClick={() => navigate('/predictions/history')} style={{ cursor: 'pointer' }}>
          <div className="stat-icon amber"><FiActivity /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total_predictions || 0}</div>
            <div className="stat-label">Tổng dự đoán</div>
          </div>
        </div>
        <div className="stat-card rose">
          <div className="stat-icon rose"><FiAlertTriangle /></div>
          <div className="stat-content">
            <div className="stat-value">{stats?.high_risk_count || 0}</div>
            <div className="stat-label">Nguy cơ cao</div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid-2">
        {/* Risk Distribution Pie Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Phân bố Nguy cơ</div>
              <div className="card-subtitle">Tỷ lệ mức nguy cơ tái nhập viện</div>
            </div>
          </div>
          <div style={{ height: 280 }}>
            {riskData.some(d => d.value > 0) ? (
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {riskData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="loading-spinner" style={{ height: '100%' }}>
                <FiActivity style={{ fontSize: 32, opacity: 0.3 }} />
                <span>Chưa có dữ liệu dự đoán</span>
              </div>
            )}
          </div>
        </div>

        {/* Model Performance Bar Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Hiệu suất Model</div>
              <div className="card-subtitle">
                {stats?.active_model 
                  ? `${stats.active_model.name} ${stats.active_model.version} (${stats.active_model.algorithm})`
                  : 'Chưa có model active'}
              </div>
            </div>
            <span className="badge badge-production">Production</span>
          </div>
          <div style={{ height: 280 }}>
            {modelMetrics.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={modelMetrics} layout="vertical" margin={{ left: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.3)" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ background: '#1f2937', border: '1px solid rgba(55,65,81,0.5)', borderRadius: 8 }}
                    formatter={(val) => [`${val}%`]}
                  />
                  <Bar dataKey="value" fill="#10b981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="loading-spinner" style={{ height: '100%' }}>
                <FiCpu style={{ fontSize: 32, opacity: 0.3 }} />
                <span>Chưa có model metrics</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Dự đoán Gần đây</div>
            <div className="card-subtitle">5 dự đoán mới nhất</div>
          </div>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate('/predictions/history')}>
            Xem tất cả
          </button>
        </div>
        {stats?.recent_predictions?.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Bệnh nhân</th>
                <th>Admission</th>
                <th>Xác suất</th>
                <th>Nguy cơ</th>
                <th>Thời gian</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_predictions.map((p) => (
                <tr key={p.prediction_id} onClick={() => navigate(`/predictions/${p.prediction_id}`)}>
                  <td>#{p.prediction_id}</td>
                  <td>Patient {p.subject_id}</td>
                  <td>{p.hadm_id}</td>
                  <td>{(p.probability * 100).toFixed(1)}%</td>
                  <td>
                    <span className={`badge badge-${p.risk_level?.toLowerCase()}`}>
                      {p.risk_level}
                    </span>
                  </td>
                  <td>{p.predicted_at ? new Date(p.predicted_at).toLocaleString('vi-VN') : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="loading-spinner">
            <span>Chưa có dự đoán nào</span>
          </div>
        )}
      </div>
    </div>
  );
}
