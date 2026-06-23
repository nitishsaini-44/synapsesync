import requests
from flask import current_app

def exchange_code_for_token(auth_code: str):
    """Exchanges an authorization code for an access token and refresh token."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def refresh_access_token(refresh_token: str):
    """Gets a new access token using a refresh token."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def get_profile_email(access_token: str):
    """Fetches the user's email address from Google Profile."""
    profile_url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(profile_url, headers=headers)
    response.raise_for_status()
    return response.json().get('emailAddress')

def fetch_latest_messages(access_token: str, last_message_id: str = None, max_results: int = 10):
    """Fetches recent emails from Gmail API."""
    # We only want messages in INBOX.
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={max_results}&q=is:inbox"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Fetch message list
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    messages_meta = response.json().get('messages', [])
    
    if not messages_meta:
        return []
        
    messages = []
    for meta in messages_meta:
        msg_id = meta['id']
        
        # Stop if we hit the last processed message
        if last_message_id and msg_id == last_message_id:
            break
            
        # Fetch full message details
        msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
        msg_resp = requests.get(msg_url, headers=headers)
        if msg_resp.status_code == 200:
            msg_data = msg_resp.json()
            
            # Extract plain text body (simplified extraction)
            body = ""
            payload = msg_data.get('payload', {})
            parts = payload.get('parts', [])
            
            if not parts:
                body_data = payload.get('body', {}).get('data', '')
            else:
                # Find plain text part
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        break
                else:
                    body_data = ""
                    
            if body_data:
                import base64
                try:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                except Exception:
                    pass
            
            # Extract sender
            sender = "Unknown"
            headers_list = payload.get('headers', [])
            for h in headers_list:
                if h['name'] == 'From':
                    sender = h['value']
                    break
                    
            messages.append({
                "id": msg_id,
                "sender": sender,
                "snippet": msg_data.get('snippet', ''),
                "body": body
            })
            
    return messages
