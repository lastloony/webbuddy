import threading
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def notify_fastapi_async(query_id):
    """
    Отправить уведомление в FastAPI в отдельном потоке.
    Не блокирует основной запрос.

    Args:
        query_id: ID созданного запроса
    """
    try:
        response = requests.post(
            f"{settings.FASTAPI_URL}/api/process-query",
            json={
                "query_id": query_id,
                "webbuddy_url": settings.WEBBUDDY_URL
            },
            timeout=2  # Короткий таймаут - не ждем долго
        )

        if response.status_code == 200:
            logger.info(f"Successfully notified FastAPI about query {query_id}")
        else:
            logger.warning(
                f"FastAPI returned {response.status_code} for query {query_id}. "
                f"Query will be picked up by polling."
            )

    except requests.exceptions.Timeout:
        logger.warning(
            f"FastAPI timeout for query {query_id}. "
            f"Query will be picked up by polling."
        )
    except requests.exceptions.ConnectionError:
        logger.warning(
            f"FastAPI unavailable for query {query_id}. "
            f"Query will be picked up by polling."
        )
    except Exception as e:
        logger.error(f"Error notifying FastAPI about query {query_id}: {e}")