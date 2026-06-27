"""
tasks.py
─────────
Celery task definitions.
"""
import logging
import math
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


@celery_app.task(bind=True, max_retries=5, default_retry_delay=60)
def send_discord_notification_task(
    self, webhook_url: str, payload: dict, retry_after: float = 0
) -> bool:
    """
    Deferred Celery task for Discord webhook notifications.

    Used when send_notification() returns a retry_after value that is too
    large to wait inline (e.g. a global rate limit of several hours).
    The task is scheduled with a countdown equal to retry_after, so Discord
    will be ready to accept the request by the time we try again.

    Retries up to 5 times with exponential back-off on top of any Discord
    rate-limit delay.
    """
    from backend.services.discord_service import send_notification

    logger.info(
        "[Celery] Sending deferred Discord notification (attempt %d/5, retry_after=%.0fs)",
        self.request.retries + 1,
        retry_after,
    )

    success, new_retry_after = send_notification(webhook_url, payload)

    if success:
        logger.info("[Celery] Deferred Discord notification sent successfully.")
        return True

    if new_retry_after > 0:
        # Still rate-limited — schedule another retry respecting the new window
        countdown = math.ceil(new_retry_after)
        logger.warning(
            "[Celery] Discord still rate-limited. Retrying in %ds.", countdown
        )
        raise self.retry(countdown=countdown)

    # Non-rate-limit failure — use exponential back-off (60s, 120s, 240s …)
    backoff = 60 * (2 ** self.request.retries)
    logger.warning(
        "[Celery] Discord notification failed. Retrying in %ds.", backoff
    )
    raise self.retry(countdown=backoff)
