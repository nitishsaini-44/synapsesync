"""
backend/renew_gmail_watches.py
──────────────────────────────
Daily Gmail watch-subscription renewal job.

Run via Render Cron Job (or any scheduler) with:

    python -m backend.renew_gmail_watches

Required environment variables (same as the web service):
    SECRET_KEY            Flask secret key
    FERNET_KEY            Base64-encoded 32-byte Fernet encryption key
    POSTGRES_HOST         PostgreSQL host
    POSTGRES_PORT         PostgreSQL port (default: 5432)
    POSTGRES_DB           PostgreSQL database name
    POSTGRES_USER         PostgreSQL user
    POSTGRES_PASSWORD     PostgreSQL password
    POSTGRES_SSLMODE      PostgreSQL SSL mode (default: require)
    GOOGLE_CLIENT_ID      Google OAuth 2.0 Client ID
    GOOGLE_CLIENT_SECRET  Google OAuth 2.0 Client Secret
    GOOGLE_REDIRECT_URI   Must match the one registered in Google Cloud Console
    GOOGLE_PUBSUB_TOPIC   Full Pub/Sub topic name (projects/<proj>/topics/<name>)

Optional (not used by this job, but loaded by Config without error):
    REDIS_URL, GROQ_API_KEY, FRONTEND_URL

Design notes:
- Runs independently of the Gunicorn web process — no scheduler inside the app.
- Each user is processed inside a Flask app context so db/encryption helpers work.
- One user's failure never prevents other users from being renewed.
- Permanent auth failures (invalid_grant) disable automation and clear the token
  so the frontend shows a reconnect prompt.
- Transient failures are logged and skipped; the stored token is never cleared.
- The watch() expiration timestamp returned by Google is logged for observability.
- Safe to re-run at any time — Gmail's watch() API is idempotent.
"""
import logging
import sys

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("renew_gmail_watches")


def _is_permanent_auth_failure(http_err: requests.exceptions.HTTPError) -> bool:
    """True when Google has permanently revoked the refresh token (invalid_grant)."""
    if http_err.response is None:
        return False
    if http_err.response.status_code != 400:
        return False
    try:
        return http_err.response.json().get("error") == "invalid_grant"
    except Exception:
        return False


def renew_watches() -> None:
    """
    Renews Gmail push-notification watch subscriptions for every active user.
    Exits with code 1 if no users could be processed (indicates a systemic
    configuration error); exits with code 0 even if individual users failed.
    """
    # Import Flask app here so config/db are initialised correctly.
    from backend.app import create_app
    from backend.database.db import get_users_for_watch_renewal, mark_gmail_needs_reauth
    from backend.services.gmail_service import refresh_access_token, watch_inbox
    from backend.utils.encryption import decrypt_data

    app = create_app()

    topic_name = app.config.get("GOOGLE_PUBSUB_TOPIC")
    if not topic_name:
        logger.error(
            "GOOGLE_PUBSUB_TOPIC is not configured — cannot renew Gmail watches. "
            "Set the environment variable and retry."
        )
        sys.exit(1)

    with app.app_context():
        try:
            users = get_users_for_watch_renewal()
        except Exception:
            logger.exception("Failed to fetch users for watch renewal — aborting.")
            sys.exit(1)

        if not users:
            logger.info("No active users with Gmail connected — nothing to renew.")
            return

        logger.info("Starting Gmail watch renewal for %d user(s).", len(users))

        succeeded = 0
        failed    = 0

        for user in users:
            user_id      = user["id"]
            google_email = user.get("google_email", "<unknown>")
            encrypted_rt = user.get("google_refresh_token")

            if not encrypted_rt:
                logger.warning(
                    "User %s (%s): no refresh token in DB row — skipping.",
                    user_id, google_email,
                )
                failed += 1
                continue

            try:
                # 1. Decrypt the stored refresh token.
                refresh_token = decrypt_data(encrypted_rt)
                if not refresh_token:
                    logger.warning(
                        "User %s (%s): failed to decrypt refresh token — skipping.",
                        user_id, google_email,
                    )
                    failed += 1
                    continue

                # 2. Exchange refresh token for a fresh access token.
                try:
                    token_data   = refresh_access_token(refresh_token)
                    access_token = token_data.get("access_token")
                    if not access_token:
                        raise ValueError("Google returned no access_token.")
                except requests.exceptions.HTTPError as http_err:
                    if _is_permanent_auth_failure(http_err):
                        logger.error(
                            "User %s (%s): refresh token permanently revoked "
                            "(invalid_grant) — disabling automation.",
                            user_id, google_email,
                        )
                        mark_gmail_needs_reauth(user_id)
                    else:
                        logger.warning(
                            "User %s (%s): transient HTTP error from Google "
                            "(status=%s) — skipping; token preserved.",
                            user_id, google_email,
                            http_err.response.status_code
                            if http_err.response is not None else "N/A",
                        )
                    failed += 1
                    continue
                except Exception:
                    logger.warning(
                        "User %s (%s): non-HTTP error obtaining access token — "
                        "skipping; token preserved.",
                        user_id, google_email, exc_info=True,
                    )
                    failed += 1
                    continue

                # 3. Renew the Gmail push-notification watch.
                try:
                    watch_result = watch_inbox(access_token, topic_name)
                    expiry_ms    = watch_result.get("expiration")
                    logger.info(
                        "User %s (%s): Gmail watch renewed successfully "
                        "(expiration_ms=%s).",
                        user_id, google_email, expiry_ms,
                    )
                    succeeded += 1
                except requests.exceptions.HTTPError as http_err:
                    # watch() failure is usually transient (quota, topic missing).
                    # Do NOT clear the refresh token — just skip and retry tomorrow.
                    logger.warning(
                        "User %s (%s): Gmail watch() call failed (status=%s) — "
                        "will retry on next run; token preserved.",
                        user_id, google_email,
                        http_err.response.status_code
                        if http_err.response is not None else "N/A",
                    )
                    failed += 1
                except Exception:
                    logger.warning(
                        "User %s (%s): unexpected error renewing watch — "
                        "skipping; token preserved.",
                        user_id, google_email, exc_info=True,
                    )
                    failed += 1

            except Exception:
                # Catch-all: one user's unexpected error must not stop others.
                logger.exception(
                    "User %s (%s): unhandled error during renewal — skipping.",
                    user_id, google_email,
                )
                failed += 1

        logger.info(
            "Gmail watch renewal complete: %d succeeded, %d failed.",
            succeeded, failed,
        )


if __name__ == "__main__":
    renew_watches()
