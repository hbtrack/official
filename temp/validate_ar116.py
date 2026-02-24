"""Validate AR_116: AR_038 validation_command corrigido para banco 0060."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/competitions').glob('AR_038*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert '0057_comp_db_004' not in vc, 'FAIL: old 0057 path ainda no VC de AR_038'
assert '0060_comp_db_004' in vc, 'FAIL: new 0060 path nao encontrado no VC de AR_038'

# Verify migration file exists
f = pathlib.Path('Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py')
assert f.exists(), 'FAIL: arquivo de migration 0060 nao existe'
c = f.read_text(encoding='utf-8')
assert 'uq_competition_standings_comp_phase_opponent' in c, 'FAIL: constraint name ausente'
assert "revision = '0060'" in c, "FAIL: revision 0060 nao encontrado"

print('PASS AR_116: AR_038 validation_command corrigido para banco 0060')
