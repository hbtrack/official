#!/usr/bin/env python3
"""Validation script for AR_002.5_A (goalkeeper_stints table)."""
import os
import sys
from pathlib import Path

# Change to backend directory
backend_dir = Path("Hb Track - Backend")
os.chdir(backend_dir)

# Add to path
sys.path.insert(0, '.')

from sqlalchemy import inspect
from app.core.db import engine

print("Validating match_goalkeeper_stints table...")

insp = inspect(engine)
tables = insp.get_table_names()

assert 'match_goalkeeper_stints' in tables, 'Tabela match_goalkeeper_stints não encontrada'

print("[PASS] Tabela match_goalkeeper_stints existe")

# Check columns
columns = [col['name'] for col in insp.get_columns('match_goalkeeper_stints')]
required_cols = ['id', 'match_id', 'athlete_id', 'start_period_number', 'start_time_seconds', 
                 'end_period_number', 'end_time_seconds', 'created_at']

for col in required_cols:
    assert col in columns, f'Coluna {col} não encontrada'
    
print(f"[PASS] Todas as colunas necessárias existem: {len(required_cols)} colunas")

# Check indexes
indexes = [idx['name'] for idx in insp.get_indexes('match_goalkeeper_stints')]
expected_indexes = ['ix_match_goalkeeper_stints_match_id', 'ix_match_goalkeeper_stints_athlete_id']

for idx in expected_indexes:
    assert idx in indexes, f'Index {idx} não encontrado'
    
print(f"[PASS] Índices criados: {expected_indexes}")

print("\n[SUCCESS] AR_002.5_A validation complete")
