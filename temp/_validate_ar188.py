c = open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md', encoding='utf-8').read()
assert '2026-03-01' in c, 'header data nao atualizada'
assert '| AR-TRAIN-006 |' in c
lines = [l for l in c.splitlines() if '| AR-TRAIN-006 |' in l]
assert 'VERIFICADO' in lines[0], 'AR-TRAIN-006 nao VERIFICADO em secao 9'
lines6 = [l for l in c.splitlines() if 'FLOW-TRAIN-012' in l]
assert all('BLOQUEADO' not in l for l in lines6), 'FLOW-TRAIN-012 ainda BLOQUEADO'
lines7 = [l for l in c.splitlines() if 'SCREEN-TRAIN-013' in l]
assert all('BLOQUEADO' not in l for l in lines7), 'SCREEN-TRAIN-013 ainda BLOQUEADO'
lines8 = [l for l in c.splitlines() if 'CONTRACT-TRAIN-086' in l]
assert all('BLOQUEADO' not in l for l in lines8), 'CONTRACT-TRAIN-086 ainda BLOQUEADO'
assert 'v1.4.0' in c, 'changelog v1.4.0 nao adicionado'
print('PASS AR_188')
