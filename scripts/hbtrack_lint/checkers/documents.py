"""
Checkers de forma de documentos — DOC-001 a DOC-005.

cannot_waive: DOC-001, DOC-003, DOC-004, DOC-005
"""
from __future__ import annotations

import json
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult
from hbtrack_lint.loader import REQUIRED_DOCS

# Marcadores de placeholder que não devem existir em documentos promovidos
_PLACEHOLDER_MARKERS = ["TODO", "TBD", "FIXME", "PLACEHOLDER", "...TBD...", "<<FILL>>"]


def check_required_documents_exist(rule: dict, ctx) -> RuleResult:
    """DOC-001: Todos os documentos requeridos devem existir."""
    missing = [name for name in REQUIRED_DOCS if name not in ctx.contracts]
    if missing:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Documentos requeridos ausentes: {missing}",
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_required_document_metadata_fields_exist(rule: dict, ctx) -> RuleResult:
    """DOC-002: Todo documento requerido deve expor campos de metadados canônicos (quando aplicável)."""
    errors = []
    for name in REQUIRED_DOCS:
        if name not in ctx.contracts:
            continue
        doc = ctx.contracts[name]
        if not isinstance(doc, dict):
            continue
        # Apenas documentos YAML/JSON com campo meta ou metadata são verificados
        if "meta" not in doc and "metadata" not in doc:
            errors.append(f"{name}: campo 'meta' ou 'metadata' ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_promoted_documents_do_not_contain_placeholders(rule: dict, ctx) -> RuleResult:
    """DOC-003: Nenhum documento promovido pode conter marcadores de placeholder."""
    errors = []
    for name in REQUIRED_DOCS:
        path = ctx.module_root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in _PLACEHOLDER_MARKERS:
            if marker in text:
                errors.append(f"{name}: contém placeholder '{marker}'")
                break

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_execution_bindings_validate_against_schema(rule: dict, ctx) -> RuleResult:
    """DOC-004: 12_ATLETAS_EXECUTION_BINDINGS.yaml deve validar contra o schema canônico."""
    doc_name = "12_ATLETAS_EXECUTION_BINDINGS.yaml"
    schema_path = ctx.module_root / "12_ATLETAS_EXECUTION_BINDINGS.schema.json"

    if doc_name not in ctx.contracts:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], f"{doc_name} não encontrado")

    if not schema_path.exists():
        return RuleResult.skip(
            rule["rule_id"], rule["checker_id"],
            f"Schema {schema_path.name} não encontrado — validação ignorada",
        )

    try:
        from jsonschema import Draft202012Validator
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errs = sorted(validator.iter_errors(ctx.contracts[doc_name]), key=lambda e: list(e.path))
        if errs:
            msgs = [e.message for e in errs[:5]]
            return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(msgs))
    except ImportError:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "jsonschema não instalado")
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], str(exc))

    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_generated_documents_exist_and_have_integrity(rule: dict, ctx) -> RuleResult:
    """DOC-005: Documentos gerados devem existir após o plano e satisfazer o contrato de integridade mínimo."""
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"
    anchor_manifest_path = (ctx.repo_root / "_reports" / "anchor_manifest.json")

    errors = []

    # Verificar handoff
    if not handoff_path.exists():
        errors.append("16_ATLETAS_AGENT_HANDOFF.json não encontrado após plano")
    else:
        try:
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            required_fields = ["meta", "integrity", "task_plan", "entry_gates", "exit_gates"]
            for field in required_fields:
                if field not in handoff:
                    errors.append(f"Handoff: campo '{field}' ausente")
            arts = handoff.get("integrity", {}).get("artifacts", [])
            if not arts:
                errors.append("Handoff: integrity.artifacts vazio")
            snap = handoff.get("integrity", {}).get("snapshot_hash", "")
            if not snap or snap == "0" * 64:
                errors.append("Handoff: snapshot_hash é placeholder zeros ou ausente")
        except Exception as exc:
            errors.append(f"Handoff: JSON inválido — {exc}")

    # anchor_manifest é opcional — apenas avisar
    if not anchor_manifest_path.exists():
        pass  # Não é bloquante (é gerado durante plan, não pré-condição)

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# --- Registro ---
register_checker("check_required_documents_exist", check_required_documents_exist)
register_checker("check_required_document_metadata_fields_exist", check_required_document_metadata_fields_exist)
register_checker("check_promoted_documents_do_not_contain_placeholders", check_promoted_documents_do_not_contain_placeholders)
register_checker("check_execution_bindings_validate_against_schema", check_execution_bindings_validate_against_schema)
register_checker("check_generated_documents_exist_and_have_integrity", check_generated_documents_exist_and_have_integrity)
