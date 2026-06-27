"""
services/discord_service.py
────────────────────────────
Discord webhook helpers.

format_lead_notification() centralises the payload structure that was previously
inlined inside automation_service.py, keeping that file cleaner.
"""
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Configure a session with automatic retries for server errors only.
# 429 handling is done manually below.
discord_session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
    respect_retry_after_header=False,
)
discord_session.mount("https://", HTTPAdapter(max_retries=retries))

# Maximum seconds to wait inline before giving up on a rate-limited request.
# Anything above this is simply skipped — we do NOT schedule deferred retries
# because Upstash Redis ignores Celery's ETA/countdown, causing immediate
# retry storms that make Discord's rate limit even worse.
MAX_INLINE_WAIT_SECONDS = 30


def validate_webhook(webhook_url: str) -> bool:
    """
    Validates a Discord webhook URL by making a GET request.
    Discord returns 200 with webhook details if valid.
    """
    try:
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            return False
        response = discord_session.get(webhook_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def format_lead_notification(
    sender: str, category: str, urgency: str, summary: str
) -> dict:
    """
    Builds the Discord embed payload for a processed lead notification.
    Extracted here so automation_service.py stays free of presentation logic.
    """
    return {
        "embeds": [
            {
                "title":  "🚨 New Lead Processed",
                "color":  0x3498DB,
                "fields": [
                    {"name": "📧 From",     "value": sender,               "inline": False},
                    {"name": "📂 Category", "value": category.capitalize(), "inline": True},
                    {"name": "⚡ Urgency",  "value": urgency.capitalize(),  "inline": True},
                    {"name": "📝 Summary",  "value": summary,               "inline": False},
                ],
                "footer": {"text": "SynapseSync AI"},
            }
        ]
    }


def send_notification(webhook_url: str, payload: dict) -> bool:
    """
    Sends a message to a Discord webhook.

    - Retries inline up to 5 times for short rate limits (≤ MAX_INLINE_WAIT_SECONDS).
    - Logs a warning and returns False for long rate limits — no deferred retry
      is scheduled because Upstash Redis ignores Celery ETA, causing retry storms.
    - Returns True on success, False on any failure.
    """
    for attempt in range(5):
        try:
            response = discord_session.post(webhook_url, json=payload, timeout=10)

            if response.status_code == 429:
                try:
                    retry_after = float(response.json().get("retry_after", 1))
                except Exception:
                    retry_after = float(response.headers.get("Retry-After", 1))

                if retry_after > MAX_INLINE_WAIT_SECONDS:
                    logger.warning(
                        "Discord 429: rate limit too long (%.0fs) — skipping notification. "
                        "The webhook may be globally rate-limited. "
                        "Use a fresh webhook URL in your account settings to restore notifications.",
                        retry_after,
                    )
                    return False

                logger.warning(
                    "Discord 429: waiting %.2fs before retry (attempt %d/5).",
                    retry_after, attempt + 1,
                )
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            logger.info("Discord notification sent successfully.")
            return True

        except requests.RequestException as exc:
            logger.warning("Discord notification request failed: %s", exc)
            return False

    logger.error("Discord notification failed after 5 attempts.")
    return False
