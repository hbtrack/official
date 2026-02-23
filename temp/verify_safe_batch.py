#!/usr/bin/env python3
"""
Verifica o lote seguro de ARs que já têm o carimbo ✅ SUCESSO.
"""

import subprocess
import sys
from pathlib import Path

# Lote seguro: ARs que foram reportadas com sucesso
SAFE_BATCH = ["046", "048", "049", "051", "052", "053", "054", "055"]

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
    print("🚀 VERIFICAÇÃO DO LOTE SEGURO")
    print(f"📋 ARs a verificar: {', '.join(SAFE_BATCH)}\n")
    print("="*80)
    
    results = []
    
    for ar_id in SAFE_BATCH:
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
    print("📊 RESUMO FINAL")
    print("="*80)
    
    verificadas = [r for r in results if r["status"] == "VERIFICADO"]
    pendentes = [r for r in results if r["status"] == "PENDENTE"]
    rejeitadas = [r for r in results if r["status"] == "REJEITADO"]
    not_ready = [r for r in results if r["status"] == "NOT_READY"]
    errors = [r for r in results if r["status"] in ["TIMEOUT", "ERROR", "UNKNOWN"]]
    
    print(f"✅ VERIFICADAS: {len(verificadas)}")
    for r in verificadas:
        print(f"   AR_{r['ar_id']}")
    
    if pendentes:
        print(f"\n⚠️ PENDENTES: {len(pendentes)}")
        for r in pendentes:
            print(f"   AR_{r['ar_id']}")
    
    if rejeitadas:
        print(f"\n❌ REJEITADAS: {len(rejeitadas)}")
        for r in rejeitadas:
            print(f"   AR_{r['ar_id']}")
    
    if not_ready:
        print(f"\n🚫 NOT READY: {len(not_ready)}")
        for r in not_ready:
            print(f"   AR_{r['ar_id']}")
    
    if errors:
        print(f"\n💥 ERROS: {len(errors)}")
        for r in errors:
            print(f"   AR_{r['ar_id']}: {r['status']}")
    
    print(f"\n📈 Taxa de Sucesso: {len(verificadas)}/{len(SAFE_BATCH)} ({100*len(verificadas)//len(SAFE_BATCH)}%)")
    
    # Exit code baseado no sucesso
    if len(verificadas) == len(SAFE_BATCH):
        print("\n🎉 PERFEITO! Todas as ARs verificadas com sucesso!")
        return 0
    elif len(verificadas) > 0:
        print(f"\n⚠️ {len(verificadas)} ARs verificadas, {len(SAFE_BATCH) - len(verificadas)} pendentes.")
        return 1
    else:
        print("\n❌ Nenhuma AR foi verificada com sucesso.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
