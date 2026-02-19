from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Any, Dict, Optional, Set


def _print_and(code: int, msg: str) -> int:
    print(msg)
    return code


def load_yaml(path: str) -> Optional[Dict[str, Any]]:
    # P0: não crashar se PyYAML não existir
    try:
        import yaml  # type: ignore
    except Exception:
        return None

    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def run_check_audit_pack(run_id: str, root: str) -> int:
    # Evita problemas de PYTHONPATH (determinístico via subprocess)
    cmd = [sys.executable, "scripts/checks/check_audit_pack.py", run_id, "--root", root]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.stdout:
            print(p.stdout.strip())
        if p.stderr:
            print(p.stderr.strip())
        return p.returncode
    except Exception as e:
        print(f"ERROR: unable to execute check_audit_pack: {e}")
        return 4


def validate_correction_case(corr_id: str, root: str = "_reports") -> int:
    # P0: bootstrap PyYAML obrigatório (se faltar, BLOCKED)
    try:
        import yaml  # noqa: F401
    except Exception:
        return _print_and(4, "ERROR: PyYAML missing (BLOCKED_INPUT). Install tooling deps deterministically.")

    case_path = os.path.join(root, "cases", corr_id)
    if not os.path.isdir(case_path):
        return _print_and(4, f"ERROR: case folder missing: {case_path}")

    # P0: arquivos mínimos do caso
    mandatory = ["state.yaml", "facts.yaml", "repro.yaml", "patch_plan.yaml", "evidence_manifest.json", "links.yaml"]
    for f in mandatory:
        if not os.path.exists(os.path.join(case_path, f)):
            return _print_and(4, f"ERROR: missing mandatory case file: {f}")

    state = load_yaml(os.path.join(case_path, "state.yaml"))
    if not state:
        return _print_and(4, "ERROR: state.yaml missing/invalid")

    # P0: identidade
    if state.get("corr_id") != corr_id:
        return _print_and(4, f"ERROR: state.yaml corr_id mismatch: {state.get('corr_id')}")

    # P0: links_ref obrigatório e coerente
    if state.get("links_ref") != "links.yaml":
        return _print_and(4, "ERROR: state.yaml links_ref MUST be 'links.yaml'")

    links = load_yaml(os.path.join(case_path, "links.yaml"))
    if not links:
        return _print_and(4, "ERROR: links.yaml missing/invalid")
    if links.get("corr_id") != corr_id:
        return _print_and(4, "ERROR: links.yaml corr_id mismatch")
    primary_run = state.get("primary_run_id")
    if not primary_run or links.get("primary_run_id") != primary_run:
        return _print_and(4, "ERROR: primary_run_id mismatch between state.yaml and links.yaml")

    # P0: carregar registry primeiro (necessário para lifecycle checks)
    registry = load_yaml("docs/_canon/_agent/GATES_REGISTRY.yaml")
    if not registry:
        return _print_and(4, "ERROR: docs/_canon/_agent/GATES_REGISTRY.yaml missing/invalid")
    
    # Indexar gates por ID para lookup rápido
    gates_by_id: Dict[str, Dict[str, Any]] = {}
    gate_ids: Set[str] = set()
    for g in (registry.get("gates") or []):
        if isinstance(g, dict) and isinstance(g.get("id"), str):
            gate_id = g["id"]
            gate_ids.add(gate_id)
            gates_by_id[gate_id] = g

    # P0: mapping + required_gates baseado em by_capability
    mapping = load_yaml("docs/_canon/_agent/FAILURE_TO_GATES.yaml")
    if not mapping:
        return _print_and(4, "ERROR: docs/_canon/_agent/FAILURE_TO_GATES.yaml missing/invalid")

    f_type = state.get("failure_type_primary")
    capability = state.get("capability")
    
    if not f_type:
        return _print_and(4, "ERROR: state.yaml must declare failure_type_primary")
    if not capability:
        return _print_and(4, "ERROR: state.yaml must declare capability")
    
    type_meta = (mapping.get("failure_types") or {}).get(f_type)
    if not isinstance(type_meta, dict):
        return _print_and(4, f"ERROR: FAILURE_TO_GATES missing failure_type: {f_type}")
    
    by_capability = type_meta.get("by_capability")
    if not isinstance(by_capability, dict):
        return _print_and(4, f"ERROR: FAILURE_TO_GATES[{f_type}] missing by_capability")
    
    base_required = by_capability.get(capability)
    if not isinstance(base_required, list) or len(base_required) == 0:
        return _print_and(4, f"ERROR: FAILURE_TO_GATES[{f_type}][{capability}] empty or missing")
    
    # P0: regra SSOT - prepend do pre-gate BUILD_LOCK_INTEGRITY
    required_min = ["BUILD_LOCK_INTEGRITY"] + base_required

    # P0: state.gates_required MUST satisfazer required_gates
    gates_required = state.get("gates_required")
    if not isinstance(gates_required, list) or len(gates_required) == 0:
        return _print_and(4, "ERROR: state.yaml gates_required must be non-empty list")

    missing = [g for g in required_min if g not in gates_required]
    if missing:
        return _print_and(4, f"ERROR: gates_required missing mandatory gates for {f_type}/{capability}: {missing}")

    # P0: cross-check gates_required com registry (evita IDs inventados)
    unknown = [g for g in gates_required if g not in gate_ids]
    if unknown:
        return _print_and(4, f"ERROR: gates_required contains unknown gate ids: {unknown}")
    
    # P0: enforcement lifecycle=MISSING → BLOCKED_INPUT (4)
    # Nota: só valida lifecycle nos gates base_required (não no pre-gate BUILD_LOCK_INTEGRITY)
    # Rationale: se BUILD_LOCK_INTEGRITY é MISSING, é um problema sistêmico, não do caso específico
    missing_lifecycle = [g for g in base_required if gates_by_id.get(g, {}).get("lifecycle") == "MISSING"]
    if missing_lifecycle:
        return _print_and(4, f"ERROR: required gates have lifecycle=MISSING (BLOCKED_INPUT): {missing_lifecycle}")

    # P0: validar audit pack real (primary_run_id) via checker
    if run_check_audit_pack(primary_run, root) != 0:
        return _print_and(4, f"ERROR: primary_run_id {primary_run} not compliant with audit pack protocol")

    # P0: repro.yaml contrato mínimo + run_id existente + audit pack válido
    repro = load_yaml(os.path.join(case_path, "repro.yaml"))
    if not repro:
        return _print_and(4, "ERROR: repro.yaml missing/invalid")
    req = ["command", "expected", "observed", "exit_code", "run_id"]
    if any(k not in repro for k in req):
        return _print_and(4, "ERROR: repro.yaml missing mandatory fields")
    repro_run = repro.get("run_id")
    if not isinstance(repro_run, str) or not repro_run or repro_run == "UNKNOWN":
        return _print_and(4, "ERROR: repro.yaml run_id invalid")
    if not os.path.isdir(os.path.join(root, "audit", repro_run)):
        return _print_and(4, f"ERROR: repro.yaml run_id not found in audit/: {repro_run}")
    if run_check_audit_pack(repro_run, root) != 0:
        return _print_and(4, f"ERROR: repro run_id {repro_run} not compliant with audit pack protocol")

    print(f"SUCCESS: correction case {corr_id} protocol compliant.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Correction Protocol Compliance Checker (P0)")
    parser.add_argument("corr_id", help="CORR_ID under _reports/cases/<CORR_ID>")
    parser.add_argument("--root", default="_reports", help="Canonical reports root (default: _reports)")
    args = parser.parse_args()
    return validate_correction_case(args.corr_id, args.root)


if __name__ == "__main__":
    sys.exit(main())
