"""AR_122: Valida fix de cmd_seal - idempotencia VERIFICADO por campo Status."""
import sys
import pathlib
import subprocess

content = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')

# Check 1: old idempotency bug removido
assert 'if "\u2705 VERIFICADO" in ar_content' not in content, 'FAIL: ainda usa busca em ar_content inteiro para idempotencia'

# Check 2: novo regex de idempotencia presente
assert '_status_idem_match = re.search' in content, 'FAIL: regex por campo Status (idem) nao encontrada'

# Check 3: _status_idem_value presente
assert '_status_idem_value' in content, 'FAIL: _status_idem_value nao encontrado'

# Check 4: hb seal 071 deve funcionar agora
r = subprocess.run(
    [sys.executable, 'scripts/run/hb_cli.py', 'seal', '071'],
    capture_output=True, text=True, encoding='utf-8'
)
assert r.returncode == 0, f'FAIL: hb seal 071 retornou {r.returncode}: {r.stderr.strip()}'
assert 'VERIFICADO' in r.stdout, f'FAIL: output={r.stdout}'

print('PASS AR_122: cmd_seal idempotencia fix aplicado, AR_071 selada com sucesso')
