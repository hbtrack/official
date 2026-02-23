#!/usr/bin/env python3
"""
Reportar AR_050 e AR_064 após correções.
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

def test_and_report(ar_id: str, ar_file: Path) -> bool:
    """Testa e reporta uma AR."""
    print(f"\n{'='*80}")
    print(f"🔧 AR_{ar_id}")
    print('='*80)
    
    # Extrair comando
    print("📋 Extraindo validation_command...")
    validation_cmd = extract_validation_command(ar_file)
    print(f"✅ Comando extraído ({len(validation_cmd)} chars)")
    
    # Testar
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
        print(f"❌ Teste falhou (exit={test_result.returncode}):")
        print(f"   {test_result.stderr}")
        return False
    
    print(f"✅ Teste passou: {test_result.stdout.strip()}")
    
    # Reportar
    print("\n📝 Executando hb report...")
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
        return True
    else:
        print(f"❌ Report falhou:")
        print(f"   {report_result.stderr[:500]}")
        return False

def main():
    print("🚀 FINALIZANDO ARs PENDENTES\n")
    
    # AR_050
    ar050_file = Path("docs/hbtrack/ars/drafts/AR_050_wellness_documentar_decisão_de_escala_0-10_e_corri.md")
    success_050 = test_and_report("050", ar050_file)
    
    # AR_064
    ar064_file = Path("docs/hbtrack/ars/drafts/AR_064_cleanup_rogue__agent_,_agentes_,_.github_cont_+_re.md")
    
    # Limpar _agent primeiro
    print(f"\n{'='*80}")
    print("🧹 AR_064 - Limpando diretório _agent")
    print('='*80)
    
    agent_path = Path("docs/_canon/_agent")
    if agent_path.exists():
        print(f"📁 Diretório encontrado: {agent_path}")
        print("🗑️ Removendo recursivamente...")
        import shutil
        try:
            shutil.rmtree(agent_path)
            print("✅ Diretório removido com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao remover: {e}")
    else:
        print(f"✅ Diretório já não existe: {agent_path}")
    
    success_064 = test_and_report("064", ar064_file)
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    
    results = {
        "050": success_050,
        "064": success_064
    }
    
    for ar_id, success in results.items():
        icon = "✅" if success else "❌"
        print(f"{icon} AR_{ar_id}: {'SUCCESS' if success else 'FAILED'}")
    
    success_count = sum(results.values())
    print(f"\n📈 Total: {success_count}/{len(results)} reportadas com sucesso")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
