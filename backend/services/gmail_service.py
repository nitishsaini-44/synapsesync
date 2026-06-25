"""
services/gmail_service.py
─────────────────────────
Google Gmail API wrappers.

Fixes applied:
- M13: base64 import moved to module top (was inside a loop)
- H6:  logging replaces print()
"""
import base64
import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)


def exchange_code_for_token(auth_code: str) -> dict:
    """Exchanges an authorisation code for an access token and refresh token."""
    data = {
        "code":          auth_code,
        "client_id":     current_app.config.get("GOOGLE_CLIENT_ID"),
        "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uri":  current_app.config.get("GOOGLE_REDIRECT_URI"),
        "grant_type":    "authorization_code",
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data, timeout=10)
    response.raise_for_status()
    return response.json()


def refresh_access_token(refresh_token: str) -> dict:
    """Gets a new access token using a refresh token."""
    data = {
        "client_id":     current_app.config.get("GOOGLE_CLIENT_ID"),
        "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type":    "refresh_token",
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data, timeout=10)
    response.raise_for_status()
    return response.json()


def get_profile_email(access_token: str) -> str | None:
    """Fetches the user's Gmail address from the Google profile API."""
    headers  = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("emailAddress")


def fetch_latest_messages(
    access_token: str,
    last_message_id: str | None = None,
    max_results: int = 10,
) -> list[dict]:
    """
    Fetches recent INBOX emails from the Gmail REST API.
    Stops when it encounters last_message_id (deduplication pointer).
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url     = (
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
        f"?maxResults={max_results}&q=is:inbox"
    )

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    messages_meta = response.json().get("messages", [])

    if not messages_meta:
        return []

    messages = []
    for meta in messages_meta:
        msg_id = meta["id"]

        if last_message_id and msg_id == last_message_id:
            break

        msg_resp = requests.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
            headers=headers,
            timeout=10,
        )
        if msg_resp.status_code != 200:
            continue

        msg_data = msg_resp.json()
        payload  = msg_data.get("payload", {})
        parts    = payload.get("parts", [])

        # Extract plain-text body
        body_data = ""
        if not parts:
            body_data = payload.get("body", {}).get("data", "")
        else:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_data = part.get("body", {}).get("data", "")
                    break

        body = ""
        if body_data:
            try:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
            except Exception:
                logger.warning("Failed to decode base64 body for message %s", msg_id)

        # Extract sender
        sender = "Unknown"
        for h in payload.get("headers", []):
            if h["name"] == "From":
                sender = h["value"]
                break

        messages.append({
            "id":      msg_id,
            "sender":  sender,
            "snippet": msg_data.get("snippet", ""),
            "body":    body,
        })

    return messages


def watch_inbox(access_token: str, topic_name: str) -> dict:
    """
    Subscribes the user's Gmail inbox to a Google Cloud Pub/Sub topic.
    Note: watch() subscriptions expire after 7 days and must be renewed.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }
    data = {"labelIds": ["INBOX"], "topicName": topic_name}

    response = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/watch",
        headers=headers,
        json=data,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
