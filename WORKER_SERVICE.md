# Worker Service - Документация для разработчика

Этот документ описывает, как интегрировать внешний сервис обработки запросов с WebBuddy API.

## Архитектура

WebBuddy использует гибридную модель обработки запросов:

1. **Push модель**: Django пытается сразу уведомить FastAPI о новых запросах через HTTP
2. **Poll модель (fallback)**: Если FastAPI недоступен, запросы остаются в БД и обрабатываются через polling

## Что делает Django

Когда пользователь создает запрос:

1. Django сохраняет запрос в БД со статусом `queued`
2. Django **асинхронно** (в отдельном потоке) отправляет HTTP POST запрос на `/api/process-query`
3. Если FastAPI недоступен - запрос остается в БД

**Важно**: Django **НЕ ждет ответа** от FastAPI и сразу возвращает ответ пользователю.

## Что должен сделать Worker Service

### 1. Принимать push-уведомления от Django

**Endpoint**: `POST /api/process-query`

**Request body**:
```json
{
  "query_id": 123,
  "webbuddy_url": "http://localhost:8000"
}
```

**Response**:
```json
{
  "status": "accepted"
}
```

**Важно**: Не нужно пытаться обработать именно `query_id` из запроса! Просто вызовите `claim_next()` - он атомарно вернет следующий доступный запрос из очереди. Это защищает от race conditions, когда polling воркер мог уже взять этот запрос.

### 2. Реализовать polling механизм (fallback)

Периодически (каждые 30 секунд) вызывать `/api/queries/claim_next/` для получения пропущенных задач.

### 3. Обрабатывать запросы атомарно

Использовать endpoint `/api/queries/claim_next/` для атомарного получения запроса:

```bash
POST http://localhost:8000/api/queries/claim_next/
Authorization: Bearer {token}
```

**Response** (если есть запросы):
```json
{
  "id": 123,
  "project": 1,
  "user": 5,
  "query_text": "Протестировать авторизацию",
  "status": "in_progress",  // Автоматически изменен!
  "query_created": "2025-11-11T12:00:00Z",
  "query_started": "2025-11-11T12:00:05Z"
}
```

**Response** (если очередь пуста):
```json
{
  "detail": "No queued queries available"
}
```
Status: 404

## API Endpoints для Worker Service

### Аутентификация

```bash
POST /api/login/
Content-Type: application/json

{
  "username": "worker",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

### Атомарное получение запроса

```bash
POST /api/queries/claim_next/
Authorization: Bearer {access_token}
```

### Обновление статуса запроса

```bash
PATCH /api/queries/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "done",
  "answer_text": "Результат обработки",
  "query_finished": "2025-11-11T12:05:00Z"
}
```

### Создание логов

```bash
POST /api/logs/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "project": 1,
  "query": 123,
  "log_data": "Начинаем обработку..."
}
```

### Получение настроек проекта

**Для UI (с замаскированными токенами)**:
```bash
GET /api/projects/my_project/
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": 1,
  "project_name": "My Project",
  "test_it_token_masked": "**********abc123",
  "test_it_project_id": "TEST-PROJECT-ID",
  "jira_token_masked": "**********xyz789",
  "jira_project_id": "JIRA-PROJECT-ID",
  "project_context": "Description of the project...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Для Worker Service (с полными токенами)**:

Вариант 1 - Получить настройки текущего пользователя:
```bash
GET /api/projects/my_project_tokens/
Authorization: Bearer {access_token}
```

Вариант 2 - Получить настройки по ID проекта (рекомендуется):
```bash
GET /api/projects/{project_id}/tokens/
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": 1,
  "project_name": "My Project",
  "test_it_token": "full_testit_token_here",
  "test_it_project_id": "TEST-PROJECT-ID",
  "jira_token": "full_jira_token_here",
  "jira_project_id": "JIRA-PROJECT-ID",
  "project_context": "Description of the project...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Важно**:
- Используйте вариант 2 (`/projects/{project_id}/tokens/`) для Worker Service
- ID проекта берется из запроса через `claim_next()`
- Endpoint возвращает полные токены - храните их в памяти, не логируйте!
- Пользователь (Worker) должен быть привязан к проекту для доступа
- Для обычного UI используйте `/my_project/` с замаскированными токенами

## Статусы запросов

- `queued` - запрос создан, ждет обработки
- `in_progress` - запрос взят воркером (автоматически устанавливается через claim_next)
- `done` - запрос успешно обработан
- `failed` - ошибка при обработке

## Пример Python клиента

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
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()

        return {"Authorization": f"Bearer {self.access_token}"}

    def claim_next_query(self):
        """Атомарно взять следующий запрос из очереди"""
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

    def get_project_settings(self, project_id=None, with_tokens=False):
        """
        Получить настройки проекта

        Args:
            project_id: ID проекта (если None, берется проект текущего пользователя)
            with_tokens: Если True, возвращает полные токены (для Worker Service)
        """
        if project_id and with_tokens:
            # Получить конкретный проект с токенами (для Worker Service)
            endpoint = f'/projects/{project_id}/tokens/'
        elif with_tokens:
            # Получить свой проект с токенами
            endpoint = '/projects/my_project_tokens/'
        else:
            # Получить свой проект без токенов (для UI)
            endpoint = '/projects/my_project/'

        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
```

## Пример реализации Worker Service

### Минимальная реализация (только polling)

```python
import asyncio
from api_client import WebBuddyAPIClient

async def worker():
    client = WebBuddyAPIClient()
    client.login("worker", "password")

    while True:
        try:
            # Взять следующий запрос
            query = client.claim_next_query()

            if query:
                # Обработать
                result = process_query(query["query_text"])

                # Завершить
                client.update_query(
                    query["id"],
                    status="done",
                    answer_text=result,
                    query_finished=datetime.now().isoformat()
                )
            else:
                # Очередь пуста, ждем
                await asyncio.sleep(30)

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(worker())
```

### Полная реализация (push + polling)

```python
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
import asyncio

# Polling воркеры (fallback)
async def polling_worker(worker_id: int):
    client = WebBuddyAPIClient()
    client.login("worker", "password")

    while True:
        await asyncio.sleep(30)  # Каждые 30 секунд

        query = await asyncio.to_thread(client.claim_next_query)
        if query:
            await process_query(client, query)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем 5 polling воркеров
    tasks = []
    for i in range(5):
        task = asyncio.create_task(polling_worker(i))
        tasks.append(task)

    yield

    for task in tasks:
        task.cancel()

app = FastAPI(lifespan=lifespan)

# Push endpoint от Django
@app.post("/api/process-query")
async def process_query_endpoint(request: dict, background_tasks: BackgroundTasks):
    """
    Обработать запрос сразу (push).
    НЕ используем query_id - просто берем следующий доступный запрос.
    """
    background_tasks.add_task(process_next_query)

    return {"status": "accepted"}

async def process_next_query():
    """
    Обработать следующий доступный запрос.
    claim_next() автоматически вернет правильный запрос.
    """
    client = WebBuddyAPIClient()
    client.login("worker", "password")

    # Берем любой следующий запрос из очереди
    query = await asyncio.to_thread(client.claim_next_query)

    if query:
        await process_query(client, query)
```

## Масштабирование

### Несколько воркеров

Можно запустить несколько экземпляров Worker Service:

```bash
# Worker 1
uvicorn main:app --port 8001

# Worker 2
uvicorn main:app --port 8002

# Worker 3
uvicorn main:app --port 8003
```

Благодаря `claim_next()` каждый воркер получит уникальный запрос.

### Настройка количества воркеров

```bash
# Переменная окружения
export NUM_WORKERS=20

# Запуск с несколькими процессами
uvicorn main:app --workers 4
# 4 процесса × 5 внутренних воркеров = 20 воркеров
```

## Рекомендации

1. **Всегда используйте `claim_next()`** вместо ручного получения и обновления статуса
2. **Записывайте логи** на каждом этапе обработки через `create_log()`
3. **Обрабатывайте ошибки** и устанавливайте `status='failed'` при сбоях
4. **Используйте polling** как fallback на случай недоступности
5. **Не забывайте про токены** - они истекают через 24 часа

## Переменные окружения

```bash
# .env для Worker Service
WEBBUDDY_URL=http://localhost:8000
WORKER_USERNAME=worker
WORKER_PASSWORD=secure_password
NUM_WORKERS=5
POLLING_INTERVAL=30
```

## Использование настроек проекта

При обработке запроса Worker Service может получить настройки проекта для интеграции с TestIt и Jira:

```python
async def process_query(client: WebBuddyAPIClient, query: dict):
    """Обработать запрос с использованием настроек проекта"""
    try:
        # Получить ID проекта из запроса
        project_id = query["project"]

        # Получить настройки проекта с полными токенами по ID
        project_settings = client.get_project_settings(
            project_id=project_id,
            with_tokens=True
        )

        client.create_log(
            project_id,
            query["id"],
            f"Загружены настройки проекта: {project_settings['project_name']}"
        )

        # Получить полные токены и настройки из API
        testit_token = project_settings.get('test_it_token')
        testit_project_id = project_settings.get('test_it_project_id')
        jira_token = project_settings.get('jira_token')
        jira_project_id = project_settings.get('jira_project_id')
        project_context = project_settings.get('project_context', '')

        # Использовать токены для интеграции с TestIt
        if testit_token and testit_project_id:
            testit_client = TestItClient(token=testit_token, project_id=testit_project_id)
            # Работа с TestIt API

        # Использовать токены для интеграции с Jira
        if jira_token and jira_project_id:
            jira_client = JiraClient(token=jira_token, project_id=jira_project_id)
            # Работа с Jira API

        # Обработать запрос с использованием настроек
        result = await ai_process_query(
            query["query_text"],
            project_context=project_context,
            testit_client=testit_client if testit_token else None,
            jira_client=jira_client if jira_token else None
        )

        # Завершить успешно
        client.update_query(
            query["id"],
            status="done",
            answer_text=result,
            query_finished=datetime.now().isoformat()
        )

    except Exception as e:
        client.create_log(query["project"], query["id"], f"Ошибка: {str(e)}")
        client.update_query(
            query["id"],
            status="failed",
            answer_text=f"Ошибка: {str(e)}",
            query_finished=datetime.now().isoformat()
        )
```

**Как это работает**:
1. Worker Service получает запрос через `claim_next()`
2. Из запроса извлекается `project_id` (поле `"project"`)
3. Worker запрашивает настройки проекта: `get_project_settings(project_id=1, with_tokens=True)`
4. API проверяет, что Worker пользователь привязан к этому проекту
5. Worker получает полные токены TestIt и Jira для работы с внешними API

**Важно**:
- ID проекта берется из запроса, а не из настроек пользователя Worker
- Worker должен быть привязан к проекту для доступа к токенам
- Токены передаются через JWT, требуется аутентификация
- Не логируйте токены в открытом виде!

## Тестирование

```bash
# Получить настройки проекта
curl -X GET http://localhost:8000/api/projects/my_project/ \
  -H "Authorization: Bearer {token}"

# Создать тестовый запрос через API
curl -X POST http://localhost:8000/api/queries/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "query_text": "Тестовый запрос"
  }'

# Проверить очередь
curl -X POST http://localhost:8000/api/queries/claim_next/ \
  -H "Authorization: Bearer {token}"
```
