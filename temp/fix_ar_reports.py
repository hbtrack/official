#!/usr/bin/env python3
"""
Script de emergência para reportar ARs bloqueadas que já foram executadas
mas não receberam o carimbo de sucesso do Executor.

Workflow:
1. Lê cada AR
2. Extrai o validation_command
3. Testa se o comando passa
4. Se passar, executa hb report para carimbar
"""

import subprocess
import sys
import re
from pathlib import Path

# ARs que precisam de report (conforme erro E_VERIFY_NOT_READY)
BLOCKED_ARS = ["046", "048", "049", "050", "051", "052", "054", "055", "064"]

def find_ar_file(ar_id: str, ar_dir: Path) -> Path:
    """Encontra arquivo AR por ID (busca recursiva)."""
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

def test_validation_command(cmd: str) -> tuple[int, str, str]:
    """Executa o validation command e retorna (exit_code, stdout, stderr)."""
    print(f"  🧪 Testando: {cmd[:80]}...")
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True, 
        encoding="utf-8", 
        errors="replace",
        timeout=30
    )
    return result.returncode, result.stdout, result.stderr

def run_hb_report(ar_id: str, validation_cmd: str) -> bool:
    """Executa hb report com o validation_command."""
    print(f"  📝 Executando hb report {ar_id}...")
    result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    
    if result.returncode == 0:
        print(f"  ✅ Report concluído para AR_{ar_id}")
        return True
    else:
        print(f"  ❌ Falha no report AR_{ar_id}:")
        print(f"     {result.stderr}")
        return False

def main():
    repo_root = Path(__file__).resolve().parent.parent
    ar_dir = repo_root / "docs" / "hbtrack" / "ars"
    
    print("🚨 SCRIPT DE EMERGÊNCIA: Fix AR Reports")
    print(f"📁 AR Directory: {ar_dir}\n")
    
    results = {}
    
    for ar_id in BLOCKED_ARS:
        print(f"\n🔍 Processando AR_{ar_id}...")
        
        try:
            # 1. Encontrar AR
            ar_file = find_ar_file(ar_id, ar_dir)
            print(f"  📄 Encontrado: {ar_file.relative_to(repo_root)}")
            
            # 2. Extrair validation_command
            validation_cmd = extract_validation_command(ar_file)
            print(f"  🔧 Validation command extraído ({len(validation_cmd)} chars)")
            
            # 3. Testar comando
            exit_code, stdout, stderr = test_validation_command(validation_cmd)
            
            if exit_code == 0:
                print(f"  ✅ Validação PASSOU")
                print(f"     Output: {stdout[:100]}")
                
                # 4. Executar hb report
                success = run_hb_report(ar_id, validation_cmd)
                results[ar_id] = "SUCCESS" if success else "REPORT_FAILED"
            else:
                print(f"  ❌ Validação FALHOU (exit={exit_code})")
                print(f"     Stderr: {stderr[:200]}")
                results[ar_id] = f"VALIDATION_FAILED (exit={exit_code})"
                
        except Exception as e:
            print(f"  💥 ERRO: {type(e).__name__}: {e}")
            results[ar_id] = f"ERROR: {e}"
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO DOS REPORTS")
    print("="*80)
    
    success_count = 0
    failed_count = 0
    
    for ar_id, status in results.items():
        icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{icon} AR_{ar_id}: {status}")
        if status == "SUCCESS":
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\n📈 Total: {success_count} sucesso(s), {failed_count} falha(s)")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
