import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    dbname=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT')
)
conn.autocommit = True
cur = conn.cursor()

# Get table names to confirm n8n tables exist
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = [t[0] for t in cur.fetchall()]

print("Factory resetting n8n tables...")
for t in tables:
    if t not in ('users', 'leads'):
        cur.execute(f"DROP TABLE IF EXISTS \"{t}\" CASCADE")
        print(f"Dropped {t}")

print("n8n factory reset successful! Your users and leads tables are perfectly safe.")

