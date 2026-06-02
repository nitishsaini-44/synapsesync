# SynapseSync 🚀

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-blue?logo=react&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Aiven-blue?logo=postgresql&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3.0-38B2AC?logo=tailwind-css&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Cloud-ff6600?logo=n8n&logoColor=white)

A full-stack, production-ready AI platform that automates operational tasks such as email summarization, lead classification, and AI-generated replies using the **OpenAI API (gpt-4o-mini)**.

---

## 🌟 Overview

The SynapseSync platform is designed to streamline business operations by automatically reading incoming emails (via n8n Cloud), categorizing leads, and generating professional responses. It integrates a Flask backend with a React frontend, uses an online PostgreSQL database, and utilizes n8n Cloud for bidirectional workflow automation (e.g., Discord alerts for urgent leads).

## ✨ Features

- **📧 Automated Email Ingestion**: Automatically reads your incoming Gmail emails via n8n and pushes them to your dashboard securely via an API Key.
- **🔐 Multi-Tenant User Authentication**: Full user registration and JWT-based login system so every user gets their own private dashboard and leads.
- **🏷️ AI Lead Classification**: Categorizes incoming queries into `Urgent`, `Sales`, `Support`, or `Spam`.
- **💬 AI Auto-Replies**: Generates context-aware, polite, and professional customer support responses.
- **📊 Analytics Dashboard**: Tracks processed workflows, category distributions, and recent AI activities.
- **🤖 Workflow Automation**: Integrates with n8n Cloud to send real-time Discord notifications when a lead is classified.

---

## 🏗️ Architecture

The system follows a modern microservices architecture running natively on your local machine and connecting to cloud services.

```mermaid
flowchart LR
    A[React Frontend] -->|REST API (JWT)| B[Flask Backend]
    B -->|psycopg3| C[(Aiven PostgreSQL Cloud)]
    B -->|API Calls| D[OpenAI API]
    B -->|Webhook| E[n8n Cloud]
    E -->|Alert| F[Discord]
    G[Incoming Gmail] -->|IMAP| E
    E -->|API Key Webhook| B
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React, Vite, Tailwind CSS, Recharts | Fast, responsive, dark-mode UI and analytics charts. |
| **Backend** | Python 3.14, Flask, psycopg3 | High-performance REST API handling business logic and auth. |
| **AI/ML** | OpenAI API (`gpt-4o-mini`) | Advanced text classification, summarization, and generation. |
| **Database** | Aiven PostgreSQL Cloud | Persistent storage for users, leads, and analytics. |
| **Automation**| n8n Cloud | Visual node-based workflow execution (Gmail -> API -> Discord). |

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (for frontend development)
- [Python 3.14](https://www.python.org/)
- An [OpenAI API Key](https://platform.openai.com/api-keys)
- An [Aiven PostgreSQL Database](https://aiven.io/)
- An [n8n Cloud Account](https://n8n.cloud/)

### 1. Backend Configuration

```bash
# Create a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies (using pure-python psycopg3)
pip install -r backend\requirements.txt
```

Edit your `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_key
POSTGRES_USER=your_aiven_user
POSTGRES_PASSWORD=your_aiven_password
POSTGRES_HOST=your_aiven_host
POSTGRES_PORT=your_aiven_port
POSTGRES_DB=defaultdb
N8N_WEBHOOK_URL=https://your-instance.app.n8n.cloud
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
APP_API_KEY=your_secure_api_key
ADMIN_USER_EMAIL=your_dashboard_login_email@gmail.com
```

### 2. Start the Backend

```bash
python -m backend.app
```
The backend will automatically initialize your database tables on the first run and host the API on `http://localhost:5000`.

### 3. Start the Frontend

In a separate terminal:
```bash
cd frontend
npm run dev
```
Access the dashboard at `http://localhost:5173`. Create an account and start managing your leads!

---

## 🔌 API Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/api/auth/register` | No | Registers a new user account |
| `POST` | `/api/auth/login` | No | Authenticates user and returns JWT |
| `GET`  | `/api/leads` | JWT | Fetches processed leads for the logged-in user |
| `GET`  | `/api/analytics` | JWT | Returns dashboard statistics |
| `POST` | `/api/classify` | JWT | Manually classifies a lead via the UI & triggers Discord |
| `POST` | `/api/webhook/email_lead` | API Key | Used by n8n to automatically submit incoming Gmails |

---

## ⚙️ n8n Cloud Setup

The platform uses n8n Cloud for two primary automations:

### 1. Sending Discord Alerts
1. Create a **Webhook Node** in n8n listening for `POST` requests at `/webhook/lead`.
2. Connect it to a **Discord Node**.
3. Map the incoming variables (`category`, `urgency`, `summary`) into the Discord message body.
4. Set the workflow to Active.

### 2. Fully Automated Email Ingestion
1. Create a **Gmail Trigger Node** listening for new unread messages.
2. Connect it to an **HTTP Request Node**.
3. Set the HTTP node to `POST` to your local backend (using Ngrok): `http://<your-ngrok-url>/api/webhook/email_lead`.
4. Add the `X-API-Key` header with your `APP_API_KEY`.
5. Map the email snippet to the `message` JSON body.
6. Set the workflow to Active. Every email you receive will automatically appear on your dashboard!

## 📄 License

MIT License. See `LICENSE` for more information.
