import sys, re
c = open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md', encoding='utf-8').read()
g = re.findall(r'(?m)^status:\s*(GAP|PARCIAL|DIVERGENTE_DO_SSOT)', c)
if g:
    print(f'FAIL: {len(g)} still not promoted: {sorted(set(g))}')
else:
    print('PASS: all invariants IMPLEMENTADO')
v = re.search(r'Vers\u00e3o:\s*v(\S+)', c)
vok = v and v.group(1) == '1.5.0'
if not vok:
    print('FAIL: version not v1.5.0, found ' + str(v.group(0) if v else 'NONE'))
else:
    print('PASS: version v1.5.0 ok')
tr = 'Promovido por Kanban+evidencia: AR_' in c
if not tr:
    print('FAIL: no traceability note found')
else:
    print('PASS: traceability note present')
sys.exit(len(g) + (0 if vok else 1) + (0 if tr else 1))
