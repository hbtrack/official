"""AR_121: Valida que AR_003 tem validation_command deterministico com UUID fixo."""
import pathlib
import subprocess
import sys

ar = list(pathlib.Path('docs/hbtrack/ars/features').glob('AR_003*.md'))[0]
content = ar.read_text(encoding='utf-8')

# Check 1: referencia legada removida da secao de Validation Command ativa
vc_section_match = content.split('## Validation Command (Contrato)')
assert len(vc_section_match) >= 2, 'FAIL: secao Validation Command nao encontrada'
vc_section = vc_section_match[1].split('## ')[0]  # apenas a secao de VC
assert 'temp/validate_ar003' not in vc_section, 'FAIL: arquivo de validacao legado ainda referenciado na secao ativa de AR_003'

# Check 2: UUID fixo presente
assert '00000000-0000-0000-0000-000000000001' in content, 'FAIL: UUID fixo nao encontrado no novo validation command'

# Check 3: encontrar code block com sys.path
blocks = content.split('```')
vc_raw = [s for s in blocks if 'sys.path' in s or ('uuid.UUID' in s and 'import' in s)]
assert vc_raw, 'FAIL: nenhum code block com UUID fixo encontrado'

cmd = vc_raw[0].strip()
# Strip "python -c " prefix se presente
if cmd.startswith('python -c '):
    cmd = cmd[len('python -c '):].strip().strip('"')

# Check 4: rodar 3 vezes e verificar determinismo
runs = [
    subprocess.run([sys.executable, '-c', cmd], capture_output=True, text=True, encoding='utf-8')
    for _ in range(3)
]
assert all(r.returncode == 0 for r in runs), f'FAIL: exit nao-zero: {runs[0].stderr[:300]}'
outputs = list(set(r.stdout.strip() for r in runs))
assert len(outputs) == 1, f'FAIL: outputs divergem entre runs (nao-deterministico): {outputs}'
assert 'PASS' in runs[0].stdout, f'FAIL: PASS nao na saida: {runs[0].stdout}'

print('PASS AR_121: AR_003 validation_command corrigido e deterministico')
