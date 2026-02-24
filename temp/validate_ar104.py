#!/usr/bin/env python3
"""Validation script for AR_104 (Windows-compatible)."""
import os
import subprocess
import sys
from pathlib import Path

# Change to backend directory
backend_dir = Path("Hb Track - Backend")
os.chdir(backend_dir)

# Run alembic upgrade head
print("Running: alembic upgrade head")
result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

if result.returncode != 0:
    print(f"❌ alembic upgrade head failed (exit {result.returncode})")
    sys.exit(result.returncode)

# Run validation Python code
print("\nRunning validation...")
validation_code = """
import sys
sys.path.insert(0, '.')
from sqlalchemy import inspect, text
from app.core.db import engine

insp = inspect(engine)
assert 'competition_standings' in insp.get_table_names(), 'Tabela competition_standings não existe'

with engine.connect() as conn:
    version = conn.execute(text('SHOW server_version')).scalar()
    major = int(version.split('.')[0])
    print(f'PostgreSQL version: {major}')
    
    constraints = [c['name'] for c in insp.get_unique_constraints('competition_standings')]
    indexes = [i['name'] for i in insp.get_indexes('competition_standings')]
    target_name = 'uq_competition_standings_comp_phase_opponent'
    
    assert target_name in constraints or target_name in indexes, f'Constraint/index {target_name} não encontrado (constraints={constraints}, indexes={indexes})'
    print(f'[PASS] Constraint/index {target_name} existe para PG {major}')
"""

result = subprocess.run([sys.executable, "-c", validation_code], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

sys.exit(result.returncode)
