"""Validate AR_115: AR_035 validation_command corrigido, sentinela usa INDEX path correto."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/governance').glob('AR_035*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only (avoid false positives from Criterios de Aceite / stamps)
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert 'docs/hbtrack/ars/_INDEX.md' not in vc, 'FAIL: old INDEX path docs/hbtrack/ars/_INDEX.md ainda no VC de AR_035'
assert 'docs/hbtrack/_INDEX.md' in vc, 'FAIL: new INDEX path docs/hbtrack/_INDEX.md nao encontrado no VC de AR_035'

# Verify hb_watch.py itself uses the correct path
src = pathlib.Path('scripts/run/hb_watch.py').read_text(encoding='utf-8')
assert 'docs/hbtrack/_INDEX.md' in src, 'FAIL: sentinela usa path INDEX incorreto'

print('PASS AR_115: AR_035 validation_command corrigido, sentinela usa INDEX path correto')
