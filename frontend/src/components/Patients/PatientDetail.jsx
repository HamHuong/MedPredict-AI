import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { FiUser, FiCalendar, FiActivity, FiArrowLeft, FiFileText } from 'react-icons/fi';

export default function PatientDetail() {
  const { subjectId } = useParams();
  const [patient, setPatient] = useState(null);
  const [selectedAdmission, setSelectedAdmission] = useState(null);
  const [admissionDetail, setAdmissionDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => { fetchPatient(); }, [subjectId]);

  const fetchPatient = async () => {
    try {
      const res = await client.get(`/patients/${subjectId}`);
      setPatient(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAdmissionDetail = async (hadmId) => {
    setSelectedAdmission(hadmId);
    try {
      const res = await client.get(`/patients/admissions/${hadmId}`);
      setAdmissionDetail(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="loading-spinner"><div className="spinner"></div> Đang tải...</div>;
  if (!patient) return <div className="loading-spinner">Không tìm thấy bệnh nhân</div>;

  return (
    <div>
      <button className="btn btn-secondary btn-sm" onClick={() => navigate('/patients')} style={{ marginBottom: 20 }}>
        <FiArrowLeft /> Quay lại
      </button>

      {/* Patient Info Card */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div className="stat-icon teal"><FiUser /></div>
            <div>
              <div className="card-title" style={{ fontSize: 20 }}>Bệnh nhân #{patient.subject_id}</div>
              <div className="card-subtitle">Tổng cộng {patient.total_admissions} lượt nhập viện</div>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => navigate(`/predictions?subject_id=${patient.subject_id}`)}>
            <FiActivity /> Dự đoán
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginTop: 8 }}>
          <div>
            <div className="stat-label">Giới tính</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>{patient.gender === 'M' ? 'Nam' : 'Nữ'}</div>
          </div>
          <div>
            <div className="stat-label">Tuổi (anchor)</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>{patient.anchor_age}</div>
          </div>
          <div>
            <div className="stat-label">Năm</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>{patient.anchor_year}</div>
          </div>
          <div>
            <div className="stat-label">Tử vong</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>{patient.dod ? new Date(patient.dod).toLocaleDateString('vi-VN') : 'Không'}</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Admissions List */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            <FiCalendar style={{ verticalAlign: 'middle', marginRight: 8 }} />
            Lịch sử Nhập viện
          </div>
          {patient.admissions?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {patient.admissions.map((a) => (
                <div 
                  key={a.hadm_id}
                  onClick={() => fetchAdmissionDetail(a.hadm_id)}
                  style={{
                    padding: '12px 16px',
                    background: selectedAdmission === a.hadm_id ? 'var(--bg-hover)' : 'var(--bg-input)',
                    border: `1px solid ${selectedAdmission === a.hadm_id ? 'var(--border-accent)' : 'var(--border-glass)'}`,
                    borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>#{a.hadm_id}</span>
                      <span style={{ marginLeft: 12, fontSize: 13, color: 'var(--text-muted)' }}>{a.admission_type}</span>
                    </div>
                    {a.hospital_expire_flag === 1 && <span className="badge badge-high">Tử vong</span>}
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                    {a.admittime ? new Date(a.admittime).toLocaleString('vi-VN') : '—'} → {a.dischtime ? new Date(a.dischtime).toLocaleString('vi-VN') : '—'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="loading-spinner">Không có dữ liệu nhập viện</div>
          )}
        </div>

        {/* Admission Detail */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            <FiFileText style={{ verticalAlign: 'middle', marginRight: 8 }} />
            Chi tiết Lượt Nhập viện
          </div>
          {admissionDetail ? (
            <div>
              <div style={{ marginBottom: 16 }}>
                <h4 style={{ color: 'var(--accent-teal)', marginBottom: 8 }}>Chẩn đoán ({admissionDetail.diagnoses?.length || 0})</h4>
                {admissionDetail.diagnoses?.slice(0, 10).map((d, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', padding: '4px 0' }}>
                    <span className="badge badge-info" style={{ marginRight: 8 }}>ICD-{d.icd_version}</span>
                    {d.icd_code}
                  </div>
                ))}
              </div>
              <div style={{ marginBottom: 16 }}>
                <h4 style={{ color: 'var(--accent-amber)', marginBottom: 8 }}>Thuốc ({admissionDetail.prescriptions?.length || 0})</h4>
                {admissionDetail.prescriptions?.slice(0, 8).map((p, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', padding: '4px 0' }}>
                    💊 {p.drug} {p.dose_val_rx && `(${p.dose_val_rx} ${p.dose_unit_rx || ''})`}
                  </div>
                ))}
              </div>
              <div style={{ marginBottom: 16 }}>
                <h4 style={{ color: 'var(--accent-purple)', marginBottom: 8 }}>ICU ({admissionDetail.icu_stays?.length || 0})</h4>
                {admissionDetail.icu_stays?.map((icu, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', padding: '4px 0' }}>
                    🏥 {icu.first_careunit} — LOS: {icu.los?.toFixed(1)} ngày
                  </div>
                ))}
              </div>
              <div>
                <h4 style={{ color: 'var(--accent-emerald)', marginBottom: 8 }}>Lab Events</h4>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                  Tổng: {admissionDetail.lab_events_count} kết quả xét nghiệm
                </div>
              </div>
              <button 
                className="btn btn-primary" 
                style={{ marginTop: 16, width: '100%' }}
                onClick={() => navigate(`/predictions?subject_id=${admissionDetail.subject_id}&hadm_id=${admissionDetail.hadm_id}`)}
              >
                <FiActivity /> Dự đoán tái nhập viện
              </button>
            </div>
          ) : (
            <div className="loading-spinner" style={{ minHeight: 200 }}>
              Chọn một lượt nhập viện để xem chi tiết
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
