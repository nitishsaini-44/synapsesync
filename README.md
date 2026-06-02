# SynapseSync 🧠⚡

> **A fully automated, AI-powered email triage and lead management platform — live in the cloud.**

SynapseSync automatically reads your Gmail, classifies each email using **Groq AI** (powered by Meta's LLaMA 3.1), saves it to a cloud PostgreSQL database, sends an instant Discord notification, and displays everything on a beautiful React dashboard — **with zero manual effort.**

[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://ai-workflow-automation-platform-wfj5.onrender.com)
[![Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/nitishsaini-44/AI-Workflow-Automation-Platform)

---

## ✨ Features

- 🤖 **AI Email Classification** — Groq AI (LLaMA 3.1-8b-instant) auto-classifies every email into: `urgent`, `sales`, `support`, or `spam`
- 📬 **Fully Automated Gmail Ingestion** — n8n Cloud reads your Gmail every minute and sends emails to the backend automatically
- 🔔 **Instant Discord Alerts** — Every classified lead triggers a real-time notification to your Discord server via n8n
- 💾 **Cloud PostgreSQL Storage** — All leads are stored persistently in an Aiven-hosted PostgreSQL database
- 📊 **Analytics Dashboard** — Visual charts and stats for your lead categories and urgency levels
- 🔐 **JWT Authentication** — Secure login/register system with bcrypt password hashing
- 🌍 **Fully Cloud-Deployed** — Backend on Render, Frontend on Vercel, DB on Aiven, Automation on n8n Cloud

---

## 🏗️ Architecture

```
Gmail Inbox
    │
    ▼ (every minute)
n8n Cloud (Gmail Trigger)
    │
    ▼ POST /api/webhook/email_lead
    │   Header: X-API-Key
Flask Backend (Render)
    │
    ├──▶ Groq AI API (LLaMA 3.1-8b-instant) ──▶ Classifies email
    │
    ├──▶ Aiven PostgreSQL ──▶ Stores lead
    │
    └──▶ n8n Webhook (/webhook/lead) ──▶ Discord Notification
    
React Dashboard (Vercel)
    │
    └──▶ Flask REST API (JWT Protected) ──▶ Display leads & analytics
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite, TailwindCSS, Recharts, React Router v7 |
| **Backend** | Python, Flask 3.1, Gunicorn |
| **AI Engine** | **Groq API** (OpenAI-compatible SDK → LLaMA 3.1-8b-instant) |
| **Database** | PostgreSQL (Aiven Cloud) via `psycopg` v3 |
| **Automation** | n8n Cloud (Gmail Trigger → HTTP Request) |
| **Notifications** | Discord Webhooks via n8n |
| **Auth** | JWT (`PyJWT`) + Bcrypt password hashing |
| **Deployment** | Render (backend), Vercel (frontend) |

---

## 🚀 Deployment

### Backend — Render

**Build Command:**
```
pip install -r backend/requirements.txt
```

**Start Command:**
```
gunicorn backend.app:app
```

**Root Directory:** *(leave blank — deploy from repo root)*

#### Required Environment Variables on Render:

| Variable | Description |
| :--- | :--- |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | A long random string for JWT encryption |
| `GROQ_API_KEY` | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `POSTGRES_HOST` | Aiven database host |
| `POSTGRES_PORT` | Aiven database port (e.g. `25060`) |
| `POSTGRES_DB` | Database name (e.g. `defaultdb`) |
| `POSTGRES_USER` | Database user (e.g. `avnadmin`) |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_SSLMODE` | `require` |
| `N8N_WEBHOOK_URL` | Your n8n Cloud instance base URL |
| `APP_API_KEY` | Secret key for n8n → backend webhook auth |
| `ADMIN_USER_EMAIL` | The email you registered on the dashboard |

---

### Frontend — Vercel

1. Import GitHub repository into Vercel
2. Set **Root Directory** to `frontend`
3. **Framework:** Vite (auto-detected)
4. Add Environment Variable:

| Variable | Value |
| :--- | :--- |
| `VITE_API_URL` | `https://your-render-url.onrender.com/api` |

---

## ⚙️ n8n Automation Setup

### Workflow: Gmail → SynapseSync → Discord

1. **Node 1: Gmail Trigger**
   - Event: `On message received`
   - Poll Mode: `Every Minute`

2. **Node 2: HTTP Request**
   - Method: `POST`
   - URL: `https://your-render-url.onrender.com/api/webhook/email_lead`
   - Headers: `X-API-Key: your_app_api_key`
   - Body (JSON):
     ```json
     {
       "message": "{{ $json.snippet }}"
     }
     ```

3. **Publish** the workflow to make it active 24/7.

The backend will automatically classify the email, save it to PostgreSQL, and trigger your n8n Discord webhook to send an alert.

---

## 📁 Project Structure

```
SynapseSync/
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── config.py               # Environment variable config
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Docker config (for local use)
│   ├── database/
│   │   └── db.py               # PostgreSQL connection & queries
│   ├── routes/
│   │   ├── auth.py             # /api/auth/login, /register
│   │   ├── classify.py         # /api/classify, /api/webhook/email_lead
│   │   ├── summarize.py        # /api/summarize
│   │   ├── reply.py            # /api/generate-reply
│   │   ├── leads.py            # /api/leads
│   │   ├── analytics.py        # /api/analytics
│   │   └── notify.py           # /api/notify/discord, /api/notify/full_workflow
│   ├── services/
│   │   ├── openai_service.py   # Groq AI client (classify, summarize, reply)
│   │   ├── discord_service.py  # Discord webhook sender
│   │   └── analytics_service.py
│   └── utils/
│       └── auth_middleware.py  # JWT & API Key decorators
│
├── frontend/
│   ├── index.html
│   ├── vercel.json             # SPA routing config for Vercel
│   ├── vite.config.js
│   └── src/
│       ├── api/
│       │   └── client.js       # Axios client (uses VITE_API_URL)
│       ├── components/
│       │   └── Navbar.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Register.jsx
│           └── Dashboard.jsx
│
├── .gitignore
├── docker-compose.yml          # For local PostgreSQL development
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | None | Register new user |
| `POST` | `/api/auth/login` | None | Login, returns JWT |
| `POST` | `/api/classify` | JWT | Manually classify a message |
| `POST` | `/api/webhook/email_lead` | API Key | n8n sends emails here |
| `POST` | `/api/summarize` | JWT | Summarize a message |
| `POST` | `/api/generate-reply` | JWT | Generate AI reply |
| `GET` | `/api/leads` | JWT | Fetch all leads |
| `GET` | `/api/analytics` | JWT | Get analytics data |
| `POST` | `/api/notify/full_workflow` | JWT | Run full AI pipeline + Discord |
| `GET` | `/health` | None | Health check |

---

## 🤖 AI Engine — Groq + LLaMA 3.1

SynapseSync uses the **Groq API** with the `openai` Python SDK pointed at Groq's base URL. This gives you:
- ⚡ **Ultra-fast inference** (Groq's custom LPU hardware)
- 💰 **Generous free tier** — no credit card needed to get started
- 🧠 **Model:** `llama-3.1-8b-instant` — optimized for structured JSON output

Get your free API key at: **[console.groq.com](https://console.groq.com)**

---

## 🔒 Security

- All dashboard API routes are protected with **JWT Bearer tokens** (24-hour expiry)
- The n8n webhook endpoint (`/api/webhook/email_lead`) uses a separate **API Key** header (`X-API-Key`) to prevent unauthorized access
- Passwords are hashed using **bcrypt** before storage
- Database connections use **SSL (`sslmode=require`)** enforced by Aiven

---

## 📦 Local Development

```bash
# Clone
git clone https://github.com/nitishsaini-44/AI-Workflow-Automation-Platform.git
cd AI-Workflow-Automation-Platform

# Backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r backend/requirements.txt

# Copy and fill in your environment variables
cp .env.example .env

# Run backend
python -m backend.app

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 📄 License

MIT License — feel free to fork and build on top of SynapseSync!
