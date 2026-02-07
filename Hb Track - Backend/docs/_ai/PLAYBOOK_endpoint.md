# PLAYBOOK — ENDPOINT/API (OpenAPI-first)

## Objetivo
Implementar/alterar endpoint garantindo consistência com OpenAPI 3.1 e persistência (quando aplicável).

## Procedimento
1) OpenAPI-first
- Abrir docs/_generated/openapi.json e identificar:
  - path + method
  - request schema
  - response schema(s)
  - status codes e erros

2) Implementação
- Localizar router/handler via busca no repo.
- Garantir validação e tipagem (Pydantic/Zod conforme camada).
- Se mexer em DB: alinhar com schema.sql e migrations.

3) Artefatos gerados
- Atualizar openapi.json/schema.sql/alembic_state.txt usando os comandos oficiais do projeto.
  (Se não existirem, criar comandos em docs/_ai/CHECKS.md e automatizar depois.)

4) Verificação
- Rodar testes relevantes (pytest; Playwright se for fluxo).
- Rodar lint/typecheck front quando tocar em TS.

## Formato de saída
Evidências:
- <paths>

Mudança:
- <patch mínimo + motivo>

Compatibilidade:
- <impacto no contrato/API>

Checks:
- <comandos e resultados>