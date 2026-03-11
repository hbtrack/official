#!/usr/bin/env python3
"""
hb_verify.py — HB Track verificador pós-execução para módulo ATLETAS.

Valida:
  1. Snapshot hash do handoff bate com arquivos atuais
  2. Integridade AST dos stubs Python (quando original_dir fornecido)
  3. Regras POST_EXECUTION do meta-contrato

Entrada:
  module_root  — diretório do contract pack

Saída:
  _reports/hb_verify_result.json
  _reports/hb_verify_result.md

Exit codes:
  0 = PASS
  2 = FAIL
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
from hbtrack_lint.loader import load_contract_pack
from hbtrack_lint.checker_registry import run_allowed_rules
from hbtrack_lint.hashing import sha256_file, sha256_jsonable
from hbtrack_lint.reports import write_verify_reports

EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_ERROR_INFRA = 3
EXIT_BLOCKED_INPUT = 4

HANDOFF_FILE = "16_ATLETAS_AGENT_HANDOFF.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HB Track verificador pós-execução — valida integridade de stubs e handoff"
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
        "--original-dir",
        type=Path,
        default=None,
        help="Diretório com cópia original dos stubs (antes da execução pelo Executor)",
    )
    parser.add_argument(
        "--working-dir",
        type=Path,
        default=None,
        help="Diretório com stubs modificados pelo Executor (padrão: repo_root)",
    )
    parser.add_argument(
        "--governance-v2-dry-run",
        action="store_true",
        default=False,
        help="[DRY-RUN] Ativa filtro de phase v2 (POST_EXECUTION) sem alteração de comportamento geral.",
    )
    return parser.parse_args()


def _verify_handoff_snapshot(handoff: dict, module_root: Path) -> list[dict]:
    """Verifica se os hashes de artefatos no handoff conferem com os arquivos atuais."""
    errors = []
    artifacts = (handoff.get("integrity") or {}).get("artifacts") or []

    for artifact in artifacts:
        name = artifact.get("name", "")
        expected_hash = artifact.get("sha256", "")
        file_path = module_root / name

        if not file_path.exists():
            errors.append({"file": name, "reason": "arquivo_nao_encontrado"})
            continue

        actual_hash = sha256_file(file_path)
        if actual_hash != expected_hash:
            errors.append({
                "file": name,
                "reason": "hash_diverge",
                "expected": expected_hash[:16] + "...",
                "actual": actual_hash[:16] + "...",
            })

    return errors


def _verify_snapshot_hash(handoff: dict) -> list[dict]:
    """Verifica se o snapshot_hash do handoff é consistente com seu conteúdo."""
    integrity = handoff.get("integrity") or {}
    stored_hash = integrity.get("snapshot_hash", "")

    if not stored_hash or stored_hash == "0" * 64:
        return [{"reason": "snapshot_hash_zero_ou_ausente"}]

    # Recalcular snapshot_hash com zeros no lugar
    check_handoff = json.loads(json.dumps(handoff))
    check_handoff.setdefault("integrity", {})
    check_handoff["integrity"]["snapshot_hash"] = "0" * 64

    recalculated = sha256_jsonable(check_handoff)
    if recalculated != stored_hash:
        return [{
            "reason": "snapshot_hash_diverge",
            "stored": stored_hash[:16] + "...",
            "recalculated": recalculated[:16] + "...",
        }]

    return []


def main() -> int:
    args = parse_args()

    try:
        repo_root = args.repo_root.resolve()
        module_root = (repo_root / args.module_root).resolve() if not args.module_root.is_absolute() else args.module_root.resolve()
        reports_dir = (repo_root / args.reports_dir).resolve() if not args.reports_dir.is_absolute() else args.reports_dir.resolve()
        reports_dir.mkdir(parents=True, exist_ok=True)

        original_dir = (repo_root / args.original_dir).resolve() if args.original_dir else None
        working_dir = (repo_root / args.working_dir).resolve() if args.working_dir else repo_root

        # ── Validação de entrada ──────────────────────────────────────────
        if not module_root.exists():
            write_verify_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"rule_id": "BLOCKED_INPUT", "message": f"module_root não existe: {module_root}"}],
                results=[],
            )
            return EXIT_BLOCKED_INPUT

        handoff_path = module_root / HANDOFF_FILE
        if not handoff_path.exists():
            write_verify_reports(
                reports_dir=reports_dir,
                status="BLOCKED_INPUT",
                errors=[{"rule_id": "BLOCKED_INPUT", "message": f"Handoff não encontrado: {handoff_path}"}],
                results=[],
            )
            return EXIT_BLOCKED_INPUT

        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))

        # ── Verificar snapshot de artefatos ───────────────────────────────
        artifact_errors = _verify_handoff_snapshot(handoff, module_root)
        snapshot_errors = _verify_snapshot_hash(handoff)

        if artifact_errors or snapshot_errors:
            all_errors = artifact_errors + snapshot_errors
            write_verify_reports(
                reports_dir=reports_dir,
                status="FAIL",
                errors=[{"rule_id": "X-012", "message": "Drift de hash detectado", "details": all_errors}],
                results=[],
            )
            return EXIT_FAIL

        # ── Carregar contratos e executar checkers POST_EXECUTION ─────────
        contracts = load_contract_pack(module_root)

        # Carregar anchor_manifest se existir
        anchor_manifest: dict | None = None
        anchor_manifest_path = reports_dir / "anchor_manifest.json"
        if anchor_manifest_path.exists():
            anchor_manifest = json.loads(anchor_manifest_path.read_text(encoding="utf-8"))

        ctx = ValidationContext(
            repo_root=repo_root,
            module_root=module_root,
            contracts=contracts,
            handoff=handoff,
            anchor_manifest=anchor_manifest,
            original_files_dir=original_dir,
            working_files_dir=working_dir,
        )

        _use_v2 = getattr(args, "governance_v2_dry_run", False) \
                  or os.environ.get("HB_GOVERNANCE_V2_PHASE_FILTER", "0") == "1"
        if _use_v2:
            lint_results = run_allowed_rules(ctx, phase="POST_EXECUTION")
        else:
            lint_results = run_allowed_rules(ctx)

        failures = [r for r in lint_results if r.status == "FAIL"]
        infra_errors = [r for r in lint_results if r.status == "ERROR"]

        if failures or infra_errors:
            write_verify_reports(
                reports_dir=reports_dir,
                status="FAIL",
                errors=[r.__dict__ for r in failures + infra_errors],
                results=[r.__dict__ for r in lint_results],
            )
            return EXIT_FAIL

        # ── PASS ──────────────────────────────────────────────────────────
        write_verify_reports(
            reports_dir=reports_dir,
            status="PASS",
            errors=[],
            results=[r.__dict__ for r in lint_results],
        )

        print(f"[hb_verify] PASS")
        return EXIT_PASS

    except Exception as exc:
        try:
            write_verify_reports(
                reports_dir=args.reports_dir.resolve() if not args.reports_dir.is_absolute() else args.reports_dir,
                status="ERROR_INFRA",
                errors=[{"rule_id": "ERROR_INFRA", "message": f"{type(exc).__name__}: {exc}"}],
                results=[],
            )
        except Exception:
            pass

        print(f"[hb_verify] ERROR_INFRA: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR_INFRA


if __name__ == "__main__":
    sys.exit(main())
