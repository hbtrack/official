"""
Checkers de conformidade do prompt de restrições — RP-001..004.

cannot_waive: RP-001, RP-002, RP-003, RP-004
"""
from __future__ import annotations

from hbtrack_lint.engine import register_checker, RuleResult

_PROMPT_FILE = "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md"


def _get_prompt_text(ctx) -> str | None:
    contracts = ctx.contracts
    raw = contracts.get(_PROMPT_FILE)
    if raw is None:
        # Pode estar no contracts como conteúdo de texto (loader carrega como str para .md)
        return None

    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return str(raw)
    return None


def check_executor_prompt_is_fail_closed(rule: dict, ctx) -> RuleResult:
    """RP-001 (PRE_PLAN, cannot_waive): Prompt deve declarar comportamento fail-closed."""
    text = _get_prompt_text(ctx)
    if text is None:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], f"'{_PROMPT_FILE}' não encontrado nos contratos")

    markers = ["fail-closed", "FAIL-CLOSED", "fail closed", "FAIL CLOSED", "falha segura"]
    if any(m in text for m in markers):
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.fail(
        rule["rule_id"], rule["checker_id"],
        f"'{_PROMPT_FILE}' não contém declaração de comportamento fail-closed. "
        f"Esperado um dos: {markers}"
    )


def check_executor_prompt_forbids_chat_history_as_truth(rule: dict, ctx) -> RuleResult:
    """RP-002 (PRE_PLAN, cannot_waive): Prompt deve proibir uso do histórico de chat como fonte de verdade."""
    text = _get_prompt_text(ctx)
    if text is None:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], f"'{_PROMPT_FILE}' não encontrado")

    markers = [
        "histórico de chat",
        "Histórico de Chat",
        "historico de chat",
        "chat history",
        "chat como fonte",
        "NÃO use histórico",
        "não use histórico",
    ]
    if any(m in text for m in markers):
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.fail(
        rule["rule_id"], rule["checker_id"],
        f"'{_PROMPT_FILE}' não contém proibição explícita de uso do histórico de chat como fonte de verdade. "
        f"Esperado: variação de 'histórico de chat'"
    )


def check_executor_prompt_requires_blocked_input_on_contract_gap(rule: dict, ctx) -> RuleResult:
    """RP-003 (PRE_PLAN, cannot_waive): Prompt deve exigir BLOCKED_INPUT quando houver lacuna de contrato."""
    text = _get_prompt_text(ctx)
    if text is None:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], f"'{_PROMPT_FILE}' não encontrado")

    if "BLOCKED_INPUT" in text:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.fail(
        rule["rule_id"], rule["checker_id"],
        f"'{_PROMPT_FILE}' não contém 'BLOCKED_INPUT' — o prompt deve exigir esse comportamento em lacunas de contrato"
    )


def check_prompt_textual_compliance_with_constitution(rule: dict, ctx) -> RuleResult:
    """RP-004 (PRE_PLAN, cannot_waive): Prompt deve estar em conformidade textual completa com a constituição."""
    text = _get_prompt_text(ctx)
    if text is None:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], f"'{_PROMPT_FILE}' não encontrado")

    constitution = ctx.contracts.get("00_ATLETAS_CROSS_LINTER_RULES.json") or {}

    # Obter marcadores obrigatórios da constituição (se declarados)
    compliance = constitution.get("rp_compliance_markers") or {}
    required_markers = compliance.get("required") or []

    # Marcadores padrão quando constituição não os especifica explicitamente
    default_required = [
        # fail-closed
        ("fail_closed", ["fail-closed", "FAIL-CLOSED"]),
        # proibição de chat como fonte
        ("chat_prohibition", ["histórico de chat", "Histórico de Chat", "historico de chat", "chat history"]),
        # BLOCKED_INPUT
        ("blocked_input", ["BLOCKED_INPUT"]),
    ]

    missing = []
    for marker_key, variants in default_required:
        if not any(v in text for v in variants):
            missing.append(marker_key)

    # Verificar marcadores extras da constituição se presentes
    for marker in required_markers:
        name = marker.get("name") if isinstance(marker, dict) else str(marker)
        variants = marker.get("variants", [name]) if isinstance(marker, dict) else [marker]
        if not any(v in text for v in variants):
            missing.append(name)

    if missing:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"'{_PROMPT_FILE}' não está em conformidade com a constituição. "
            f"Marcadores ausentes: {', '.join(missing)}"
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_executor_prompt_is_fail_closed", check_executor_prompt_is_fail_closed)
register_checker("check_executor_prompt_forbids_chat_history_as_truth", check_executor_prompt_forbids_chat_history_as_truth)
register_checker("check_executor_prompt_requires_blocked_input_on_contract_gap", check_executor_prompt_requires_blocked_input_on_contract_gap)
register_checker("check_prompt_textual_compliance_with_constitution", check_prompt_textual_compliance_with_constitution)
