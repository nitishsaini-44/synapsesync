CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    google_email VARCHAR(255),
    google_refresh_token TEXT,
    discord_webhook TEXT,
    automation_enabled BOOLEAN DEFAULT FALSE,
    last_message_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    gmail_message_id VARCHAR(255) UNIQUE,
    message TEXT NOT NULL,
    category VARCHAR(50),
    summary TEXT,
    urgency VARCHAR(20),
    ai_reply TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
