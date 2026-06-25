import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}?sslmode=require"

try:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET automation_enabled = false WHERE google_email = 'nitishsaini044@gmail.com'")
            conn.commit()
            print("Successfully disabled automation to break the loop!")
except Exception as e:
    print(f"Error: {e}")
