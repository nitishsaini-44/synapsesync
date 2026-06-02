import requests
from flask import current_app

class DiscordService:
    @staticmethod
    def send_notification(message):
        """
        Sends a notification to the configured Discord webhook.
        """
        webhook_url = current_app.config.get('DISCORD_WEBHOOK_URL')
        
        if not webhook_url:
            print("Discord Webhook URL not configured.")
            return False, "Discord Webhook URL not configured."
            
        payload = {
            "content": message
        }
        
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            return True, "Notification sent successfully."
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to send Discord notification: {str(e)}"
            print(error_message)
            return False, error_message
