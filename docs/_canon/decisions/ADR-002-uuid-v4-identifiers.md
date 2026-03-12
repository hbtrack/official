# ADR-002: UUID v4 como identificadores globais de entidade

- Status: Accepted
- Date: 2026-03-11
- Deciders: Equipe HB Track
- Tags: data-conventions, identifiers, api

## Context

O HB Track precisa de uma estratégia de identificadores para todas as entidades persistidas e expostas via API. As alternativas clássicas são: inteiros auto-incrementais (simples, sequenciais, previsíveis) ou UUIDs (opacos, não sequenciais, geráveis no cliente). A plataforma expõe IDs diretamente em paths de URL e em payloads de API.

## Decision

Usar UUID v4 como string em todos os identificadores de entidade expostos via API pública e persistidos no banco de dados. Formato canônico: string, lower-case, com hífens (ex: `"3f7a1c2e-8b4d-4e9f-a3c1-0d5f6b7e8a9c"`).

Esta decisão está documentada em `docs/_canon/DATA_CONVENTIONS.md` como convenção canônica.

## Consequences

### Positive
- IDs opacos: não vaza sequência, volume ou data de criação para o cliente.
- Geração no cliente: permite criar IDs antes de persistir (útil para idempotência e pre-confirm).
- Segurança: não permite enumeração de recursos por incremento.

### Negative
- Performance de índice: UUIDs são menos eficientes que inteiros em índices B-tree em PostgreSQL; mitigado via `uuid-ossp` ou `gen_random_uuid()` com índice.
- Verbosidade: payloads e URLs ficam maiores.

## Alternatives Considered

- **Inteiros auto-incrementais**: simples, mas vaza informação de volume e sequência; vulnerável a enumeração. Rejeitado.
- **ULID**: ordenável cronologicamente, mas não amplamente suportado em tooling de validação OpenAPI. Rejeitado por ora.
- **Short ID / slug**: adequado para URLs amigáveis, mas requer mapeamento separado. Rejeitado como identificador primário.

## Links

- Related docs: `docs/_canon/DATA_CONVENTIONS.md`, `docs/_canon/API_CONVENTIONS.md`
- Related contracts: `contracts/openapi/openapi.yaml`, `contracts/openapi/components/parameters/`