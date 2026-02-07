import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))
url = os.getenv('DATABASE_URL_SYNC').replace('postgresql+psycopg2://', 'postgresql://')
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT id, email, is_superadmin, is_locked, status FROM users WHERE email = 'admin@hbtracking.com'")
result = cur.fetchone()
if result:
    print(f"ID: {result[0]}")
    print(f"Email: {result[1]}")
    print(f"is_superadmin: {result[2]}")
    print(f"is_locked: {result[3]}")
    print(f"status: {result[4]}")
else:
    print("Usuário não encontrado!")
cur.close()
conn.close()
