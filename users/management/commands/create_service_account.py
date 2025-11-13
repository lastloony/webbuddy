"""
Management command для создания сервисного аккаунта
"""
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from users.models import User, UserRole


class Command(BaseCommand):
    help = 'Создать сервисный аккаунт с доступом ко всем проектам'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Имя пользователя для сервисного аккаунта'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email для сервисного аккаунта'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль (если не указан, будет сгенерирован автоматически)'
        )
        parser.add_argument(
            '--fio',
            type=str,
            default='',
            help='ФИО для сервисного аккаунта'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        fio_name = options.get('fio', f'Service Account: {username}')

        # Проверка существования пользователя
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Пользователь с username "{username}" уже существует!')
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Пользователь с email "{email}" уже существует!')
            )
            return

        # Генерация пароля, если не указан
        if not password:
            password = get_random_string(20)
            generated_password = True
        else:
            generated_password = False

        # Создание сервисного аккаунта
        try:
            service_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                fio_name=fio_name,
                role=UserRole.SERVICE,
                first_login=False,  # Для сервисного аккаунта не требуется смена пароля
                project=None  # Сервисные аккаунты не привязаны к проекту
            )

            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('Сервисный аккаунт успешно создан!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'Username: {service_user.username}')
            self.stdout.write(f'Email: {service_user.email}')
            self.stdout.write(f'Role: {service_user.role}')
            self.stdout.write(f'FIO: {service_user.fio_name}')
            
            if generated_password:
                self.stdout.write(self.style.WARNING(f'\nПароль (сохраните его!): {password}'))
            
            self.stdout.write(self.style.SUCCESS('\nВозможности сервисного аккаунта:'))
            self.stdout.write('  - Доступ ко всем проектам')
            self.stdout.write('  - Доступ ко всем запросам')
            self.stdout.write('  - Доступ ко всем логам')
            self.stdout.write('  - Возможность изменять любые проекты')
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании сервисного аккаунта: {str(e)}')
            )
