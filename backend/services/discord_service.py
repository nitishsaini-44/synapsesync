"""
services/discord_service.py
────────────────────────────
Discord webhook helpers.
"""
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

discord_session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
    respect_retry_after_header=False,
)
discord_session.mount("https://", HTTPAdapter(max_retries=retries))

# Maximum seconds to wait inline before giving up.
MAX_INLINE_WAIT_SECONDS = 30


def validate_webhook(webhook_url: str) -> bool:
    """Validates a Discord webhook URL."""
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
    """Builds the Discord embed payload for a processed lead notification."""
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

    - Retries inline up to 5 times for short rate limits (≤ 30s).
    - Logs a warning and returns False for long rate limits without retrying.
      Celery solo pool does not honor ETA/countdown, so deferred retries
      fire immediately and make the rate limit worse.
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
                    # Rate limit too long — skip cleanly.
                    # The rate limit will expire on Discord's side naturally.
                    # The next email arriving after expiry will send normally.
                    hours = retry_after / 3600
                    logger.warning(
                        "Discord webhook rate-limited for %.1fh. "
                        "Notification skipped. Will resume automatically after rate limit expires. "
                        "If this persists, generate a new webhook URL in Discord and update it in your account settings.",
                        hours,
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
