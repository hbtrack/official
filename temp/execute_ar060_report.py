#!/usr/bin/env python
"""Executa hb report para AR_060 lendo o comando exato da AR."""
import subprocess
import sys
import re
from pathlib import Path

# Lê a AR para extrair o validation command exato
ar_path = Path('docs/hbtrack/ars/features/AR_060_verificar_integridade_do_contrato_openapi_ssot_214.md')
ar_content = ar_path.read_text(encoding='utf-8')

# Extrai o validation command da AR (entre os backticks de código)
match = re.search(r'## Validation Command \(Contrato\)\s*```\s*\n(.*?)\n```', ar_content, re.DOTALL)
if not match:
    print("ERRO: Não foi possível extrair o validation command da AR")
    sys.exit(1)

validation_cmd = match.group(1).strip()
print(f"Validation command extraído: {validation_cmd[:80]}...")

# Executa hb report com o comando exato  
result = subprocess.run(
    ['python', 'scripts/run/hb_cli.py', 'report', '060', validation_cmd],
    cwd=Path.cwd()
)

sys.exit(result.returncode)
