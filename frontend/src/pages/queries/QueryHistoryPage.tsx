import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { queriesApi } from '../../services/api';
import { Query } from '../../types';
import './QueryPages.css';

export function QueryHistoryPage() {
  const [queries, setQueries] = useState<Query[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

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