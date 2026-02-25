#!/usr/bin/env python3
"""Validate AR_036 migration 0056 content"""
import pathlib

f = pathlib.Path('Hb Track - Backend/db/alembic/versions/0056_comp_db_003_scoring_rules_competitions.py')
assert f.exists(), 'FAIL: migration file not found'

c = f.read_text(encoding='utf-8')

# Check revision
assert "revision = '0056'" in c or 'revision = "0056"' in c, 'FAIL: wrong revision id'
assert 'points_per_draw' in c, 'FAIL: points_per_draw missing'
assert 'points_per_loss' in c, 'FAIL: points_per_loss missing'
assert 'server_default' in c, 'FAIL: server_default missing'

print('PASS: migration 0056 content validated')
