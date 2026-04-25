#!/usr/bin/env python3
"""
generate_merge_policy.py — Gera `.github/merge-policy.md` a partir do manifesto
local e do snapshot versionado do ruleset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _checks_by_category(manifest: dict, category: str) -> list[dict]:
    return sorted(
        (check for check in manifest.get("checks", []) if check.get("category") == category),
        key=lambda item: item.get("context", ""),
    )


def render_merge_policy(*, manifest: dict, snapshot: dict) -> str:
    if manifest.get("ruleset_id") != snapshot.get("ruleset_id"):
        raise ValueError(
            "merge-readiness.json e contract-gates.snapshot.json divergem em `ruleset_id`."
        )
    if manifest.get("ruleset_name") != snapshot.get("ruleset_name"):
        raise ValueError(
            "merge-readiness.json e contract-gates.snapshot.json divergem em `ruleset_name`."
        )

    required_checks = list(snapshot.get("required_status_checks") or [])
    required_workflows = {
        check["context"]: check["workflow"]
        for check in _checks_by_category(manifest, "required")
    }
    missing_workflows = [context for context in required_checks if context not in required_workflows]
    if missing_workflows:
        quoted = ", ".join(f"`{item}`" for item in missing_workflows)
        raise ValueError(f"Manifesto não define workflow para required check(s): {quoted}.")

    informational_checks = _checks_by_category(manifest, "informational")
    conditional_checks = _checks_by_category(manifest, "conditional")

    lines = [
        f"# Merge Policy — {manifest.get('target_branch', 'main')}",
        "",
        "> **ARTEFATO GERADO — DERIVADO NÃO-SOBERANO. Não editar manualmente.**",
        "> Gerador: `python3 scripts/audit/generate_merge_policy.py --write`",
        "> Fontes: `merge-readiness.json` + `.github/rulesets/contract-gates.snapshot.json`",
        "> Paridade live: `python3 scripts/audit/check_live_ruleset_parity.py --json`",
        "",
        "## Required checks (bloqueiam merge via ruleset `contract-gates`)",
        "",
        (
            f"Estes {len(required_checks)} checks devem passar para que qualquer PR possa ser "
            f"merged em `{manifest.get('target_branch', 'main')}`."
        ),
        (
            "Configurados no ruleset GitHub ID "
            f"{snapshot.get('ruleset_id')} com "
            f"`strict_required_status_checks_policy: {str(snapshot.get('strict_required_status_checks_policy', False)).lower()}`."
        ),
        "",
        "| # | Contexto requerido (exato) | Workflow |",
        "|---|---|---|",
    ]

    for index, context in enumerate(required_checks, start=1):
        lines.append(f"| {index} | `{context}` | `{required_workflows[context]}` |")

    lines.extend([
        "",
        "## Informational checks (não bloqueiam merge)",
        "",
    ])
    if informational_checks:
        lines.extend([
            "| Contexto | Workflow | Motivo |",
            "|---|---|---|",
        ])
        for check in informational_checks:
            lines.append(
                f"| `{check['context']}` | `{check['workflow']}` | {check.get('reason', 'N/A')} |"
            )
    else:
        lines.append("Nenhum check informativo declarado no manifesto.")

    lines.extend([
        "",
        "## Conditional checks (só executam quando a condição declarada for satisfeita)",
        "",
    ])
    if conditional_checks:
        lines.extend([
            "| Contexto | Workflow | Condição |",
            "|---|---|---|",
        ])
        for check in conditional_checks:
            lines.append(
                f"| `{check['context']}` | `{check['workflow']}` | `{check.get('condition', 'N/A')}` |"
            )
    else:
        lines.append("Nenhum check condicional declarado no manifesto.")

    enforcement = manifest.get("enforcement") or {}
    bypass_actors = snapshot.get("bypass_actors") or []
    lines.extend([
        "",
        "## Regras de enforcement verificáveis",
        "",
        (
            f"- **Atualização obrigatória com a branch base**: "
            f"{'sim' if snapshot.get('strict_required_status_checks_policy') else 'não'}"
        ),
        f"- **Aprovações requeridas**: {snapshot.get('required_approving_review_count')}",
        (
            f"- **Code owner review**: "
            f"{'sim' if snapshot.get('require_code_owner_review') else 'não'}"
        ),
        (
            f"- **Resolver todas as threads**: "
            f"{'obrigatório' if snapshot.get('required_review_thread_resolution') else 'não'}"
        ),
        f"- **Force push**: {'proibido' if snapshot.get('block_force_push') else 'permitido'}",
        f"- **Deletion da branch default**: {'proibido' if snapshot.get('block_deletion') else 'permitido'}",
        (
            f"- **Bypass actors declarados no manifesto**: "
            f"{json.dumps(enforcement.get('bypass_actors', []), ensure_ascii=False)}"
        ),
        "",
        "## Bypass actors expostos pelo ruleset normalizado",
        "",
    ])
    if bypass_actors:
        lines.extend([f"- `{json.dumps(actor, ensure_ascii=False, sort_keys=True)}`" for actor in bypass_actors])
    else:
        lines.append("Nenhum. O ruleset normalizado expõe `bypass_actors: []`.")

    lines.append("")
    return "\n".join(lines)


def generate_merge_policy(root: Path) -> str:
    manifest = _load_json(root / "merge-readiness.json")
    snapshot = _load_json(root / ".github" / "rulesets" / "contract-gates.snapshot.json")
    return render_merge_policy(manifest=manifest, snapshot=snapshot)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera .github/merge-policy.md a partir do snapshot.")
    parser.add_argument("--root", default=None, help="Raiz do repositório.")
    parser.add_argument("--write", action="store_true", help="Persistir o arquivo gerado.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    output = generate_merge_policy(root)

    if args.write:
        target = root / ".github" / "merge-policy.md"
        target.write_text(output, encoding="utf-8")
        print(str(target.relative_to(root)))
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
