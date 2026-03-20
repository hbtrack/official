---
module: "reports"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
  - "ADR-010: sensitive-data-policy (relatórios podem conter PHI)"
domain_rules_ref: "./DOMAIN_RULES_REPORTS.md"
invariants_ref: "./INVARIANTS_REPORTS.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_REPORTS.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `reports` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listReportJobs` | ✅ | ✅ | ✅ (próprios) | ✅ (próprios) | ❌ | BOLA: cada usuário vê apenas os jobs que criou |
| `createReportJob` | ✅ | ✅ | ✅ | ✅ (escopo próprio) | ❌ | Athlete pode criar relatório sobre si mesmo; staff pode criar sobre equipe |
| `getReportJob` | ✅ | ✅ | ✅ (próprio) | ✅ (próprio) | ❌ | BOLA: acesso ao job restrito ao criador e gestores |
| `updateReportJob` | ✅ | ✅ | ✅ (próprio) | ❌ | ❌ | Atualização de parâmetros antes da execução; athlete não pode alterar jobs |
| `downloadReportArtifact` | ✅ | ✅ | ✅ (próprio) | ✅ (próprio) | ❌ | **Conteúdo pode ser PHI** — restrito ao criador do job e gestores |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-REP-001 | Relatórios com dados agregados de time somente para staff (coordinator acima) | DOMAIN_RULES_REPORTS |
| PERM-REP-002 | Download de relatório com PHI gera `data_access_log` obrigatório | ADR-010, DOMAIN_RULES_REPORTS |
| PERM-REP-003 | Jobs em status RUNNING não podem ser atualizados; somente QUEUED | DOMAIN_RULES_REPORTS |
