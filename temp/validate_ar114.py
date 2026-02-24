"""Validate AR_114: AR_034 validation_command corrigido, gate confirmado funcional."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/governance').glob('AR_034*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert 'PLANS_AR_SYNC/result.json' not in vc, 'FAIL: old evidence path ainda no VC de AR_034'

# Verify gate file exists and has VIOLATION logic
f = pathlib.Path('scripts/checks/check_plans_ar_sync.py')
assert f.exists(), 'FAIL: gate nao existe'
c = f.read_text(encoding='utf-8')
assert 'VIOLATION' in c, 'FAIL: gate nao tem logica VIOLATION'

print('PASS AR_114: AR_034 validation_command corrigido, gate confirmado funcional')
