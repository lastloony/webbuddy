import { useState, useEffect } from 'react';
import { projectsApi } from '../../services/api';
import { Layout } from '../../components/layout/Layout';
import type { Project } from '../../types';
import './SettingsPage.css';

export function SettingsPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Form fields
  const [testItToken, setTestItToken] = useState('');
  const [testItProjectId, setTestItProjectId] = useState('');
  const [jiraToken, setJiraToken] = useState('');
  const [jiraProjectId, setJiraProjectId] = useState('');
  const [projectContext, setProjectContext] = useState('');

  useEffect(() => {
    loadProject();
  }, []);

  const loadProject = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await projectsApi.getMyProject();
      setProject(data);
      setTestItProjectId(data.test_it_project_id || '');
      setJiraProjectId(data.jira_project_id || '');
      setProjectContext(data.project_context || '');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки настроек проекта');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setIsSaving(true);

    if (!project) {
      setError('Проект не загружен');
      setIsSaving(false);
      return;
    }

    try {
      const updateData: any = {
        test_it_project_id: testItProjectId,
        jira_project_id: jiraProjectId,
        project_context: projectContext,
      };

      // Only include tokens if they were changed
      if (testItToken.trim()) {
        updateData.test_it_token = testItToken;
      }
      if (jiraToken.trim()) {
        updateData.jira_token = jiraToken;
      }

      await projectsApi.update(project.id, updateData);
      setSuccess(true);

      // Clear token fields after successful save
      setTestItToken('');
      setJiraToken('');

      // Reload project to get updated masked tokens
      await loadProject();

      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при сохранении настроек');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="settings-container">
          <div className="loading">Загрузка настроек...</div>
        </div>
      </Layout>
    );
  }

  if (!project) {
    return (
      <Layout>
        <div className="settings-container">
          <div className="alert alert-error">{error || 'Проект не найден'}</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="settings-container">
        <div className="settings-card card">
          <h1 className="settings-title">Настройки проекта</h1>
          <p className="settings-subtitle">Проект: {project.project_name}</p>

          {error && <div className="alert alert-error">{error}</div>}
          {success && (
            <div className="alert alert-success">
              Настройки успешно сохранены!
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* TestIt Section */}
            <div className="settings-section">
              <h2 className="section-title">TestIt</h2>

              <div className="form-group">
                <label className="form-label" htmlFor="test-it-token">
                  TestIt Token
                </label>
                {project.test_it_token_masked && (
                  <div className="token-info">
                    Текущий токен: <code>{project.test_it_token_masked}</code>
                  </div>
                )}
                <input
                  type="password"
                  id="test-it-token"
                  className="input"
                  value={testItToken}
                  onChange={(e) => setTestItToken(e.target.value)}
                  placeholder="Введите новый токен для изменения"
                  disabled={isSaving}
                />
                <small className="form-hint">
                  Оставьте пустым, если не хотите изменять токен
                </small>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="test-it-project-id">
                  TestIt Project ID
                </label>
                <input
                  type="text"
                  id="test-it-project-id"
                  className="input"
                  value={testItProjectId}
                  onChange={(e) => setTestItProjectId(e.target.value)}
                  placeholder="Введите ID проекта в TestIt"
                  disabled={isSaving}
                />
              </div>
            </div>

            {/* Jira Section */}
            <div className="settings-section">
              <h2 className="section-title">Jira</h2>

              <div className="form-group">
                <label className="form-label" htmlFor="jira-token">
                  Jira Token
                </label>
                {project.jira_token_masked && (
                  <div className="token-info">
                    Текущий токен: <code>{project.jira_token_masked}</code>
                  </div>
                )}
                <input
                  type="password"
                  id="jira-token"
                  className="input"
                  value={jiraToken}
                  onChange={(e) => setJiraToken(e.target.value)}
                  placeholder="Введите новый токен для изменения"
                  disabled={isSaving}
                />
                <small className="form-hint">
                  Оставьте пустым, если не хотите изменять токен
                </small>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="jira-project-id">
                  Jira Project ID
                </label>
                <input
                  type="text"
                  id="jira-project-id"
                  className="input"
                  value={jiraProjectId}
                  onChange={(e) => setJiraProjectId(e.target.value)}
                  placeholder="Введите ID проекта в Jira"
                  disabled={isSaving}
                />
              </div>
            </div>

            {/* Project Context Section */}
            <div className="settings-section">
              <h2 className="section-title">Контекст проекта</h2>

              <div className="form-group">
                <label className="form-label" htmlFor="project-context">
                  Описание проекта
                </label>
                <textarea
                  id="project-context"
                  className="input textarea"
                  value={projectContext}
                  onChange={(e) => setProjectContext(e.target.value)}
                  placeholder="Введите описание проекта, используемые технологии, особенности и т.д."
                  rows={6}
                  disabled={isSaving}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSaving}
            >
              {isSaving ? 'Сохранение...' : 'Сохранить настройки'}
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}