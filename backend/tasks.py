"""
tasks.py
─────────
Celery task definitions.
"""
import logging
from backend.celery_worker import celery_app
from backend.services.automation_service import process_user_emails

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_email_task(self, user_id: int) -> bool:
    """
    Celery task that wraps process_user_emails with auto-retry logic.
    Retries up to 3 times (5-second countdown) on unhandled exceptions
    (e.g. Groq API timeouts, transient DB errors).
    """
    try:
        logger.info("[Celery] Starting email processing for user %s", user_id)
        return process_user_emails(user_id)
    except Exception as exc:
        logger.warning(
            "[Celery] Task failed for user %s, retrying... (%s)", user_id, exc
        )
        raise self.retry(exc=exc, countdown=5)
