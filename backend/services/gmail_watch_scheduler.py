import logging
import os
from zoneinfo import ZoneInfo

import requests

# APScheduler 3.x — optional; only required when ENABLE_GMAIL_WATCH_SCHEDULER=true.
# Imported at module level so tests can patch these names via patch().
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    _APSCHEDULER_AVAILABLE = True
except ImportError:
    BackgroundScheduler = None  # type: ignore[assignment,misc]
    CronTrigger = None          # type: ignore[assignment,misc]
    _APSCHEDULER_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Module-level guard ───────────────────────────────────────────────────────
# Prevents duplicate scheduler initialisation across repeated imports or
# Flask's development reloader.
_scheduler_started: bool = False
_scheduler_instance = None  # holds the BackgroundScheduler reference


# ── Internal helpers ─────────────────────────────────────────────────────────

def _is_permanent_auth_failure(http_err: requests.exceptions.HTTPError) -> bool:
    """
    True only when Google has permanently revoked the refresh token
    (HTTP 400 with error=invalid_grant).

    Any other HTTP error (5xx, 429, etc.) is considered transient.
    """
    if http_err.response is None:
        return False
    if http_err.response.status_code != 400:
        return False
    try:
        return http_err.response.json().get("error") == "invalid_grant"
    except Exception:
        return False


def _run_renewal_job(app) -> None:
    """
    The actual Gmail watch renewal job that APScheduler calls.

    Runs inside a Flask application context so all helpers (db, encryption,
    gmail_service) work correctly.

    Reports: eligible users, succeeded, failed, reauth-required.
    """
    with app.app_context():
        from backend.database.db import get_users_for_watch_renewal, mark_gmail_needs_reauth
        from backend.services.gmail_service import refresh_access_token, watch_inbox
        from backend.utils.encryption import decrypt_data

        topic_name = app.config.get("GOOGLE_PUBSUB_TOPIC", "")
        if not topic_name:
            logger.error(
                "[GmailWatchScheduler] GOOGLE_PUBSUB_TOPIC is not configured — "
                "cannot renew Gmail watches. Set the environment variable."
            )
            return

        logger.info("[GmailWatchScheduler] Starting daily Gmail watch renewal run.")

        try:
            users = get_users_for_watch_renewal()
        except Exception:
            logger.exception(
                "[GmailWatchScheduler] Failed to fetch users from DB — aborting this run."
            )
            return

        if not users:
            logger.info("[GmailWatchScheduler] No eligible users — nothing to renew.")
            return

        total     = len(users)
        succeeded = 0
        failed    = 0
        reauth    = 0

        logger.info("[GmailWatchScheduler] Renewing Gmail watches for %d user(s).", total)

        for user in users:
            user_id      = user["id"]
            google_email = user.get("google_email", "<unknown>")
            encrypted_rt = user.get("google_refresh_token")

            if not encrypted_rt:
                logger.warning(
                    "[GmailWatchScheduler] User %s (%s): no refresh token in DB — skipping.",
                    user_id, google_email,
                )
                failed += 1
                continue

            try:
                # Step 1: Decrypt stored refresh token.
                refresh_token = decrypt_data(encrypted_rt)
                if not refresh_token:
                    logger.warning(
                        "[GmailWatchScheduler] User %s (%s): token decryption failed — skipping.",
                        user_id, google_email,
                    )
                    failed += 1
                    continue

                # Step 2: Exchange refresh token for a fresh access token.
                try:
                    token_data   = refresh_access_token(refresh_token)
                    access_token = token_data.get("access_token")
                    if not access_token:
                        raise ValueError("Google returned no access_token.")
                except requests.exceptions.HTTPError as http_err:
                    if _is_permanent_auth_failure(http_err):
                        logger.error(
                            "[GmailWatchScheduler] User %s (%s): token permanently revoked "
                            "(invalid_grant) — marking for reauth.",
                            user_id, google_email,
                        )
                        mark_gmail_needs_reauth(user_id)
                        reauth += 1
                    else:
                        logger.warning(
                            "[GmailWatchScheduler] User %s (%s): transient HTTP error "
                            "(status=%s) — skipping; token preserved.",
                            user_id, google_email,
                            http_err.response.status_code
                            if http_err.response is not None else "N/A",
                        )
                    failed += 1
                    continue
                except Exception:
                    logger.warning(
                        "[GmailWatchScheduler] User %s (%s): non-HTTP error obtaining "
                        "access token — skipping; token preserved.",
                        user_id, google_email, exc_info=True,
                    )
                    failed += 1
                    continue

                # Step 3: Register / renew the Gmail push-notification watch.
                try:
                    watch_result = watch_inbox(access_token, topic_name)
                    expiry_ms    = watch_result.get("expiration")
                    logger.info(
                        "[GmailWatchScheduler] User %s (%s): watch renewed successfully "
                        "(expiration_ms=%s).",
                        user_id, google_email, expiry_ms,
                    )
                    succeeded += 1
                except requests.exceptions.HTTPError as http_err:
                    # watch() failure is usually a transient quota / Pub/Sub issue.
                    # Never clear the refresh token for a watch() failure.
                    logger.warning(
                        "[GmailWatchScheduler] User %s (%s): Gmail watch() call failed "
                        "(status=%s) — will retry on next run; token preserved.",
                        user_id, google_email,
                        http_err.response.status_code
                        if http_err.response is not None else "N/A",
                    )
                    failed += 1
                except Exception:
                    logger.warning(
                        "[GmailWatchScheduler] User %s (%s): unexpected error renewing watch "
                        "— skipping; token preserved.",
                        user_id, google_email, exc_info=True,
                    )
                    failed += 1

            except Exception:
                # Catch-all so one user never stops processing the rest.
                logger.exception(
                    "[GmailWatchScheduler] User %s (%s): unhandled error — skipping.",
                    user_id, google_email,
                )
                failed += 1

        logger.info(
            "[GmailWatchScheduler] Renewal complete — "
            "total=%d  succeeded=%d  failed=%d  reauth_required=%d",
            total, succeeded, failed, reauth,
        )


# ── Public API ────────────────────────────────────────────────────────────────

def init_gmail_watch_scheduler(app) -> None:
    """
    Initialise and start the APScheduler BackgroundScheduler.

    Call once from create_app() — after all Flask extensions are bound.
    Does nothing if ENABLE_GMAIL_WATCH_SCHEDULER is not "true".

    The module-level _scheduler_started flag guarantees this function is
    idempotent even if called multiple times (Flask reloader, test setUp, etc.).
    """
    global _scheduler_started, _scheduler_instance

    # ── Guard 1: env-var gate ─────────────────────────────────────────────────
    enabled = os.environ.get("ENABLE_GMAIL_WATCH_SCHEDULER", "").strip().lower()
    if enabled != "true":
        logger.debug(
            "[GmailWatchScheduler] ENABLE_GMAIL_WATCH_SCHEDULER is not 'true' — "
            "scheduler not started (safe in dev / test / Celery workers)."
        )
        return

    # ── Guard 2: idempotency ──────────────────────────────────────────────────
    if _scheduler_started:
        logger.debug(
            "[GmailWatchScheduler] Scheduler already initialised — skipping duplicate init."
        )
        return

    if not _APSCHEDULER_AVAILABLE:
        logger.error(
            "[GmailWatchScheduler] APScheduler is not installed. "
            "Add 'APScheduler>=3.10,<4.0' to requirements.txt and redeploy."
        )
        return

    # ── Build scheduler ───────────────────────────────────────────────────────
    ist = ZoneInfo("Asia/Kolkata")
    scheduler = BackgroundScheduler(timezone=ist)

    # Daily at 03:00 IST (UTC+5:30 → 21:30 UTC previous day)
    trigger = CronTrigger(hour=3, minute=0, timezone=ist)

    scheduler.add_job(
        func=_run_renewal_job,
        trigger=trigger,
        args=[app],
        id="gmail_watch_daily_renewal",
        name="Daily Gmail Watch Renewal",
        replace_existing=True,       # safe re-registration on restart
        max_instances=1,             # no overlapping runs within this process
        coalesce=True,               # collapse missed triggers into one
        misfire_grace_time=3600,     # fire up to 1 hour late after restart
    )

    scheduler.start()
    _scheduler_started = True
    _scheduler_instance = scheduler

    logger.info(
        "[GmailWatchScheduler] Scheduler started. "
        "Daily Gmail watch renewal scheduled at 03:00 Asia/Kolkata."
    )

    # ── Clean shutdown on process exit ────────────────────────────────────────
    import atexit
    atexit.register(_shutdown_scheduler)


def _shutdown_scheduler() -> None:
    """Gracefully shuts down the scheduler on process exit."""
    global _scheduler_started, _scheduler_instance
    if _scheduler_instance is not None:
        try:
            _scheduler_instance.shutdown(wait=False)
            logger.info("[GmailWatchScheduler] Scheduler shut down cleanly.")
        except Exception:
            logger.exception("[GmailWatchScheduler] Error during scheduler shutdown.")
        finally:
            _scheduler_started = False
            _scheduler_instance = None
