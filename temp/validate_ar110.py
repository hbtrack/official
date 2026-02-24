import pathlib, re
src = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8')
m = re.search(r'def cmd_seal.*?(?=\ndef )', src, re.DOTALL)
assert m, 'cmd_seal não encontrada'
fn = m.group(0)
assert 'testador_stamps = re.findall' in fn, 'Regex de extração ausente'
assert 'E_SEAL_MULTIPLE_TESTADOR_STAMPS' in fn, 'Constante não usada em cmd_seal'
assert 'len(testador_stamps) > 1' in fn, 'Check múltiplos carimbos ausente'
assert '🔴 REJEITADO' in fn or 'REJEITADO' in fn, 'Check REJEITADO ausente'
idx_check = fn.find('testador_stamps = re.findall')
idx_old = fn.find('if "✅ SUCESSO" not in ar_content')
assert idx_check < idx_old if idx_old > 0 else True, 'Checks devem vir ANTES do check original'
print('PASS: cmd_seal guarda anti-múltiplos-carimbos implementada')
