"""Validate AR_118: AR_044 validation_command corrigido, counts OK."""
import pathlib

ar = list(pathlib.Path('docs/hbtrack/ars/drafts').glob('AR_044*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only (stamp still has old command with assert not orphans)
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert 'assert not orphans' not in vc, 'FAIL: old assert not orphans ainda no VC de AR_044'
assert '>=8' in vc, 'FAIL: competitions>=8 nao encontrado no VC de AR_044'
assert '>=3' in vc, 'FAIL: infra>=3 nao encontrado no VC de AR_044'
assert '>=4' in vc, 'FAIL: features>=4 nao encontrado no VC de AR_044'

# Verify actual counts
base = pathlib.Path('docs/_canon/planos')
counts = {d: len(list((base / d).glob('*.json'))) for d in ['governance', 'competitions', 'infra', 'features']}
assert counts.get('governance', 0) >= 11, f'FAIL: governance count insuficiente: {counts}'
assert counts.get('competitions', 0) >= 8, f'FAIL: competitions count insuficiente: {counts}'
assert counts.get('infra', 0) >= 3, f'FAIL: infra count insuficiente: {counts}'
assert counts.get('features', 0) >= 4, f'FAIL: features count insuficiente: {counts}'

print(f'PASS AR_118: AR_044 validation_command corrigido, counts OK {counts}')
