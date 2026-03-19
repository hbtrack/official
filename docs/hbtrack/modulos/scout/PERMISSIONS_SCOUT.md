---
module: "scout"
type: "permissions"
decisions_ref: ".contract_driven/decisions/DECISION_IR_SCOUT.yaml"
domain_rules_ref: "docs/hbtrack/modulos/scout/DOMAIN_RULES_SCOUT.md"
updated: "2026-03-19"
---

# PERMISSIONS_SCOUT.md

## Objetivo
Registra as regras de controle de acesso do módulo `scout` derivadas das decisões
DEC-SCOUT-001=C, DEC-SCOUT-002=B, DEC-SCOUT-003=C e dos ADRs de autenticação/autorização.

## Roles canônicos (ADR-008)
| Role | Descrição |
|---|---|
| admin | Acesso irrestrito a todos os endpoints e todos os times |
| coordinator | Leitura e escrita com filtro obrigatório de teamId |
| coach | Leitura e escrita com filtro obrigatório de teamId |
| athlete | Leitura somente de eventos onde athleteUserId == self |
| member | Bloqueado em todos os endpoints (403) |

## Regras de permissão

### PERM-SCOUT-001 — Filtro contextual obrigatório para coordinator/coach
- **Endpoint:** listScoutEvents, getScoutAggregations
- **Regra:** coordinator e coach DEVEM informar `teamId` no query parameter.
  Requisição sem `teamId` retorna **403** (não 400).
- **Fundamento:** OWASP API1:2023 (BOLA), DEC-SCOUT-002=B.

### PERM-SCOUT-002 — BOLA enforcement no getScoutEvent
- **Endpoint:** getScoutEvent
- **Regra:** backend DEVE verificar que o ator autenticado tem acesso ao time/atleta
  do evento solicitado. Se não tiver acesso, retorna **403** (não 404).
- **Fundamento:** OWASP API1:2023, DEC-SCOUT-002=B.

### PERM-SCOUT-003 — Athlete read-only de eventos próprios
- **Endpoint:** listScoutEvents, getScoutEvent, getScoutAggregations
- **Regra:** athlete pode SOMENTE ler eventos/agregações onde `athleteUserId == self`
  ou partidas em que participou. Não pode criar eventos (403 no createScoutEvent
  e completeScoutSession).
- **Fundamento:** DEC-SCOUT-002=B, transparência do atleta sem violar integridade observacional.

### PERM-SCOUT-004 — Member bloqueado
- **Endpoint:** TODOS
- **Regra:** role `member` recebe **403** em qualquer endpoint do scout.
- **Fundamento:** OWASP API2:2023 (BFLA), DEC-SCOUT-002=B.

### PERM-SCOUT-005 — Escrita restrita a admin/coordinator/coach
- **Endpoint:** createScoutEvent, completeScoutSession
- **Regra:** somente admin, coordinator e coach podem criar eventos e finalizar sessões.
  coordinator/coach devem operar no time que gerenciam.
- **Fundamento:** DR-SCOUT-001 (scout soberano de observações), DEC-SCOUT-002=B.

## Matriz de acesso por endpoint

| Endpoint | admin | coordinator | coach | athlete | member |
|---|:---:|:---:|:---:|:---:|:---:|
| listScoutEvents | ✅ | ✅ (teamId obrig.) | ✅ (teamId obrig.) | ✅ (self only) | ❌ 403 |
| createScoutEvent | ✅ | ✅ (seu time) | ✅ (seu time) | ❌ 403 | ❌ 403 |
| getScoutEvent | ✅ | ✅ (seu time) | ✅ (seu time) | ✅ (self only) | ❌ 403 |
| getScoutAggregations | ✅ | ✅ (teamId obrig.) | ✅ (teamId obrig.) | ✅ (suas partidas) | ❌ 403 |
| completeScoutSession | ✅ | ✅ (seu time) | ✅ (seu time) | ❌ 403 | ❌ 403 |
