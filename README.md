# SynapseSync 🧠⚡

> **A fully automated, AI-powered email triage and lead management platform — live in the cloud.**

SynapseSync reads your Gmail automatically using **official Google OAuth 2.0**, classifies each email using **Groq AI** (Meta's LLaMA 3.1-8b-instant), saves the result to a cloud PostgreSQL database, fires an instant **Discord embed notification**, and renders everything in a beautiful **React dashboard** — all with **zero manual effort**.

[![Live Frontend](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://synapsesync-sam.vercel.app)
[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://synapsesync-flask-api.onrender.com)
[![Repo](https://img.shields.io/badge/GitHub-synapsesync-181717?logo=github)](https://github.com/nitishsaini-44/synapsesync)

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-latest-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Aiven-4169E1?logo=postgresql&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Self_Hosted-EA4B71)
![Discord](https://img.shields.io/badge/Discord-Webhook_Embeds-5865F2?logo=discord&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)
![Fernet](https://img.shields.io/badge/Encryption-AES--256-red)

---

## ✨ Complete Feature List

### 🤖 AI Engine (Groq + LLaMA 3.1)
- **Email Classification** — Every email is classified into exactly one of: `urgent`, `sales`, `support`, or `spam`, with a priority level (`high`, `medium`, `low`) and a 1-2 sentence AI summary. The classifier uses detailed conflict-resolution rules (e.g., "ASAP + pricing = urgent, not sales").
- **Email Summarization** — Standalone summarization endpoint that extracts the key point of any message in one to two concise sentences.
- **AI Reply Generation** — Generates a polite, professional, 3-sentence reply pre-tuned to the message's category. Supports one-click **Regenerate** from the UI.
- **Forced JSON Output** — All AI calls use `response_format={"type": "json_object"}` to guarantee structured, parse-safe responses.

### 📬 Fully Automated Gmail Pipeline
- **Google OAuth 2.0 per User** — Each user connects their own personal Gmail via Google's official OAuth 2.0 consent screen. No shared credentials.
- **Refresh Token Persistence** — After consent, the long-lived refresh token is stored (encrypted) and automatically used to obtain fresh access tokens for every automation cycle.
- **Newest-First Email Polling** — Fetches up to 5 latest INBOX messages per cycle. Processes oldest-first to preserve correct `last_message_id` ordering.
- **Duplicate Prevention** — Each processed email's `gmail_message_id` is stored. Already-processed IDs are skipped on every subsequent run.
- **Full Body Extraction** — Decodes `base64url` email bodies from Gmail's multipart MIME structure, falling back to the snippet if the body is empty.
- **Auto-Healing Token Management** — If the Google access token refresh fails (e.g., user revoked access), automation is automatically disabled for that user to prevent infinite error loops.

### ⚙️ Background Automation Engine (n8n + Flask)
- **Self-Hosted n8n** — Runs as a Docker container on Render. No monthly n8n Cloud subscription required.
- **Per-User Orchestration** — A master n8n workflow polls `GET /api/users/active` every minute and fires `POST /api/process-user` for each active user independently.
- **Secure Internal Channel** — The n8n ↔ Flask communication uses an `X-Internal-Secret` header validated against `APP_API_KEY`. Not accessible from the public internet.
- **Automation Toggle** — Users can enable or pause their own automation from the Integrations page at any time without affecting other users.

### 🔒 Security & Encryption
- **AES-256 Fernet Encryption at Rest** — Google Refresh Tokens and Discord Webhook URLs are encrypted in the database using Python's `cryptography.fernet.Fernet`. They are only decrypted in memory at the moment they are used.
- **JWT Authentication** — All user-facing API routes require a valid JWT Bearer token (24-hour expiry). Tokens are signed using the `SECRET_KEY`.
- **bcrypt Password Hashing** — User passwords are hashed with `bcrypt` before being stored. Plain-text passwords never touch the database.
- **SSL Database Connections** — All PostgreSQL connections enforce `sslmode=require` as required by Aiven Cloud.

### 🔔 Per-User Discord Notifications (Rich Embeds)
- **Personal Webhooks** — Each user sets their own Discord Webhook URL from the Integrations page.
- **Live Validation** — When a user submits a webhook, the backend makes a real test call to the Discord API to confirm it is valid before saving it.
- **Encrypted Storage** — Webhook URLs are AES-256 encrypted before being stored in the database.
- **Rich Discord Embeds** — Notifications are sent as formatted Discord Embeds (not plain text) with dedicated fields for: Sender, Category, Urgency, and AI Summary.

### 📊 Analytics Dashboard
- **4 Stat Cards** — Shows total emails processed, urgent count, sales leads count, and support tickets count in real time.
- **Donut Chart** — An interactive `recharts` donut chart showing the category distribution (urgent / sales / support / spam) of all processed emails.
- **Recent Activity Feed** — A live feed of the 10 most recently processed leads, each clickable to open a full **Lead Detail Modal** showing the complete email text, AI category, urgency badge, and summary.

### 📋 Lead Management Page
- **Full Lead Table** — Displays every classified lead for the logged-in user with sender, category, urgency, summary, and timestamp columns.
- **Category Filter** — Filter the table by `all`, `urgent`, `sales`, `support`, or `spam` with a single click.

### 🤖 AI Assistant Page (Manual Mode)
- **Paste-and-Process** — A dedicated page where users can paste any email or message text and manually trigger any of the three AI tools.
- **Summarize** — Get a category, urgency badge, and 1-2 sentence summary instantly.
- **Classify** — Get a detailed category and priority classification with conflict-resolution logic applied.
- **Auto-Reply** — Get a professional drafted reply, with a **Copy to Clipboard** button and a **Regenerate** button.

### 🔐 Authentication System
- **JWT-based Login/Register** — Secure login and registration flow. JWT tokens are stored in `localStorage` and sent as `Authorization: Bearer` headers on every API call.
- **Protected Routes** — All dashboard pages are protected. Unauthenticated users are redirected to the Login page.

### 🌐 Integrations & Settings Page
- **Google Gmail Card** — Shows connection status and the connected email address. Includes a **Beta Access** notice with a one-click link that opens a pre-written Gmail compose window addressed to the developer, so new users can request to be added as a Google Test User.
- **Discord Webhook Card** — Input field to save a personal Discord webhook. Once saved, the field shows a masked `••••••••` placeholder with a security note.
- **Automation Engine Card** — Real-time Active/Paused status badge. A large toggle button enables or pauses background automation. Locked (with error hint) if Gmail is not yet connected.

### 🚀 Cloud Deployment
- **Frontend** on **Vercel** — Automatic builds on every `git push`. SPA routing handled by `vercel.json` rewrites.
- **Flask Backend** on **Render** — Runs via `gunicorn`. PostgreSQL connection pool initialized on startup.
- **n8n Engine** on **Render** — Self-hosted Docker container backed by the same Aiven PostgreSQL database.
- **Database** on **Aiven Cloud PostgreSQL** — Shared by both Flask and n8n. All connections use SSL.

---

## 🏗️ Architecture

```
┌──────────────────────┐      ┌────────────────────────────────────┐
│   User's Browser     │      │          Render Cloud              │
│  (Vercel Frontend)   │      │                                    │
│                      │─────▶│  Flask Backend API                 │
│  React + Vite +      │      │  (gunicorn + Flask Blueprints      │
│  TailwindCSS +       │      │   + psycopg3 connection pool)      │
│  Recharts            │      │            │                       │
└──────────────────────┘      │            │ Docker internal net   │
                              │            ▼                       │
                              │  n8n Automation Engine             │
                              │  (self-hosted Docker container)    │
                              │  Every 60s:                        │
                              │   1. GET /api/users/active         │
                              │   2. POST /api/process-user        │
                              └────────────────────────────────────┘
                                           │
                     ┌─────────────────────▼──────────────────────┐
                     │         Aiven Cloud PostgreSQL              │
                     │  users (encrypted tokens) | leads          │
                     └────────────────────────────────────────────┘
                              │                     │
              ┌───────────────▼──────┐  ┌───────────▼───────────┐
              │  Gmail REST API      │  │  Discord Webhook API  │
              │  (Google OAuth 2.0)  │  │  (Rich Embed Alerts)  │
              └──────────────────────┘  └───────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite, TailwindCSS, Recharts, React Router v7, Lucide Icons |
| **Backend** | Python 3.11, Flask 3.1, Gunicorn, Flask-CORS |
| **AI Engine** | **Groq API** via OpenAI SDK → `llama-3.1-8b-instant` (classify, summarize, reply) |
| **Database** | PostgreSQL (Aiven Cloud) via `psycopg` v3 with connection pooling |
| **Encryption** | `cryptography.fernet` — AES-256 symmetric encryption for tokens at rest |
| **Auth** | JWT (`PyJWT`) + Bcrypt password hashing |
| **Automation** | Self-hosted n8n (Docker) on Render |
| **Gmail** | Google OAuth 2.0 + Gmail REST API (`gmail.readonly` scope) |
| **Notifications** | Discord Webhook API (Rich Embed format) |
| **Deployment** | Render (Backend + n8n), Vercel (Frontend), Aiven (Database) |

---

## 📁 Project Structure

```text
SynapseSync/
│
├── backend/
│   ├── app.py                     # Flask app factory — registers all blueprints
│   ├── config.py                  # Loads all env vars into a Config class
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Docker build for Render deployment
│   │
│   ├── database/
│   │   ├── db.py                  # psycopg3 connection pool + all DB query functions
│   │   │                          # (create_user, get_leads, insert_lead, get_active_users,
│   │   │                          #  update_google_tokens, is_lead_processed, etc.)
│   │   └── init.sql               # Initial table schema (users, leads)
│   │
│   ├── routes/
│   │   ├── auth.py                # POST /api/auth/register, /api/auth/login
│   │   ├── oauth.py               # GET /api/google/connect, GET /api/google/callback
│   │   ├── user.py                # GET/PUT /api/user/settings
│   │   ├── discord.py             # POST /api/discord/save (validates + encrypts webhook)
│   │   ├── internal.py            # GET /api/users/active, POST /api/process-user (n8n only)
│   │   ├── classify.py            # POST /api/classify
│   │   ├── summarize.py           # POST /api/summarize
│   │   ├── reply.py               # POST /api/generate-reply
│   │   ├── leads.py               # GET /api/leads
│   │   └── analytics.py           # GET /api/analytics
│   │
│   ├── services/
│   │   ├── ai_service.py          # Groq AI: classify_lead(), summarize_message(), generate_reply()
│   │   ├── gmail_service.py       # Google OAuth token exchange + Gmail REST API (fetch, decode)
│   │   ├── discord_service.py     # validate_webhook() + send_notification() with Embed payload
│   │   └── automation_service.py  # process_user_emails(): the full 9-step automation pipeline
│   │
│   └── utils/
│       ├── encryption.py          # encrypt_data() / decrypt_data() using Fernet (AES-256)
│       └── auth_middleware.py     # @token_required (JWT) and @require_internal_secret decorators
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js          # Axios instance (reads VITE_API_URL) + all API call exports
│   │   ├── components/
│   │   │   ├── Navbar.jsx         # Top navigation bar
│   │   │   ├── Sidebar.jsx        # Side navigation menu
│   │   │   ├── StatCard.jsx       # Reusable stat metric card
│   │   │   ├── RecentSummaries.jsx# Clickable recent activity feed
│   │   │   ├── LeadDetailModal.jsx# Popup modal for full lead view
│   │   │   ├── UrgencyBadge.jsx   # Colored urgency level badge
│   │   │   └── LoadingSpinner.jsx # Reusable loading indicator
│   │   └── pages/
│   │       ├── Login.jsx          # JWT login form
│   │       ├── Register.jsx       # New user registration form
│   │       ├── Dashboard.jsx      # Stat cards + donut chart + recent activity feed
│   │       ├── LeadManagement.jsx # Full leads table with category filter tabs
│   │       ├── AIAssistant.jsx    # Manual Summarize / Classify / Auto-Reply tool
│   │       └── Integrations.jsx   # Google OAuth connect, Discord webhook, automation toggle
│   ├── vercel.json                # Rewrites all paths to index.html for SPA routing on Vercel
│   └── vite.config.js
│
├── workflows/
│   └── n8n-master-workflow.json   # Exported n8n workflow — import into your n8n instance
│
├── docker-compose.yml             # Runs flask-app + n8n together, sharing env vars & network
├── reset_n8n.py                   # Admin utility: drops and re-creates all n8n DB tables
└── README.md
```

---

## 🔌 API Reference

### Public Endpoints (No auth required)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Create a new user account (`name`, `email`, `password`) |
| `POST` | `/api/auth/login` | Login and receive a JWT token |
| `GET`  | `/health` | Health check — returns `{"status": "healthy"}` |

### User Endpoints (JWT required — `Authorization: Bearer <token>`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`  | `/api/google/connect` | Returns a Google OAuth authorization URL for the user to visit |
| `GET`  | `/api/google/callback` | Handles the OAuth redirect, exchanges code for tokens, encrypts and stores refresh token |
| `GET`  | `/api/user/settings` | Returns profile, Gmail connection status, Discord status, automation state |
| `PUT`  | `/api/user/settings` | Update `automation_enabled` state |
| `POST` | `/api/discord/save` | Validate a Discord webhook URL, then encrypt and save it |
| `GET`  | `/api/leads` | Get all classified leads for the authenticated user (optional `?category=` filter) |
| `GET`  | `/api/analytics` | Get total count, category breakdown, urgency breakdown, recent 10 summaries |
| `POST` | `/api/classify` | Manually classify a message — returns `{category, priority, summary}` |
| `POST` | `/api/summarize` | Summarize a message — returns `{summary, category, urgency}` |
| `POST` | `/api/generate-reply` | Generate a professional reply — returns `{reply}` |

### Internal Endpoints (`X-Internal-Secret` header required — n8n use only)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`  | `/api/users/active` | Returns list of users with Gmail connected and automation enabled |
| `POST` | `/api/process-user` | Runs the complete 9-step email pipeline for `{"user_id": N}` |

---

## ⚙️ Automation Pipeline — Step by Step

Every 60 seconds the n8n master workflow fires this sequence for each active user:

```
n8n → GET /api/users/active → gets [user_id, ...]

For each user_id:
n8n → POST /api/process-user { user_id }

Flask automation_service.process_user_emails(user_id):
  Step 1 → Load user row from PostgreSQL
  Step 2 → Decrypt Google Refresh Token (Fernet AES-256)
  Step 3 → Call Google OAuth API → exchange refresh token for fresh access token
            └─ If refresh fails → disable automation for user → stop
  Step 4 → Call Gmail REST API → fetch up to 5 latest INBOX messages
  Step 5 → Filter out already-processed IDs using gmail_message_id deduplication
  Step 6 → For each new message:
            a. Decode base64url email body; extract sender from headers
            b. Build full text: "From: <sender>\n\n<body>"
            c. Send to Groq AI (LLaMA 3.1-8b-instant)
            d. Receive { category, priority, summary }
            e. INSERT lead into PostgreSQL
            f. Decrypt user's Discord webhook (if configured)
            g. POST rich Discord Embed notification
            h. UPDATE last_message_id pointer in users table
  Step 7 → Return success/failure status to n8n
```

---

## 🔒 Security Architecture

| Threat | Mitigation |
| :--- | :--- |
| Unauthorized API access | All user routes require a valid JWT Bearer token (24-hour expiry) |
| Stolen database | Google Refresh Tokens and Discord Webhooks are AES-256 encrypted at rest — raw values never stored |
| n8n → Flask spoofing | Internal endpoints require `X-Internal-Secret` header matching `APP_API_KEY` |
| Password theft | Passwords are hashed with `bcrypt` before storage — plain-text never persisted |
| Man-in-the-middle | PostgreSQL connections enforce `sslmode=require` (Aiven Cloud requirement) |
| Token revocation spiral | If Google token refresh fails, automation is automatically disabled for that user |

---

## 🚀 Deployment Guide

### 1. Backend — Render Web Service

| Setting | Value |
| :--- | :--- |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `gunicorn backend.app:app` |
| **Root Directory** | *(leave blank — deploy from repo root)* |

**Required Environment Variables:**

| Variable | Description |
| :--- | :--- |
| `SECRET_KEY` | Long random string for JWT signing |
| `FLASK_ENV` | `production` |
| `FERNET_KEY` | Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `GROQ_API_KEY` | From [console.groq.com](https://console.groq.com) |
| `POSTGRES_HOST` | Aiven database hostname |
| `POSTGRES_PORT` | Aiven database port (e.g. `22668`) |
| `POSTGRES_DB` | Database name (e.g. `defaultdb`) |
| `POSTGRES_USER` | Database user (e.g. `avnadmin`) |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_SSLMODE` | `require` |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console → Credentials |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console → Credentials |
| `GOOGLE_REDIRECT_URI` | `https://<your-render-backend>.onrender.com/api/google/callback` |
| `FRONTEND_URL` | `https://<your-vercel-app>.vercel.app` |
| `APP_API_KEY` | Long random secret — used to authenticate n8n → Flask internal calls |
| `N8N_WEBHOOK_URL` | Base URL of your n8n service (e.g. `https://synapsesync-n8n.onrender.com`) |

---

### 2. n8n Automation Engine — Render Web Service (Docker)

Deploy as a **Render Docker** service using the `n8n` section of `docker-compose.yml`.

**Required Environment Variables:**

| Variable | Value |
| :--- | :--- |
| `DB_TYPE` | `postgresdb` |
| `DB_POSTGRESDB_HOST` | Same Aiven host as Flask |
| `DB_POSTGRESDB_PORT` | Same Aiven port as Flask |
| `DB_POSTGRESDB_DATABASE` | Same DB name as Flask |
| `DB_POSTGRESDB_USER` | Same user as Flask |
| `DB_POSTGRESDB_PASSWORD` | Same password as Flask |
| `DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED` | `false` |
| `N8N_ENCRYPTION_KEY` | Same value as `APP_API_KEY` |
| `APP_API_KEY` | Same value as Flask `APP_API_KEY` |
| `FLASK_INTERNAL_URL` | `https://<your-render-backend>.onrender.com` |

After n8n starts, log in and **import** `workflows/n8n-master-workflow.json`. Activate the workflow.

---

### 3. Frontend — Vercel

1. Import your GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework auto-detected as **Vite**.
4. Add Environment Variable:

| Variable | Value |
| :--- | :--- |
| `VITE_API_URL` | `https://<your-render-backend>.onrender.com/api` |

> ⚠️ The `/api` suffix at the end is **required**. After saving, go to the **Deployments** tab and click **Redeploy** to apply the change.

---

### 4. Google Cloud Console Setup

1. Go to **APIs & Services** → **Enable APIs** → enable the **Gmail API**.
2. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID** → Type: **Web Application**.
3. Add to **Authorized Redirect URIs**:
   `https://<your-render-backend>.onrender.com/api/google/callback`
4. Go to **OAuth Consent Screen** → add your Render and Vercel domains to **Authorized Domains**.
5. While in **Testing** mode, add Gmail addresses to **Test Users** (up to 100 users for free — no audit required).

---

## 📦 Local Development

```bash
# 1. Clone the repository
git clone https://github.com/nitishsaini-44/synapsesync.git
cd synapsesync

# 2. Create your environment file
# Copy .env.example to .env and fill in all required values.
# Generate a FERNET_KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Start Flask Backend + n8n together (Docker Compose)
docker-compose up --build
# Flask API → http://localhost:5000
# n8n Dashboard → http://localhost:5678

# 4. Start the React Frontend (new terminal)
cd frontend
npm install
npm run dev
# Frontend → http://localhost:5173
```

> 💡 **Tip:** Render's free tier spins down after 15 minutes of inactivity. The first request after sleep may take ~30 seconds while the server wakes up. Subsequent requests are instant.

---

## 📄 License

MIT License — feel free to fork and build on top of SynapseSync!
