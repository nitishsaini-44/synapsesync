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

# Configure a session with automatic retries for rate limits (429) and server errors
discord_session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
    respect_retry_after_header=False
)
discord_session.mount("https://", HTTPAdapter(max_retries=retries))


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
    """Sends a message to a Discord webhook."""
    for attempt in range(5):
        try:
            response = discord_session.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 429:
                try:
                    retry_after = float(response.json().get("retry_after", 1))
                except Exception:
                    retry_after = float(response.headers.get("Retry-After", 1))
                
                if retry_after > 30:
                    logger.error("Discord 429 rate limit is too high (%.2fs). Aborting to prevent hanging.", retry_after)
                    return False
                    
                logger.warning("Discord 429 Rate Limit. Retrying after %.2fs (attempt %d/5)...", retry_after, attempt + 1)
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            return True
        except requests.RequestException:
            logger.warning("Discord notification failed", exc_info=True)
            return False
    return False
