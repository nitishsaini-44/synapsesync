from backend.celery_worker import celery_app
from backend.services.automation_service import process_user_emails

@celery_app.task(bind=True, max_retries=3)
def process_email_task(self, user_id):
    """
    Celery task that acts as a robust wrapper around process_user_emails.
    It will automatically retry up to 3 times if it fails (e.g. Groq rate limit).
    """
    try:
        print(f"[Celery] Starting email processing for user {user_id}")
        success = process_user_emails(user_id)
        if not success:
            # We could trigger a retry here, but process_user_emails usually handles its own logical fails
            # We only really want to retry on unhandled exceptions (like API timeouts)
            pass
        return success
    except Exception as exc:
        print(f"[Celery] Task failed for user {user_id}, retrying... ({exc})")
        raise self.retry(exc=exc, countdown=5)
