import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://ai:ai@localhost:5432/ai_learning",
)

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        print(cur.fetchone())  # expect ('vector',)