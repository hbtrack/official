#!/usr/bin/env python3
"""
check_live_ruleset_parity.py — Verifica paridade entre ruleset live, snapshot local
e artefatos operacionais que prometem o enforcement de merge do repositório.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from generate_merge_policy import render_merge_policy


@dataclass
class ParityReport:
    status: str  # PASS | FAIL | ERROR
    message: str
    checked_files: list[str] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    violations: list[dict] = field(default_factory=list)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _required_checks_from_manifest(manifest: dict) -> list[str]:
    return sorted(
        check["context"]
        for check in manifest.get("checks", [])
        if check.get("category") == "required"
    )


def _required_workflows_from_manifest(manifest: dict) -> dict[str, str]:
    return {
        check["context"]: check["workflow"]
        for check in manifest.get("checks", [])
        if check.get("category") == "required"
    }


def _normalize_live_ruleset(payload: dict) -> dict:
    normalized = {
        "ruleset_id": payload.get("id"),
        "ruleset_name": payload.get("name"),
        "repository": payload.get("source"),
        "enforcement": payload.get("enforcement"),
        "required_status_checks": [],
        "strict_required_status_checks_policy": False,
        "required_approving_review_count": None,
        "require_code_owner_review": None,
        "required_review_thread_resolution": None,
        "block_force_push": False,
        "block_deletion": False,
        "bypass_actors": payload.get("bypass_actors") or [],
    }
    for rule in payload.get("rules", []):
        rule_type = rule.get("type")
        params = rule.get("parameters") or {}
        if rule_type == "required_status_checks":
            normalized["strict_required_status_checks_policy"] = bool(
                params.get("strict_required_status_checks_policy")
            )
            normalized["required_status_checks"] = sorted(
                check.get("context")
                for check in params.get("required_status_checks", [])
                if check.get("context")
            )
        elif rule_type == "pull_request":
            normalized["required_approving_review_count"] = params.get(
                "required_approving_review_count"
            )
            normalized["require_code_owner_review"] = bool(
                params.get("require_code_owner_review")
            )
            normalized["required_review_thread_resolution"] = bool(
                params.get("required_review_thread_resolution")
            )
        elif rule_type == "non_fast_forward":
            normalized["block_force_push"] = True
        elif rule_type == "deletion":
            normalized["block_deletion"] = True
    return normalized


def _extract_merge_policy_required_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    in_required_section = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## Required checks"):
            in_required_section = True
            continue
        if in_required_section and line.startswith("## "):
            break
        if not in_required_section or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] in {"#", "---"} or cells[1].startswith("---"):
            continue
        context = cells[1].strip("` ")
        workflow = cells[2].strip("` ")
        if context and workflow and context != "Job name (exato — conforme `name:` no YAML)":
            rows[context] = workflow
    return rows


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compare_ruleset_parity(
    *,
    manifest: dict,
    live_ruleset: dict,
    snapshot: dict | None,
    merge_policy_text: str,
) -> list[dict]:
    violations: list[dict] = []
    manifest_required = _required_checks_from_manifest(manifest)
    live_required = sorted(live_ruleset.get("required_status_checks") or [])

    if manifest.get("ruleset_id") != live_ruleset.get("ruleset_id"):
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": "merge-readiness.json",
            "message": (
                f"ruleset_id divergente: manifesto={manifest.get('ruleset_id')} "
                f"live={live_ruleset.get('ruleset_id')}"
            ),
            "severity": "error",
        })
    if manifest.get("ruleset_name") != live_ruleset.get("ruleset_name"):
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": "merge-readiness.json",
            "message": (
                f"ruleset_name divergente: manifesto={manifest.get('ruleset_name')!r} "
                f"live={live_ruleset.get('ruleset_name')!r}"
            ),
            "severity": "error",
        })
    if manifest_required != live_required:
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": "merge-readiness.json",
            "message": "Required checks do manifesto divergem do ruleset live.",
            "severity": "error",
            "details": {
                "manifest_required": manifest_required,
                "live_required": live_required,
            },
        })

    enforcement = manifest.get("enforcement") or {}
    mapping = [
        ("require_conversation_resolution", "required_review_thread_resolution"),
        ("require_up_to_date", "strict_required_status_checks_policy"),
        ("block_force_push", "block_force_push"),
        ("block_deletion", "block_deletion"),
    ]
    for manifest_key, live_key in mapping:
        if bool(enforcement.get(manifest_key)) != bool(live_ruleset.get(live_key)):
            violations.append({
                "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
                "artifact": "merge-readiness.json",
                "message": (
                    f"Enforcement `{manifest_key}` diverge do live "
                    f"({enforcement.get(manifest_key)!r} != {live_ruleset.get(live_key)!r})."
                ),
                "severity": "error",
            })

    if snapshot and snapshot != live_ruleset:
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": ".github/rulesets/contract-gates.snapshot.json",
            "message": "Snapshot versionado diverge do ruleset live normalizado.",
            "severity": "error",
            "details": {
                "snapshot_required": snapshot.get("required_status_checks"),
                "live_required": live_ruleset.get("required_status_checks"),
            },
        })

    merge_policy_rows = _extract_merge_policy_required_rows(merge_policy_text)
    if sorted(merge_policy_rows.keys()) != live_required:
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": ".github/merge-policy.md",
            "message": "Tabela de required checks em merge-policy.md diverge do ruleset live.",
            "severity": "error",
            "details": {
                "merge_policy_required": sorted(merge_policy_rows.keys()),
                "live_required": live_required,
            },
        })
    manifest_workflows = _required_workflows_from_manifest(manifest)
    for context, workflow in merge_policy_rows.items():
        expected_workflow = manifest_workflows.get(context)
        if expected_workflow and workflow != expected_workflow:
            violations.append({
                "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
                "artifact": ".github/merge-policy.md",
                "message": (
                    f"Workflow de `{context}` em merge-policy.md diverge do manifesto "
                    f"({workflow!r} != {expected_workflow!r})."
                ),
                "severity": "error",
            })

    try:
        expected_merge_policy = render_merge_policy(
            manifest=manifest,
            snapshot=snapshot or live_ruleset,
        )
    except Exception as exc:
        violations.append({
            "blocking_code": "ERROR_INFRA",
            "artifact": ".github/merge-policy.md",
            "message": f"Falha ao gerar merge-policy esperado: {exc}",
            "severity": "error",
        })
        return violations

    if merge_policy_text != expected_merge_policy:
        violations.append({
            "blocking_code": "BLOCKED_LIVE_ENFORCEMENT_PARITY",
            "artifact": ".github/merge-policy.md",
            "message": "merge-policy.md diverge do artefato gerado esperado.",
            "severity": "error",
            "details": {
                "actual_sha256": _sha256_text(merge_policy_text),
                "expected_sha256": _sha256_text(expected_merge_policy),
            },
        })

    return violations


def _fetch_live_ruleset(ruleset_id: int) -> dict:
    result = subprocess.run(
        ["gh", "api", f"repos/hbtrack/official/rulesets/{ruleset_id}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh api falhou ao consultar ruleset live")
    return json.loads(result.stdout)


def run_check(root: Path) -> ParityReport:
    manifest_path = root / "merge-readiness.json"
    merge_policy_path = root / ".github" / "merge-policy.md"
    snapshot_path = root / ".github" / "rulesets" / "contract-gates.snapshot.json"
    generator_path = root / "scripts" / "audit" / "generate_merge_policy.py"
    checked_files = [
        str(manifest_path.relative_to(root)),
        str(merge_policy_path.relative_to(root)),
        str(snapshot_path.relative_to(root)),
        str(generator_path.relative_to(root)),
    ]

    if not manifest_path.exists():
        return ParityReport(
            status="ERROR",
            message="merge-readiness.json não encontrado.",
            checked_files=checked_files,
            violations=[{
                "blocking_code": "ERROR_INFRA",
                "artifact": str(manifest_path.relative_to(root)),
                "message": "Arquivo obrigatório ausente.",
                "severity": "error",
            }],
        )

    manifest = _load_json(manifest_path)
    snapshot = _load_json(snapshot_path) if snapshot_path.exists() else None
    merge_policy_text = merge_policy_path.read_text(encoding="utf-8") if merge_policy_path.exists() else ""

    try:
        live_payload = _fetch_live_ruleset(int(manifest["ruleset_id"]))
        live_ruleset = _normalize_live_ruleset(live_payload)
    except Exception as exc:
        return ParityReport(
            status="ERROR",
            message=f"Falha ao obter ruleset live: {exc}",
            checked_files=checked_files,
            violations=[{
                "blocking_code": "ERROR_INFRA",
                "artifact": "gh api repos/hbtrack/official/rulesets/<id>",
                "message": str(exc),
                "severity": "error",
            }],
        )

    evidence_dir = root / "_reports" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "live_ruleset_contract-gates.json"
    evidence_path.write_text(
        json.dumps(live_ruleset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    violations = compare_ruleset_parity(
        manifest=manifest,
        live_ruleset=live_ruleset,
        snapshot=snapshot,
        merge_policy_text=merge_policy_text,
    )
    if violations:
        return ParityReport(
            status="FAIL",
            message=f"Paridade do ruleset live falhou com {len(violations)} divergência(s).",
            checked_files=checked_files,
            evidence_files=[str(evidence_path.relative_to(root))],
            violations=violations,
        )

    return ParityReport(
        status="PASS",
        message="Ruleset live, snapshot local e artefatos operacionais estão em paridade.",
        checked_files=checked_files,
        evidence_files=[str(evidence_path.relative_to(root))],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida paridade do ruleset live do GitHub.")
    parser.add_argument("--json", action="store_true", help="Emitir relatório em JSON.")
    parser.add_argument("--root", default=None, help="Raiz do repositório.")
    args = parser.parse_args()

    if args.root:
        root = Path(args.root).resolve()
    else:
        root = Path(__file__).resolve().parents[2]

    report = run_check(root)
    if args.json:
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print(f"[{report.status}] {report.message}")
        for violation in report.violations:
            print(f"  - {violation.get('artifact')}: {violation.get('message')}")
    return 0 if report.status == "PASS" else 1 if report.status == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
