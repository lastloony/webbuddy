import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-container">
          <Link to="/" className="navbar-brand">
            WebBuddy
          </Link>
          {user && (
            <div className="navbar-menu">
              <Link to="/" className="nav-link">
                История запросов
              </Link>
              <Link to="/queries/create" className="nav-link">
                Создать запрос
              </Link>
              <span className="nav-user">
                {user.fio_name || user.username}
              </span>
              <button onClick={handleLogout} className="btn btn-secondary btn-sm">
                Выход
              </button>
            </div>
          )}
        </div>
      </nav>
      <main className="main-content">{children}</main>
    </div>
  );
}