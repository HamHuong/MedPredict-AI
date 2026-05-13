import { useState, useEffect } from 'react';
import client from '../../api/client';
import { FiCpu, FiRefreshCw, FiArrowUp, FiArchive } from 'react-icons/fi';

export default function ModelManagement() {
  const [models, setModels] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [modelsRes, jobsRes] = await Promise.all([
        client.get('/admin/models'),
        client.get('/admin/retrain/jobs')
      ]);
      setModels(modelsRes.data);
      setJobs(jobsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const changeStage = async (modelId, stage) => {
    try {
      await client.put(`/admin/models/${modelId}/stage`, { stage });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const triggerRetrain = async () => {
    setRetraining(true);
    try {
      await client.post('/admin/retrain', { trigger_reason: 'Manual retrain from UI' });
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setRetraining(false);
    }
  };

  if (loading) return <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
        <h3 style={{ fontSize: 18, fontWeight: 600 }}>ML Models</h3>
        <button className="btn btn-primary" onClick={triggerRetrain} disabled={retraining}>
          <FiRefreshCw className={retraining ? 'spinning' : ''} /> {retraining ? 'Đang train...' : 'Retrain Model'}
        </button>
      </div>

      {/* Models Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 20, marginBottom: 24 }}>
        {models.map((m) => (
          <div key={m.model_id} className="card">
            <div className="card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div className="stat-icon purple"><FiCpu /></div>
                <div>
                  <div className="card-title">{m.name}</div>
                  <div className="card-subtitle">{m.algorithm} — {m.version}</div>
                </div>
              </div>
              <span className={`badge badge-${m.stage}`}>{m.stage}</span>
            </div>
            {m.metrics && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, margin: '12px 0' }}>
                {Object.entries(m.metrics).map(([key, val]) => (
                  <div key={key} style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-teal)' }}>
                      {typeof val === 'number' ? (val * 100).toFixed(0) + '%' : val}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            )}
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              {m.stage !== 'production' && (
                <button className="btn btn-sm btn-primary" onClick={() => changeStage(m.model_id, 'production')}>
                  <FiArrowUp /> Production
                </button>
              )}
              {m.stage !== 'archived' && (
                <button className="btn btn-sm btn-secondary" onClick={() => changeStage(m.model_id, 'archived')}>
                  <FiArchive /> Archive
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Retraining Jobs */}
      <div className="card">
        <div className="card-title" style={{ marginBottom: 16 }}>Lịch sử Retraining</div>
        {jobs.length > 0 ? (
          <table className="data-table">
            <thead><tr><th>Job ID</th><th>Lý do</th><th>Trạng thái</th><th>Bắt đầu</th><th>Kết thúc</th></tr></thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.job_id}>
                  <td>#{j.job_id}</td>
                  <td>{j.trigger_reason || '—'}</td>
                  <td>
                    <span className={`badge ${j.status === 'completed' ? 'badge-low' : j.status === 'failed' ? 'badge-high' : 'badge-medium'}`}>
                      {j.status}
                    </span>
                  </td>
                  <td style={{ fontSize: 13 }}>{j.started_at ? new Date(j.started_at).toLocaleString('vi-VN') : '—'}</td>
                  <td style={{ fontSize: 13 }}>{j.finished_at ? new Date(j.finished_at).toLocaleString('vi-VN') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="loading-spinner">Chưa có job retraining</div>
        )}
      </div>
    </div>
  );
}
