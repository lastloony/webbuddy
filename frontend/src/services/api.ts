import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/login/', { username, password });
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string, confirmPassword: string) => {
    const response = await api.post('/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/me/');
    return response.data;
  },
};

// Queries API
export const queriesApi = {
  getAll: async () => {
    const response = await api.get('/queries/');
    return response.data.results || response.data; // Support paginated response
  },

  getById: async (id: number) => {
    const response = await api.get(`/queries/${id}/`);
    return response.data;
  },

  create: async (projectId: number, queryText: string) => {
    const response = await api.post('/queries/', {
      project: projectId,
      query_text: queryText,
    });
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await api.patch(`/queries/${id}/`, data);
    return response.data;
  },

  getLogs: async (id: number) => {
    const response = await api.get(`/queries/${id}/logs/`);
    return response.data.results || response.data; // Support paginated response
  },

  getByStatus: async (status: string) => {
    const response = await api.get(`/queries/by_status/?status=${status}`);
    return response.data;
  },
};

// Logs API
export const logsApi = {
  create: async (projectId: number, queryId: number, logData: string) => {
    const response = await api.post('/logs/', {
      project: projectId,
      query: queryId,
      log_data: logData,
    });
    return response.data;
  },
};

// Projects API
export const projectsApi = {
  getMyProject: async () => {
    const response = await api.get('/projects/my_project/');
    return response.data;
  },

  update: async (id: number, data: {
    test_it_token?: string;
    test_it_project_id?: string;
    jira_token?: string;
    jira_project_id?: string;
    project_context?: string;
  }) => {
    const response = await api.patch(`/projects/${id}/`, data);
    return response.data;
  },
};