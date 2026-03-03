"""Re-executa hb report 200 com a nova validation_command (split-por-linha)."""
import subprocess, sys, os

os.chdir(r"c:\HB TRACK")

validation_command = (
    "python -c \"import os,sys; base='_reports/training'; "
    "ids=['INV-001','INV-002','INV-003','INV-004','INV-005','INV-008','INV-009','INV-030','INV-032','CONTRACT-077-085']; "
    "[sys.exit('FAIL: missing '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if not os.path.exists(base+'/TEST-TRAIN-'+i+'.md')]; "
    "[sys.exit('FAIL: AR Origem ausente em '+base+'/TEST-TRAIN-'+i+'.md') for i in ids if 'AR Origem: AR_200' not in open(base+'/TEST-TRAIN-'+i+'.md',encoding='utf-8').read()]; "
    "t=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); "
    "assert 'v1.7.0' in t,'FAIL: TEST_MATRIX nao bump para v1.7.0'; "
    "inv=[('001','INV-TRAIN-001'),('002','INV-TRAIN-002'),('003','INV-TRAIN-003'),('004','INV-TRAIN-004'),"
    "('005','INV-TRAIN-005'),('008','INV-TRAIN-008'),('009','INV-TRAIN-009'),('030','INV-TRAIN-030'),('032','INV-TRAIN-032')]; "
    "[sys.exit('FAIL: NOT_RUN persiste na linha '+lbl) for _,lbl in inv if any('NOT_RUN' in ln for ln in t.split('\\n') if ln.startswith('| '+lbl+' '))]; "
    "ct_ids=['CONTRACT-TRAIN-077','CONTRACT-TRAIN-078','CONTRACT-TRAIN-079','CONTRACT-TRAIN-080','CONTRACT-TRAIN-081',"
    "'CONTRACT-TRAIN-082','CONTRACT-TRAIN-083','CONTRACT-TRAIN-084','CONTRACT-TRAIN-085']; "
    "[sys.exit('FAIL: NOT_RUN persiste na linha '+c) for c in ct_ids if any('NOT_RUN' in ln for ln in t.split('\\n') if ln.startswith('| '+c+' '))]; "
    "print('PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido')\""
)

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "200", validation_command],
    capture_output=True, text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
sys.exit(result.returncode)
