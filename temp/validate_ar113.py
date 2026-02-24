"""Validate AR_113: AR_032 validation_command corrigido para aceitar v1.x."""
import pathlib
import subprocess
import sys

ar = list(pathlib.Path('docs/hbtrack/ars/governance').glob('AR_032*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Extract VC section only
vc = content.split('## Validation Command (Contrato)')[1].split('```')[1] if 'Validation Command' in content else ''

assert "'v1.1.0' in v.stdout" not in vc, 'FAIL: old v1.1.0 assertion still present in VC section'
assert "'v1.' in v.stdout" in vc, 'FAIL: new v1. assertion not found in VC section'
assert 'E_TRIVIAL_CMD' in vc, 'FAIL: keywords check removido do VC section'

# Also verify CLI actually reports v1.x
v_run = subprocess.run(
    [sys.executable, 'scripts/run/hb_cli.py', 'version'],
    capture_output=True, text=True, encoding='utf-8'
)
assert 'v1.' in v_run.stdout, f'FAIL: CLI version inesperado: {v_run.stdout.strip()}'

print('PASS AR_113: AR_032 validation_command corrigido para aceitar v1.x')
