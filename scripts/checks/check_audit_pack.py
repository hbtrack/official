from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional, Set

ALLOWED_EXIT = {0, 2, 3, 4}
STATUS_MAP = {0: "PASS", 2: "FAIL_ACTIONABLE", 3: "ERROR_INFRA", 4: "BLOCKED_INPUT"}
REQUIRED_FIELDS = ["id", "command", "exit_code", "status", "duration_ms", "artifacts"]


def load_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def severity(code: int) -> int:
    # Ordem canônica: 0 < 2 < 3 < 4
    return {0: 0, 2: 1, 3: 2, 4: 3}.get(code, 1)


def validate_audit_pack(run_id: str, root: str = "_reports") -> int:
    audit_path = os.path.join(root, "audit", run_id)
    if not os.path.isdir(audit_path):
        print(f"ERROR: audit folder missing: {audit_path}")
        return 4

    summary_path = os.path.join(audit_path, "summary.json")
    if not os.path.exists(summary_path):
        print(f"ERROR: summary.json missing in {run_id}")
        return 4

    ctx = load_json(os.path.join(audit_path, "context.json"))
    if not ctx:
        print("ERROR: context.json missing/invalid")
        return 4
    commit = (ctx.get("git") or {}).get("commit")
    if not commit or commit == "UNKNOWN":
        print("ERROR: context.json git.commit invalid (UNKNOWN/Missing)")
        return 4

    checks_dir = os.path.join(audit_path, "checks")
    if not os.path.isdir(checks_dir):
        print("ERROR: checks/ dir missing")
        return 4

    # P0: não aceitar pack com zero gates
    gate_folders = [
        name for name in os.listdir(checks_dir)
        if os.path.isdir(os.path.join(checks_dir, name))
    ]
    if not gate_folders:
        print("ERROR: no gate folders found in checks/")
        return 4

    summary = load_json(summary_path)
    if not summary:
        print("ERROR: summary.json invalid JSON")
        return 4

    # P0: contrato mínimo do summary
    if summary.get("run_id") != run_id:
        print("ERROR: summary.json run_id mismatch")
        return 4
    checks_list = summary.get("checks")
    if not isinstance(checks_list, list) or len(checks_list) == 0:
        print("ERROR: summary.json checks must be non-empty list")
        return 4
    overall = summary.get("overall_exit_code")
    if overall not in ALLOWED_EXIT:
        print("ERROR: summary.json overall_exit_code invalid")
        return 4

    # P0: coerência summary <-> folders
    summary_ids: Set[str] = set()
    for item in checks_list:
        if not isinstance(item, dict):
            print("ERROR: summary.json checks[] item is not object")
            return 4
        gid = item.get("id")
        ec = item.get("exit_code")
        st = item.get("status")
        if not gid or not isinstance(gid, str):
            print("ERROR: summary.json checks[] missing id")
            return 4
        if ec not in ALLOWED_EXIT:
            print(f"ERROR: summary.json checks[{gid}] exit_code invalid")
            return 4
        if st != STATUS_MAP.get(ec):
            print(f"ERROR: summary.json checks[{gid}] status != exit_code mapping")
            return 4
        summary_ids.add(gid)

    folder_ids = set(gate_folders)
    if summary_ids != folder_ids:
        missing_in_folders = sorted(list(summary_ids - folder_ids))
        extra_in_folders = sorted(list(folder_ids - summary_ids))
        print("ERROR: summary.json checks ids != checks/ folders")
        print(f"  missing_in_folders: {missing_in_folders}")
        print(f"  extra_in_folders: {extra_in_folders}")
        return 4

    # P0: validar cada gate folder (estrutura + artifacts)
    computed_overall = 0
    for gate_id in gate_folders:
        gate_path = os.path.join(checks_dir, gate_id)

        # arquivos mínimos físicos
        for fname in ("stdout.log", "stderr.log", "result.json"):
            if not os.path.exists(os.path.join(gate_path, fname)):
                print(f"ERROR: gate [{gate_id}] missing {fname}")
                return 4

        res = load_json(os.path.join(gate_path, "result.json"))
        if not res or any(k not in res for k in REQUIRED_FIELDS):
            print(f"ERROR: gate [{gate_id}] violates result.json contract")
            return 4

        if res.get("id") != gate_id:
            print(f"ERROR: gate [{gate_id}] id mismatch")
            return 4

        exit_code = res.get("exit_code")
        status = res.get("status")
        if exit_code not in ALLOWED_EXIT:
            print(f"ERROR: gate [{gate_id}] exit_code invalid")
            return 4
        if status != STATUS_MAP.get(exit_code):
            print(f"ERROR: gate [{gate_id}] status != exit_code mapping")
            return 4

        # command coercion rules
        cmd = res.get("command", None)
        if cmd is None and exit_code != 4:
            print(f"ERROR: gate [{gate_id}] command cannot be null unless BLOCKED_INPUT")
            return 4

        # duration_ms
        dur = res.get("duration_ms")
        if not isinstance(dur, int) or dur < 0:
            print(f"ERROR: gate [{gate_id}] duration_ms must be int >= 0")
            return 4

        # artifacts: MUST be list, MUST include stdout/stderr, MUST exist physically
        arts = res.get("artifacts")
        if not isinstance(arts, list) or len(arts) == 0:
            print(f"ERROR: gate [{gate_id}] artifacts must be non-empty list")
            return 4
        if "stdout.log" not in arts or "stderr.log" not in arts:
            print(f"ERROR: gate [{gate_id}] artifacts must include stdout.log and stderr.log")
            return 4
        for a in arts:
            if not isinstance(a, str) or not a:
                print(f"ERROR: gate [{gate_id}] artifact entry invalid")
                return 4
            ap = os.path.join(gate_path, a)
            if not os.path.exists(ap):
                print(f"ERROR: gate [{gate_id}] artifact missing on disk: {a}")
                return 4

        # compute overall
        computed_overall = max(computed_overall, int(exit_code), key=severity)

    if computed_overall != overall:
        print(f"ERROR: summary overall_exit_code mismatch: summary={overall} computed={computed_overall}")
        return 4

    print(f"SUCCESS: audit pack {run_id} verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Pack Integrity Checker (SSOT)")
    parser.add_argument("run_id", help="RUN_ID under _reports/audit/<RUN_ID>")
    parser.add_argument("--root", default="_reports", help="Canonical reports root (default: _reports)")
    args = parser.parse_args()
    return validate_audit_pack(args.run_id, args.root)


if __name__ == "__main__":
    sys.exit(main())
