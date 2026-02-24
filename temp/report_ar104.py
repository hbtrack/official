#!/usr/bin/env python3
"""Execute hb report for AR_104."""
import subprocess
import sys

validation_cmd = r"""cd 'Hb Track - Backend' && alembic upgrade head && python -c "from sqlalchemy import inspect, text; from db.session import engine; insp = inspect(engine); assert 'competition_standings' in insp.get_table_names(), 'Tabela competition_standings não existe'; with engine.connect() as conn: version = conn.execute(text('SHOW server_version')).scalar(); major = int(version.split('.')[0]); print(f'PostgreSQL version: {major}'); constraints = [c['name'] for c in insp.get_unique_constraints('competition_standings')]; indexes = [i['name'] for i in insp.get_indexes('competition_standings')]; target_name = 'uq_competition_standings_comp_phase_opponent'; assert target_name in constraints or target_name in indexes, f'Constraint/index {target_name} não encontrado (constraints={constraints}, indexes={indexes})'; print(f'✅ PASS: Constraint/index {target_name} existe para PG {major}')" """

result = subprocess.run(
    ["python", "scripts/run/hb_cli.py", "report", "104", validation_cmd],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
