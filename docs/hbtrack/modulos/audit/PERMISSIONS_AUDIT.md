# PERMISSIONS_AUDIT.md
# Módulo: audit
# Tabela de controle de acesso RBAC (ADR-008)
# Decisions: DEC-AUD-002=B
# Domain rules: DR-AUD-001
# Invariants: INV-AUD-002
# OWASP: API1:2023 (BOLA), API2:2023 (BFLA), API5:2023 (Function Level Auth)

---
module: "audit"
rbac_model: "flat_5_roles"
adr_ref: "ADR-008"
decision_ref: "DEC-AUD-002=B"
updated: "2026-03-19"
---

# PERMISSIONS_AUDIT.md

## Modelo de acesso (DEC-AUD-002=B)

**admin**: acesso irrestrito a todas as entradas do trilho de auditoria, sem filtros obrigatórios.

**coordinator**: acesso contextual — somente entradas relacionadas a recursos do time/organização que gerencia. Os parâmetros `teamId` ou `organizationId` são obrigatórios nas requisições de listagem e exportação.

**coach / athlete / member**: sem acesso ao audit trail (403 BFLA — OWASP API2:2023).

---

## Tabela de permissões por operação

| Operação | admin | coordinator | coach | athlete | member | Observação |
|---|:---:|:---:|:---:|:---:|:---:|---|
| `listAuditEntries` (GET /audit/entries) | ✅ | ✅ ⚠️ | ❌ | ❌ | ❌ | coordinator: teamId ou organizationId obrigatório |
| `createAuditEntry` (POST /audit/entries) | ✅ | ✅ ⚠️ | ❌ | ❌ | ❌ | coordinator: apenas entradas dentro do seu contexto |
| `getAuditEntry` (GET /audit/entries/{entryId}) | ✅ | ✅ ⚠️ | ❌ | ❌ | ❌ | coordinator: apenas entradas do seu contexto (BOLA) |
| `exportAuditEntries` (GET /audit/entries/export) | ✅ | ✅ ⚠️ | ❌ | ❌ | ❌ | coordinator: teamId ou organizationId obrigatório |

**Legenda:**
- ✅ – Permitido sem restrição adicional.
- ✅ ⚠️ – Permitido com filtro obrigatório de contexto (teamId ou organizationId).
- ❌ – Proibido (retorna 403 Forbidden — BFLA).

---

## Regras de enforcement

### PERM-AUD-001 — Coordinator filtro obrigatório
Quando o ator autenticado tem role `coordinator`, os endpoints `listAuditEntries`, `createAuditEntry` (verificação server-side do target) e `exportAuditEntries` exigem ao menos um dos parâmetros `teamId` ou `organizationId` correspondente à organização que o coordinator gerencia. Violar esta regra retorna 400 Bad Request com mensagem descritiva.

### PERM-AUD-002 — BOLA enforcement (getAuditEntry)
Quando um `coordinator` acessa `GET /audit/entries/{entryId}`, o servidor verifica se o `targetResourceId` da entrada pertence a um recurso dentro do contexto do coordinator. Se não pertencer, retorna 403 (não 404, para evitar leak de existência).

### PERM-AUD-003 — Append-only via API
Nenhum role pode modificar ou deletar uma entrada de auditoria existente via API. O módulo audit não expõe endpoints PATCH/PUT/DELETE (INV-AUD-002).

### PERM-AUD-004 — Auto-audit da exportação
Toda chamada bem-sucedida a `exportAuditEntries` gera automaticamente uma nova entrada no próprio audit trail com `action: audit.export_requested` e `actorUserId` do solicitante. Esta entrada é append-only e não pode ser filtrada para suprimir evidência da exportação.

### PERM-AUD-005 — Ingestão cross-module
Outros módulos do HB Track (ex.: identity_access, training, notifications) podem usar `POST /audit/entries` com o token do ator real (`actorUserId` = usuário que disparou a ação no módulo de origem). Chamadas com `actorUserId` diferente do userId do token JWT são permitidas apenas para role `admin`.

---

## Referências
- `ADR-008` — RBAC flat 5 roles
- `DR-AUD-001` — audit é soberano do trilho imutável
- `INV-AUD-002` — append-only
- `DEC-AUD-002=B` — modelo de acesso admin/coordinator/deny
- OWASP API Security Top 10 (2023): API1 BOLA, API2 BFLA, API5 Function Level Auth
