# SynapseSync 🧠⚡

> **A fully automated, AI-powered email triage and lead management platform — live in the cloud.**

SynapseSync reads your Gmail automatically using **official Google OAuth 2.0**, classifies each email using **Groq AI** (Meta's LLaMA 3.1), saves the result to a cloud PostgreSQL database, fires an instant **Discord embed notification**, and renders everything in a beautiful **React dashboard** — all with **zero manual effort**.

[![Live Frontend](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://synapsesync-sam.vercel.app)
[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://synapsesync-flask-api.onrender.com)
[![Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/nitishsaini-44/AI-Workflow-Automation-Platform)

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-latest-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Aiven-4169E1?logo=postgresql&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Self_Hosted_on_Render-EA4B71)
![Discord](https://img.shields.io/badge/Discord-Webhook_Embeds-5865F2?logo=discord&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)
![Fernet](https://img.shields.io/badge/Encryption-AES--256_Fernet-red)

---

## ✨ What's New — Recent Changes

This section documents all major features and architectural changes made after initial project setup.

### 🔐 Google OAuth 2.0 — Per-User Gmail Connection
Previously, the app used a single admin Gmail account. We redesigned the architecture so that **every registered user can connect their own personal Gmail account** securely.

- A new `GET /api/google/connect` route generates a Google authorization URL with the `gmail.readonly` scope.
- The user is redirected to Google's official consent screen to grant access.
- Google redirects the user back to `GET /api/google/callback`, where the one-time authorization code is exchanged for a long-lived **refresh token**.
- The refresh token is **AES-256 Fernet encrypted** before being stored in the database.
- The user's connected email address (`google_email`) is also stored and shown in the dashboard.

### 🔒 AES-256 Fernet Encryption at Rest
A new `backend/utils/encryption.py` module was created to protect all sensitive third-party credentials stored in the database.

- All **Google Refresh Tokens** are encrypted before `INSERT` and decrypted only at the moment they are needed by the automation engine.
- All **Discord Webhook URLs** are also encrypted before saving and decrypted only when a notification needs to be dispatched.
- Encryption uses Python's `cryptography.fernet.Fernet` library (symmetric AES-256 under the hood), powered by the `FERNET_KEY` environment variable.

### ⚙️ Background Automation Engine — Self-Contained per User
Previously, a single n8n Cloud workflow handled email ingestion for one fixed admin account. We rebuilt this into a **fully automated, multi-user background daemon**.

- A new `backend/services/automation_service.py` module contains the complete `process_user_emails(user_id)` function.
- This service: decrypts the user's Google refresh token → obtains a fresh access token → fetches the latest 5 inbox emails → checks for duplicates → classifies each with Groq AI → saves the lead → sends a Discord embed → updates the `last_message_id` pointer to avoid re-processing.
- If the Google token is revoked or expired, the engine **automatically disables automation** for that user and logs a warning, preventing infinite error loops.
- A self-hosted n8n instance (running as a Docker container on Render) handles the scheduling and orchestration by polling `/api/users/active` and firing `/api/process-user` for each active user in sequence.

### 🔗 Internal Microservice API — Secured n8n ↔ Flask Channel
A new `backend/routes/internal.py` blueprint creates two protected internal-only endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/users/active` | Returns the list of users with Gmail connected and automation enabled |
| `POST` | `/api/process-user` | Triggers `process_user_emails()` for a given `user_id` |

Both endpoints are guarded by a `require_internal_secret` decorator that validates the `X-Internal-Secret` header against the `APP_API_KEY` environment variable. They are not accessible from the public internet.

### 🤖 n8n Self-Hosted on Render (Docker)
We moved from n8n Cloud to a **self-hosted n8n instance running as a Docker container on Render**.

- The `docker-compose.yml` was updated to define two services: `flask-app` and `n8n`.
- The `n8n` service uses the Aiven PostgreSQL database (same as Flask) to persist its workflows.
- n8n communicates with Flask internally via `http://flask-app:5000` within the Docker network, so no public internet traffic is needed for the automation loop.
- The master workflow JSON (`workflows/n8n-master-workflow.json`) was updated to point to these live Render internal URLs.

### 👥 Multi-User Settings System
A new `backend/routes/user.py` blueprint provides the settings API for each individual user:

- `GET /api/user/settings` — Returns the user's name, email, connected Google account, Discord webhook status, and current automation toggle state.
- `PUT /api/user/settings` — Allows the user to change their automation toggle state.

### 🔔 Per-User Discord Notifications with Embed Format
A new `backend/routes/discord.py` blueprint handles Discord webhook setup:

- When a user submits their Discord webhook URL from the Integrations page, the backend **first validates** it by making a real test request to the Discord API.
- If valid, the URL is **AES-256 encrypted** and saved to the user's row in the database.
- When an email is classified, the `automation_service` decrypts the user's personal webhook and dispatches a rich **Discord Embed** (not plain text) with fields for: Sender, Category, Urgency, and AI Summary.

### 🌐 Integrations & Settings Dashboard Page (Frontend)
The `frontend/src/pages/Integrations.jsx` page was built from scratch to expose all the above features to the user through a beautiful 3-card UI:

1. **Google Gmail Card** — Shows connection status and connected email, or a "Connect Gmail Account" button. Includes a **Beta Access Request** panel that opens a pre-written Gmail compose window for new users who need to be added as a Google Test User.
2. **Discord Webhook Card** — An input field to save a webhook. Once saved, the field shows a masked `••••••••••` placeholder and a security notice.
3. **Automation Engine Card** — Shows a live Active/Paused status badge. A prominent button toggles automation on/off. The button is locked and shows an error hint if Gmail is not yet connected.

### 🚀 Full Cloud Deployment (Vercel + Render)
The entire project is now live:

- **Frontend** deployed on **Vercel** at `https://synapsesync-sam.vercel.app`.
- **Flask Backend API** deployed on **Render** at `https://synapsesync-flask-api.onrender.com`.
- **n8n Automation Engine** deployed as a separate **Render Web Service** at `https://synapsesync-n8n.onrender.com`.
- **Database** hosted on **Aiven Cloud PostgreSQL**.
- All CORS, environment variables, Google OAuth redirect URIs, and Authorized Domains are configured for the live URLs.

---

## ✨ Full Feature List

- 🤖 **AI Email Classification** — Groq AI (LLaMA 3.1-8b-instant) classifies emails into: `urgent`, `sales`, `support`, or `spam` with a summary and urgency score.
- 🔐 **Google OAuth 2.0** — Secure per-user Gmail connection via Google's official consent screen.
- 🔒 **AES-256 Encryption at Rest** — Google tokens and Discord webhooks are encrypted in the database using Fernet symmetric encryption.
- ⚙️ **Fully Automated Background Engine** — A self-hosted n8n + Flask daemon that scans each user's inbox every minute, completely hands-free.
- 🛡️ **Auto-Healing Token Management** — If a user's Google token expires, automation is automatically disabled to prevent repeated failures.
- 🔔 **Per-User Discord Embeds** — Rich Discord embeds for every new classified lead, personalized per user.
- 💾 **Cloud PostgreSQL Storage** — Aiven-hosted database with SSL enforced, connection pooling, and duplicate-prevention via `gmail_message_id`.
- 📊 **Analytics Dashboard** — Visual stats for lead categories and urgency breakdowns.
- 👥 **Multi-Tenant Architecture** — Multiple users, each with their own Gmail, Discord, automation toggle, and lead history.
- 🌍 **Full Cloud Deployment** — Zero local dependencies. Runs entirely on Vercel, Render, and Aiven.
- 📧 **Beta Access Workflow** — Users who aren't on the Google Test Users list can request access with one click, which opens a pre-written Gmail compose window.

---

## 🏗️ Architecture

```
┌─────────────────────┐      ┌──────────────────────────────┐
│   User's Browser    │      │        Render Cloud          │
│  (Vercel Frontend)  │      │                              │
│                     │─────▶│  Flask Backend API           │
│  React + Vite +     │      │  (gunicorn + Flask Blueprints│
│  TailwindCSS        │      │   + psycopg3 pool)           │
└─────────────────────┘      │         │                    │
                             │         │ internal Docker    │
      ┌──────────────────────│─────────▼────────────────┐   │
      │                      │   n8n Automation Engine  │   │
      │  Every 60s:          │   (self-hosted Docker)   │   │
      │  GET /api/users/active│         │               │   │
      │  POST /api/process-user│        │               │   │
      └──────────────────────│──────────│───────────────┘   │
                             │          │                    │
                             └──────────│────────────────────┘
                                        │
              ┌─────────────────────────▼──────────────────────┐
              │              Aiven Cloud PostgreSQL             │
              │  users (encrypted tokens) | leads | analytics  │
              └────────────────────────────────────────────────┘
                        │                          │
          ┌─────────────▼────────┐    ┌────────────▼──────────┐
          │  Gmail API           │    │  Discord Webhook API  │
          │  (Google OAuth 2.0)  │    │  (Rich Embed Alerts)  │
          └──────────────────────┘    └───────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite, TailwindCSS, Recharts, React Router v7, Lucide Icons |
| **Backend** | Python 3.11, Flask 3.1, Gunicorn, Flask-CORS |
| **AI Engine** | **Groq API** (OpenAI-compatible SDK → `llama-3.1-8b-instant`) |
| **Database** | PostgreSQL (Aiven Cloud) via `psycopg` v3 with connection pooling |
| **Encryption** | `cryptography.fernet` (AES-256 symmetric encryption) |
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
│   ├── Dockerfile                 # Multi-stage Docker build for Render deployment
│   │
│   ├── database/
│   │   ├── db.py                  # psycopg3 connection pool + all DB query functions
│   │   └── init.sql               # Initial table creation schema (users, leads)
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
│   │   └── analytics.py          # GET /api/analytics
│   │
│   ├── services/
│   │   ├── ai_service.py          # Groq API client — classify, summarize, generate reply
│   │   ├── gmail_service.py       # Google OAuth token exchange + Gmail REST API calls
│   │   ├── discord_service.py     # Validates webhooks + sends Discord embeds
│   │   └── automation_service.py  # Core engine: decrypt → refresh token → fetch emails
│   │                              #   → deduplicate → classify → insert → notify → update pointer
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
│   │   │   ├── Sidebar.jsx        # Side navigation
│   │   │   └── LoadingSpinner.jsx # Reusable loading component
│   │   └── pages/
│   │       ├── Login.jsx          # JWT login form
│   │       ├── Register.jsx       # New user registration form
│   │       ├── Dashboard.jsx      # Charts + recent lead summaries
│   │       ├── LeadManagement.jsx # Full leads table with category filter
│   │       ├── AIAssistant.jsx    # Manual AI classify/summarize/reply chat
│   │       └── Integrations.jsx   # Google OAuth connect, Discord webhook, automation toggle
│   ├── vercel.json                # Rewrites all paths to index.html for SPA routing
│   └── vite.config.js
│
├── workflows/
│   └── n8n-master-workflow.json   # Exported n8n workflow — import this into your n8n instance
│
├── docker-compose.yml             # Runs flask-app + n8n together with shared env vars
├── reset_n8n.py                   # Admin utility: drops and re-creates all n8n DB tables
└── README.md
```

---

## 🔌 API Reference

### Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Create a new user account |
| `POST` | `/api/auth/login` | Authenticate and receive a JWT |
| `GET` | `/health` | Health check — returns `{"status": "healthy"}` |

### User Endpoints (JWT Required — `Authorization: Bearer <token>`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/google/connect` | Returns a Google OAuth authorization URL to redirect the user to |
| `GET` | `/api/google/callback` | Handles the OAuth redirect, exchanges code for tokens, encrypts and stores refresh token |
| `GET` | `/api/user/settings` | Returns the user's profile, Gmail connection status, and Discord/automation state |
| `PUT` | `/api/user/settings` | Updates `automation_enabled` toggle for the user |
| `POST` | `/api/discord/save` | Validates the Discord webhook URL, then encrypts and saves it |
| `GET` | `/api/leads` | Returns all classified leads for the authenticated user (optional `?category=` filter) |
| `GET` | `/api/analytics` | Returns total counts, category breakdown, and urgency breakdown |
| `POST` | `/api/classify` | Manually classify a message text using Groq AI |
| `POST` | `/api/summarize` | Summarize a message text |
| `POST` | `/api/generate-reply` | Generate an AI reply for a given message and category |

### Internal Endpoints (`X-Internal-Secret` Header Required — n8n use only)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/users/active` | Returns all users with `automation_enabled = TRUE` and a Google token |
| `POST` | `/api/process-user` | Runs the complete email processing pipeline for `{"user_id": N}` |

---

## ⚙️ How the Automation Engine Works (Step by Step)

```
Every 60 seconds, the n8n Master Workflow runs:

1. n8n  →  GET /api/users/active  →  Flask
   Returns list of users who have Gmail connected + automation enabled

2. n8n  →  For each user, POST /api/process-user { user_id }  →  Flask

3. Flask: automation_service.process_user_emails(user_id)
   ├── Reads user row from PostgreSQL
   ├── Decrypts the encrypted Google Refresh Token (Fernet AES-256)
   ├── Calls Google OAuth API → exchanges refresh token for fresh access token
   │   └── If refresh fails → disables automation for user, stops processing
   ├── Calls Gmail REST API → fetches up to 5 latest INBOX messages
   ├── Filters out already-processed messages using gmail_message_id deduplication
   ├── For each new message:
   │   ├── Extracts email body (base64 decoded) and sender header
   │   ├── Sends "From: <sender>\n\n<body>" to Groq AI (LLaMA 3.1-8b-instant)
   │   ├── Receives { category, urgency, summary }
   │   ├── INSERTs lead into PostgreSQL
   │   ├── Decrypts user's Discord webhook URL (if configured)
   │   ├── POSTs a rich Discord Embed notification
   │   └── Updates last_message_id pointer in users table
   └── Returns success/failure status to n8n
```

---

## 🚀 Deployment Guide

### Backend (Flask API) — Render Web Service

| Setting | Value |
| :--- | :--- |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `gunicorn backend.app:app` |
| **Root Directory** | *(leave blank — deploy from repo root)* |

**Required Environment Variables:**

| Variable | Description |
| :--- | :--- |
| `SECRET_KEY` | Long random string used for JWT signing |
| `FLASK_ENV` | `production` |
| `FERNET_KEY` | A Fernet-compatible base64 key. Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `GROQ_API_KEY` | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `POSTGRES_HOST` | Aiven database hostname |
| `POSTGRES_PORT` | Aiven database port (e.g. `22668`) |
| `POSTGRES_DB` | Database name (e.g. `defaultdb`) |
| `POSTGRES_USER` | Database user (e.g. `avnadmin`) |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_SSLMODE` | `require` |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console → Credentials → OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console → Credentials → OAuth 2.0 Client ID |
| `GOOGLE_REDIRECT_URI` | `https://<your-render-url>.onrender.com/api/google/callback` |
| `FRONTEND_URL` | `https://<your-vercel-url>.vercel.app` |
| `APP_API_KEY` | A long random secret — used to authenticate n8n → Flask internal calls |
| `N8N_WEBHOOK_URL` | Base URL of your n8n service, e.g. `https://synapsesync-n8n.onrender.com` |

---

### n8n (Automation Engine) — Render Web Service (Docker)

Deploy using **Render → New Web Service → Docker**, pointing to the `n8n` service in `docker-compose.yml`.

**Required Environment Variables:**

| Variable | Value |
| :--- | :--- |
| `DB_TYPE` | `postgresdb` |
| `DB_POSTGRESDB_HOST` | Same Aiven host as Flask |
| `DB_POSTGRESDB_PORT` | Same Aiven port as Flask |
| `DB_POSTGRESDB_DATABASE` | Same Aiven DB name as Flask |
| `DB_POSTGRESDB_USER` | Same Aiven user as Flask |
| `DB_POSTGRESDB_PASSWORD` | Same Aiven password as Flask |
| `DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED` | `false` |
| `N8N_ENCRYPTION_KEY` | Use the same value as your `APP_API_KEY` |
| `FLASK_INTERNAL_URL` | `https://synapsesync-flask-api.onrender.com` |
| `APP_API_KEY` | Same value as your Flask `APP_API_KEY` |

After n8n starts, go to `https://your-n8n.onrender.com`, log in, and **import** the `workflows/n8n-master-workflow.json` file. Activate the workflow.

---

### Frontend — Vercel

1. Import your GitHub repository into Vercel.
2. Set the **Root Directory** to `frontend`.
3. Framework will be auto-detected as **Vite**.
4. Add the following Environment Variable:

| Variable | Value |
| :--- | :--- |
| `VITE_API_URL` | `https://<your-render-url>.onrender.com/api` |

> ⚠️ **Important:** The `/api` suffix at the end is required. After saving the variable, you must **Redeploy** from the Deployments tab for the change to take effect.

---

### Google Cloud Console Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **APIs & Services** → **Enable APIs** → Enable the **Gmail API**.
2. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID** → Type: **Web Application**.
3. Add your Render backend URL to **Authorized Redirect URIs**:
   `https://synapsesync-flask-api.onrender.com/api/google/callback`
4. Go to **OAuth Consent Screen** → Add your Vercel and Render domains to **Authorized Domains**.
5. While in **Testing** mode, add your Gmail address(es) to the **Test Users** list.

---

## 🔒 Security Architecture

| Threat | Mitigation |
| :--- | :--- |
| Unauthorized API access | All user routes require a valid JWT Bearer token (24h expiry) |
| Stolen database | Google tokens and Discord webhooks are AES-256 encrypted at rest — raw tokens never stored |
| n8n → Flask spoofing | Internal endpoints require `X-Internal-Secret` header matching `APP_API_KEY` |
| Password theft | Passwords are hashed with `bcrypt` before storage |
| Man-in-the-middle | PostgreSQL connections use `sslmode=require` enforced by Aiven |
| Token revocation | If Google token refresh fails, automation is automatically disabled to prevent cascading failures |

---

## 📦 Local Development

```bash
# 1. Clone the repository
git clone https://github.com/nitishsaini-44/AI-Workflow-Automation-Platform.git
cd AI-Workflow-Automation-Platform

# 2. Create your environment file
# Copy .env.example to .env and fill in all required values.
# You MUST generate a FERNET_KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Start everything with Docker Compose
#    This starts: PostgreSQL-backed Flask API + self-hosted n8n engine
docker-compose up --build

# The Flask API will be available at: http://localhost:5000
# The n8n dashboard will be available at:  http://localhost:5678

# 4. Start the Frontend (new terminal)
cd frontend
npm install
npm run dev
# The React app will be available at: http://localhost:5173
```

---

## 📄 License

MIT License — feel free to fork and build on top of SynapseSync!
