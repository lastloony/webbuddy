"""
Management command для сброса пароля сервисного аккаунта
"""
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from users.models import User


class Command(BaseCommand):
    help = 'Сбросить пароль сервисного аккаунта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Имя пользователя сервисного аккаунта'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Новый пароль (если не указан, будет сгенерирован автоматически)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options.get('password')

        # Находим пользователя
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Пользователь "{username}" не найден!')
            )
            return

        # Генерация пароля, если не указан
        if not password:
            password = get_random_string(20)
            generated_password = True
        else:
            generated_password = False

        # Сброс пароля
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Пароль успешно сброшен!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Role: {user.role}')
        
        if generated_password:
            self.stdout.write(self.style.WARNING(f'\nНовый пароль (сохраните его!): {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'\nПароль успешно изменен на указанный'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
