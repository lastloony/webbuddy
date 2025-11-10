import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/auth/LoginPage';
import { ChangePasswordPage } from './pages/auth/ChangePasswordPage';
import { QueryHistoryPage } from './pages/queries/QueryHistoryPage';
import { QueryDetailPage } from './pages/queries/QueryDetailPage';
import { CreateQueryPage } from './pages/queries/CreateQueryPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <QueryHistoryPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/change-password"
            element={
              <ProtectedRoute>
                <ChangePasswordPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/queries/create"
            element={
              <ProtectedRoute>
                <CreateQueryPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/queries/:id"
            element={
              <ProtectedRoute>
                <QueryDetailPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
