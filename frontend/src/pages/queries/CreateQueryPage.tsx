import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { queriesApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import './QueryPages.css';

export function CreateQueryPage() {
  const [queryText, setQueryText] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { user } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!queryText.trim()) {
      setError('Введите описание запроса');
      return;
    }

    if (!user?.project) {
      setError('Пользователь не привязан к проекту');
      return;
    }

    setIsLoading(true);

    try {
      const query = await queriesApi.create(user.project, queryText);
      navigate(`/queries/${query.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании запроса');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="container">
        <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ marginBottom: '24px' }}>Создать новый запрос</h1>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="query-text">
                Описание задачи
              </label>
              <textarea
                id="query-text"
                className="input"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                rows={10}
                placeholder="Опишите задачу для тестирования..."
                required
                autoFocus
                disabled={isLoading}
                style={{ resize: 'vertical', minHeight: '200px' }}
              />
              <small style={{ color: '#666', display: 'block', marginTop: '8px' }}>
                Опишите подробно задачу, которую необходимо протестировать
              </small>
            </div>

            <div style={{ display: 'flex', gap: '16px' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? 'Создание...' : 'Создать запрос'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/')}
                disabled={isLoading}
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}