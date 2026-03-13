---
doc_type: canon
version: "2.0.0"
last_reviewed: "2026-03-12"
status: active
---

# ERROR_MODEL.md

## Objetivo
Padronizar o formato de erros HTTP do HB Track usando **Problem Details for HTTP APIs** (RFC 7807) sem duplicar regras normativas fora da SSOT.

## SSOT (fonte canônica)
As regras determinísticas de shape, validação e uso do modelo de erro vivem em:
- `.contract_driven/DOMAIN_AXIOMS.json` (seção `error_axioms`)
- `.contract_driven/templates/api/api_rules.yaml` (convenções HTTP/OpenAPI)
- `contracts/openapi/components/schemas/shared/problem.yaml` (schema OpenAPI do payload de erro)

Este documento existe como ponteiro e visão humana (não-SSOT).

## Ponteiros operacionais
- Media type canônico: `application/problem+json`
- Shape OpenAPI: `contracts/openapi/components/schemas/shared/problem.yaml`
- Convenções de API (SSOT): `.contract_driven/templates/api/api_rules.yaml`
