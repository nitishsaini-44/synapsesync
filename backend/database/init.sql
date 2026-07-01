-- ─────────────────────────────────────────────────────────────────────────────
--  SynapseSync — Database schema
--  Idempotent: safe to re-run on an already-initialised database.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id                   SERIAL PRIMARY KEY,
    name                 VARCHAR(100)  NOT NULL,
    email                VARCHAR(255)  UNIQUE NOT NULL,
    password_hash        VARCHAR(255)  NOT NULL,
    google_email         VARCHAR(255),
    google_refresh_token TEXT,
    discord_webhook      TEXT,
    automation_enabled   BOOLEAN       DEFAULT FALSE,
    last_message_id      VARCHAR(255),
    google_connected_at  TIMESTAMP,
    created_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id               SERIAL PRIMARY KEY,
    gmail_message_id VARCHAR(255) UNIQUE,
    message          TEXT         NOT NULL,
    category         VARCHAR(50)  CHECK (category IN ('urgent', 'sales', 'support', 'spam')),
    summary          TEXT,
    urgency          VARCHAR(20)  CHECK (urgency IN ('high', 'medium', 'low')),
    ai_reply         TEXT,
    user_id          INTEGER      REFERENCES users(id) ON DELETE CASCADE,
    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ── Performance indexes ────────────────────────────────────────────────────────
-- Covers all WHERE user_id = %s queries on leads (fetching, analytics, etc.)
CREATE INDEX IF NOT EXISTS idx_leads_user_id    ON leads(user_id);
-- Covers WHERE user_id = %s AND category = %s filter queries
CREATE INDEX IF NOT EXISTS idx_leads_category   ON leads(user_id, category);
-- Covers ORDER BY created_at DESC scans per user
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(user_id, created_at DESC);
