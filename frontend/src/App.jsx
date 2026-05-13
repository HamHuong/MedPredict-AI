import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import LoginPage from './components/Auth/LoginPage';
import Dashboard from './components/Dashboard/Dashboard';
import PatientList from './components/Patients/PatientList';
import PatientDetail from './components/Patients/PatientDetail';
import PredictionRequest from './components/Predictions/PredictionRequest';
import PredictionHistory from './components/Predictions/PredictionHistory';
import UserManagement from './components/Admin/UserManagement';
import ModelManagement from './components/Admin/ModelManagement';
import MonitoringDashboard from './components/Admin/MonitoringDashboard';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: 'var(--bg-primary)' }}>
        <div className="spinner" style={{ width: 32, height: 32 }}></div>
      </div>
    );
  }
  return user ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { user } = useAuth();
  if (user?.role !== 'admin') return <Navigate to="/" />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <LoginPage />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="patients" element={<PatientList />} />
        <Route path="patients/:subjectId" element={<PatientDetail />} />
        <Route path="predictions" element={<PredictionRequest />} />
        <Route path="predictions/history" element={<PredictionHistory />} />
        <Route path="admin/users" element={<AdminRoute><UserManagement /></AdminRoute>} />
        <Route path="admin/models" element={<AdminRoute><ModelManagement /></AdminRoute>} />
        <Route path="admin/monitoring" element={<AdminRoute><MonitoringDashboard /></AdminRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
