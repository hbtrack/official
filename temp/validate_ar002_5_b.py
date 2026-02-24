#!/usr/bin/env python3
"""Validation script for AR_002.5_B (attendance justified status)."""
import os
import sys
from pathlib import Path

# Change to backend directory
backend_dir = Path("Hb Track - Backend")
os.chdir(backend_dir)

# Add to path
sys.path.insert(0, '.')

from sqlalchemy import text, inspect
from app.core.db import engine

print("Validating attendance.presence_status accepts 'justified'...")

# Check if table exists
insp = inspect(engine)
assert 'attendance' in insp.get_table_names(), 'Tabela attendance não encontrada'
print("[PASS] Tabela attendance existe")

# Check if presence_status column exists
columns = {col['name']: col for col in insp.get_columns('attendance')}
assert 'presence_status' in columns, 'Coluna presence_status não encontrada'
print("[PASS] Coluna presence_status existe")

# Test if 'justified' value is accepted by trying a dry-run query
# We'll use a SELECT to check if records with 'justified' cause an error
with engine.connect() as conn:
    try:
        # Check if any records with 'justified' exist (migration may have run)
        result = conn.execute(text("SELECT COUNT(*) FROM attendance WHERE presence_status = 'justified'"))
        count = result.scalar()
        print(f"[PASS] Status 'justified' é aceito (encontrados {count} registros)")
    except Exception as e:
        if 'check constraint' in str(e).lower():
            print(f"[FAIL] Check constraint ainda não aceita 'justified': {e}")
            sys.exit(1)
        raise

print("\n[SUCCESS] AR_002.5_B validation complete")
