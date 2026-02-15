# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ,DB_WRITE,FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=NO
# HB_SCRIPT_ENTRYPOINT=python scripts/ops/db/maintenance/check_athletes_columns.py
# HB_SCRIPT_OUTPUTS=stdout
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='athletes' 
    ORDER BY ordinal_position
""")

print("Colunas da tabela athletes:")
print("-" * 50)
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()

