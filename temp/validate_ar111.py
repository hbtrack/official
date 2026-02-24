import pathlib, re
src = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')
m = re.search(r'def cmd_verify.*?(?=\ndef )', src, re.DOTALL)
assert m, 'cmd_verify nao encontrada'
fn = m.group(0)
assert re.search(r're\.sub.*Verificacao Testador', fn), 'Regex de limpeza ausente'
assert 're.DOTALL' in fn or 'flags=re.DOTALL' in fn, 'Flag DOTALL ausente'
assert 'Remover carimbos anteriores' in fn or 'idempotencia' in fn.lower() or 'idempot' in fn.lower(), 'Comentario ausente'
idx_clean = fn.find('re.sub')
idx_append = fn.find('ar_updated + stamp') if 'ar_updated + stamp' in fn else fn.find('ar_updated +')
assert idx_clean < idx_append if idx_append > 0 else True, 'Limpeza deve vir ANTES do append'
print('PASS: cmd_verify limpeza de carimbos antigos implementada')
