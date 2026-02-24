"""AR_120: Valida fix de cmd_seal - verificacao de REJEITADO por campo Status."""
import sys
import pathlib
import subprocess

content = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')

# Check 1: old bug removido
assert "if '🔴 REJEITADO' in ar_content" not in content, 'FAIL: ainda usa busca em ar_content inteiro'

# Check 2: novo regex por campo presente
assert '_status_match = re.search' in content, 'FAIL: regex por campo Status nao encontrada'

# Check 3: _status_value presente
assert '_status_value' in content, 'FAIL: _status_value nao encontrado no cmd_seal'

# Check 4: hb seal 110 deve funcionar agora
r = subprocess.run(
    [sys.executable, 'scripts/run/hb_cli.py', 'seal', '110'],
    capture_output=True, text=True, encoding='utf-8'
)
assert r.returncode == 0, f'FAIL: hb seal 110 retornou {r.returncode}: {r.stderr.strip()}'
assert 'VERIFICADO' in r.stdout, f'FAIL: VERIFICADO nao na saida: {r.stdout}'

print('PASS AR_120: cmd_seal fix aplicado, AR_110 selada com sucesso')
