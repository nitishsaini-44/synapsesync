import requests

def validate_webhook(webhook_url: str) -> bool:
    """
    Validates a Discord webhook URL by making a GET request.
    Discord webhooks return a 200 OK with webhook details if valid.
    """
    try:
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            return False
            
        response = requests.get(webhook_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def send_notification(webhook_url: str, payload: dict) -> bool:
    """
    Sends a message to a Discord webhook.
    """
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Discord Notification Error: {e}")
        return False
