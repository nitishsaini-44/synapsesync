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


@celery_app.task(bind=True, max_retries=5)
def send_discord_notification_task(
    self, user_id: int, payload: dict
) -> bool:
    """
    Deferred Celery task for Discord webhook notifications.

    Fetches the webhook URL fresh from the database on every attempt so that
    if the user updates their webhook URL between retries, the new URL is used.

    Scheduled with a countdown equal to Discord's retry_after value.
    Retries up to 5 times with exponential back-off on non-rate-limit failures.
    """
    from backend.database.db import get_user_by_id
    from backend.utils.encryption import decrypt_data
    from backend.services.discord_service import send_notification

    logger.info(
        "[Celery] Sending deferred Discord notification for user %s (attempt %d/5)",
        user_id, self.request.retries + 1,
    )

    # Always fetch the latest webhook URL from DB — handles webhook URL changes
    user = get_user_by_id(user_id)
    if not user:
        logger.warning("[Celery] User %s not found — aborting Discord notification.", user_id)
        return False

    encrypted_webhook = user.get("discord_webhook")
    if not encrypted_webhook:
        logger.warning("[Celery] User %s has no webhook set — aborting.", user_id)
        return False

    webhook_url = decrypt_data(encrypted_webhook)
    if not webhook_url:
        logger.warning("[Celery] Could not decrypt webhook for user %s — aborting.", user_id)
        return False

    success, retry_after = send_notification(webhook_url, payload)

    if success:
        logger.info("[Celery] Deferred Discord notification sent for user %s.", user_id)
        return True

    if retry_after > 0:
        # Still rate-limited — retry after Discord's specified window
        countdown = math.ceil(retry_after)
        logger.warning(
            "[Celery] Discord still rate-limiting user %s (%.0fs). Retrying in %ds.",
            user_id, retry_after, countdown,
        )
        raise self.retry(countdown=countdown)

    # Non-rate-limit failure — exponential back-off (60s, 120s, 240s, 480s, 960s)
    backoff = 60 * (2 ** self.request.retries)
    logger.warning(
        "[Celery] Discord notification failed for user %s. Retrying in %ds.", user_id, backoff
    )
    raise self.retry(countdown=backoff)
