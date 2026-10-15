from celery import Celery

from app.config import get_settings

celery_app = Celery("orbit", broker=get_settings().redis_url, include=["app.worker.tasks"])

celery_app.conf.update(
    # JSON only: pickle payloads can execute arbitrary code when deserialized.
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    # Acknowledge after the task finishes so a crashed worker's job is retried.
    # This means tasks must be safe to run more than once (idempotent).
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
