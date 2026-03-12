<!-- TEMPLATE: global-canon-template | DEST: docs/_canon/GLOBAL_INVARIANTS.md | SOURCE: .contract_driven/templates/globais/GLOBAL_INVARIANTS.md -->

# GLOBAL_INVARIANTS.md

## Objetivo
Registrar regras que devem permanecer verdadeiras em todo o sistema.

## Invariantes Globais
1. Todo recurso público deve ter identificador estável.
2. Toda interface HTTP pública deve existir em `contracts/openapi/openapi.yaml`.
3. Todo payload público estável deve possuir schema correspondente.
4. Toda mudança breaking deve ser explicitamente classificada e revisada.
5. Toda regra de negócio derivada do handebol deve ser rastreável para `HANDBALL_RULES_DOMAIN.md`.
6. Toda resposta de erro HTTP deve seguir `ERROR_MODEL.md`.
7. Toda tela que dependa de API pública deve estar alinhada ao contrato vigente.
8. Toda permissão sensível deve estar documentada e verificável.

## Formato recomendado
| ID | Invariante | Escopo | Fonte | Como verificar |
|---|---|---|---|---|
| GI-001 | {{INVARIANT}} | Global | {{SOURCE}} | {{CHECK_METHOD}} |

## Violação
Qualquer violação de invariante global deve bloquear merge até resolução ou exceção formal registrada.
