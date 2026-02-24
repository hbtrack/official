"""Validate AR_117: AR_040 validation_command corrigido para banco 0061."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/competitions').glob('AR_040*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert '0058_comp_db_006' not in vc, 'FAIL: old 0058 path ainda no VC de AR_040'
assert '0061_comp_db_006' in vc, 'FAIL: new 0061 path nao encontrado no VC de AR_040'

# Verify migration file exists
f = pathlib.Path('Hb Track - Backend/db/alembic/versions/0061_comp_db_006_status_check_constraints.py')
assert f.exists(), 'FAIL: arquivo de migration 0061 nao existe'
c = f.read_text(encoding='utf-8')
assert 'ck_competitions_status' in c, 'FAIL: check constraint ck_competitions_status ausente'
assert "revision = '0061'" in c, "FAIL: revision 0061 nao encontrado"

print('PASS AR_117: AR_040 validation_command corrigido para banco 0061')
