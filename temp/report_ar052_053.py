#!/usr/bin/env python3
"""
Script para reportar AR_052 e AR_053 com novos validation_commands corrigidos.
"""

import subprocess
import sys
from pathlib import Path

def execute_report(ar_id: str, validation_cmd: str) -> bool:
    """Executa hb report para uma AR."""
    print(f"\n🔄 Reportando AR_{ar_id}...")
    print(f"   Comando: {validation_cmd[:80]}...")
    
    # Primeiro, testar o comando
    print(f"\n   🧪 Testando comando...")
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
        print(f"   ❌ Comando falhou:")
        print(f"      {test_result.stderr}")
        return False
    
    print(f"   ✅ Comando passou: {test_result.stdout.strip()}")
    
    # Agora, executar hb report
    print(f"\n   📝 Executando hb report...")
    report_result = subprocess.run(
        ["python", "scripts/run/hb_cli.py", "report", ar_id, validation_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60
    )
    
    if report_result.returncode == 0:
        print(f"   ✅ Report concluído para AR_{ar_id}")
        return True
    else:
        print(f"   ❌ Report falhou:")
        print(f"      {report_result.stderr}")
        return False

def main():
    print("🚀 REPORTANDO ARs CORRIGIDAS\n")
    
    # AR_052
    ar052_cmd = """python -c "import pathlib, psycopg2; p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py')); assert p, 'FAIL: 0055 not found'; c=p[0].read_text(encoding='utf-8'); assert 'revision' in c and '\\"0055\\"' in c, 'FAIL: revision 0055 not found'; assert 'down_revision' in c and '\\"0054\\"' in c, 'FAIL: down_revision 0054 not found'; conn=psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev'); cur=conn.cursor(); cur.execute(\\"SELECT count(*) FROM information_schema.columns WHERE table_name IN ('match_events','competition_matches','competition_opponent_teams','competition_phases','match_roster') AND column_name='deleted_at'\\"); cols=cur.fetchone()[0]; assert cols==5, f'FAIL: expected 5 cols, got {cols}'; cur.execute(\\"SELECT count(*) FROM information_schema.triggers WHERE trigger_name LIKE '%%block_delete%%'\\"); trigs=cur.fetchone()[0]; assert trigs>=24, f'FAIL: expected >=24 triggers, got {trigs}'; cur.execute(\\"SELECT version_num FROM alembic_version\\"); head=cur.fetchone()[0]; conn.close(); print(f'PASS: 0055 verified on head {head} — {cols} cols, {trigs} triggers')"""
    
    # AR_053
    ar053_cmd = "python scripts/run/hb_watch.py --check > nul 2>&1 && echo WATCH_OK"
    
    results = {}
    
    # Executar reports
    results["052"] = execute_report("052", ar052_cmd)
    results["053"] = execute_report("053", ar053_cmd)
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    
    success_count = 0
    for ar_id, success in results.items():
        icon = "✅" if success else "❌"
        print(f"{icon} AR_{ar_id}: {'SUCCESS' if success else 'FAILED'}")
        if success:
            success_count += 1
    
    print(f"\n📈 Total: {success_count}/{len(results)} reportadas com sucesso")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
