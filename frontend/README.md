# WebBuddy Frontend

React-приложение для WebBuddy AI-Powered Testing Platform.

## Технологический стек

- **React 18** + **TypeScript** - UI библиотека с типизацией
- **Vite** - быстрый сборщик и dev server
- **React Router** - клиентский роутинг
- **Axios** - HTTP клиент с автообновлением JWT токенов

## Быстрый старт

```bash
# Установка зависимостей
npm install

# Запуск dev server (http://localhost:5173)
npm run dev

# Production build
npm run build
```

## Конфигурация

Создайте файл `.env` (уже создан):

```env
VITE_API_URL=http://localhost:8000
```

## Структура

- `src/components/` - переиспользуемые компоненты
- `src/pages/` - страницы приложения
- `src/services/api.ts` - API клиент с JWT
- `src/contexts/AuthContext.tsx` - глобальный auth state
- `src/types/` - TypeScript типы

## API интеграция

Все API запросы автоматически:
- Добавляют JWT токен в заголовки
- Обновляют токен при истечении
- Редиректят на login при 401

```typescript
import { authApi, queriesApi } from './services/api';

// Вход
await authApi.login('username', 'password');

// Получить запросы
const queries = await queriesApi.getAll();
```

## Deployment

### Development
```bash
npm run dev  # Frontend на :5173
# Django на :8000
```

### Production
```bash
npm run build  # Создаёт frontend/dist/
python manage.py runserver  # Django отдаёт React
```

Django автоматически serving React из `frontend/dist/`
