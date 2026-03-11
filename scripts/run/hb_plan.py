#!/usr/bin/env python3
"""
hb_plan.py — HB Track deterministic planner para módulo ATLETAS.

Entrada:
  module_root  — diretório do contract pack (ex: docs/hbtrack/modulos/atletas)

Saída:
  _reports/hb_plan_result.json
  _reports/hb_plan_result.md
  _reports/anchor_manifest.json
  <module_root>/16_ATLETAS_AGENT_HANDOFF.json

Exit codes:
  0 = PASS
  2 = FAIL_ACTIONABLE
  3 = ERROR_INFRA
  4 = BLOCKED_INPUT

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Garantir import do pacote hbtrack_lint (em scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from hbtrack_lint.context import ValidationContext
from hbtrack_lint.loader import load_contract_pack, REQUIRED_DOCS
from hbtrack_lint.schemas import validate_documents_against_schemas
from hbtrack_lint.checker_registry import run_allowed_rules
from hbtrack_lint.anchor_manifest import build_anchor_manifest
from hbtrack_lint.handoff_builder import build_handoff
from hbtrack_lint.hashing import sha256_file, sha256_jsonable
from hbtrack_lint.reports import write_plan_reports

EXIT_PASS = 0
EXIT_FAIL_ACTIONABLE = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HB Track deterministic planner — valida contratos e gera handoff"
    )
    parser.add_argument(
        "module_root",
        type=Path,
        help="Caminho para o diretório do contract pack (ex: docs/hbtrack/modulos/atletas)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Raiz do repositório (padrão: diretório de trabalho atual)",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("_reports"),
        help="Diretório de saída para relatórios (padrão: _reports)",
    )
    parser.add_argument(
        "--governance-v2-dry-run",
        action="store_true",
        default=False,
        help="[DRY-RUN] Ativa filtro de phase v2 (PRE_PLAN + POST_PLAN) sem alteração de comportamento geral.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        repo_root = args.repo_root.resolve()
        module_root = (repo_root / args.module_root).resolve() if not args.module_root.is_absolute() else args.module_root.resolve()
        reports_dir = (repo_root / args.reports_dir).resolve() if not args.reports_dir.is_absolute() else args.reports_dir.resolve()
        reports_dir.mkdir(parents=True, exist_ok=True)

        # ── Validação de entrada ──────────────────────────────────────────
        if not module_root.exists():
            write_plan_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"rule_id": "BLOCKED_INPUT", "message": f"module_root não existe: {module_root}"}],
                warnings=[],
                results=[],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_BLOCKED_INPUT

        # ── Carregar contratos ────────────────────────────────────────────
        contracts = load_contract_pack(module_root)

        missing_required = [d for d in REQUIRED_DOCS if d not in contracts]
        if missing_required:
            write_plan_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[
                    {"rule_id": "BLOCKED_INPUT", "message": f"Documentos obrigatórios ausentes: {', '.join(missing_required)}"}
                ],
                warnings=[],
                results=[],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_BLOCKED_INPUT

        # ── Validação de schemas (progressive — erros viram warnings) ────────
        schema_results = validate_documents_against_schemas(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )
        # Erros de schema são tratados como warnings (pipeline progressivo conforme MOTORES.md).
        # Apenas erros infra (schema inválido em si) são hard-blocking.
        schema_warnings = schema_results.warnings + [
            {"rule_id": "SCHEMA_WARNING", "document": e.get("document", "?"), "reason": e["reason"]}
            for e in schema_results.errors
        ]

        # ── Contexto de validação ─────────────────────────────────────────
        ctx = ValidationContext(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )

        # ── Execução dos checkers ─────────────────────────────────────────
        _use_v2 = getattr(args, "governance_v2_dry_run", False) \
                  or os.environ.get("HB_GOVERNANCE_V2_PHASE_FILTER", "0") == "1"
        if _use_v2:
            _pre = run_allowed_rules(ctx, phase="PRE_PLAN")
            _post = run_allowed_rules(ctx, phase="POST_PLAN")
            lint_results = _pre + _post
        else:
            lint_results = run_allowed_rules(ctx)

        failures = [r for r in lint_results if r.status == "FAIL"]
        infra_errors = [r for r in lint_results if r.status == "ERROR"]

        if failures or infra_errors:
            write_plan_reports(
                reports_dir=reports_dir,
                status="FAIL_ACTIONABLE" if failures else "ERROR_INFRA",
                errors=[r.__dict__ for r in failures + infra_errors],
                warnings=schema_warnings,
                results=[r.__dict__ for r in lint_results],
                handoff_path=None,
                anchor_manifest_path=None,
            )
            return EXIT_FAIL_ACTIONABLE if failures else EXIT_ERROR_INFRA

        # ── Build anchor manifest ─────────────────────────────────────────
        anchor_manifest = build_anchor_manifest(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
        )

        anchor_manifest_path = reports_dir / "anchor_manifest.json"
        anchor_manifest_path.write_text(
            json.dumps(anchor_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        ctx.anchor_manifest = anchor_manifest

        # ── Build handoff ─────────────────────────────────────────────────
        handoff = build_handoff(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            anchor_manifest=anchor_manifest,
            reports_dir=reports_dir,
        )

        # Incorporar hash do manifesto de âncoras
        handoff.setdefault("integrity", {})
        handoff["integrity"]["anchor_manifest_sha256"] = sha256_file(anchor_manifest_path)

        # Calcular snapshot_hash final (com zeros como placeholder para evitar circularidade)
        provisional = json.loads(json.dumps(handoff))
        provisional["integrity"]["snapshot_hash"] = "0" * 64
        snapshot_hash = sha256_jsonable(provisional)
        handoff["integrity"]["snapshot_hash"] = snapshot_hash

        # Gravar handoff
        handoff_path = module_root / "16_ATLETAS_AGENT_HANDOFF.json"
        handoff_path.write_text(
            json.dumps(handoff, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # ── Relatório final ───────────────────────────────────────────────
        write_plan_reports(
            reports_dir=reports_dir,
            status="PASS",
            errors=[],
            warnings=schema_warnings + [r.__dict__ for r in lint_results if r.status == "SKIP"],
            results=[r.__dict__ for r in lint_results],
            handoff_path=handoff_path,
            anchor_manifest_path=anchor_manifest_path,
        )

        print(f"[hb_plan] PASS — handoff gravado em {handoff_path}")
        return EXIT_PASS

    except Exception as exc:
        try:
            write_plan_reports(
                reports_dir=args.reports_dir.resolve() if not args.reports_dir.is_absolute() else args.reports_dir,
                status="ERROR_INFRA",
                errors=[{"rule_id": "ERROR_INFRA", "message": f"{type(exc).__name__}: {exc}"}],
                warnings=[],
                results=[],
                handoff_path=None,
                anchor_manifest_path=None,
            )
        except Exception:
            pass

        print(f"[hb_plan] ERROR_INFRA: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR_INFRA


if __name__ == "__main__":
    sys.exit(main())
