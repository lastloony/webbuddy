import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { queriesApi } from '../../services/api';
import type { Query } from '../../types';
import './QueryPages.css';

export function QueryHistoryPage() {
  const [queries, setQueries] = useState<Query[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    loadQueries();
  }, []);

  const loadQueries = async () => {
    try {
      const data = await queriesApi.getAll();
      setQueries(data);
    } catch (err: any) {
      setError('Ошибка при загрузке запросов');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, queryId: number) => {
    e.stopPropagation(); // Предотвращаем переход к деталям запроса

    if (!confirm('Вы уверены, что хотите удалить этот запрос?')) {
      return;
    }

    setDeletingId(queryId);
    try {
      await queriesApi.delete(queryId);
      // Обновляем список запросов после удаления
      setQueries(queries.filter(q => q.id !== queryId));
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Ошибка при удалении запроса';
      alert(errorMsg);
    } finally {
      setDeletingId(null);
    }
  };

  const canDelete = (status: string) => {
    return status === 'done' || status === 'failed';
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

  const formatDate = (dateString: string) => {
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

  return (
    <Layout>
      <div className="container">
        <div className="query-table-container">
          <div className="query-header">
            <h1 style={{ margin: 0 }}>История запросов</h1>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/queries/create')}
            >
              Создать запрос
            </button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {queries.length === 0 ? (
            <div className="no-data">
              <p>Нет созданных запросов</p>
              <button
                className="btn btn-primary mt-3"
                onClick={() => navigate('/queries/create')}
              >
                Создать первый запрос
              </button>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Описание</th>
                  <th>Статус</th>
                  <th>Создан</th>
                  <th>Завершен</th>
                  <th style={{ width: '100px' }}>Действия</th>
                </tr>
              </thead>
              <tbody>
                {queries.map((query) => (
                  <tr
                    key={query.id}
                    className="query-row"
                    onClick={() => navigate(`/queries/${query.id}`)}
                  >
                    <td>#{query.id}</td>
                    <td>
                      {query.query_text.length > 100
                        ? query.query_text.substring(0, 100) + '...'
                        : query.query_text}
                    </td>
                    <td>
                      <span className={getStatusBadgeClass(query.status)}>
                        {getStatusText(query.status)}
                      </span>
                    </td>
                    <td>{formatDate(query.query_created)}</td>
                    <td>
                      {query.query_finished
                        ? formatDate(query.query_finished)
                        : '-'}
                    </td>
                    <td>
                      {canDelete(query.status) && (
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={(e) => handleDelete(e, query.id)}
                          disabled={deletingId === query.id}
                          title="Удалить запрос"
                        >
                          {deletingId === query.id ? '...' : '🗑️'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </Layout>
  );
}