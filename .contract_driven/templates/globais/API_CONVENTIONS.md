<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/API_CONVENTIONS.md | SOURCE: .contract_driven/templates/globais/API_CONVENTIONS.md -->

# API_CONVENTIONS.md

## Objetivo
Padronizar o design e a evolução das APIs de `{{PROJECT_NAME}}`.

## Fonte canônica (SSOT)
As convenções, validações e templates canônicos de APIs vivem em:

- `.contract_driven/templates/api/api_rules.yaml`

Regras:
- este documento **NÃO** deve duplicar regras; ele deve apenas **apontar** para `api_rules.yaml`.
- em caso de conflito com qualquer outra convenção, prevalece `api_rules.yaml` (salvo exceção HB Track explícita e normativa).
- se uma convenção necessária não estiver explícita em `api_rules.yaml`, ela não pode ser inferida (bloquear com `BLOCKED_MISSING_API_CONVENTION`).

## Referência
- Regras e desempate: `api_rules.yaml` (conflict_resolution)
- Templates de OpenAPI: `api_rules.yaml` (contract_templates)
- Segurança: `api_rules.yaml` (security_rules)
