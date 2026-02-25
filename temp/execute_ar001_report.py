#!/usr/bin/env python
"""Execute hb report for AR_001"""
import subprocess
import sys

cmd = [
    sys.executable,
    "scripts/run/hb_cli.py",
    "report",
    "001",
    "python -c \"import pathlib; migration_files = list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('*_competition_standings_add_team_id.py')); assert len(migration_files) >= 1, 'FAIL: Migration file not found'; content = migration_files[0].read_text(encoding='utf-8'); assert 'add_column' in content and 'team_id' in content, 'FAIL: Migration content invalid (missing add_column or team_id)'; assert 'fk_competition_standings_team_id' in content, 'FAIL: FK constraint fk_competition_standings_team_id missing in migration'; assert 'ix_competition_standings_team_id' in content, 'FAIL: Index ix_competition_standings_team_id missing in migration'; print(f'PASS AR_001: Migration file validated: {migration_files[0].name}')\""
]

result = subprocess.run(cmd, capture_output=False, text=True)
sys.exit(result.returncode)
