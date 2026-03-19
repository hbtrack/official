---
module: "ai_ingestion"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_AI_INGESTION.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_AI_INGESTION.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `ai_ingestion` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listIngestionJobs` | ✅ | ✅ | ❌ | ❌ | ❌ | Acesso restrito a gestores; dados de ingestão são internos |
| `createIngestionJob` | ✅ | ✅ | ❌ | ❌ | ❌ | Operação de plataforma — requer role de gestão |
| `getIngestionJob` | ✅ | ✅ | ❌ | ❌ | ❌ | Monitoramento de job; técnico interno |
| `retryIngestionJob` | ✅ | ✅ | ❌ | ❌ | ❌ | Operação de retry requer permissão de gestão |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-AI-001 | Apenas admin e coordinator têm acesso a jobs de ingestão de IA | ADR-008, DOMAIN_RULES_AI_INGESTION |
| PERM-AI-002 | Jobs de ingestão não expõem dados de atletas diretamente — encapsula pipeline de ML | DOMAIN_RULES_AI_INGESTION |
| PERM-AI-003 | Retry de job requer validação de estado: FAILED ou ERROR (não reprocessar jobs em PROCESSING) | DOMAIN_RULES_AI_INGESTION |
