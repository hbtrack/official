import os, sys
base = '_reports/training'
ids = ['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']

for i in ids:
    path = base + '/TEST-TRAIN-' + i + '.md'
    if not os.path.exists(path):
        sys.exit('FAIL: missing ' + path)

for i in ids:
    path = base + '/TEST-TRAIN-' + i + '.md'
    if 'AR Origem: AR_200' not in open(path, encoding='utf-8').read():
        sys.exit('FAIL: AR Origem ausente em ' + path)

t = open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md', encoding='utf-8').read()
assert 'v1.7.0' in t, 'FAIL: TEST_MATRIX nao bump para v1.7.0'

inv = [('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),
       ('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]

for _, lbl in inv:
    pos = t.find('| ' + lbl)
    if pos != -1 and 'NOT_RUN' in t[pos:pos+450]:
        sys.exit('FAIL: NOT_RUN persiste na linha ' + lbl)

ct_ids = ['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080',
          'CONTRACT-TRAIN-081','CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']

for c in ct_ids:
    pos = t.find('| ' + c)
    if pos != -1 and 'NOT_RUN' in t[pos:pos+450]:
        sys.exit('FAIL: NOT_RUN persiste na linha ' + c)

print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')
