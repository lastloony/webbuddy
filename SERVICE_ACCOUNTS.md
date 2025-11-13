# Сервисные аккаунты в WebBuddy

## Описание

Сервисные аккаунты - это специальные пользователи с расширенными правами доступа, предназначенные для автоматизации и интеграции с внешними системами.

## Возможности сервисного аккаунта

Сервисные аккаунты имеют следующие привилегии:

- ✅ **Доступ ко всем проектам** - могут просматривать и редактировать любые проекты
- ✅ **Доступ ко всем запросам** - видят запросы всех проектов через API
- ✅ **Доступ ко всем логам** - имеют доступ к QueryLog и TokenUsageLog всех проектов
- ✅ **Не привязаны к проекту** - поле `project` может быть NULL
- ✅ **Обход ограничений** - методы `has_cross_project_access()` возвращают True

## Создание сервисного аккаунта

### Способ 1: Management Command (рекомендуется)

```bash
# С автогенерацией пароля
python manage.py create_service_account --username service_api --email service@example.com

# С указанием пароля
python manage.py create_service_account --username service_api --email service@example.com --password "your_secure_password"

# С дополнительными параметрами
python manage.py create_service_account --username service_api --email service@example.com --fio "API Service Account"
```

**Пример вывода:**
```
============================================================
Сервисный аккаунт успешно создан!
============================================================
Username: service_api
Email: service@example.com
Role: service
FIO: Service Account: service_api

Пароль (сохраните его!): xK9mP2nQ5rT8wV1zY4cB

Возможности сервисного аккаунта:
  - Доступ ко всем проектам
  - Доступ ко всем запросам
  - Доступ ко всем логам
  - Возможность изменять любые проекты

============================================================
```

### Способ 2: Django Shell

```python
python manage.py shell

from users.models import User, UserRole

# Создание сервисного аккаунта
service_user = User.objects.create_user(
    username='service_api',
    email='service@example.com',
    password='your_secure_password',
    role=UserRole.SERVICE,
    fio_name='API Service Account',
    first_login=False,  # Для сервисного аккаунта не требуется смена пароля
    project=None  # Сервисные аккаунты не привязаны к проекту
)

print(f"Создан: {service_user.username}")
print(f"Сервисный: {service_user.is_service_account()}")
print(f"Cross-project доступ: {service_user.has_cross_project_access()}")
```

### Способ 3: Django Admin

1. Откройте Django Admin `/admin/users/user/add/`
2. Заполните поля:
   - **Username**: `service_api`
   - **Email**: `service@example.com`
   - **Role**: выберите **Service** из выпадающего списка
   - **Project**: оставьте пустым (не обязательно для сервисных аккаунтов)
   - Задайте пароль
3. Нажмите "Save"

## Использование сервисного аккаунта

### Базовый пример

```python
import requests

# 1. Аутентификация
response = requests.post('http://localhost:8000/api/login/', json={
    'username': 'service_api',
    'password': 'your_password'
})

data = response.json()
access_token = data['access']
refresh_token = data['refresh']

# 2. Использование токена
headers = {'Authorization': f'Bearer {access_token}'}

# Получение всех проектов (доступно только сервисным аккаунтам!)
projects = requests.get('http://localhost:8000/api/projects/', headers=headers).json()

# Получение всех запросов
queries = requests.get('http://localhost:8000/api/queries/', headers=headers).json()

# Получение логов
query_logs = requests.get('http://localhost:8000/api/query-logs/', headers=headers).json()
token_logs = requests.get('http://localhost:8000/api/token-usage-logs/', headers=headers).json()
```

### Расширенный клиент с автообновлением токена

```python
import requests
from datetime import datetime, timedelta

class ServiceAccountClient:
    """
    Клиент для работы с API через сервисный аккаунт
    """
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.login()

    def login(self):
        """Вход и получение токенов"""
        response = requests.post(
            f"{self.base_url}/api/login/",
            json={"username": self.username, "password": self.password}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access"]
        self.refresh_token = data["refresh"]
        # JWT токены обычно живут 24 часа
        self.token_expires_at = datetime.now() + timedelta(hours=24)

    def refresh_access_token(self):
        """Обновление access токена через refresh токен"""
        response = requests.post(
            f"{self.base_url}/api/token/refresh/",
            json={"refresh": self.refresh_token}
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access"]
        self.token_expires_at = datetime.now() + timedelta(hours=24)

    def get_headers(self):
        """Получить заголовки с автоматическим обновлением токена"""
        # Обновляем токен за 5 минут до истечения
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()

        return {"Authorization": f"Bearer {self.access_token}"}

    def get_all_projects(self):
        """Получить все проекты (доступно только сервисным аккаунтам)"""
        response = requests.get(
            f"{self.base_url}/api/projects/",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_all_queries(self, filters=None):
        """Получить все запросы всех проектов"""
        params = filters or {}
        response = requests.get(
            f"{self.base_url}/api/queries/",
            headers=self.get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_query_logs(self, filters=None):
        """Получить логи всех запросов"""
        params = filters or {}
        response = requests.get(
            f"{self.base_url}/api/query-logs/",
            headers=self.get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_token_usage_logs(self, filters=None):
        """Получить логи использования токенов"""
        params = filters or {}
        response = requests.get(
            f"{self.base_url}/api/token-usage-logs/",
            headers=self.get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id, data):
        """Обновить проект (доступно только сервисным аккаунтам)"""
        response = requests.patch(
            f"{self.base_url}/api/projects/{project_id}/",
            headers=self.get_headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()

# Использование
client = ServiceAccountClient(
    base_url='http://localhost:8000',
    username='service_api',
    password='your_password'
)

# Получаем данные
all_projects = client.get_all_projects()
all_queries = client.get_all_queries()

# Фильтрация
recent_logs = client.get_query_logs({
    'created_at__gte': '2025-11-01'
})

# Обновление проекта
updated = client.update_project(1, {'name': 'Updated Project Name'})
```

### Пример интеграции с мониторингом

```python
from service_account_client import ServiceAccountClient
import time

client = ServiceAccountClient(
    base_url='http://localhost:8000',
    username='monitor_service',
    password='secure_password'
)

def monitor_projects():
    """Мониторинг активности проектов"""
    projects = client.get_all_projects()

    for project in projects:
        # Получаем запросы проекта за последние 24 часа
        queries = client.get_all_queries({
            'project': project['id'],
            'created_at__gte': (datetime.now() - timedelta(days=1)).isoformat()
        })

        print(f"Проект: {project['name']}")
        print(f"  Запросов за 24ч: {len(queries)}")

        if len(queries) == 0:
            print(f"  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Нет активности!")

        # Получаем использование токенов
        token_logs = client.get_token_usage_logs({
            'project': project['id']
        })

        total_tokens = sum(log['tokens_used'] for log in token_logs)
        print(f"  Всего токенов использовано: {total_tokens}")

# Запускаем мониторинг каждые 5 минут
while True:
    monitor_projects()
    time.sleep(300)
```

## Роли пользователей

В системе реализовано 3 типа ролей:

| Роль | Код | Описание | Доступ к проектам | Особенности |
|------|-----|----------|-------------------|-------------|
| `user` | `UserRole.USER` | Обычный пользователь | Только свой проект | Привязан к одному проекту |
| `admin` | `UserRole.ADMIN` | Администратор | Все проекты | Cross-project доступ |
| `service` | `UserRole.SERVICE` | Сервисный аккаунт | Все проекты | Автоматизация, не требует `first_login` |

### Роли определены в `users/models.py:5-11`:

```python
class UserRole(models.TextChoices):
    USER = 'user', 'User'
    ADMIN = 'admin', 'Admin'
    SERVICE = 'service', 'Service'
```

## Методы модели User

### `is_service_account()`

**Файл**: `users/models.py:36-38`

Проверяет, является ли пользователь сервисным аккаунтом.

```python
def is_service_account(self):
    """Проверка, является ли пользователь сервисным аккаунтом"""
    return self.role == UserRole.SERVICE or self.is_superuser
```

**Возвращает**: `True` если пользователь имеет роль `SERVICE` или является `superuser`

### `has_cross_project_access()`

**Файл**: `users/models.py:40-42`

Проверяет, имеет ли пользователь доступ ко всем проектам.

```python
def has_cross_project_access(self):
    """Проверка, имеет ли пользователь доступ ко всем проектам"""
    return self.role in [UserRole.ADMIN, UserRole.SERVICE] or self.is_superuser
```

**Возвращает**: `True` если пользователь является `ADMIN`, `SERVICE` или `superuser`

## Как это работает в коде

### ProjectViewSet (`projects/views.py:15-23`)

```python
def get_queryset(self):
    """
    Пользователи могут видеть только свой проект
    Сервисные аккаунты и администраторы видят все проекты
    """
    user = self.request.user
    if user.has_cross_project_access():
        return Project.objects.all()
    return Project.objects.filter(id=user.project_id)
```

### QueryViewSet (`queries/views.py:33-40`)

```python
def get_queryset(self):
    """
    Фильтрация запросов по проекту пользователя
    Сервисные аккаунты и администраторы видят все запросы
    """
    user = self.request.user
    if user.has_cross_project_access():
        return Query.objects.all()
    return Query.objects.filter(project=user.project)
```

## Custom Permissions

В `users/permissions.py` доступны готовые классы для использования в ViewSet:

### `IsServiceAccount`

Разрешает доступ только сервисным аккаунтам:

```python
from users.permissions import IsServiceAccount

class SecretViewSet(viewsets.ModelViewSet):
    permission_classes = [IsServiceAccount]
    # Только сервисные аккаунты могут обращаться к этому ViewSet
```

### `IsServiceAccountOrReadOnly`

Запись только для сервисных аккаунтов, чтение для всех:

```python
from users.permissions import IsServiceAccountOrReadOnly

class ConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [IsServiceAccountOrReadOnly]
    # GET доступен всем, POST/PUT/PATCH/DELETE только сервисным аккаунтам
```

### `HasCrossProjectAccess`

Доступ для пользователей с cross-project правами (admin, service, superuser):

```python
from users.permissions import HasCrossProjectAccess

class AllProjectsViewSet(viewsets.ModelViewSet):
    permission_classes = [HasCrossProjectAccess]
    # Доступ только для admin, service и superuser
```

## Безопасность

### Рекомендации по безопасности

1. **Используйте сложные пароли**
   - Минимум 20 символов
   - Используйте автогенерацию при создании через management command
   - Комбинация букв, цифр и спецсимволов

2. **Храните пароли безопасно**
   - Используйте менеджеры паролей (1Password, LastPass, Bitwarden)
   - Никогда не коммитьте пароли в git
   - Используйте переменные окружения для хранения credentials

3. **Ротация паролей**
   - Меняйте пароли каждые 90 дней
   - При подозрении на компрометацию - немедленно меняйте

4. **Логирование действий**
   - Отслеживайте все действия сервисных аккаунтов
   - Настройте алерты на подозрительную активность

5. **Принцип минимальных привилегий**
   - Создавайте сервисные аккаунты только когда действительно нужен cross-project доступ
   - Для обычных задач используйте роль `user`

### Пример Middleware для аудита

```python
# middleware.py
import logging

logger = logging.getLogger(__name__)

class ServiceAccountAuditMiddleware:
    """Логирование всех действий сервисных аккаунтов"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_service_account():
            logger.info(
                f"Service account access: "
                f"user={request.user.username} "
                f"method={request.method} "
                f"path={request.path} "
                f"ip={request.META.get('REMOTE_ADDR')}"
            )

        response = self.get_response(request)
        return response
```

### Использование переменных окружения

```python
# .env (НЕ КОММИТИТЬ!)
SERVICE_ACCOUNT_USERNAME=service_api
SERVICE_ACCOUNT_PASSWORD=xK9mP2nQ5rT8wV1zY4cB

# your_script.py
import os
from dotenv import load_dotenv

load_dotenv()

client = ServiceAccountClient(
    base_url='http://localhost:8000',
    username=os.getenv('SERVICE_ACCOUNT_USERNAME'),
    password=os.getenv('SERVICE_ACCOUNT_PASSWORD')
)
```

## Миграция существующих пользователей

Если нужно преобразовать существующего пользователя в сервисный аккаунт:

```python
python manage.py shell

from users.models import User, UserRole

# Находим пользователя
user = User.objects.get(username='existing_user')

# Меняем роль на сервисную
user.role = UserRole.SERVICE
user.project = None  # Убираем привязку к проекту
user.first_login = False  # Сервисным аккаунтам не нужна смена пароля
user.save()

print(f"Пользователь {user.username} теперь сервисный аккаунт")
print(f"Cross-project доступ: {user.has_cross_project_access()}")
```

## Troubleshooting

### Проблема: Сервисный аккаунт не видит все проекты

**Решение:**
1. Проверьте роль пользователя:
   ```python
   user = User.objects.get(username='service_api')
   print(f"Role: {user.role}")
   print(f"Has cross-project: {user.has_cross_project_access()}")
   ```

2. Убедитесь, что применены все миграции:
   ```bash
   python manage.py migrate
   ```

3. Проверьте, что токен актуален и принадлежит правильному пользователю

### Проблема: Command not found

**Решение:** Убедитесь, что созданы все необходимые файлы:
```
users/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── create_service_account.py
```

### Проблема: 403 Forbidden при доступе к ресурсам

**Возможные причины:**
1. Пользователь не имеет роль `SERVICE`
2. Токен истек - обновите через `/api/token/refresh/`
3. В ViewSet не учтен `has_cross_project_access()`

## Примеры использования

### 1. Автоматический сбор статистики

```python
from service_account_client import ServiceAccountClient
import pandas as pd
from datetime import datetime, timedelta

client = ServiceAccountClient(
    base_url='http://localhost:8000',
    username='stats_service',
    password=os.getenv('SERVICE_PASSWORD')
)

# Собираем статистику по всем проектам
projects = client.get_all_projects()
token_logs = client.get_token_usage_logs()

# Создаем DataFrame для анализа
df = pd.DataFrame(token_logs)
df['created_at'] = pd.to_datetime(df['created_at'])

# Группируем по проектам
stats = df.groupby('project_id').agg({
    'tokens_used': 'sum',
    'id': 'count'
}).rename(columns={'id': 'requests_count'})

print("Статистика использования по проектам:")
print(stats)
```

### 2. Автоматическая очистка старых логов

```python
from service_account_client import ServiceAccountClient
from datetime import datetime, timedelta

client = ServiceAccountClient(
    base_url='http://localhost:8000',
    username='cleanup_service',
    password=os.getenv('SERVICE_PASSWORD')
)

# Удаляем логи старше 90 дней
cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()

old_logs = client.get_query_logs({
    'created_at__lt': cutoff_date
})

print(f"Найдено старых логов: {len(old_logs)}")
# Здесь код для удаления...
```

### 3. Синхронизация данных между системами

```python
from service_account_client import ServiceAccountClient
import requests

# WebBuddy client
webbuddy = ServiceAccountClient(
    base_url='http://localhost:8000',
    username='sync_service',
    password=os.getenv('WEBBUDDY_SERVICE_PASSWORD')
)

# Получаем все запросы
queries = webbuddy.get_all_queries()

# Отправляем в систему аналитики
for query in queries:
    requests.post(
        'http://127.0.0.1:8000/api/queries',
        json=query,
        headers={'Authorization': f'Bearer {ANALYTICS_TOKEN}'}
    )

print(f"Синхронизировано {len(queries)} запросов")
```

## См. также

- [WORKER_SERVICE.md](./WORKER_SERVICE.md) - Документация по работе с Worker Service
- Django Admin: `/admin/users/user/`
- Исходный код: `users/models.py`, `users/permissions.py`

## Дополнительная информация

### Структура файлов

```
users/
├── models.py                      # UserRole, User с методами is_service_account()
├── permissions.py                 # Custom permission классы
├── admin.py                       # Django Admin конфигурация
├── management/
│   └── commands/
│       └── create_service_account.py  # Management command
└── migrations/
    └── 0002_user_role.py         # Миграция добавления поля role
```

### API Endpoints с cross-project доступом

Следующие endpoints доступны сервисным аккаунтам со всеми данными:

- `GET /api/projects/` - все проекты
- `GET /api/queries/` - все запросы
- `GET /api/query-logs/` - все логи запросов
- `GET /api/token-usage-logs/` - все логи использования токенов
- `PATCH /api/projects/{id}/` - обновление любого проекта
- `PUT /api/projects/{id}/` - полное обновление любого проекта

