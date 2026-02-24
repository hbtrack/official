import pathlib
src = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')
assert 'E_SEAL_MULTIPLE_TESTADOR_STAMPS' in src, 'Constante ausente'
assert '# Seal abort:' in src or '# múltiplos carimbos' in src.lower(), 'Comentário ausente'
lines = [i for i, line in enumerate(src.split('\n')) if 'E_SEAL_MULTIPLE_TESTADOR_STAMPS' in line]
assert lines, 'Constante não encontrada'
assert lines[0] < 200, 'Constante deve estar no bloco de Exit Codes (top 200 linhas)'
print('PASS: E_SEAL_MULTIPLE_TESTADOR_STAMPS adicionada')