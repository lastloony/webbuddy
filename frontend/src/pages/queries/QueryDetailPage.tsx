import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { queriesApi } from '../../services/api';
import type { Query, QueryLog } from '../../types';
import './QueryPages.css';

export function QueryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [query, setQuery] = useState<Query | null>(null);
  const [logs, setLogs] = useState<QueryLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;

    loadQuery();
    loadLogs();

    // Set up polling for updates
    const interval = setInterval(() => {
      if (query?.status !== 'done' && query?.status !== 'failed') {
        loadQuery();
        loadLogs();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id, query?.status]);

  const loadQuery = async () => {
    if (!id) return;
    try {
      const queryId = parseInt(id, 10);
      if (isNaN(queryId)) {
        setError('Неверный ID запроса');
        setIsLoading(false);
        return;
      }
      const data = await queriesApi.getById(queryId);
      setQuery(data);
    } catch (err: any) {
      setError('Ошибка при загрузке запроса');
    } finally {
      setIsLoading(false);
    }
  };

  const loadLogs = async () => {
    if (!id) return;
    try {
      const queryId = parseInt(id, 10);
      if (isNaN(queryId)) return;
      const data = await queriesApi.getLogs(queryId);
      setLogs(data);
    } catch (err: any) {
      console.error('Error loading logs:', err);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    return `status-badge status-${status}`;
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      queued: 'В очереди',
      in_progress: 'В работе',
      done: 'Завершено',
      failed: 'Ошибка',
    };
    return statusMap[status] || status;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="container text-center" style={{ paddingTop: '100px' }}>
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: '20px', color: 'white' }}>Загрузка...</p>
        </div>
      </Layout>
    );
  }

  if (!query) {
    return (
      <Layout>
        <div className="container text-center" style={{ paddingTop: '100px' }}>
          <h1 style={{ color: 'white' }}>Запрос не найден</h1>
          <button className="btn btn-primary mt-3" onClick={() => navigate('/')}>
            Вернуться к списку
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container query-detail-container">
        <div className="query-detail-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h1>Запрос #{query.id}</h1>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              Вернуться
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <div style={{ marginBottom: '20px' }}>
            <span className={getStatusBadgeClass(query.status)}>
              {getStatusText(query.status)}
            </span>
          </div>

          <div className="query-info-grid">
            <div className="query-info-item">
              <div className="query-info-label">Создан</div>
              <div className="query-info-value">{formatDate(query.query_created)}</div>
            </div>
            <div className="query-info-item">
              <div className="query-info-label">Начат</div>
              <div className="query-info-value">{formatDate(query.query_started)}</div>
            </div>
            <div className="query-info-item">
              <div className="query-info-label">Завершен</div>
              <div className="query-info-value">{formatDate(query.query_finished)}</div>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <h3 style={{ marginBottom: '12px' }}>Описание задачи:</h3>
            <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
              {query.query_text}
            </p>
          </div>
        </div>

        {query.answer_text && (
          <div className="query-answer">
            <h2 style={{ marginBottom: '16px' }}>Результат:</h2>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
              {query.answer_text}
            </div>
          </div>
        )}

        <div className="query-logs">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>Логи выполнения</h2>
            {(query.status === 'in_progress' || query.status === 'queued') && (
              <div className="spinner" style={{ width: '24px', height: '24px', borderWidth: '3px' }}></div>
            )}
          </div>

          {logs.length === 0 ? (
            <div className="no-data">
              <p>Логов пока нет</p>
            </div>
          ) : (
            <div>
              {logs.map((log) => (
                <div key={log.id} className="log-entry">
                  <div className="log-timestamp">
                    {formatDate(log.created)}
                  </div>
                  <div>{log.log_data}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}