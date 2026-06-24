# SynapseSync 🧠⚡

> **An enterprise-grade, AI-powered email triage and lead management SaaS platform — running live in production.**

SynapseSync transforms your Gmail inbox into an intelligent, fully-automated lead pipeline. The moment an email lands in your inbox, Google's Pub/Sub system pushes an instant webhook to the backend. Flask queues it into **Upstash Redis**, and a dedicated **Celery Worker** picks it up, strips all HTML and links from the email body for token efficiency, and sends the clean text to **Groq AI (LLaMA 3.1-8b-instant)** using **True Parallel Processing**. The AI classifies the email, assigns urgency, writes a summary, saves the lead to **PostgreSQL**, fires a rich **Discord embed notification**, and instantly pushes the lead to your **React dashboard** via **WebSockets** — all within seconds of the email arriving.

[![Live Frontend](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://synapsesync-sam.vercel.app)
[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://synapsesync-flask-api.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-synapsesync-181717?logo=github)](https://github.com/nitishsaini-44/synapsesync)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?logo=flask&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.4.0-37814A)
![Redis](https://img.shields.io/badge/Upstash_Redis-Serverless-DC382D?logo=redis&logoColor=white)
![SocketIO](https://img.shields.io/badge/Flask--SocketIO-5.4.1-010101?logo=socketdotio&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1--8b--instant-F55036)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Aiven_Cloud-4169E1?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-Rich_Embeds-5865F2?logo=discord&logoColor=white)

---

## 🏗️ Architecture & Data Flow

This is the exact sequence of events from the moment an email arrives to the moment it appears on the dashboard:

```
 1. Email arrives in Gmail inbox
        │
        ▼
 2. Google Cloud Pub/Sub fires an INSTANT webhook
    POST /api/webhooks/gmail (runs on Render)
        │
        ▼ (takes < 10ms)
 3. Flask decodes the base64 Pub/Sub payload,
    looks up the user by google_email,
    calls process_email_task.delay(user_id)  ──────► Upstash Redis Queue
    and immediately returns 200 OK to Google.         (Task safely stored)
        │                                                     │
        │                                                     │ (Celery picks it up)
        │                                                     ▼
        │                                          4. Celery Worker boots
        │                                             process_user_emails(user_id)
        │
        │    Inside Celery Worker (process_user_emails):
        │    ┌──────────────────────────────────────────────────────┐
        │    │ a. Load user from PostgreSQL (get_user_by_id)        │
        │    │ b. Decrypt Fernet-encrypted Google Refresh Token     │
        │    │ c. Exchange Refresh Token → Fresh Access Token       │
        │    │    (If this fails, automation is auto-disabled)      │
        │    │ d. Call Gmail REST API → fetch up to 5 new INBOX     │
        │    │    messages since last_message_id                    │
        │    │ e. Filter already-processed IDs (deduplication)     │
        │    │ f. Reverse list (process oldest-first)               │
        │    │ g. ThreadPoolExecutor (max 5 workers) processes      │
        │    │    ALL new emails concurrently                       │
        │    └──────────────────────────────────────────────────────┘
        │
        │    For EACH email (in parallel via process_single_message):
        │    ┌──────────────────────────────────────────────────────┐
        │    │ 1. Check is_lead_processed(msg_id) → skip if seen    │
        │    │ 2. Extract body text + sender from MIME headers      │
        │    │ 3. clean_email_body():                               │
        │    │    - BeautifulSoup strips ALL HTML tags              │
        │    │    - Removes <style> and <script> blocks            │
        │    │    - Replaces all URLs with [link] placeholder       │
        │    │    - Collapses all whitespace                        │
        │    │ 4. classify_lead(cleaned_text) → Groq AI            │
        │    │    Returns: {category, priority, summary}            │
        │    │ 5. insert_lead() → PostgreSQL leads table            │
        │    │ 6. socketio.emit('new_lead', lead_data)              │
        │    │    → React Dashboard updates INSTANTLY               │
        │    │ 7. Decrypt Discord webhook URL (Fernet)              │
        │    │ 8. POST Rich Embed to Discord                        │
        │    │ 9. update_last_message_id() → prevent reprocessing   │
        │    └──────────────────────────────────────────────────────┘
        │
        ▼
 5. React Dashboard (real-time via Socket.IO)
    - Receives 'new_lead' event
    - Prepends lead to state array (no page refresh)
    - Increments analytics counters live
```

---

## ✨ Complete Feature Breakdown

### ⚡ Gmail Push Notifications (Google Cloud Pub/Sub)
- **Zero-polling architecture** — Instead of checking Gmail every minute, the backend uses `gmail.users.watch()` to subscribe to Google Cloud Pub/Sub. Google sends an HTTP POST to `/api/webhooks/gmail` the moment any email hits the watched inbox.
- **Auto-renewal on OAuth connect** — The `watch()` call fires immediately when a user connects their Gmail via OAuth, and again when they toggle automation ON.
- **User lookup by `google_email`** — The webhook payload contains the user's email address, which is used to look up the correct user in the database (`get_user_by_google_email`).
- **Automation guard** — If `automation_enabled` is `False` for the user, the webhook is acknowledged (`200 OK`) but no processing happens.

### 🎯 Enterprise Task Queue (Celery + Upstash Redis)
- **Non-blocking webhook** — Flask's webhook handler calls `process_email_task.delay(user_id)` (Celery's `.delay()` method) which pushes the task ID into the Upstash Redis queue and returns instantly. Flask never blocks waiting for email processing.
- **Crash safety** — If the Render server restarts mid-task, the task remains in Redis and Celery will pick it up again automatically on restart.
- **Auto-retry (up to 3 times)** — The `process_email_task` is decorated with `@celery_app.task(bind=True, max_retries=3)`. Any unhandled exception (network timeout, Groq API downtime) will automatically retry after a 5-second countdown.
- **Solo pool for memory efficiency** — The Celery worker runs with `--pool=solo` to use a single lightweight process, keeping the Render free tier (512MB RAM) stable.
- **Upstash Serverless Redis** — Uses a `rediss://` (TLS-secured) connection with `ssl_cert_reqs=CERT_NONE` for maximum Upstash compatibility.

### 🔀 True Concurrency (ThreadPoolExecutor)
- Instead of processing emails one-by-one in a loop, `process_user_emails` calls `concurrent.futures.ThreadPoolExecutor(max_workers=5)` and submits all new emails as parallel futures.
- All emails are classified by Groq AI, saved to the database, and have Discord notifications sent **simultaneously**. A batch of 5 emails takes the same time as a single email.

### 🤖 AI Engine (Groq API + LLaMA 3.1-8b-instant)
Three distinct AI functions in `backend/services/ai_service.py`:

| Function | Endpoint | System Prompt Focus |
| :--- | :--- | :--- |
| `classify_lead(message)` | Automatic pipeline + `/api/classify` | Full 4-category classifier with conflict resolution rules |
| `summarize_message(message)` | `/api/summarize` (manual) | Concise 1-2 sentence summary + urgency/category extraction |
| `generate_reply(message, category)` | `/api/generate-reply` (manual) | Professional 3-sentence reply tuned to the message category |

**Classification Categories:**
- `urgent` — System outages, legal threats, payment failures, ASAP deadlines, security breaches
- `sales` — Pricing inquiries, demos, partnerships, RFPs, upgrade requests
- `support` — How-to questions, non-critical bug reports, onboarding, feature requests
- `spam` — Marketing, newsletters, phishing, no-reply notifications

**Priority Levels:** `high` / `medium` / `low`

**Conflict Resolution Rules (built into the system prompt):**
- `urgent + sales` → always resolves to `urgent`
- `support + sales` → always resolves to `sales`
- `spam` → always `low` priority
- Hackathon/event notifications → `support` with `medium`

All AI calls use `response_format={"type": "json_object"}` to guarantee parse-safe structured JSON responses.

### 🧹 Email Pre-Processing (Token Saver)
Before any email is sent to Groq AI, it passes through `utils/email_cleaner.py`:
1. **HTML entity decoding** — `html.unescape()` converts `&amp;`, `&lt;`, etc.
2. **HTML stripping** — `BeautifulSoup` parses and removes all HTML tags. `<style>` and `<script>` blocks are fully decomposed.
3. **URL replacement** — All `https://...` links are replaced with `[link]` using regex, saving hundreds of tokens from tracking pixels and unsubscribe links.
4. **Whitespace collapse** — Multiple spaces, newlines, and tabs are collapsed to a single space.

This dramatically reduces token usage and cost for every AI call.

### 📡 Real-Time WebSocket Dashboard (Flask-SocketIO)
- **Flask-SocketIO** runs in `async_mode='threading'` (compatible with Gunicorn's `gthread` worker).
- The Celery Worker calls `socketio.emit('new_lead', lead_data)` directly after saving each lead.
- The React frontend (`Dashboard.jsx` and `LeadManagement.jsx`) imports a shared `socket.js` client instance and registers `socket.on('new_lead', callback)` listeners.
- When a new lead event is received, React **prepends** it to the state array and **increments** analytics counters — no API call or page refresh needed.

### 🔒 Security & Encryption
| Mechanism | Implementation |
| :--- | :--- |
| **Token Encryption at Rest** | Google Refresh Tokens and Discord Webhook URLs are encrypted using `cryptography.fernet.Fernet` (AES-256 CBC) before being stored in PostgreSQL. They are only decrypted in-memory at the moment of use. |
| **JWT Auth** | All user-facing routes are protected by `@token_required` decorator in `utils/auth_middleware.py`. Tokens have a 24-hour expiry, signed with `SECRET_KEY`. |
| **bcrypt Password Hashing** | Registration hashes passwords with `bcrypt.hashpw()`. Login verifies with `bcrypt.checkpw()`. Plain-text passwords never touch the database. |
| **PostgreSQL SSL** | All connections use `sslmode=require` (mandatory for Aiven Cloud). |
| **Auto-Healing Token** | If `refresh_access_token()` fails (e.g., user revoked Gmail access), `update_user_settings(user_id, automation_enabled=False)` is called automatically, preventing infinite error loops. |
| **Internal Route Guard** | `@require_internal_secret` checks the `X-Internal-Secret` header against `APP_API_KEY` on admin-only routes. |

### 🔔 Discord Rich Embed Notifications
Each processed email fires a `POST` to the user's personal Discord Webhook with a rich embed payload containing:

```python
payload = {
    "embeds": [{
        "title": "🚨 New Lead Processed",
        "color": 0x3498db,
        "fields": [
            {"name": "📧 From",     "value": sender,              "inline": False},
            {"name": "📂 Category", "value": category.capitalize(),"inline": True},
            {"name": "⚡ Urgency",  "value": urgency.capitalize(), "inline": True},
            {"name": "📝 Summary",  "value": summary,             "inline": False}
        ],
        "footer": {"text": "SynapseSync AI"}
    }]
}
```

Webhook URLs are AES-256 encrypted at rest and decrypted only when a notification is about to be sent.

---

## 📁 Complete File Structure

```text
SynapseSync/
│
├── backend/
│   ├── app.py                     # Flask app factory
│   │                              #  - Creates Flask app, loads Config
│   │                              #  - Initializes Flask-SocketIO (threading mode)
│   │                              #  - Registers all 11 Blueprint routes
│   │                              #  - Calls init_db() on startup
│   │                              #  - Exposes /health endpoint
│   │
│   ├── celery_worker.py           # Celery application factory
│   │                              #  - make_celery() wraps Flask app in ContextTask
│   │                              #  - ContextTask ensures DB calls work in worker threads
│   │                              #  - Imports backend.tasks to register tasks on boot
│   │                              #  - celery_app instance used by start.sh
│   │
│   ├── tasks.py                   # Celery task definitions
│   │                              #  - @celery_app.task(bind=True, max_retries=3)
│   │                              #  - process_email_task(self, user_id)
│   │                              #  - Auto-retries with 5s countdown on failure
│   │
│   ├── config.py                  # Environment variable loader
│   │                              #  - SECRET_KEY, FERNET_KEY, APP_API_KEY
│   │                              #  - DISCORD_WEBHOOK_URL, FRONTEND_URL
│   │                              #  - GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI
│   │                              #  - GOOGLE_PUBSUB_TOPIC
│   │                              #  - CELERY_BROKER_URL, CELERY_RESULT_BACKEND
│   │                              #  - Auto-appends ssl_cert_reqs=CERT_NONE for rediss://
│   │
│   ├── requirements.txt           # Python dependencies
│   │                              #  flask, flask-cors, openai, psycopg[binary,pool]
│   │                              #  gunicorn, bcrypt, PyJWT, cryptography
│   │                              #  beautifulsoup4, flask-socketio, celery, redis
│   │
│   ├── Dockerfile                 # Docker container definition
│   │                              #  - python:3.11-slim base
│   │                              #  - Installs libpq-dev, gcc
│   │                              #  - Sets PYTHONPATH=/app
│   │                              #  - Executes start.sh as CMD
│   │
│   ├── start.sh                   # Container startup script
│   │                              #  - celery ... worker --pool=solo & (background)
│   │                              #  - exec gunicorn ... backend.app:app (foreground)
│   │
│   ├── database/
│   │   ├── db.py                  # PostgreSQL connection pool + all query functions
│   │   │                          #  Pool: min_size=1, max_size=5, timeout=10
│   │   │                          #  Functions:
│   │   │                          #   init_db()               – runs init.sql on startup
│   │   │                          #   create_user()           – INSERT with bcrypt hash
│   │   │                          #   get_user_by_email()     – login lookup
│   │   │                          #   get_user_by_google_email() – webhook lookup
│   │   │                          #   get_user_by_id()        – general user fetch
│   │   │                          #   update_user_settings()  – discord_webhook, automation_enabled
│   │   │                          #   update_google_tokens()  – stores encrypted refresh token
│   │   │                          #   update_last_message_id() – deduplication pointer
│   │   │                          #   insert_lead()           – saves classified email
│   │   │                          #   get_all_leads()         – with optional category filter
│   │   │                          #   get_analytics()         – counts by category + urgency
│   │   │                          #   get_active_users()      – automation_enabled + gmail connected
│   │   │                          #   is_lead_processed()     – checks gmail_message_id
│   │   │
│   │   └── init.sql               # Schema definition
│   │                              #  - users table: id, name, email, password_hash,
│   │                              #    google_email, google_refresh_token (encrypted),
│   │                              #    discord_webhook (encrypted), automation_enabled,
│   │                              #    last_message_id, created_at
│   │                              #  - leads table: id, user_id, message, category,
│   │                              #    summary, urgency, ai_reply, gmail_message_id,
│   │                              #    created_at
│   │
│   ├── routes/
│   │   ├── auth.py                # POST /api/auth/register (bcrypt hash, JWT return)
│   │   │                          # POST /api/auth/login (verify hash, return JWT)
│   │   │
│   │   ├── oauth.py               # GET /api/google/connect (returns OAuth URL)
│   │   │                          # GET /api/google/callback (exchanges code, stores
│   │   │                          #   encrypted refresh token, calls watch_inbox)
│   │   │
│   │   ├── webhooks.py            # POST /api/webhooks/gmail
│   │   │                          #  - Decodes base64 Pub/Sub envelope
│   │   │                          #  - Extracts emailAddress from JSON payload
│   │   │                          #  - Looks up user by google_email
│   │   │                          #  - Checks automation_enabled
│   │   │                          #  - Calls process_email_task.delay(user_id)
│   │   │                          #  - Always returns 200 OK
│   │   │
│   │   ├── user.py                # GET /api/user/settings (returns profile + status)
│   │   │                          # PUT /api/user/settings (toggle automation_enabled,
│   │   │                          #   triggers watch_inbox refresh if turned ON)
│   │   │
│   │   ├── discord.py             # POST /api/discord/save
│   │   │                          #  - Makes test POST to Discord API to validate URL
│   │   │                          #  - Encrypts URL with Fernet before storing
│   │   │
│   │   ├── classify.py            # POST /api/classify (manual mode)
│   │   │                          #  - Calls classify_lead(message)
│   │   │                          #  - Returns {category, priority, summary}
│   │   │
│   │   ├── summarize.py           # POST /api/summarize (manual mode)
│   │   │                          #  - Calls summarize_message(message)
│   │   │                          #  - Returns {summary, category, urgency}
│   │   │
│   │   ├── reply.py               # POST /api/generate-reply (manual mode)
│   │   │                          #  - Calls generate_reply(message, category)
│   │   │                          #  - Returns {reply}
│   │   │
│   │   ├── leads.py               # GET /api/leads (JWT required)
│   │   │                          #  - Optional ?category= query param filter
│   │   │                          #  - Returns all user leads ordered by created_at DESC
│   │   │
│   │   ├── analytics.py           # GET /api/analytics (JWT required)
│   │   │                          #  - Returns total_processed, urgent_count,
│   │   │                          #    sales_count, support_count, spam_count,
│   │   │                          #    recent_summaries (last 10)
│   │   │
│   │   └── internal.py            # X-Internal-Secret protected admin routes
│   │                              # GET /api/users/active
│   │                              # POST /api/process-user
│   │
│   ├── services/
│   │   ├── automation_service.py  # Core email processing pipeline
│   │   │                          #  process_user_emails(user_id):
│   │   │                          #    1. Load user from DB
│   │   │                          #    2. Decrypt Fernet refresh token
│   │   │                          #    3. Refresh access token (auto-disable on failure)
│   │   │                          #    4. Fetch latest INBOX messages
│   │   │                          #    5. Reverse list (oldest-first)
│   │   │                          #    6. ThreadPoolExecutor(max_workers=5)
│   │   │                          #  process_single_message(app, user, msg):
│   │   │                          #    1. Deduplication check
│   │   │                          #    2. Extract body + sender
│   │   │                          #    3. clean_email_body() preprocessing
│   │   │                          #    4. classify_lead() → Groq AI
│   │   │                          #    5. insert_lead() → PostgreSQL
│   │   │                          #    6. socketio.emit('new_lead', ...)
│   │   │                          #    7. Decrypt + send Discord embed
│   │   │                          #    8. update_last_message_id()
│   │   │
│   │   ├── gmail_service.py       # Google API wrappers
│   │   │                          #  exchange_code_for_token(auth_code) – OAuth flow
│   │   │                          #  refresh_access_token(refresh_token) – get new token
│   │   │                          #  get_profile_email(access_token) – fetch gmail address
│   │   │                          #  fetch_latest_messages(token, last_id, max=5)
│   │   │                          #    - Fetches INBOX messages
│   │   │                          #    - Stops at last_message_id
│   │   │                          #    - Decodes base64url body
│   │   │                          #    - Extracts From header
│   │   │                          #  watch_inbox(access_token, topic_name)
│   │   │                          #    - Calls gmail.users.watch()
│   │   │                          #    - Subscribes to Pub/Sub topic
│   │   │
│   │   ├── ai_service.py          # Groq AI wrappers (OpenAI SDK)
│   │   │                          #  Model: llama-3.1-8b-instant
│   │   │                          #  classify_lead(message) → {category, priority, summary}
│   │   │                          #  summarize_message(message) → {summary, category, urgency}
│   │   │                          #  generate_reply(message, category) → {reply}
│   │   │                          #  All use response_format={"type": "json_object"}
│   │   │
│   │   └── discord_service.py     # Discord notification helpers
│   │                              #  send_notification(url, payload) – POST to webhook
│   │
│   └── utils/
│       ├── email_cleaner.py       # Email preprocessing for token efficiency
│       │                          #  clean_email_body(raw_html) → clean str
│       │                          #  - html.unescape() entities
│       │                          #  - BeautifulSoup strip HTML (bs4)
│       │                          #  - Remove <script>/<style> blocks
│       │                          #  - Replace all URLs with [link]
│       │                          #  - Collapse whitespace
│       │
│       ├── auth_middleware.py     # Route decorators
│       │                          #  @token_required – JWT verification
│       │                          #  @require_internal_secret – APP_API_KEY check
│       │
│       └── encryption.py         # Fernet AES-256 helpers
│                                  #  encrypt_data(plain_text) → encrypted bytes
│                                  #  decrypt_data(encrypted) → plain str
│
├── frontend/
│   ├── vite.config.js             # Vite build config, chunkSizeWarningLimit: 1000
│   │
│   ├── src/
│   │   ├── main.jsx               # React root entry (StrictMode + createRoot)
│   │   ├── App.jsx                # React Router setup + ProtectedRoute wrapper
│   │   │                          # Routes: / → Dashboard, /leads, /ai-assistant,
│   │   │                          #         /integrations, /login, /register
│   │   │
│   │   ├── index.css              # Global TailwindCSS directives + custom tokens
│   │   │
│   │   ├── api/
│   │   │   ├── client.js          # Axios instance (VITE_API_URL base)
│   │   │   │                      # Exports: getAnalytics(), getLeads(), classify(),
│   │   │   │                      #          summarize(), generateReply(),
│   │   │   │                      #          getUserSettings(), updateSettings(),
│   │   │   │                      #          getGoogleConnectUrl(), saveDiscordWebhook()
│   │   │   │
│   │   │   └── socket.js          # Socket.IO client singleton
│   │   │                          # Connects to VITE_API_URL (same Render backend)
│   │   │                          # Shared instance imported by Dashboard + LeadManagement
│   │   │
│   │   ├── components/
│   │   │   ├── AuthContext.jsx     # React Context for user auth state + JWT storage
│   │   │   ├── Navbar.jsx          # Top navigation bar with user avatar + logout
│   │   │   ├── StatCard.jsx        # Reusable metric card (icon, label, value, color)
│   │   │   ├── RecentSummaries.jsx # Clickable activity feed of recent 10 leads
│   │   │   ├── LeadDetailModal.jsx # Full-screen modal: email body, AI fields, reply gen
│   │   │   ├── UrgencyBadge.jsx    # Colored pill badge for high/medium/low urgency
│   │   │   └── LoadingSpinner.jsx  # Centered loading indicator component
│   │   │
│   │   └── pages/
│   │       ├── Login.jsx           # JWT login form → stores token in localStorage
│   │       ├── Register.jsx        # User registration form
│   │       │
│   │       ├── Dashboard.jsx       # Main analytics view
│   │       │                       # - Fetches /api/analytics on mount
│   │       │                       # - socket.on('new_lead') → prepend to state + update counts
│   │       │                       # - Stat Cards: Total, Urgent, Sales, Support
│   │       │                       # - Recharts Donut (PieChart) for category distribution
│   │       │                       # - RecentSummaries feed → opens LeadDetailModal
│   │       │
│   │       ├── LeadManagement.jsx  # Full leads table
│   │       │                       # - Fetches /api/leads on mount
│   │       │                       # - socket.on('new_lead') → prepend new lead instantly
│   │       │                       # - Category filter tabs: all/urgent/sales/support/spam
│   │       │                       # - Click row → opens LeadDetailModal
│   │       │
│   │       ├── AIAssistant.jsx     # Manual AI tools page (paste-and-process)
│   │       │                       # - Summarize: calls /api/summarize
│   │       │                       # - Classify: calls /api/classify
│   │       │                       # - Auto-Reply: calls /api/generate-reply
│   │       │                       #   + Copy to Clipboard + Regenerate buttons
│   │       │
│   │       └── Integrations.jsx    # User settings & connections page
│   │                               # - Google Gmail Card: OAuth connect button,
│   │                               #   shows connected email, Beta Access notice
│   │                               # - Discord Webhook Card: URL input + validation,
│   │                               #   masked display after save
│   │                               # - Automation Engine Card: Active/Paused badge,
│   │                               #   toggle button (locked if Gmail not connected)
│   │
│   └── vercel.json                 # SPA routing: rewrites all paths to index.html
│
├── docker-compose.yml              # Local development: runs Flask backend only
└── README.md
```

---

## 🔌 Complete API Reference

### Public Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Create account (`name`, `email`, `password`) → returns JWT |
| `POST` | `/api/auth/login` | Login (`email`, `password`) → returns JWT |
| `GET` | `/health` | Returns `{"status": "healthy"}` |

### User Endpoints *(JWT required: `Authorization: Bearer <token>`)*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/google/connect` | Returns Google OAuth authorization URL |
| `GET` | `/api/google/callback` | Handles OAuth redirect, encrypts + stores refresh token, calls `watch_inbox()` |
| `GET` | `/api/user/settings` | Returns full profile (Gmail status, Discord status, automation state) |
| `PUT` | `/api/user/settings` | Updates `automation_enabled`. If set to `True`, refreshes Gmail `watch()` |
| `POST` | `/api/discord/save` | Validates Discord webhook URL against Discord API, then encrypts + stores |
| `GET` | `/api/leads` | All classified leads (optional `?category=urgent\|sales\|support\|spam`) |
| `GET` | `/api/analytics` | `{total_processed, urgent_count, sales_count, support_count, spam_count, recent_summaries}` |
| `POST` | `/api/classify` | Manual classify: `{"message": "..."}` → `{category, priority, summary}` |
| `POST` | `/api/summarize` | Manual summarize: `{"message": "..."}` → `{summary, category, urgency}` |
| `POST` | `/api/generate-reply` | Manual reply: `{"message": "...", "category": "..."}` → `{reply}` |

### Webhook Endpoint *(Google Cloud Pub/Sub only)*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/webhooks/gmail` | Receives base64-encoded Pub/Sub push notification, dispatches Celery task |

### Internal Endpoints *(`X-Internal-Secret` header required)*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/users/active` | Returns users with Gmail connected + automation enabled |
| `POST` | `/api/process-user` | Manually triggers `process_user_emails()` for `{"user_id": N}` |

### WebSocket Events *(Socket.IO)*

| Event | Direction | Payload |
| :--- | :--- | :--- |
| `new_lead` | Server → Client | Full lead object: `{id, user_id, message, category, summary, urgency, gmail_message_id, created_at}` |

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
| :--- | :--- | :--- |
| **Frontend Framework** | React | 19 |
| **Build Tool** | Vite | Latest |
| **Styling** | TailwindCSS | 3.4 |
| **Charts** | Recharts | Latest |
| **WebSocket Client** | socket.io-client | Latest |
| **Backend Framework** | Flask | 3.1.0 |
| **HTTP Server** | Gunicorn | 23.0.0 |
| **Real-Time** | Flask-SocketIO | 5.4.1 |
| **Task Queue** | Celery | 5.4.0 |
| **Message Broker** | Redis (Upstash, TLS) | 5.0.3 |
| **AI Engine** | Groq API (LLaMA 3.1-8b-instant) | openai SDK 1.63.0 |
| **Database Driver** | psycopg v3 + psycopg_pool | ≥3.3.0 |
| **Auth** | PyJWT + bcrypt | 2.8.0 / 4.1.2 |
| **Encryption** | cryptography (Fernet/AES-256) | ≥41.0.0 |
| **HTML Parsing** | BeautifulSoup4 | ≥4.12.0 |
| **Gmail Push** | Google Cloud Pub/Sub + Gmail Watch API | — |
| **Database** | PostgreSQL (Aiven Cloud) | — |
| **Frontend Host** | Vercel | — |
| **Backend Host** | Render (Docker) | — |

---

## 🚀 Deployment Guide

### Prerequisites
1. **Aiven Cloud** PostgreSQL database
2. **Google Cloud Project** with Gmail API + Pub/Sub API enabled
3. **Upstash** Serverless Redis database (free tier: 10,000 commands/day)
4. **Discord Server** with a Webhook URL per user

### Step 1: Google Cloud Setup
1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable **Gmail API** and **Cloud Pub/Sub API**
3. Create OAuth 2.0 credentials (Web Application type)
4. Add your Render backend URL to **Authorized Redirect URIs**: `https://your-backend.onrender.com/api/google/callback`
5. Create a Pub/Sub **Topic** (e.g., `projects/your-project/topics/gmail-push`)
6. Create a **Push Subscription** pointing to: `https://your-backend.onrender.com/api/webhooks/gmail`
7. Grant `gmail-api-push@system.gserviceaccount.com` the `Pub/Sub Publisher` role on the topic

### Step 2: Upstash Redis
1. Go to [upstash.com](https://upstash.com/) and create a free Redis database
2. Select your nearest region
3. Copy the connection string starting with `rediss://`

### Step 3: Backend — Render Docker Deployment
1. Connect your GitHub repository to Render
2. Select **Docker** as the environment (Render auto-detects the `backend/Dockerfile`)
3. Set all required environment variables:

| Variable | Description |
| :--- | :--- |
| `POSTGRES_HOST` | Aiven PostgreSQL host |
| `POSTGRES_PORT` | Aiven PostgreSQL port |
| `POSTGRES_DB` | Database name (e.g., `defaultdb`) |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `SECRET_KEY` | Flask secret key (any random string) |
| `FERNET_KEY` | Base64-encoded 32-byte Fernet key |
| `APP_API_KEY` | Your Groq API key |
| `GROQ_API_KEY` | Your Groq API key (same value) |
| `REDIS_URL` | `rediss://default:PWD@HOST:PORT` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | `https://YOUR-BACKEND.onrender.com/api/google/callback` |
| `GOOGLE_PUBSUB_TOPIC` | `projects/YOUR-PROJECT/topics/gmail-push` |
| `FRONTEND_URL` | Your Vercel frontend URL |

> **Note:** `start.sh` automatically boots both Celery and Gunicorn. No manual start command change needed in Render.

### Step 4: Frontend — Vercel
1. Connect the `frontend` directory to Vercel
2. Add environment variable: `VITE_API_URL` = `https://your-backend.onrender.com`
3. Vercel uses `vercel.json` to handle SPA routing automatically

### Step 5: Activate Per-User Pipeline
After deployment:
1. Register an account on the frontend
2. Go to **Integrations** → Connect Gmail (completes OAuth + registers Gmail Push watch)
3. Add your Discord webhook URL
4. Toggle **Automation Enabled** to ON
5. Send a test email to your Gmail — it should appear on the dashboard within seconds

---

## 🔒 Security Architecture

| Threat | Mitigation |
| :--- | :--- |
| Unauthorized API access | `@token_required` enforces JWT on all user routes |
| Database breach | Google tokens and Discord URLs are AES-256 Fernet encrypted at rest |
| Token theft/replay | JWTs expire after 24 hours, signed with secret key |
| Password theft | `bcrypt.hashpw()` — plain text never persisted |
| Database MITM | `sslmode=require` on all PostgreSQL connections |
| Gmail token revocation | Auto-disables automation if refresh fails, preventing infinite error loops |
| Webhook spoofing | Internal routes require `X-Internal-Secret` matching `APP_API_KEY` |
| SSL handshake with Redis | `ssl_cert_reqs=CERT_NONE` appended automatically for `rediss://` Upstash URLs |

---

## ⚡ Performance Notes

- **Email → Dashboard latency:** ~2-5 seconds (Pub/Sub push + Celery pickup + Groq API)
- **Token savings:** HTML stripping reduces email token size by 60-80%
- **Concurrency:** Up to 5 emails processed in parallel per webhook
- **Celery pool:** `--pool=solo` keeps RAM under 512MB on Render free tier
- **DB pool:** `min_size=1, max_size=5` prevents connection exhaustion
- **Deduplication:** `gmail_message_id` prevents double-processing on Pub/Sub retries
