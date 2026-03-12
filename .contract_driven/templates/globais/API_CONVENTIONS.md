<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/API_CONVENTIONS.md | SOURCE: .contract_driven/templates/globais/API_CONVENTIONS.md -->

# API_CONVENTIONS.md

## Objetivo
Padronizar o design e a evolução das APIs de `{{PROJECT_NAME}}`.

## Fonte canônica (SSOT)
As convenções, validações e templates canônicos de APIs vivem em:

- `.contract_driven/templates/API_RULES/API_RULES.yaml`

Regras:
- este documento **NÃO** deve duplicar regras; ele deve apenas **apontar** para `API_RULES.yaml`.
- em caso de conflito com qualquer outra convenção, prevalece `API_RULES.yaml` (salvo exceção HB Track explícita e normativa).
- se uma convenção necessária não estiver explícita em `API_RULES.yaml`, ela não pode ser inferida (bloquear com `BLOCKED_MISSING_API_CONVENTION`).

## Referência
- Regras e desempate: `API_RULES.yaml` (conflict_resolution)
- Templates de OpenAPI: `API_RULES.yaml` (contract_templates)
- Segurança: `API_RULES.yaml` (security_rules)
