# WebBuddy - AI-Powered Testing Platform

WebBuddy - это портал для автоматизированного тестирования с использованием AI-агентов, интегрированный с Jira и TestIt.

## Возможности

- Управление проектами тестирования
- Создание и отслеживание тестовых запросов
- Интеграция с Jira и TestIt
- REST API с JWT аутентификацией
- Система временных паролей для новых пользователей
- Логирование использования AI-токенов
- Real-time обновление логов выполнения тестов

## Технологический стек

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL (SQLite для разработки)
- **Authentication**: Django Auth + JWT (SimpleJWT)
- **Frontend**: Django Templates, Vanilla JavaScript

## Установка и запуск

### 1. Клонирование репозитория

```bash
cd webbuddy
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Установка зависимостей

Проект использует Poetry для управления зависимостями:

```bash
# Установка Poetry (если еще не установлен)
pip install poetry

# Установка зависимостей
poetry install
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

Для разработки можно оставить SQLite (по умолчанию).

### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

Следуйте инструкциям для создания администратора.

### 7. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## Структура проекта

```
webbuddy/
├── manage.py
├── webbuddy/              # Главные настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                 # Приложение пользователей
│   ├── models.py         # Кастомная модель User
│   ├── admin.py          # Админка с функцией сброса пароля
│   ├── views.py          # Вход, смена пароля
│   └── serializers.py
├── projects/              # Приложение проектов
│   ├── models.py         # Модель Project
│   ├── admin.py
│   └── serializers.py
├── queries/               # Приложение запросов и логов
│   ├── models.py         # Query, QueryLog, TokenUsageLog
│   ├── views.py          # Web views и API viewsets
│   ├── serializers.py
│   ├── urls.py           # API URLs
│   └── urls_web.py       # Web URLs
└── templates/             # HTML шаблоны
    ├── base.html
    ├── users/
    └── queries/
```

## Использование

### Для администратора

1. Войдите в админ-панель: http://127.0.0.1:8000/admin/
2. Создайте проект (Project)
3. Создайте пользователей и привяжите их к проекту
4. При создании пользователя можно не указывать пароль - будет сгенерирован временный
5. Функция "Reset password to temporary" сбрасывает пароль пользователя

### Для пользователя

1. Войдите на портал: http://127.0.0.1:8000/login/
2. При первом входе система предложит сменить временный пароль
3. Создайте запрос: http://127.0.0.1:8000/queries/create/
4. Просматривайте статус и логи: http://127.0.0.1:8000/queries/{id}/
5. История запросов: http://127.0.0.1:8000/queries/

### Работа с API

#### Алгоритм работы с API

**Шаг 1: Создание пользователя**

Администратор создаёт пользователя через админ-панель: http://127.0.0.1:8000/admin/users/user/add/

- Укажите username, email, fio_name и выберите проект
- Пароль можно не указывать - система сгенерирует временный автоматически

**Шаг 2: Получение JWT токенов**

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

**Шаг 3: Использование Access токена в запросах**

Все API запросы требуют заголовок авторизации:

```bash
curl -X GET http://localhost:8000/api/queries/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Формат заголовка:**
```
Authorization: Bearer {ваш_access_token}
```

**Шаг 4: Обновление токена**

Когда access токен истечёт (через 24 часа), используйте refresh токен:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "ваш_refresh_token"
  }'
```

**Ответ:**
```json
{
  "access": "новый_access_token"
}
```

**Шаг 5: Смена пароля (при первом входе)**

Если в ответе `/api/login/` пришло `"first_login": true`, необходимо сменить пароль:

```bash
curl -X POST http://localhost:8000/api/users/change_password/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "временный_пароль",
    "new_password": "новый_безопасный_пароль",
    "confirm_password": "новый_безопасный_пароль"
  }'
```

#### Пример класса для автоматического управления токенами (Python)

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

        print(f"Успешный вход. First login: {data['first_login']}")
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

        print("Токен успешно обновлён")
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

# Использование
client = WebBuddyAPIClient()
client.login("username", "password")

# Создать запрос
query = client.create_query(project_id=1, query_text="Протестировать функцию авторизации")

# Обновить статус
client.update_query(query["id"], status="in_progress")

# Добавить лог
client.create_log(project_id=1, query_id=query["id"], log_data="Начинаем обработку...")

# Получить все запросы в очереди
queued = client.get_queries(status="queued")
```

#### API Endpoints

**Аутентификация**

| Endpoint | Метод | Авторизация | Описание |
|----------|-------|-------------|----------|
| `/api/login/` | POST | Нет | Получение JWT токенов |
| `/api/token/refresh/` | POST | Нет | Обновление access токена |
| `/api/users/me/` | GET | Да | Информация о текущем пользователе |
| `/api/users/change_password/` | POST | Да | Смена пароля |

#### Запросы (Queries)

```bash
# Список запросов
GET /api/queries/

# Создание запроса
POST /api/queries/
{
  "project": 1,
  "query_text": "Test description"
}

# Детали запроса
GET /api/queries/{id}/

# Логи запроса
GET /api/queries/{id}/logs/

# Фильтр по статусу
GET /api/queries/by_status/?status=queued
```

#### Логи

```bash
# Создание лога (для внешнего сервиса)
POST /api/logs/
{
  "project": 1,
  "query": 1,
  "log_data": "Log message"
}

# Список логов
GET /api/logs/
```

#### Статистика токенов

```bash
# Создание записи использования токенов
POST /api/token-usage/

# Статистика
GET /api/token-usage/statistics/
GET /api/token-usage/statistics/?query_id=1
```

## Интеграция с внешним сервисом обработки

Внешний сервис должен:

1. Периодически опрашивать `/api/queries/by_status/?status=queued`
2. Взять запрос и обновить статус на `in_progress`
3. Записывать логи через `/api/logs/`
4. После завершения:
   - Обновить `answer_text`
   - Изменить статус на `done` или `failed`
   - Проставить `query_finished`

Пример кода для внешнего сервиса:

```python
import requests

API_URL = "http://localhost:8000/api"
TOKEN = "your-jwt-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Получить очередные запросы
response = requests.get(
    f"{API_URL}/queries/by_status/?status=queued",
    headers=HEADERS
)
queries = response.json()

for query in queries:
    # Обновить статус
    requests.patch(
        f"{API_URL}/queries/{query['id']}/",
        json={"status": "in_progress"},
        headers=HEADERS
    )

    # Создать лог
    requests.post(
        f"{API_URL}/logs/",
        json={
            "project": query['project'],
            "query": query['id'],
            "log_data": "Starting processing..."
        },
        headers=HEADERS
    )

    # ... обработка запроса ...

    # Завершить
    requests.patch(
        f"{API_URL}/queries/{query['id']}/",
        json={
            "status": "done",
            "answer_text": "Test completed successfully",
            "query_finished": datetime.now().isoformat()
        },
        headers=HEADERS
    )
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
- Временные пароли при первом входе
- CSRF защита для web форм

## Лицензия

MIT License

## Автор

Vladimir Lamkin (lastloony@gmail.com)