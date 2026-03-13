# GLOBAL_INVARIANTS.md

## Objetivo
Registrar regras que devem permanecer verdadeiras em todo o sistema.

## Invariantes Globais
1. Todo recurso público deve ter identificador estável.
2. Toda interface HTTP pública deve existir em `contracts/openapi/openapi.yaml`.
3. Toda convenção de API HTTP (design/validação/templates) deve seguir `.contract_driven/templates/api/api_rules.yaml`.
4. Todo payload público estável deve possuir schema correspondente.
5. Toda mudança breaking deve ser explicitamente classificada e revisada.
6. Toda regra de negócio derivada do handebol deve ser rastreável para `HANDBALL_RULES_DOMAIN.md`.
7. Toda resposta de erro HTTP deve seguir a SSOT (`.contract_driven/DOMAIN_AXIOMS.json#error_axioms` + `contracts/openapi/components/schemas/shared/problem.yaml`).
8. Toda tela que dependa de API pública deve estar alinhada ao contrato vigente.
9. Toda permissão sensível deve estar documentada e verificável.

## Formato recomendado
| ID | Invariante | Escopo | Fonte | Como verificar |
|---|---|---|---|---|
| GI-001 | Nenhuma rota pública fora do OpenAPI | Global | contracts/openapi/openapi.yaml | Redocly lint + revisão de paths |
| GI-002 | Sem versionamento na URI | API HTTP | .contract_driven/templates/api/api_rules.yaml | Spectral ruleset + revisão |
| GI-003 | Erros seguem RFC 7807 + extensões aprovadas | API HTTP | .contract_driven/DOMAIN_AXIOMS.json + problem.yaml | Lint + testes de contrato |

## Violação
Qualquer violação de invariante global deve bloquear merge até resolução ou exceção formal registrada (ADR).
