"""
services/discord_service.py
────────────────────────────
Discord webhook helpers.

format_lead_notification() centralises the payload structure that was previously
inlined inside automation_service.py, keeping that file cleaner.
"""
import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Configure a session with automatic retries for rate limits (429) and server errors
discord_session = requests.Session()
discord_session.headers.update({
    "User-Agent": "SynapseSync/1.0 (https://synapsesync-sam.vercel.app, 1.0)"
})
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
    respect_retry_after_header=True
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
            
        frontend_url = os.getenv("FRONTEND_URL", "https://synapsesync-sam.vercel.app").rstrip("/")
        proxy_url = f"{frontend_url}/api/discord-proxy"
        
        response = discord_session.get(
            proxy_url, 
            headers={
                "x-discord-webhook": webhook_url,
                "x-proxy-secret": os.getenv("PROXY_SECRET", "")
            },
            timeout=5
        )
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
    try:
        frontend_url = os.getenv("FRONTEND_URL", "https://synapsesync-sam.vercel.app").rstrip("/")
        proxy_url = f"{frontend_url}/api/discord-proxy"
        
        # Increased timeout to allow for retries including rate-limit waits
        response = discord_session.post(
            proxy_url, 
            json=payload, 
            headers={
                "x-discord-webhook": webhook_url,
                "x-proxy-secret": os.getenv("PROXY_SECRET", "")
            },
            timeout=15
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.warning("Discord notification failed", exc_info=True)
        return False
