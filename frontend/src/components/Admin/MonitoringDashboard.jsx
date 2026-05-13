import { useState, useEffect } from 'react';
import client from '../../api/client';
import { FiBarChart2, FiTrendingUp } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchMetrics(); }, []);

  const fetchMetrics = async () => {
    try {
      const res = await client.get('/admin/metrics');
      setMetrics(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>;

  const riskData = metrics?.risk_distribution 
    ? Object.entries(metrics.risk_distribution).map(([k, v]) => ({ name: k, count: v }))
    : [];

  const dailyData = metrics?.daily_predictions || [];

  const modelMetricsData = metrics?.active_model_metrics
    ? Object.entries(metrics.active_model_metrics).map(([k, v]) => ({ 
        name: k.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()), 
        value: Math.round(v * 100) 
      }))
    : [];

  return (
    <div>
      {/* Stats Row */}
      <div className="stat-cards">
        <div className="stat-card blue">
          <div className="stat-icon blue"><FiBarChart2 /></div>
          <div className="stat-content">
            <div className="stat-value">{metrics?.total_models || 0}</div>
            <div className="stat-label">Tổng Models</div>
          </div>
        </div>
        <div className="stat-card emerald">
          <div className="stat-icon emerald"><FiTrendingUp /></div>
          <div className="stat-content">
            <div className="stat-value">
              {metrics?.active_model_metrics?.roc_auc 
                ? `${(metrics.active_model_metrics.roc_auc * 100).toFixed(0)}%` 
                : 'N/A'}
            </div>
            <div className="stat-label">AUC Score</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Risk Distribution */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Phân bố Nguy cơ</div>
          <div style={{ height: 280 }}>
            {riskData.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={riskData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.3)" />
                  <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid rgba(55,65,81,0.5)', borderRadius: 8 }} />
                  <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="loading-spinner" style={{ height: '100%' }}>Chưa có dữ liệu</div>
            )}
          </div>
        </div>

        {/* Daily Predictions */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Dự đoán theo Ngày (7 ngày)</div>
          <div style={{ height: 280 }}>
            {dailyData.length > 0 ? (
              <ResponsiveContainer>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.3)" />
                  <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid rgba(55,65,81,0.5)', borderRadius: 8 }} />
                  <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="loading-spinner" style={{ height: '100%' }}>Chưa có dữ liệu</div>
            )}
          </div>
        </div>

        {/* Model Metrics */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="card-title" style={{ marginBottom: 16 }}>Hiệu suất Model Hiện tại</div>
          <div style={{ height: 280 }}>
            {modelMetricsData.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={modelMetricsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.3)" />
                  <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid rgba(55,65,81,0.5)', borderRadius: 8 }} formatter={(v) => [`${v}%`]} />
                  <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="loading-spinner" style={{ height: '100%' }}>Chưa có model metrics</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
