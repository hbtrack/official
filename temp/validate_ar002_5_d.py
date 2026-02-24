#!/usr/bin/env python3
"""Validation script for AR_002.5_D (match_analytics_cache table)."""
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

print("Validating match_analytics_cache table...")

insp = inspect(engine)
tables = insp.get_table_names()

assert 'match_analytics_cache' in tables, 'Tabela match_analytics_cache não encontrada'
print("[PASS] Tabela match_analytics_cache existe")

# CheckColumns
columns = [col['name'] for col in insp.get_columns('match_analytics_cache')]
required_cols = ['id', 'match_id', 'team_id', 'athlete_id', 'cache_type',
                 'total_shots', 'total_goals', 'shot_conversion_pct',
                 'total_saves', 'goals_conceded', 'goalkeeper_efficiency_pct',
                 'yellow_cards', 'red_cards', 'computed_at', 'is_final']

for col in required_cols:
    assert col in columns, f'Coluna {col} não encontrada'
    
print(f"[PASS] Todas as colunas necessárias existem: {len(required_cols)} colunas")

# Check indexes
indexes = [idx['name'] for idx in insp.get_indexes('match_analytics_cache')]
expected_indexes = ['ix_match_analytics_cache_match_id', 'ux_match_analytics_cache_match_team_athlete']

for idx in expected_indexes:
    assert idx in indexes, f'Index {idx} não encontrado'
    
print(f"[PASS] Índices criados: {expected_indexes}")

print("\n[SUCCESS] AR_002.5_D validation complete")
