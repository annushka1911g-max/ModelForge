import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './authentication/AuthContext';
import { ProtectedRoute } from './authentication/ProtectedRoute';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { ModelsPage } from './pages/ModelsPage';
import { ModelDetailPage } from './pages/ModelDetailPage';
import { DeploymentsPage } from './pages/DeploymentsPage';
import { PlaygroundPage } from './pages/PlaygroundPage';
import { BatchPredictPage } from './pages/BatchPredictPage';
import { MonitoringPage } from './pages/MonitoringPage';
import { UserAdminPage } from './pages/UserAdminPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Application Shell */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <div className="flex flex-col min-h-screen">
                  <Navbar />
                  <div className="flex flex-1">
                    <Sidebar />
                    <main className="flex-1 p-8 bg-slate-950 overflow-y-auto">
                      <Routes>
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/models" element={<ModelsPage />} />
                        <Route path="/models/:id" element={<ModelDetailPage />} />
                        <Route path="/deployments" element={<DeploymentsPage />} />
                        <Route path="/playground" element={<PlaygroundPage />} />
                        <Route path="/batch" element={<BatchPredictPage />} />
                        <Route path="/monitoring" element={<MonitoringPage />} />
                        <Route
                          path="/users"
                          element={
                            <ProtectedRoute allowedRoles={['ADMIN']}>
                              <UserAdminPage />
                            </ProtectedRoute>
                          }
                        />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                      </Routes>
                    </main>
                  </div>
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
