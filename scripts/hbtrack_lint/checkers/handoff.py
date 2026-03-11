"""
Checkers de handoff — HO-001 a HO-004.

cannot_waive: HO-002
"""
from __future__ import annotations

import json
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult


def check_markdown_handoff_is_not_authoritative(rule: dict, ctx) -> RuleResult:
    """HO-001: Handoff Markdown não pode ser autoritativo."""
    # Verificar que não há arquivo .md sendo usado como handoff autoritativo
    md_handoffs = list(ctx.module_root.glob("*handoff*.md"))
    if md_handoffs:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Arquivo(s) Markdown de handoff encontrado(s): {[f.name for f in md_handoffs]}. "
            f"Somente 16_ATLETAS_AGENT_HANDOFF.json é autoritativo.",
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_executor_starts_only_from_structured_manifest(rule: dict, ctx) -> RuleResult:
    """HO-002: Executor só pode iniciar a partir de manifest estruturado com hashes de integridade."""
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"

    if not handoff_path.exists():
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            "16_ATLETAS_AGENT_HANDOFF.json não encontrado — Executor não pode iniciar",
        )

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], f"JSON inválido: {exc}")

    errors = []
    integrity = handoff.get("integrity") or {}
    artifacts = integrity.get("artifacts") or []
    snapshot_hash = integrity.get("snapshot_hash")

    if not artifacts:
        errors.append("integrity.artifacts vazio — sem hashes de integridade")
    if not snapshot_hash or snapshot_hash == "0" * 64:
        errors.append("integrity.snapshot_hash ausente ou é placeholder zeros")

    # Verificar campos mínimos do meta
    meta = handoff.get("meta") or {}
    if not meta.get("handoff_id"):
        errors.append("meta.handoff_id ausente")
    if not meta.get("status"):
        errors.append("meta.status ausente")

    if not handoff.get("task_plan"):
        errors.append("task_plan ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_execution_blocks_on_hash_drift(rule: dict, ctx) -> RuleResult:
    """HO-003: Se qualquer hash de artefato requerido divergir do snapshot, execução deve ser bloqueada."""
    # Esta regra é verificada por X-012 (check_handoff_hashes_match_snapshot)
    # Aqui verificamos se a política está declarada no handoff
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"
    if not handoff_path.exists():
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Handoff não encontrado")

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], str(exc))

    stale_policy = (handoff.get("integrity") or {}).get("stale_snapshot_policy")
    if stale_policy != "block_execution":
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"integrity.stale_snapshot_policy='{stale_policy}' mas deve ser 'block_execution'",
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_handoff_scope_is_subset_of_allowed_targets(rule: dict, ctx) -> RuleResult:
    """HO-004: Task plan deve ser subconjunto das operações e caminhos de arquivo permitidos."""
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    if not handoff_path.exists():
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Handoff não encontrado")

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], str(exc))

    traced_ops = {op["operation_id"] for op in (traceability.get("operations") or [])}
    allowed_ops = (handoff.get("execution_scope") or {}).get("allowed_operation_ids") or []

    errors = []
    for op_id in allowed_ops:
        if op_id not in traced_ops:
            errors.append(f"'{op_id}' em allowed_operation_ids mas não em traceability")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_markdown_handoff_is_not_authoritative", check_markdown_handoff_is_not_authoritative)
register_checker("check_executor_starts_only_from_structured_manifest", check_executor_starts_only_from_structured_manifest)
register_checker("check_execution_blocks_on_hash_drift", check_execution_blocks_on_hash_drift)
register_checker("check_handoff_scope_is_subset_of_allowed_targets", check_handoff_scope_is_subset_of_allowed_targets)
