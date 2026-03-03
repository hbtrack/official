"""Executa hb report 201 com a validation_command canônica da AR_201."""
import subprocess, sys, os

os.chdir(r"c:\HB TRACK")

validation_command = (
    "python -c \"import sys; "
    "ar200=open('docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md',encoding='utf-8').read(); "
    "assert '+450' not in ar200,'FAIL: janela 450 ainda presente em AR_200'; "
    "assert 'split' in ar200,'FAIL: split-por-linha ausente em AR_200'; "
    "log=open('docs/hbtrack/evidence/AR_200/executor_main.log',encoding='utf-8').read(); "
    "assert 'Exit Code: 0' in log,'FAIL: executor_main.log AR_200 nao tem Exit Code: 0'; "
    "assert 'PASS: 10 evidencias' in log,'FAIL: PASS ausente em executor_main.log AR_200'; "
    "print('PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0')\""
)

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "201", validation_command],
    capture_output=True, text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
sys.exit(result.returncode)
