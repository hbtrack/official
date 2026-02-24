"""Validate AR_119: AR_045 validation_command corrigido, AR counts OK."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/drafts').glob('AR_045*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only (stamps still have old ==25 references — check VC only)
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert '==25' not in vc, f'FAIL: old governance==25 ainda no VC de AR_045'
assert '>=25' in vc, 'FAIL: governance>=25 nao encontrado no VC de AR_045'
assert '>=7' in vc, 'FAIL: features>=7 nao encontrado no VC de AR_045'

# Verify actual AR counts
base = pathlib.Path('docs/hbtrack/ars')
counts = {d: len(list((base / d).glob('*.md'))) for d in ['governance', 'competitions', 'features']}
assert counts.get('governance', 0) >= 25, f'FAIL: governance count insuficiente: {counts}'
assert counts.get('features', 0) >= 7, f'FAIL: features count insuficiente: {counts}'

print(f'PASS AR_119: AR_045 validation_command corrigido, AR counts OK {counts}')
