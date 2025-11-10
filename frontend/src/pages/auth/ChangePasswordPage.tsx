import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi } from '../../services/api';
import { Layout } from '../../components/layout/Layout';
import './AuthPages.css';

export function ChangePasswordPage() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const isFirstLogin = location.state?.firstLogin;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (newPassword.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    setIsLoading(true);

    try {
      await authApi.changePassword(oldPassword, newPassword, confirmPassword);
      setSuccess(true);

      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.old_password?.[0] ||
        err.response?.data?.new_password?.[0] ||
        'Ошибка при смене пароля'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="auth-container">
        <div className="auth-card card">
          <h1 className="auth-title">
            {isFirstLogin ? 'Первый вход' : 'Смена пароля'}
          </h1>
          {isFirstLogin && (
            <p className="auth-subtitle">
              Пожалуйста, смените временный пароль на постоянный
            </p>
          )}

          {error && <div className="alert alert-error">{error}</div>}
          {success && (
            <div className="alert alert-success">
              Пароль успешно изменен! Перенаправление...
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="old-password">
                {isFirstLogin ? 'Временный пароль' : 'Текущий пароль'}
              </label>
              <input
                type="password"
                id="old-password"
                className="input"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                required
                autoFocus
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="new-password">
                Новый пароль (минимум 8 символов)
              </label>
              <input
                type="password"
                id="new-password"
                className="input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirm-password">
                Подтверждение пароля
              </label>
              <input
                type="password"
                id="confirm-password"
                className="input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%' }}
              disabled={isLoading}
            >
              {isLoading ? 'Сохранение...' : 'Сменить пароль'}
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}