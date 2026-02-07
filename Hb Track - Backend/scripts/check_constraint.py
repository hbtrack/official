#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL', '').replace('postgresql+psycopg2://', 'postgresql://').replace('postgresql+asyncpg://', 'postgresql://')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=== ÍNDICES ÚNICOS em org_memberships ===")
cur.execute("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'org_memberships' 
    AND indexdef LIKE '%UNIQUE%'
""")
for row in cur.fetchall():
    print(f"\nÍndice: {row[0]}")
    print(f"Definição: {row[1]}")

print("\n\n=== CONSTRAINTS em org_memberships ===")
cur.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'org_memberships'::regclass
""")
for row in cur.fetchall():
    print(f"\nConstraint: {row[0]}")
    print(f"Tipo: {row[1]}")
    print(f"Definição: {row[2]}")

cur.close()
conn.close()
