from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """
    Роли пользователей в системе
    """
    USER = 'user', 'User'
    ADMIN = 'admin', 'Admin'
    SERVICE = 'service', 'Service'


class User(AbstractUser):
    """
    Пользовательская модель User с дополнительными полями
    """
    fio_name = models.CharField(max_length=150, blank=True, verbose_name='FIO')
    email = models.EmailField(max_length=50, unique=True, verbose_name='Email')
    first_login = models.BooleanField(default=True, verbose_name='First Login')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Role'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Project',
        null=True,
        blank=True
    )

    def is_service_account(self):
        """Проверка, является ли пользователь сервисным аккаунтом"""
        return self.role == UserRole.SERVICE or self.is_superuser

    def has_cross_project_access(self):
        """Проверка, имеет ли пользователь доступ ко всем проектам"""
        return self.role in [UserRole.ADMIN, UserRole.SERVICE] or self.is_superuser

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} - {self.fio_name}"