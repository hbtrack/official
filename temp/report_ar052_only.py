#!/usr/bin/env python3
"""
Extrai o validation_command da AR_052 e executa hb report com ele.
"""

import subprocess
import sys
import re
from pathlib import Path

def extract_validation_command(ar_file: Path) -> str:
    """Extrai o validation_command da AR."""
    content = ar_file.read_text(encoding="utf-8")
    match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
    if not match:
        raise ValueError(f"No validation command found in {ar_file.name}")
    return match.group(1).strip()

def main():
    ar_file = Path("docs/hbtrack/ars/drafts/AR_052_ar_008_re-validação_evidence_pack_3-camadas_para_m.md")
    
    print("🔍 Extraindo validation_command da AR_052...")
    validation_cmd = extract_validation_command(ar_file)
    print(f"✅ Comando extraído ({len(validation_cmd)} chars)")
    
    # Testar o comando primeiro
    print("\n🧪 Testando comando...")
    test_result = subprocess.run(
        validation_cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )
    
    if test_result.returncode != 0:
        print(f"❌ Comando falhou:")
        print(f"   {test_result.stderr}")
        return 1
    
    print(f"✅ Comando passou: {test_result.stdout.strip()}")
    
    # Executar hb report
    print("\n📝 Executando hb report 052...")
    report_result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "report", "052", validation_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    
    if report_result.returncode == 0:
        print("✅ Report concluído para AR_052")
        print(report_result.stdout)
        return 0
    else:
        print("❌ Report falhou:")
        print(report_result.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
