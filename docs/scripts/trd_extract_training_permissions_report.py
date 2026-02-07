"""
TRD Verification Script - Extract permission requirements for Training scope endpoints

Usage:
    python3 docs/scripts/trd_extract_training_permissions_report.py

Output:
    docs/_generated/trd_training_permissions_report.txt
"""

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OPENAPI = Path("Hb Track - Backend/docs/_generated/openapi.json")
ROUTERS_DIR = Path("Hb Track - Backend/app/api/v1/routers")
PERMISSIONS_MAP = Path("Hb Track - Backend/app/core/permissions_map.py")
OUT = Path("docs/_generated/trd_training_permissions_report.txt")

SCOPE_PREFIXES = (
    "/api/v1/training-sessions",
    "/api/v1/training_sessions",
    "/api/v1/wellness-pre",
    "/api/v1/wellness_pre",
    "/api/v1/wellness-post",
    "/api/v1/wellness_post",
    "/api/v1/exercises",
    "/api/v1/exercise-tags",
    "/api/v1/exercise_tags",
    "/api/v1/exercise-favorites",
    "/api/v1/exercise_favorites",
    "/api/v1/training-cycles",
    "/api/v1/training_cycles",
    "/api/v1/training-microcycles",
    "/api/v1/training_microcycles",
    "/api/v1/session-templates",
    "/api/v1/session_templates",
    "/api/v1/training/alerts-suggestions",
    "/api/v1/attendance",
    "/api/v1/analytics/wellness-rankings",
    "/api/v1/analytics/team",
)


def _load_openapi() -> Dict[str, Any]:
    if not OPENAPI.exists():
        raise FileNotFoundError(f"{OPENAPI} not found")
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def _operation_name(op_id: str) -> str:
    return op_id.split("_api_v1_")[0] if "_api_v1_" in op_id else op_id


def _build_openapi_map(spec: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    for path, methods in spec.get("paths", {}).items():
        if not any(path.startswith(prefix) for prefix in SCOPE_PREFIXES):
            continue
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId")
            if not op_id:
                continue
            name = _operation_name(op_id)
            mapping[name] = {
                "operationId": op_id,
                "method": method.upper(),
                "path": path,
            }
    return mapping


def _extract_permission_dep(expr: ast.AST) -> Optional[Dict[str, Any]]:
    if not isinstance(expr, ast.Call):
        return None
    func_name = None
    if isinstance(expr.func, ast.Name):
        func_name = expr.func.id
    elif isinstance(expr.func, ast.Attribute):
        func_name = expr.func.attr
    if func_name != "Depends":
        return None
    if not expr.args:
        return None
    target = expr.args[0]
    if isinstance(target, ast.Name) and target.id == "permission_dep":
        return {"roles": None, "require_org": False, "require_team": False, "require_team_registration": False}
    if not isinstance(target, ast.Call):
        return None
    if isinstance(target.func, ast.Name) and target.func.id != "permission_dep":
        return None
    if isinstance(target.func, ast.Attribute) and target.func.attr != "permission_dep":
        return None

    roles: Optional[List[str]] = None
    require_org = False
    require_team = False
    require_team_registration = False

    if target.args:
        if isinstance(target.args[0], (ast.List, ast.Tuple)):
            roles = [elt.value for elt in target.args[0].elts if isinstance(elt, ast.Constant)]

    for kw in target.keywords:
        if kw.arg == "roles":
            if isinstance(kw.value, (ast.List, ast.Tuple)):
                roles = [elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant)]
        elif kw.arg == "require_org":
            if isinstance(kw.value, ast.Constant):
                require_org = bool(kw.value.value)
        elif kw.arg == "require_team":
            if isinstance(kw.value, ast.Constant):
                require_team = bool(kw.value.value)
        elif kw.arg == "require_team_registration":
            if isinstance(kw.value, ast.Constant):
                require_team_registration = bool(kw.value.value)

    return {
        "roles": roles,
        "require_org": require_org,
        "require_team": require_team,
        "require_team_registration": require_team_registration,
    }


def _extract_ctx_permissions(node: ast.AST) -> List[str]:
    perms: List[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if isinstance(child.func.value, ast.Name) and child.func.value.id == "ctx":
                if child.func.attr in {"requires", "can"} and child.args:
                    if isinstance(child.args[0], ast.Constant) and isinstance(child.args[0].value, str):
                        perms.append(child.args[0].value)
    return sorted(set(perms))


def _permission_map_lines(permission_keys: List[str]) -> Dict[str, int]:
    if not permission_keys or not PERMISSIONS_MAP.exists():
        return {}
    lines = PERMISSIONS_MAP.read_text(encoding="utf-8").splitlines()
    results: Dict[str, int] = {}
    for key in permission_keys:
        for idx, line in enumerate(lines, start=1):
            if f"\"{key}\"" in line or f"'{key}'" in line:
                results[key] = idx
                break
    return results


def _scan_routers() -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    for path in sorted(ROUTERS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            perm_info = None
            evidence_line = None
            # Match permission_dep in function params (Depends(...))
            defaults = list(node.args.defaults)
            args = node.args.args[-len(defaults):] if defaults else []
            for arg, default in zip(args, defaults):
                info = _extract_permission_dep(default)
                if info is not None:
                    perm_info = info
                    evidence_line = getattr(default, "lineno", None)
                    break
            ctx_perms = _extract_ctx_permissions(node)
            results[node.name] = {
                "roles": perm_info["roles"] if perm_info else None,
                "require_org": perm_info["require_org"] if perm_info else None,
                "require_team": perm_info["require_team"] if perm_info else None,
                "require_team_registration": perm_info["require_team_registration"] if perm_info else None,
                "permission_keys": ctx_perms,
                "router_file": path,
                "router_line": evidence_line or getattr(node, "lineno", None),
            }
    return results


def main() -> int:
    spec = _load_openapi()
    openapi_map = _build_openapi_map(spec)
    router_map = _scan_routers()

    rows: List[Dict[str, Any]] = []
    for func_name, op in sorted(openapi_map.items(), key=lambda x: x[1]["path"]):
        router_info = router_map.get(func_name)
        roles = router_info.get("roles") if router_info else None
        require_org = router_info.get("require_org") if router_info else None
        require_team = router_info.get("require_team") if router_info else None
        require_team_registration = router_info.get("require_team_registration") if router_info else None
        permission_keys = router_info.get("permission_keys") if router_info else []
        router_file = router_info.get("router_file") if router_info else None
        router_line = router_info.get("router_line") if router_info else None

        perm_map_lines = _permission_map_lines(permission_keys or [])
        if perm_map_lines:
            evidence_map = ", ".join([f"{key}@{line}" for key, line in perm_map_lines.items()])
        else:
            evidence_map = "—"

        if router_file:
            evidence_router = f"{router_file}:{router_line}"
        else:
            evidence_router = "—"

        rows.append({
            "operationId": op["operationId"],
            "method": op["method"],
            "path": op["path"],
            "roles": ", ".join(roles) if roles else "—",
            "require_org": str(require_org) if require_org is not None else "—",
            "require_team": str(require_team) if require_team is not None else "—",
            "require_team_registration": str(require_team_registration) if require_team_registration is not None else "—",
            "permission_keys": ", ".join(permission_keys) if permission_keys else "—",
            "evidence_router": evidence_router,
            "evidence_map": evidence_map,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    report_lines = []
    report_lines.append("# TRD Training Permissions Report")
    report_lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}Z")
    report_lines.append("")
    report_lines.append("Nota: permission_dep é role-based; chaves de permissão só aparecem quando há ctx.requires/ctx.can explícito.")
    report_lines.append("")
    report_lines.append("| operationId | method | path | roles_required | require_org | require_team | require_team_registration | permission_keys | evidence_router | evidence_permissions_map |")
    report_lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        report_lines.append(
            f"| {row['operationId']} | {row['method']} | {row['path']} | {row['roles']} | "
            f"{row['require_org']} | {row['require_team']} | {row['require_team_registration']} | "
            f"{row['permission_keys']} | {row['evidence_router']} | {row['evidence_map']} |"
        )
    OUT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Report written to: {OUT}")
    print(f"Rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
