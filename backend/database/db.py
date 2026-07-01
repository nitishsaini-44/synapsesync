"""
database/db.py
───────────────
PostgreSQL connection pool management and all query functions.

Fixes applied:
- H6:  print() replaced with logging
- M9:  get_analytics() now uses a single SQL aggregation query (was 4 queries)
- All user-fetching queries use explicit column lists to avoid returning password_hash
  to contexts that don't need it (use get_user_with_secrets() for internal auth flows)
"""
import os
import logging

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)

# ── Connection pool ──────────────────────────────────────────────────────────
_db_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    global _db_pool
    if _db_pool is None:
        conninfo = (
            f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
            f"port={os.environ.get('POSTGRES_PORT', '5432')} "
            f"dbname={os.environ.get('POSTGRES_DB', 'ai_workflow_db')} "
            f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
            f"password={os.environ.get('POSTGRES_PASSWORD', 'postgres')} "
            f"sslmode={os.environ.get('POSTGRES_SSLMODE', 'require')}"
        )
        _db_pool = ConnectionPool(conninfo, min_size=1, max_size=5, timeout=10)
        logger.info("PostgreSQL connection pool initialised.")
    return _db_pool


def get_connection():
    return get_pool().getconn()


def release_connection(conn):
    if _db_pool and conn:
        _db_pool.putconn(conn)


def close_pool():
    """Explicitly closes the pool (call only on intentional app shutdown)."""
    global _db_pool
    if _db_pool is not None:
        _db_pool.close()
        _db_pool = None
        logger.info("PostgreSQL connection pool closed.")


def init_db():
    """Executes init.sql to create tables and indexes if they don't exist."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            init_sql_path = os.path.join(os.path.dirname(__file__), "init.sql")
            if os.path.exists(init_sql_path):
                with open(init_sql_path, "r") as f:
                    cur.execute(f.read())
                conn.commit()
                logger.info("Database schema initialised successfully.")
    except Exception:
        logger.exception("Failed to initialise database schema")
        if conn:
            conn.rollback()
    finally:
        release_connection(conn)


# ── User queries ─────────────────────────────────────────────────────────────

_USER_PUBLIC_COLS = """
    id, name, email, google_email, discord_webhook,
    automation_enabled, last_message_id, created_at
"""

_USER_ALL_COLS = """
    id, name, email, password_hash, google_email,
    google_refresh_token, discord_webhook,
    automation_enabled, last_message_id,
    google_connected_at, created_at
"""


def create_user(name: str, email: str, password_hash: str) -> dict | None:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, created_at
                """,
                (name, email, password_hash),
            )
            new_user = cur.fetchone()
            conn.commit()
            return new_user
    except psycopg.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return None
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        release_connection(conn)


def get_user_by_email(email: str) -> dict | None:
    """Returns full user row including password_hash — used for login only."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {_USER_ALL_COLS} FROM users WHERE email = %s", (email,)
            )
            result = cur.fetchone()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def get_user_by_google_email(google_email: str) -> dict | None:
    """Returns the user matched by Google email — includes tokens for OAuth flows."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {_USER_ALL_COLS} FROM users WHERE google_email = %s",
                (google_email,),
            )
            result = cur.fetchone()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def get_user_by_id(user_id: int) -> dict | None:
    """Returns full user row including tokens — used internally by automation pipeline."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {_USER_ALL_COLS} FROM users WHERE id = %s", (user_id,)
            )
            result = cur.fetchone()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def get_user_public(user_id: int) -> dict | None:
    """Returns the user row WITHOUT secrets — safe to serialise and return to frontend."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {_USER_PUBLIC_COLS} FROM users WHERE id = %s", (user_id,)
            )
            result = cur.fetchone()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def update_user_settings(user_id: int, discord_webhook=None, automation_enabled=None) -> dict | None:
    """Updates only the fields explicitly provided."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            updates = []
            params  = []
            if discord_webhook is not None:
                updates.append("discord_webhook = %s")
                params.append(discord_webhook)
            if automation_enabled is not None:
                updates.append("automation_enabled = %s")
                params.append(automation_enabled)

            if not updates:
                return get_user_by_id(user_id)

            # Column names are hardcoded above — no injection risk.
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING *"
            params.append(user_id)
            cur.execute(query, tuple(params))
            updated = cur.fetchone()
            conn.commit()
            return updated
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        release_connection(conn)


def update_google_tokens(
    user_id: int, google_email: str | None, google_refresh_token: str | None
) -> dict | None:
    """
    Saves or clears Google OAuth tokens for a user.
    - When google_refresh_token is provided: sets google_connected_at = NOW()
      so we can track the 6-day reconnect window.
    - When google_refresh_token is None (disconnect): clears google_connected_at.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            if google_refresh_token is not None:
                cur.execute(
                    """
                    UPDATE users
                    SET google_email          = %s,
                        google_refresh_token  = %s,
                        google_connected_at   = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *
                    """,
                    (google_email, google_refresh_token, user_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE users
                    SET google_email          = %s,
                        google_refresh_token  = %s,
                        google_connected_at   = NULL
                    WHERE id = %s
                    RETURNING *
                    """,
                    (google_email, google_refresh_token, user_id),
                )

            updated = cur.fetchone()
            conn.commit()
            return updated
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        release_connection(conn)


def update_last_message_id(user_id: int, last_message_id: str) -> dict | None:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE users SET last_message_id = %s WHERE id = %s RETURNING id
                """,
                (last_message_id, user_id),
            )
            updated = cur.fetchone()
            conn.commit()
            return updated
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        release_connection(conn)


# ── Lead queries ─────────────────────────────────────────────────────────────

def insert_lead(
    user_id: int,
    message: str,
    category: str,
    summary: str,
    urgency: str,
    ai_reply: str | None = None,
    gmail_message_id: str | None = None,
) -> dict | None:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO leads (user_id, message, category, summary, urgency, ai_reply, gmail_message_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, message, category, summary, urgency, ai_reply, gmail_message_id, created_at
                """,
                (user_id, message, category, summary, urgency, ai_reply, gmail_message_id),
            )
            new_lead = cur.fetchone()
            conn.commit()
            return new_lead
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        release_connection(conn)


def get_all_leads(
    user_id: int, category_filter: str | None = None, limit: int = 50, offset: int = 0
) -> list[dict]:
    """
    Returns paginated leads for a user, optionally filtered by category.
    Server-side limit/offset prevents loading unbounded data (M11).
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            if category_filter and category_filter != "all":
                cur.execute(
                    """
                    SELECT id, user_id, message, category, summary, urgency, ai_reply,
                           gmail_message_id, created_at
                    FROM leads
                    WHERE user_id = %s AND category = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, category_filter, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT id, user_id, message, category, summary, urgency, ai_reply,
                           gmail_message_id, created_at
                    FROM leads
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset),
                )
            result = cur.fetchall()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def get_analytics(user_id: int) -> dict:
    """
    Returns analytics counts and recent summaries.
    M9: Uses a single aggregation query instead of 4 separate round trips.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            # Single query for all category counts
            cur.execute(
                """
                SELECT
                    COUNT(*)                                        AS total_processed,
                    COUNT(*) FILTER (WHERE category = 'urgent')    AS urgent_count,
                    COUNT(*) FILTER (WHERE category = 'sales')     AS sales_count,
                    COUNT(*) FILTER (WHERE category = 'support')   AS support_count,
                    COUNT(*) FILTER (WHERE category = 'spam')      AS spam_count
                FROM leads
                WHERE user_id = %s
                """,
                (user_id,),
            )
            counts = cur.fetchone() or {}

            # Recent summaries (separate query — different shape)
            cur.execute(
                """
                SELECT id, message, category, summary, urgency, created_at
                FROM leads
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 10
                """,
                (user_id,),
            )
            recent = cur.fetchall()

        conn.commit()
        return {
            "total_processed":  counts.get("total_processed", 0),
            "urgent_count":     counts.get("urgent_count", 0),
            "sales_count":      counts.get("sales_count", 0),
            "support_count":    counts.get("support_count", 0),
            "spam_count":       counts.get("spam_count", 0),
            "recent_summaries": list(recent),
        }
    finally:
        release_connection(conn)


def get_active_users() -> list[dict]:
    """Returns users with automation enabled and a connected Google account."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, google_refresh_token, discord_webhook, last_message_id
                FROM users
                WHERE automation_enabled = TRUE
                  AND google_refresh_token IS NOT NULL
                """
            )
            result = cur.fetchall()
        conn.commit()
        return result
    finally:
        release_connection(conn)


def is_lead_processed(gmail_message_id: str) -> bool:
    """Checks if a lead with the given gmail_message_id already exists (deduplication)."""
    if not gmail_message_id:
        return False
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id FROM leads WHERE gmail_message_id = %s", (gmail_message_id,)
            )
            result = cur.fetchone() is not None
        conn.commit()
        return result
    finally:
        release_connection(conn)
