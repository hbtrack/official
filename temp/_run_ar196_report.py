"""Helper: roda hb report 196 com validation_command canônico."""
import subprocess, sys, os

os.chdir(r'c:\HB TRACK')

validation_command = (
    "python -c \""
    "import re,sys;e=[];"
    "b=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read();"
    "n_pend=len(re.findall(r'AR-TRAIN-0[12][0-9].*PENDENTE',b));"
    "e+=[f'FAIL backlog still has {n_pend} PENDENTE AR-TRAINs'] if n_pend>0 else [None];"
    "inv=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();"
    "seg40=inv[inv.index('INV-TRAIN-040'):inv.index('INV-TRAIN-040')+300] if 'INV-TRAIN-040' in inv else '';"
    "seg41=inv[inv.index('INV-TRAIN-041'):inv.index('INV-TRAIN-041')+300] if 'INV-TRAIN-041' in inv else '';"
    "e+=['FAIL INV-040 still PARCIAL'] if 'PARCIAL' in seg40 else [None];"
    "e+=['FAIL INV-041 still PARCIAL'] if 'PARCIAL' in seg41 else [None];"
    "sc=open('docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md',encoding='utf-8').read();"
    "seg13=sc[sc.index('SCREEN-TRAIN-013'):sc.index('SCREEN-TRAIN-013')+400] if 'SCREEN-TRAIN-013' in sc else '';"
    "e+=['FAIL SCREEN-013 still BLOQUEADO'] if 'BLOQUEADO' in seg13 else [None];"
    "ct=open('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md',encoding='utf-8').read();"
    "g91=len(re.findall(r'CONTRACT-TRAIN-09[1-5].*GAP',ct));"
    "e+=[f'FAIL CONTRACT-091..095 GAP={g91}'] if g91>0 else [None];"
    "errs=[x for x in e if x];"
    "[print(x) for x in errs];"
    "print('PASS: all AC checks ok') if not errs else None;"
    "sys.exit(len(errs))\""
)

result = subprocess.run(
    [sys.executable, 'scripts/run/hb_cli.py', 'report', '196', validation_command],
    capture_output=False,
    text=True,
    cwd=r'c:\HB TRACK',
    env={**os.environ, 'PYTHONUTF8': '1'}
)

sys.exit(result.returncode)
