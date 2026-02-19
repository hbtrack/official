from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_EXIT = {0, 2, 3, 4}
STATUS_MAP = {0: "PASS", 2: "FAIL_ACTIONABLE", 3: "ERROR_INFRA", 4: "BLOCKED_INPUT"}


def severity(code: int) -> int:
    return {0: 0, 2: 1, 3: 2, 4: 3}.get(code, 1)


def normalize_exit_code(raw: int) -> int:
    if raw in ALLOWED_EXIT:
        return raw
    return 2 if raw != 0 else 0


def load_yaml(path: str) -> Optional[Dict[str, Any]]:
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


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"])
        v = out.decode("ascii", errors="replace").strip()
        return v or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_git_branch() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        v = out.decode("ascii", errors="replace").strip()
        return v or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def write_json(path: str, obj: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def run_command(command: str, timeout_seconds: int, cwd: Optional[str] = None) -> Tuple[int, str, str, int]:
    start = time.perf_counter()
    try:
        p = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            cwd=cwd,
        )
        dur = int((time.perf_counter() - start) * 1000)
        return p.returncode, p.stdout or "", p.stderr or "", dur
    except subprocess.TimeoutExpired as e:
        dur = int((time.perf_counter() - start) * 1000)
        return 3, e.stdout or "", f"ERROR_INFRA: timeout after {timeout_seconds}s\n", dur
    except Exception as e:
        dur = int((time.perf_counter() - start) * 1000)
        return 3, "", f"ERROR_INFRA: exception running command: {e}\n", dur


def execute_audit(run_id: str, gate_ids: List[str], root: str = "_reports") -> int:
    audit_dir = os.path.join(root, "audit", run_id)
    checks_dir = os.path.join(audit_dir, "checks")
    ensure_dir(checks_dir)

    # context.json (sempre)
    ctx = {
        "run_id": run_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "git": {"commit": get_git_commit(), "branch": get_git_branch()},
        "environment": {"python_version": sys.version.split()[0], "os": sys.platform},
        "base_url": os.getenv("HB_AUDIT_BASE_URL", "MISSING"),
    }
    write_json(os.path.join(audit_dir, "context.json"), ctx)

    # registry (SSOT)
    registry_path = "docs/_canon/_agent/GATES_REGISTRY.yaml"
    registry = load_yaml(registry_path)
    if not registry or not isinstance(registry.get("gates"), list):
        # P0: sem registry => todos os gates pedidos viram BLOCKED_INPUT, sem "skip"
        overall = 4
        checks_summary: List[Dict[str, Any]] = []
        for gid in gate_ids:
            check_path = os.path.join(checks_dir, gid)
            ensure_dir(check_path)
            write_text(os.path.join(check_path, "stdout.log"), "")
            write_text(os.path.join(check_path, "stderr.log"), "BLOCKED_INPUT: registry missing/invalid\n")
            res = {
                "id": gid,
                "command": None,
                "exit_code": 4,
                "status": "BLOCKED_INPUT",
                "duration_ms": 0,
                "artifacts": ["stdout.log", "stderr.log"],
            }
            write_json(os.path.join(check_path, "result.json"), res)
            checks_summary.append({"id": gid, "exit_code": 4, "status": "BLOCKED_INPUT"})
        write_json(os.path.join(audit_dir, "summary.json"), {
            "run_id": run_id,
            "overall_exit_code": overall,
            "checks": checks_summary,
        })
        return overall

    # build index of gates
    gate_index: Dict[str, Dict[str, Any]] = {}
    for g in registry["gates"]:
        if isinstance(g, dict) and isinstance(g.get("id"), str):
            gate_index[g["id"]] = g

    if not gate_ids:
        # P0: run sem gates é inválido
        ensure_dir(os.path.join(checks_dir, "AUDIT_EMPTY"))
        write_text(os.path.join(checks_dir, "AUDIT_EMPTY", "stdout.log"), "")
        write_text(os.path.join(checks_dir, "AUDIT_EMPTY", "stderr.log"), "BLOCKED_INPUT: no gates provided\n")
        write_json(os.path.join(checks_dir, "AUDIT_EMPTY", "result.json"), {
            "id": "AUDIT_EMPTY",
            "command": None,
            "exit_code": 4,
            "status": "BLOCKED_INPUT",
            "duration_ms": 0,
            "artifacts": ["stdout.log", "stderr.log"],
        })
        write_json(os.path.join(audit_dir, "summary.json"), {
            "run_id": run_id,
            "overall_exit_code": 4,
            "checks": [{"id": "AUDIT_EMPTY", "exit_code": 4, "status": "BLOCKED_INPUT"}],
        })
        return 4

    overall_exit = 0
    summary_checks: List[Dict[str, Any]] = []

    for gid in gate_ids:
        meta = gate_index.get(gid)
        check_path = os.path.join(checks_dir, gid)
        ensure_dir(check_path)

        stdout_path = os.path.join(check_path, "stdout.log")
        stderr_path = os.path.join(check_path, "stderr.log")
        result_path = os.path.join(check_path, "result.json")

        # defaults: sempre criar logs (mesmo vazio)
        write_text(stdout_path, "")
        write_text(stderr_path, "")

        command = meta.get("command") if meta else None
        requires_env = meta.get("requires_env") if meta else []
        timeout_seconds = int(meta.get("timeout_seconds", 600)) if meta else 600
        cwd = meta.get("cwd") if meta else None

        # gate inexistente ou command ausente => BLOCKED_INPUT (sem skip)
        if not meta or not command:
            write_text(stderr_path, "BLOCKED_INPUT: gate missing in registry or command not defined\n")
            res = {
                "id": gid,
                "command": None,
                "exit_code": 4,
                "status": "BLOCKED_INPUT",
                "duration_ms": 0,
                "artifacts": ["stdout.log", "stderr.log"],
            }
            write_json(result_path, res)
            summary_checks.append({"id": gid, "exit_code": 4, "status": "BLOCKED_INPUT"})
            overall_exit = max(overall_exit, 4, key=severity)
            continue

        # prereqs env => se faltar, BLOCKED_INPUT
        missing_env = []
        if isinstance(requires_env, list):
            for k in requires_env:
                if isinstance(k, str):
                    v = os.getenv(k)
                    if v is None or v == "":
                        missing_env.append(k)
        if missing_env:
            write_text(stderr_path, f"BLOCKED_INPUT: missing required env vars: {missing_env}\n")
            res = {
                "id": gid,
                "command": command,
                "exit_code": 4,
                "status": "BLOCKED_INPUT",
                "duration_ms": 0,
                "artifacts": ["stdout.log", "stderr.log"],
            }
            write_json(result_path, res)
            summary_checks.append({"id": gid, "exit_code": 4, "status": "BLOCKED_INPUT"})
            overall_exit = max(overall_exit, 4, key=severity)
            continue

        raw_code, out, err, dur = run_command(str(command), timeout_seconds, cwd)
        norm = normalize_exit_code(raw_code)
        status = STATUS_MAP.get(norm, "FAIL_ACTIONABLE")

        # persist logs
        write_text(stdout_path, out)
        write_text(stderr_path, err)

        res = {
            "id": gid,
            "command": command,
            "exit_code": norm,
            "status": status,
            "duration_ms": int(dur),
            "artifacts": ["stdout.log", "stderr.log"],
        }
        write_json(result_path, res)

        summary_checks.append({"id": gid, "exit_code": norm, "status": status})
        overall_exit = max(overall_exit, norm, key=severity)

    write_json(os.path.join(audit_dir, "summary.json"), {
        "run_id": run_id,
        "overall_exit_code": overall_exit,
        "checks": summary_checks,
    })
    return overall_exit


def main() -> int:
    parser = argparse.ArgumentParser(description="HB Track Audit Runner (Ground Truth Generator)")
    parser.add_argument("run_id", help="RUN_ID under _reports/audit/<RUN_ID>")
    parser.add_argument("gate_ids", nargs="+", help="One or more GATE_IDs to execute")
    parser.add_argument("--root", default="_reports", help="Canonical reports root (default: _reports)")
    args = parser.parse_args()
    return execute_audit(args.run_id, args.gate_ids, args.root)


if __name__ == "__main__":
    sys.exit(main())
