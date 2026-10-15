from celery.utils.log import get_task_logger

from app.worker.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task
def ping() -> str:
    """Smoke-test task that confirms the worker is consuming jobs."""
    logger.info("pong")
    return "pong"
