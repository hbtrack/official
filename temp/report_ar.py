#!/usr/bin/env python3
"""
Reportar uma AR extraindo o validation_command do arquivo.
Usage: python report_ar.py <ar_id>
"""

import subprocess
import sys
import re
from pathlib import Path

def find_ar_file(ar_id: str) -> Path:
    """Encontra o arquivo da AR."""
    ar_dir = Path("docs/hbtrack/ars")
    ar_files = list(ar_dir.rglob(f"AR_{ar_id}_*.md"))
    if not ar_files:
        raise FileNotFoundError(f"AR_{ar_id} not found")
    return ar_files[0]

def extract_validation_command(ar_file: Path) -> str:
    """Extrai o validation_command da AR."""
    content = ar_file.read_text(encoding="utf-8")
    match = re.search(r"## Validation Command \(Contrato\)\n```\n(.+?)\n```", content, re.DOTALL)
    if not match:
        raise ValueError(f"No validation command found in {ar_file.name}")
    return match.group(1).strip()

def main():
    if len(sys.argv) != 2:
        print("Usage: python report_ar.py <ar_id>")
        return 1
    
    ar_id = sys.argv[1]
    
    print(f"🔍 Buscando AR_{ar_id}...")
    ar_file = find_ar_file(ar_id)
    print(f"✅ Encontrado: {ar_file.name}")
    
    print(f"\n📋 Extraindo validation_command...")
    validation_cmd = extract_validation_command(ar_file)
    print(f"✅ Comando extraído ({len(validation_cmd)} chars)")
    
    # Testar o comando primeiro
    print(f"\n🧪 Testando comando...")
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
    print(f"\n📝 Executando hb report {ar_id}...")
    report_result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    
    if report_result.returncode == 0:
        print(f"✅ Report concluído para AR_{ar_id}")
        print(report_result.stdout)
        return 0
    else:
        print(f"❌ Report falhou:")
        print(report_result.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
