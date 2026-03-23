#!/usr/bin/env python3
"""
Executar auditoria de completude de domínio contra todos os 17 módulos.
Gera relatório consolidado com resultados comparativos.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import yaml

# Adicionar scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.run_domain_completeness import DomainCompletenessAuditor


def load_module_registry() -> List[str]:
    """Carregar lista de módulos do MODULE_REGISTRY.yaml"""
    registry_path = Path(__file__).parent.parent.parent / "docs/_canon/MODULE_REGISTRY.yaml"
    
    with open(registry_path, 'r') as f:
        data = yaml.safe_load(f)
    
    modules = list(data.get("modules", {}).keys())
    return sorted(modules)


def run_all_modules_audit() -> Dict[str, Dict]:
    """Executar auditoria para todos os módulos"""
    modules = load_module_registry()
    results = {}
    
    print(f"\n{'='*80}")
    print(f"AUDITORIA DE COMPLETUDE — 17 MÓDULOS")
    print(f"{'='*80}\n")
    
    for i, module in enumerate(modules, 1):
        print(f"[{i:2d}/17] Auditando módulo: {module.upper():<20}", end=" ", flush=True)
        
        try:
            auditor = DomainCompletenessAuditor(
                Path(__file__).parent.parent.parent,
                module=module,
                task_type="new_contract"
            )
            passed = auditor.run()
            
            results[module] = {
                "passed": passed,
                "dc1_determinism": auditor.result.dc1_determinism,
                "dc2_artifacts": auditor.result.dc2_artifacts,
                "dc3_boundary": auditor.result.dc3_boundary,
                "dc4_gaps": auditor.result.dc4_gaps,
                "dc5_handoff": auditor.result.dc5_handoff,
                "final_status": auditor.result.final_status,
                "correct_blocks": auditor.result.correct_blocks,
                "total_blocks": auditor.result.total_blocks,
                "silent_gaps": len(auditor.result.silent_gaps),
                "inference_count": auditor.result.inference_count,
            }
            
            status_icon = "✓ PASS" if passed else "✗ FAIL"
            print(status_icon)
            
        except Exception as e:
            results[module] = {
                "passed": False,
                "error": str(e),
                "final_status": "ERROR"
            }
            print(f"✗ ERROR: {str(e)[:40]}")
    
    return results


def generate_consolidated_report(results: Dict[str, Dict]) -> str:
    """Gerar relatório consolidado em markdown"""
    
    # Contar resultados
    total = len(results)
    passed = sum(1 for r in results.values() if r.get("passed", False))
    failed = total - passed
    
    # Organizar por status
    passed_modules = sorted([m for m, r in results.items() if r.get("passed")])
    failed_modules = sorted([m for m, r in results.items() if not r.get("passed")])
    
    # Detalhar por critério
    dc1_pass = sum(1 for r in results.values() if r.get("dc1_determinism"))
    dc2_pass = sum(1 for r in results.values() if r.get("dc2_artifacts"))
    dc3_pass = sum(1 for r in results.values() if r.get("dc3_boundary"))
    dc4_pass = sum(1 for r in results.values() if r.get("dc4_gaps"))
    dc5_pass = sum(1 for r in results.values() if r.get("dc5_handoff"))
    
    report = []
    report.append("╔════════════════════════════════════════════════════════════════════════════╗")
    report.append("║       AUDITORIA DE COMPLETUDE — 17 MÓDULOS HB TRACK                       ║")
    report.append("╚════════════════════════════════════════════════════════════════════════════╝")
    report.append(f"\nData: {datetime.now().isoformat()}")
    report.append(f"Executor: run_all_modules_audit.py v1.0.0")
    report.append(f"Total de módulos: {total}")
    report.append("")
    
    # Sumário executivo
    report.append("SUMÁRIO EXECUTIVO")
    report.append("─" * 80)
    report.append(f"✓ PASS: {passed}/{total} módulos ({100*passed//total}%)")
    report.append(f"✗ FAIL: {failed}/{total} módulos ({100*failed//total}%)")
    report.append("")
    
    # Resultados por critério
    report.append("DESEMPENHO POR CRITÉRIO")
    report.append("─" * 80)
    report.append(f"DC1 (Determinismo):    {dc1_pass:2d}/{total} PASS ({100*dc1_pass//total:3d}%)")
    report.append(f"DC2 (Artefatos):       {dc2_pass:2d}/{total} PASS ({100*dc2_pass//total:3d}%)")
    report.append(f"DC3 (Boundary):        {dc3_pass:2d}/{total} PASS ({100*dc3_pass//total:3d}%)")
    report.append(f"DC4 (Gaps):            {dc4_pass:2d}/{total} PASS ({100*dc4_pass//total:3d}%)")
    report.append(f"DC5 (Handoff):         {dc5_pass:2d}/{total} PASS ({100*dc5_pass//total:3d}%)")
    report.append("")
    
    # Lista de módulos PASS
    if passed_modules:
        report.append("MÓDULOS APROVADOS (PASS)")
        report.append("─" * 80)
        for i, module in enumerate(passed_modules, 1):
            r = results[module]
            report.append(f"✓ {i:2d}. {module.upper():20} — 5/5 critérios")
        report.append("")
    
    # Lista de módulos FAIL
    if failed_modules:
        report.append("MÓDULOS REPROVADOS (FAIL)")
        report.append("─" * 80)
        for i, module in enumerate(failed_modules, 1):
            r = results[module]
            if "error" in r:
                report.append(f"✗ {i:2d}. {module.upper():20} — ERROR: {r['error'][:50]}")
            else:
                # Contar quantos critérios passaram
                num_pass = sum([
                    r.get("dc1_determinism"),
                    r.get("dc2_artifacts"),
                    r.get("dc3_boundary"),
                    r.get("dc4_gaps"),
                    r.get("dc5_handoff"),
                ])
                report.append(f"✗ {i:2d}. {module.upper():20} — {num_pass}/5 critérios")
        report.append("")
    
    # Tabela de critérios
    report.append("MATRIZ DE RESULTADOS")
    report.append("─" * 80)
    report.append("módulo               │ DC1 │ DC2 │ DC3 │ DC4 │ DC5 │ Final")
    report.append("─" * 80)
    
    for module in sorted(results.keys()):
        r = results[module]
        if "error" in r:
            status = "ERROR"
            dc1 = dc2 = dc3 = dc4 = dc5 = "E"
        else:
            status = "PASS" if r.get("passed") else "FAIL"
            dc1 = "✓" if r.get("dc1_determinism") else "✗"
            dc2 = "✓" if r.get("dc2_artifacts") else "✗"
            dc3 = "✓" if r.get("dc3_boundary") else "✗"
            dc4 = "✓" if r.get("dc4_gaps") else "✗"
            dc5 = "✓" if r.get("dc5_handoff") else "✗"
        
        report.append(f"{module.upper():20} │ {dc1} │ {dc2} │ {dc3} │ {dc4} │ {dc5} │ {status}")
    
    report.append("─" * 80)
    report.append(f"\nLegenda: ✓ = PASS, ✗ = FAIL, E = ERROR")
    report.append("")
    
    # Estatísticas gerais
    report.append("ESTATÍSTICAS GERAIS")
    report.append("─" * 80)
    total_blocks = sum(r.get("total_blocks", 0) for r in results.values())
    correct_blocks = sum(r.get("correct_blocks", 0) for r in results.values())
    total_gaps = sum(r.get("silent_gaps", 0) for r in results.values())
    total_inferences = sum(r.get("inference_count", 0) for r in results.values())
    
    report.append(f"Bloqueios corretos: {correct_blocks}/{total_blocks}")
    report.append(f"Lacunas silenciosas: {total_gaps}")
    report.append(f"Inferências necessárias: {total_inferences}")
    report.append("")
    
    report.append("════════════════════════════════════════════════════════════════════════════════")
    report.append("")
    
    return "\n".join(report)


def main():
    """Executar auditoria completa"""
    workspace_root = Path(__file__).parent.parent.parent
    
    # Executar auditorias
    results = run_all_modules_audit()
    
    # Gerar relatório
    report = generate_consolidated_report(results)
    print("\n" + report)
    
    # Salvar em markdown
    reports_dir = workspace_root / "_reports"
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Markdown report
    report_file = reports_dir / f"DOMAIN_COMPLETENESS_ALL_MODULES_{timestamp}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    # JSON report
    json_file = reports_dir / f"DOMAIN_COMPLETENESS_ALL_MODULES_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Relatório salvo: {report_file}")
    print(f"📊 JSON salvo: {json_file}")
    
    # Retornar código de saída baseado em sucesso
    passed = sum(1 for r in results.values() if r.get("passed", False))
    total = len(results)
    
    if passed == total:
        print(f"\n✅ SUCESSO: Todos os {total} módulos passaram!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} módulos falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
