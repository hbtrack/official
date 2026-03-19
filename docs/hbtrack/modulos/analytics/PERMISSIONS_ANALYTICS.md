---
module: "analytics"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_ANALYTICS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_ANALYTICS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `analytics` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listAnalyticsSnapshots` | ✅ | ✅ | ✅ | ✅ (próprios) | ❌ | Athlete vê apenas snapshots gerados a partir de seus próprios dados |
| `createAnalyticsSnapshot` | ✅ | ✅ | ✅ | ❌ | ❌ | Snapshot de grupo requer role staff |
| `getAnalyticsSnapshot` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | BOLA: athlete acessa somente snapshot de seus dados |
| `listAnalyticsDashboards` | ✅ | ✅ | ✅ | ✅ (próprios) | ❌ | Dashboard personalizado por atleta vs. dashboards de equipe (staff only) |
| `queryAnalyticsData` | ✅ | ✅ | ✅ | ❌ | ❌ | Query ad-hoc restrita a gestores; dados agregados de time são sensíveis |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-ANL-001 | Athlete só acessa dados derivados dos seus próprios atributos (BOLA) | ADR-008, DOMAIN_RULES_ANALYTICS |
| PERM-ANL-002 | Queries analíticas com escopo de time requerem role coordinator ou acima | DOMAIN_RULES_ANALYTICS |
| PERM-ANL-003 | Dados de analytics são read-only para todos; nenhum role pode sobrescrever snapshots computados | DOMAIN_RULES_ANALYTICS |
