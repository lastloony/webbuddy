# WebBuddy - AI-Powered Testing Platform

WebBuddy - это портал для автоматизированного тестирования с использованием AI-агентов, интегрированный с Jira и TestIt.

## Возможности

- Управление проектами тестирования
- Создание и отслеживание тестовых запросов
- Интеграция с Jira и TestIt
- **Страница настроек проекта** - управление токенами TestIt и Jira через веб-интерфейс
- REST API с JWT аутентификацией
- **Worker Service Integration** - атомарная обработка запросов через FastAPI
- Система временных паролей для новых пользователей
- Логирование использования AI-токенов
- Real-time обновление логов выполнения тестов
- Push/Poll модель обработки запросов

## Технологический стек

- **Backend**: Django 5.2, Django REST Framework
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL (SQLite для разработки)
- **Authentication**: JWT (SimpleJWT) с автообновлением токенов
- **API**: REST API с полной документацией

## Установка и запуск

### 1. Клонирование репозитория

```bash
cd webbuddy
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

Для разработки можно оставить SQLite (по умолчанию).

### 5. Применение миграций

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

Следуйте инструкциям для создания администратора.

### 7. Установка Frontend зависимостей

```bash
cd frontend
npm install
cd ..
```

### 8. Сборка и запуск

**Соберите frontend:**

```bash
cd frontend
npm run build
cd ..
```

**Запустите Django сервер:**

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## Структура проекта

```
webbuddy/
├── manage.py
├── requirements.txt       # Python зависимости
├── webbuddy/             # Главные настройки проекта
│   ├── settings.py
│   ├── urls.py
│   ├── views.py          # React app view
│   ├── middleware.py     # CSRF middleware для API
│   └── wsgi.py
├── users/                # Приложение пользователей
│   ├── models.py         # Кастомная модель User
│   ├── admin.py          # Админка с функцией сброса пароля
│   ├── views.py          # API views
│   └── serializers.py
├── projects/             # Приложение проектов
│   ├── models.py         # Модель Project
│   ├── admin.py
│   └── serializers.py
├── queries/              # Приложение запросов и логов
│   ├── models.py         # Query, QueryLog, TokenUsageLog
│   ├── views.py          # API viewsets
│   ├── serializers.py
│   └── urls.py           # API URLs
└── frontend/             # React приложение
    ├── src/
    │   ├── components/   # UI компоненты
    │   ├── pages/        # Страницы
    │   ├── services/     # API клиент
    │   ├── contexts/     # Auth context
    │   └── App.tsx       # Главный компонент
    ├── package.json
    └── vite.config.ts
```

## Использование

### Для администратора

1. Войдите в админ-панель: http://localhost:8000/admin/
2. Создайте проект (Project)
3. Создайте пользователей и привяжите их к проекту
4. При создании пользователя можно не указывать пароль - будет сгенерирован временный
5. Функция "Reset password to temporary" сбрасывает пароль пользователя

### Для пользователя

1. Войдите на портал: http://localhost:8000/
2. При первом входе система предложит сменить временный пароль
3. Перейдите в раздел **Настройки** для управления токенами проекта:
   - Настройте токены TestIt и ID проекта
   - Настройте токены Jira и ID проекта
   - Добавьте контекст проекта для AI-агента
4. Создавайте и отслеживайте запросы через веб-интерфейс

## API Documentation

### Аутентификация

**Получение JWT токенов:**

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ваш_username",
    "password": "ваш_пароль"
  }'
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "project": 1,
    "first_login": true
  },
  "first_login": true
}
```

**Время жизни токенов:**
- `access` токен - **24 часа**
- `refresh` токен - **7 дней**

**Обновление токена:**

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "ваш_refresh_token"
  }'
```

### API Endpoints

**Аутентификация**

| Endpoint | Метод | Авторизация | Описание |
|----------|-------|-------------|----------|
| `/api/login/` | POST | Нет | Получение JWT токенов |
| `/api/token/refresh/` | POST | Нет | Обновление access токена |
| `/api/users/me/` | GET | Да | Информация о текущем пользователе |
| `/api/users/change_password/` | POST | Да | Смена пароля |

**Запросы (Queries)**

```bash
# Список запросов
GET /api/queries/
Authorization: Bearer {token}

# Создание запроса
POST /api/queries/
Authorization: Bearer {token}
{
  "project": 1,
  "query_text": "Test description"
}

# Детали запроса
GET /api/queries/{id}/
Authorization: Bearer {token}

# Логи запроса
GET /api/queries/{id}/logs/
Authorization: Bearer {token}

# Фильтр по статусу
GET /api/queries/by_status/?status=queued
Authorization: Bearer {token}

# Атомарно взять следующий запрос из очереди (для воркеров)
POST /api/queries/claim_next/
Authorization: Bearer {token}
# Возвращает запрос и автоматически меняет его статус на "in_progress"
# Если очередь пуста, возвращает 404
```

**Логи**

```bash
# Создание лога (для внешнего сервиса)
POST /api/logs/
Authorization: Bearer {token}
{
  "project": 1,
  "query": 1,
  "log_data": "Log message"
}

# Список логов
GET /api/logs/
Authorization: Bearer {token}
```

**Статистика токенов**

```bash
# Создание записи использования токенов
POST /api/token-usage/
Authorization: Bearer {token}

# Статистика
GET /api/token-usage/statistics/
GET /api/token-usage/statistics/?query_id=1
Authorization: Bearer {token}
```

**Настройки проектов**

```bash
# Получить настройки своего проекта (с замаскированными токенами для UI)
GET /api/projects/my_project/
Authorization: Bearer {token}

# Получить настройки с полными токенами (для Worker Service)
GET /api/projects/my_project_tokens/
Authorization: Bearer {token}

# Получить настройки конкретного проекта с токенами (рекомендуется для Worker)
GET /api/projects/{project_id}/tokens/
Authorization: Bearer {token}

# Обновить настройки проекта
PATCH /api/projects/{id}/
Authorization: Bearer {token}
{
  "test_it_token": "new_token",
  "test_it_project_id": "PROJECT-ID",
  "jira_token": "new_token",
  "jira_project_id": "PROJECT-ID",
  "project_context": "Project description for AI"
}
```

## Worker Service Integration

Для интеграции с внешним Worker Service (FastAPI) см. подробную документацию:

**[WORKER_SERVICE.md](./WORKER_SERVICE.md)** - полная документация по интеграции с Worker Service

Основные возможности:
- Push/Poll модель обработки запросов
- Атомарное получение запросов через `claim_next()`
- Получение настроек проекта с полными токенами для интеграции с TestIt и Jira
- Примеры реализации на Python/FastAPI
- Рекомендации по масштабированию

## Интеграция с внешним сервисом (базовый пример)

Пример Python клиента для работы с API:

```python
import requests
from datetime import datetime, timedelta

class WebBuddyAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def login(self, username, password):
        """Вход и получение токенов"""
        response = requests.post(
            f"{self.base_url}/api/login/",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access"]
        self.refresh_token = data["refresh"]
        self.token_expires_at = datetime.now() + timedelta(hours=24)

        return data

    def refresh_access_token(self):
        """Обновление access токена"""
        response = requests.post(
            f"{self.base_url}/api/token/refresh/",
            json={"refresh": self.refresh_token}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access"]
        self.token_expires_at = datetime.now() + timedelta(hours=24)

        return data

    def get_headers(self):
        """Получить заголовки с автоматическим обновлением токена"""
        # Обновляем токен за 5 минут до истечения
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()

        return {"Authorization": f"Bearer {self.access_token}"}

    def get_queries(self, status=None):
        """Получить список запросов"""
        url = f"{self.base_url}/api/queries/"
        if status:
            url = f"{self.base_url}/api/queries/by_status/?status={status}"

        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()

    def create_query(self, project_id, query_text):
        """Создать новый запрос"""
        response = requests.post(
            f"{self.base_url}/api/queries/",
            json={"project": project_id, "query_text": query_text},
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def update_query(self, query_id, **fields):
        """Обновить запрос"""
        response = requests.patch(
            f"{self.base_url}/api/queries/{query_id}/",
            json=fields,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def claim_next_query(self):
        """
        Атомарно взять следующий запрос из очереди
        Возвращает запрос или None если очередь пуста
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/queries/claim_next/",
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None  # Очередь пуста
            raise

    def create_log(self, project_id, query_id, log_data):
        """Создать лог"""
        response = requests.post(
            f"{self.base_url}/api/logs/",
            json={
                "project": project_id,
                "query": query_id,
                "log_data": log_data
            },
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

# Использование для воркеров (рекомендуется)
client = WebBuddyAPIClient()
client.login("worker_username", "password")

while True:
    # Атомарно взять следующий запрос из очереди
    query = client.claim_next_query()

    if query:
        try:
            # Обрабатываем запрос
            client.create_log(query["project"], query["id"], "Начинаем обработку...")

            # Ваша логика обработки
            result = process_query(query["query_text"])

            # Завершаем успешно
            client.update_query(
                query["id"],
                status="done",
                answer_text=result,
                query_finished=datetime.now().isoformat()
            )
        except Exception as e:
            # При ошибке
            client.create_log(query["project"], query["id"], f"Ошибка: {str(e)}")
            client.update_query(
                query["id"],
                status="failed",
                answer_text=f"Ошибка: {str(e)}",
                query_finished=datetime.now().isoformat()
            )
    else:
        # Очередь пуста, ждем
        time.sleep(5)
```

## Настройка для production

1. Измените `DEBUG = False` в settings.py
2. Настройте PostgreSQL
3. Установите правильный `SECRET_KEY`
4. Настройте `ALLOWED_HOSTS`
5. Настройте CORS для фронтенда
6. Используйте gunicorn/uwsgi для запуска
7. Настройте nginx как reverse proxy
8. Настройте SSL сертификаты

## Безопасность

- Все API endpoints требуют аутентификации (кроме login)
- JWT токены с ограниченным сроком действия
- Пользователи видят только данные своего проекта
- **Токены TestIt и Jira**:
  - В UI отображаются замаскированными (последние 4 символа)
  - Полные токены доступны только через специальный endpoint для Worker Service
  - Worker должен быть привязан к проекту для доступа к токенам
- Временные пароли при первом входе
- CSRF защита отключена только для API endpoints (`/api/*`)

## Что нового

### Последний коммит (add settings page)

- ✅ Добавлена страница **Настройки проекта** (`/settings`)
- ✅ Управление токенами TestIt и Jira через веб-интерфейс
- ✅ Поле "Контекст проекта" для AI-агента
- ✅ Безопасное отображение токенов (маскирование)
- ✅ API endpoints для получения настроек проекта:
  - `/api/projects/my_project/` - с замаскированными токенами (для UI)
  - `/api/projects/{id}/tokens/` - с полными токенами (для Worker Service)
- ✅ Обновлена документация WORKER_SERVICE.md
