from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Query
from .utils import notify_fastapi_async
import threading
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Query)
def handle_query_created(sender, instance, created, **kwargs):
    """
    При создании запроса пытаемся уведомить FastAPI.

    Если FastAPI недоступен - запрос останется в БД со статусом 'queued'
    и будет обработан через polling механизм (claim_next endpoint).

    Уведомление отправляется в отдельном потоке, чтобы не блокировать
    ответ пользователю.
    """
    if created and instance.status == 'queued':
        logger.info(f"New query {instance.id} created, notifying FastAPI...")

        # Запускаем отправку в отдельном потоке
        # daemon=True означает, что поток завершится при завершении программы
        thread = threading.Thread(
            target=notify_fastapi_async,
            args=(instance.id,),
            daemon=True
        )
        thread.start()