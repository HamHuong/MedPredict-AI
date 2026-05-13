-- ============================================
-- Seed Data: Default Users
-- Password hashes generated with bcrypt
-- admin/admin123, doctor/doctor123
-- ============================================

INSERT INTO users (username, password_hash, full_name, role, is_active) VALUES
('admin', '$2b$12$LJ3m4ys3GZfnMKVdxEBXxOQZHGFMUGVDdIBCyLq8Q7s5ZhHdqBHvi', 'System Administrator', 'admin', TRUE),
('doctor', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Dr. Nguyễn Văn A', 'doctor', TRUE)
ON CONFLICT (username) DO NOTHING;

-- Insert a default ML model entry for testing
INSERT INTO ml_models (name, version, algorithm, stage, metrics) VALUES
('readmission_predictor', 'v1.0', 'XGBoost', 'production', 
 '{"accuracy": 0.82, "precision": 0.78, "recall": 0.75, "f1": 0.76, "roc_auc": 0.85}')
ON CONFLICT DO NOTHING;
