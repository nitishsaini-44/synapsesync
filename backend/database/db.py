import os
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

# Global connection pool
_db_pool = None

def get_pool():
    global _db_pool
    if _db_pool is None:
        try:
            conninfo = (
                f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
                f"port={os.environ.get('POSTGRES_PORT', '5432')} "
                f"dbname={os.environ.get('POSTGRES_DB', 'ai_workflow_db')} "
                f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
                f"password={os.environ.get('POSTGRES_PASSWORD', 'postgres')} "
                f"sslmode={os.environ.get('POSTGRES_SSLMODE', 'require')}"
            )
            _db_pool = ConnectionPool(conninfo, min_size=1, max_size=20)
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise e
    return _db_pool

def get_connection():
    return get_pool().getconn()

def release_connection(conn):
    if _db_pool and conn:
        _db_pool.putconn(conn)

def init_db():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # We are reading from init.sql in the same directory
            init_sql_path = os.path.join(os.path.dirname(__file__), 'init.sql')
            if os.path.exists(init_sql_path):
                with open(init_sql_path, 'r') as f:
                    cur.execute(f.read())
                conn.commit()
                print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        if conn:
            conn.rollback()
    finally:
        release_connection(conn)

def create_user(name, email, password_hash):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, created_at
            """, (name, email, password_hash))
            new_user = cur.fetchone()
            conn.commit()
            return new_user
    except psycopg.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return None # User exists
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        release_connection(conn)

def get_user_by_email(email):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()
    except Exception as e:
        raise e
    finally:
        release_connection(conn)

def insert_lead(user_id, message, category, summary, urgency, ai_reply=None):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO leads (user_id, message, category, summary, urgency, ai_reply)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, message, category, summary, urgency, ai_reply, created_at
            """, (user_id, message, category, summary, urgency, ai_reply))
            new_lead = cur.fetchone()
            conn.commit()
            return new_lead
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        release_connection(conn)

def get_all_leads(user_id, category_filter=None):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            if category_filter and category_filter != 'all':
                cur.execute("SELECT * FROM leads WHERE user_id = %s AND category = %s ORDER BY created_at DESC", (user_id, category_filter))
            else:
                cur.execute("SELECT * FROM leads WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            return cur.fetchall()
    except Exception as e:
        raise e
    finally:
        release_connection(conn)

def get_analytics(user_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(row_factory=dict_row) as cur:
            # Total processed
            cur.execute("SELECT COUNT(*) as count FROM leads WHERE user_id = %s", (user_id,))
            total = cur.fetchone()['count']
            
            # Count by category
            cur.execute("SELECT category, COUNT(*) as count FROM leads WHERE user_id = %s GROUP BY category", (user_id,))
            category_counts = {row['category']: row['count'] for row in cur.fetchall()}
            
            # Count by urgency
            cur.execute("SELECT urgency, COUNT(*) as count FROM leads WHERE user_id = %s GROUP BY urgency", (user_id,))
            urgency_counts = {row['urgency']: row['count'] for row in cur.fetchall()}

            # Recent summaries
            cur.execute("SELECT id, message, category, summary, urgency, created_at FROM leads WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (user_id,))
            recent = cur.fetchall()

            return {
                "total_processed": total,
                "urgent_count": category_counts.get("urgent", 0),
                "sales_count": category_counts.get("sales", 0),
                "support_count": category_counts.get("support", 0),
                "spam_count": category_counts.get("spam", 0),
                "recent_summaries": recent
            }
    except Exception as e:
        raise e
    finally:
        release_connection(conn)
