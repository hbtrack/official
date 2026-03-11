"""
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
