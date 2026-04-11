#!/usr/bin/env python3
"""
adversarial_analysis_gate.py
Gate ADVERSARIAL_ANALYSIS_GATE — verifica relatórios de análise adversarial.

Lógica:
  - SKIP_NOT_APPLICABLE: _reports/adversarial/ não existe ou está vazia
  - PASS: todos os relatórios .adversarial.json encontrados têm overall_status=PASS
  - FAIL (BLOCKED_ADVERSARIAL_PENDING): qualquer relatório com overall_status!=PASS

Usado como standalone ou importado por validate_contracts.py.
"""
from __future__ import annotations

import json
import pathlib
import time


GATE_ID = "ADVERSARIAL_ANALYSIS_GATE"
BLOCKING_CODE = "BLOCKED_ADVERSARIAL_PENDING"


def run_gate(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    reports_dir = root / "_reports" / "adversarial"

    if not reports_dir.exists():
        return _result("SKIP_NOT_APPLICABLE",
                       "_reports/adversarial/ ausente — nenhum módulo submetido à análise adversarial.",
                       [], [], t0)

    report_files = list(reports_dir.rglob("*.adversarial.json"))
    if not report_files:
        return _result("SKIP_NOT_APPLICABLE",
                       "_reports/adversarial/ vazia — nenhum relatório adversarial encontrado.",
                       [], [], t0)

    checked = [str(p) for p in report_files]
    violations: list[dict] = []

    for rpath in report_files:
        try:
            data = json.loads(rpath.read_text(encoding="utf-8"))
        except Exception as e:
            violations.append({
                "blocking_code": BLOCKING_CODE,
                "artifact": str(rpath.relative_to(root)),
                "message": f"Relatório adversarial não pôde ser lido: {e}",
                "severity": "error",
            })
            continue

        overall = data.get("overall_status")
        if overall != "PASS":
            module = data.get("module", "?")
            resource = data.get("resource", "?")
            findings = data.get("critical_findings", [])
            msg = (f"Análise adversarial FAIL: módulo={module}, recurso={resource}, "
                   f"status={overall}, achados_críticos={len(findings)}")
            violations.append({
                "blocking_code": BLOCKING_CODE,
                "artifact": str(rpath.relative_to(root)),
                "message": msg,
                "severity": "error",
            })

    if violations:
        return _result("FAIL",
                       f"Análise adversarial: {len(violations)} relatório(s) com FAIL — "
                       "handoff para implementação bloqueado.",
                       checked, violations, t0)

    return _result("PASS",
                   f"Análise adversarial: {len(report_files)} relatório(s) — todos PASS.",
                   checked, [], t0)


def _ms(t0: float) -> int:
    return int((time.monotonic() - t0) * 1000)


def _result(status: str, summary: str, checked: list, violations: list, t0: float) -> dict:
    blocking = status == "FAIL"
    return {
        "gate_id": GATE_ID,
        "status": status,
        "blocking": blocking,
        "blocking_code": BLOCKING_CODE if blocking else None,
        "summary": summary,
        "inputs": [],
        "artifacts_checked": checked,
        "evidence_files": [],
        "violations": violations,
        "metrics": {
            "errors": len(violations),
            "warnings": 0,
            "violations": len(violations),
            "duration_ms": _ms(t0),
        },
    }


if __name__ == "__main__":
    import sys
    root = pathlib.Path(__file__).resolve().parents[3]
    result = run_gate(root)
    status = result["status"]
    print(f"[{status}] {GATE_ID}: {result['summary']}")
    sys.exit(0 if status in ("PASS", "SKIP_NOT_APPLICABLE") else 1)
