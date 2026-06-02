# SynapseSync 🧠⚡

> **A fully automated, AI-powered email triage and lead management platform — live in the cloud.**

SynapseSync automatically reads your Gmail, classifies each email using **Groq AI** (powered by Meta's LLaMA 3.1), saves it to a cloud PostgreSQL database, sends an instant Discord notification, and displays everything on a beautiful React dashboard — **with zero manual effort.**

[![Live Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://ai-workflow-automation-platform-wfj5.onrender.com)
[![Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/nitishsaini-44/AI-Workflow-Automation-Platform)

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8.0-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?logo=groq&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Aiven-4169E1?logo=postgresql&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Cloud-EA4B71?logo=n8n&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-Webhooks-5865F2?logo=discord&logoColor=white)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)

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

## ⚙️ n8n Workflow Setup (Step-by-Step)

SynapseSync uses **two n8n workflows** working together. Follow these steps carefully to set them up.

### Prerequisites

- Create a free account at [n8n.cloud](https://n8n.cloud)
- Have your **Render backend URL** ready (e.g. `https://your-app.onrender.com`)
- Have a **Discord server** with a channel where you want to receive alerts

---

### Workflow 1: Gmail → SynapseSync (Email Ingestion)

This workflow automatically reads new emails from Gmail and sends them to your backend for AI classification.

#### Step 1: Create a New Workflow
- In your n8n dashboard, click **"Add workflow"**
- Name it: `Gmail Email Ingestion`

#### Step 2: Add Gmail Trigger Node
1. Click the **`+`** button to add a new node
2. Search for **"Gmail"** → Under **Triggers**, select **"On message received"**
3. Click **"Credential"** → Connect your Google account
   - When Google asks for permissions, check **"Select all"** and click **Allow**
4. Configure the node:
   - **Poll Times → Mode:** `Every Minute`
   - **Event:** `Message Received`
   - **Simplify:** `ON` (toggle enabled)
   - **Max Emails per Poll:** `10`
5. Click **"Fetch Test Event"** to pull a sample email — you should see email data appear in the OUTPUT panel

#### Step 3: Add HTTP Request Node
1. Click the **`+`** button on the Gmail node's output wire
2. Search for and select **"HTTP Request"**
3. Configure the node:

   | Setting | Value |
   | :--- | :--- |
   | **Method** | `POST` |
   | **URL** | `https://your-render-url.onrender.com/api/webhook/email_lead` |

4. **Headers Setup:**
   - Toggle **"Send Headers"** → `ON`
   - **Specify Headers:** `Using Fields Below`
   - Click **"Add Header"**
     - **Name:** `X-API-Key`
     - **Value:** *(the value of your `APP_API_KEY` env variable on Render)*

5. **Body Setup:**
   - Toggle **"Send Body"** → `ON`
   - **Body Content Type:** `JSON`
   - **Specify Body:** `Using JSON`
   - **JSON:**
     ```json
     {
       "message": "{{ $json.snippet }}"
     }
     ```
   - You should see a preview below the JSON box showing the actual email snippet

6. Click **"Execute step"** to test — you should see `"Email classified successfully"` in the output

#### Step 4: Activate the Workflow
- Click **"Publish"** (top right corner)
- The workflow is now **live** — every new Gmail message will be automatically ingested, classified, and stored!

---

### Workflow 2: SynapseSync → Discord (Alert Notifications)

This workflow receives classified lead data from your backend and sends a formatted message to your Discord channel.

#### Step 1: Create a New Workflow
- Create another new workflow in n8n
- Name it: `Discord Lead Alerts`

#### Step 2: Add Webhook Node
1. Click **`+`** → Search for **"Webhook"** → Select it
2. Configure the node:

   | Setting | Value |
   | :--- | :--- |
   | **HTTP Method** | `POST` |
   | **Path** | `lead` |
   | **Respond** | `Immediately` |

3. **Important:** Click **"Production URL"** tab and copy that URL — this is the base URL you set as `N8N_WEBHOOK_URL` on Render
   - The full production URL will look like: `https://your-instance.app.n8n.cloud/webhook/lead`
   - On Render, set `N8N_WEBHOOK_URL` to just the base: `https://your-instance.app.n8n.cloud`

#### Step 3: Add Discord Node
1. Click **`+`** on the Webhook node's output wire
2. Search for **"Discord"** → Select **"Send a Message"**
3. Connect your Discord bot or use **"Discord Webhook"** instead:
   - Go to your Discord server → Channel Settings → Integrations → **Webhooks** → Create Webhook
   - Copy the Webhook URL and paste it in n8n
4. **Message Content** — Use an expression to format the lead data:
   ```
   🚨 **New Lead Classified!**

   📧 **Message:** {{ $json.body.message }}
   📂 **Category:** {{ $json.body.category }}
   ⚡ **Urgency:** {{ $json.body.urgency }}
   📝 **Summary:** {{ $json.body.summary }}
   🆔 **Lead ID:** {{ $json.body.id }}
   ```

#### Step 4: Activate the Workflow
- Click **"Publish"** to make it live
- Now every time your backend classifies an email, Discord will instantly ping you!

---

### 🔄 Complete Automated Flow

Once both workflows are published and active:

```
📧 New email arrives in Gmail
        ↓
⚡ n8n Workflow 1 reads it (every minute)
        ↓
🌐 POST → /api/webhook/email_lead (Render)
        ↓
🤖 Groq AI classifies: category + urgency + summary
        ↓
💾 Saved to Aiven PostgreSQL
        ↓
📡 Backend triggers n8n Workflow 2
        ↓
🔔 Discord notification sent instantly
        ↓
📊 Lead visible on React Dashboard (Vercel)
```

> **💡 Tip:** Render's free tier puts your server to sleep after 15 minutes of inactivity. The first email after a sleep period may take ~30 seconds to process while the server wakes up. Subsequent emails are instant.

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
