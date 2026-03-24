"""
⚠️  LEGADO — DEPRECATED: Este pacote (hbtrack_lint) não está mais no caminho crítico do HB Track.
A validação de contratos migrou para scripts/contracts/validate/validate_contracts.py.
Mantenha este pacote apenas como referência histórica. NÃO importar em código novo.
(FASE 7 do AGENT_COMPLIANCE_EXECUTION_PLAN.md — LEGACY isolation)

HB Track Lint — pacote de validação determinística de contratos para o módulo ATLETAS.

Estrutura:
    context.py         — ValidationContext
    hashing.py         — sha256_file, sha256_jsonable
    loader.py          — load_contract_pack
    engine.py          — RuleResult, run_rule
    schemas.py         — validate_documents_against_schemas
    reports.py         — write_plan_reports
    anchor_manifest.py — build_anchor_manifest
    handoff_builder.py — build_handoff
    checker_registry.py— run_allowed_rules, CHECKERS

Referência canônica: docs/hbtrack/modulos/atletas/MOTORES.md
"""
