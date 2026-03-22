from celery import Celery

from config.env_settings import get_settings


settings = get_settings()


celery_app = Celery(
    "doc_chat_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.autodiscover_tasks(["api.tasks"])
