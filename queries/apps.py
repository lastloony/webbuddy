from django.apps import AppConfig


class QueriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'queries'

    def ready(self):
        """Регистрируем signals при запуске приложения"""
        import queries.signals
