from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Пользовательская модель User с дополнительными полями
    """
    fio_name = models.CharField(max_length=150, blank=True, verbose_name='FIO')
    email = models.EmailField(max_length=50, unique=True, verbose_name='Email')
    first_login = models.BooleanField(default=True, verbose_name='First Login')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Project',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} - {self.fio_name}"