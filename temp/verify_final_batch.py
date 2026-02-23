#!/usr/bin/env python3
"""
Verificação final do lote completo de ARs.
"""

import subprocess
import sys
from pathlib import Path

# Lote completo: 8 ARs anteriores + 2 novas
FINAL_BATCH = ["046", "048", "049", "050", "051", "052", "053", "054", "055", "064"]

def run_verify(ar_id: str) -> dict:
    """Executa hb verify para uma AR e retorna resultado."""
    print(f"\n🔬 Verificando AR_{ar_id}...")
    
    result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "verify", ar_id],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180
    )
    
    output = result.stdout + result.stderr
    
    # Parsear resultado
    if "✅ VERIFICADO" in output:
        status = "VERIFICADO"
        icon = "✅"
    elif "⚠️ PENDENTE" in output:
        status = "PENDENTE"
        icon = "⚠️"
    elif "REJEITADO" in output:
        status = "REJEITADO"
        icon = "❌"
    elif "E_VERIFY_NOT_READY" in output:
        status = "NOT_READY"
        icon = "🚫"
    else:
        status = "UNKNOWN"
        icon = "❓"
    
    print(f"{icon} AR_{ar_id}: {status}")
    
    if status not in ["VERIFICADO", "NOT_READY"]:
        # Mostrar mais detalhes para falhas
        lines = output.split('\n')
        for line in lines:
            if 'Reason' in line or 'FAIL' in line or 'Consistency' in line:
                print(f"   {line.strip()}")
    
    return {
        "ar_id": ar_id,
        "status": status,
        "exit_code": result.returncode,
        "output": output
    }

def main():
    print("🚀 VERIFICAÇÃO FINAL - LOTE COMPLETO")
    print(f"📋 ARs a verificar: {', '.join(FINAL_BATCH)}")
    print(f"📊 Total: {len(FINAL_BATCH)} ARs\n")
    print("="*80)
    
    results = []
    
    for ar_id in FINAL_BATCH:
        try:
            result = run_verify(ar_id)
            results.append(result)
        except subprocess.TimeoutExpired:
            print(f"⏱️ AR_{ar_id}: TIMEOUT")
            results.append({
                "ar_id": ar_id,
                "status": "TIMEOUT",
                "exit_code": -1,
                "output": ""
            })
        except Exception as e:
            print(f"💥 AR_{ar_id}: ERROR - {e}")
            results.append({
                "ar_id": ar_id,
                "status": "ERROR",
                "exit_code": -1,
                "output": str(e)
            })
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO FINAL — AUDITORIA COMPLETA")
    print("="*80)
    
    verificadas = [r for r in results if r["status"] == "VERIFICADO"]
    pendentes = [r for r in results if r["status"] == "PENDENTE"]
    rejeitadas = [r for r in results if r["status"] == "REJEITADO"]
    not_ready = [r for r in results if r["status"] == "NOT_READY"]
    errors = [r for r in results if r["status"] in ["TIMEOUT", "ERROR", "UNKNOWN"]]
    
    print(f"\n✅ VERIFICADAS: {len(verificadas)}/{len(FINAL_BATCH)}")
    for r in verificadas:
        print(f"   • AR_{r['ar_id']}")
    
    if pendentes:
        print(f"\n⚠️ PENDENTES: {len(pendentes)}")
        for r in pendentes:
            print(f"   • AR_{r['ar_id']}")
    
    if rejeitadas:
        print(f"\n❌ REJEITADAS: {len(rejeitadas)}")
        for r in rejeitadas:
            print(f"   • AR_{r['ar_id']}")
    
    if not_ready:
        print(f"\n🚫 NOT READY: {len(not_ready)}")
        for r in not_ready:
            print(f"   • AR_{r['ar_id']}")
    
    if errors:
        print(f"\n💥 ERROS: {len(errors)}")
        for r in errors:
            print(f"   • AR_{r['ar_id']}: {r['status']}")
    
    # Estatísticas
    success_rate = (len(verificadas) * 100) // len(FINAL_BATCH)
    print(f"\n📈 Taxa de Sucesso: {len(verificadas)}/{len(FINAL_BATCH)} ({success_rate}%)")
    
    # Mensagem final baseada no resultado
    if len(verificadas) == len(FINAL_BATCH):
        print("\n🎉 PERFEITO! Todas as ARs verificadas com sucesso!")
        print("✅ Sistema pronto para commit e deploy.")
        return 0
    elif success_rate >= 80:
        print(f"\n✅ BOA! {success_rate}% de sucesso.")
        print(f"⚠️ {len(FINAL_BATCH) - len(verificadas)} AR(s) pendente(s).")
        return 1
    else:
        print(f"\n⚠️ Apenas {success_rate}% de sucesso.")
        print("❌ Requer atenção do Arquiteto.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
