export interface User {
  id: number;
  username: string;
  fio_name: string;
  email: string;
  project: number;
  project_name?: string;
  first_login: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
  first_login: boolean;
}

export interface Query {
  id: number;
  project: number;
  project_name?: string;
  user: number;
  user_name?: string;
  query_text: string;
  answer_text: string;
  status: 'queued' | 'in_progress' | 'done' | 'failed';
  query_created: string;
  query_started: string | null;
  query_finished: string | null;
}

export interface QueryLog {
  id: number;
  project: number;
  query: number;
  log_data: string;
  created: string;
}

export interface TokenUsage {
  id: number;
  project: number;
  query: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  created: string;
}