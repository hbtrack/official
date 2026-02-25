import pathlib

p = pathlib.Path('docs/_canon/context_map.md')
assert p.exists(), 'FAIL: docs/_canon/context_map.md nao existe'
c = p.read_text(encoding='utf-8')
lines = [l for l in c.splitlines() if l.strip()]
assert len(lines) >= 20, f'FAIL: context_map.md muito curto ({len(lines)} linhas nao-vazias, minimo 20)'
assert any('Governance' in l or 'governance' in l for l in lines), 'FAIL: secao Governance ausente'
assert any('Feature' in l or 'feature' in l for l in lines), 'FAIL: secao Features ausente'
assert ('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c), 'FAIL: cabeçalho context map ausente'
print(f'PASS AR_059: context_map.md existe com {len(lines)} linhas e secoes obrigatorias')
