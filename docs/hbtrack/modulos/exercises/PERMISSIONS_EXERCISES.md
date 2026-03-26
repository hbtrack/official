---
module: "exercises"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_EXERCISES.md"
invariants_ref: "./INVARIANTS_EXERCISES.md"
updated_at: "2026-03-18"
---

# PERMISSIONS_EXERCISES.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização.
> Este artefato **documenta** como `exercises` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).
>
> **Escopo de conteúdo:** exercícios `scope = SYSTEM` são gerenciados por curadores HB Track
> (admin interno); exercícios `scope = ORG` são gerenciados por coaches da organização.
> O role `member` (espectador/familiar) nunca pode criar ou editar conteúdo do catálogo.

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listExercises` | ✅ | ✅ | ✅ | ✅ | ✅ | Todos autenticados; resultado filtrado por scope/ACL (DR-EXB-003, DR-EXB-004) |
| `createExercise` | ✅ | ✅ | ✅ | ❌ | ❌ | Coach cria exercícios `scope = ORG` para sua organização; admin pode criar `scope = SYSTEM` |
| `getExercise` | ✅ | ✅ | ✅ | ✅ (SYSTEM ou ORG acessível) | ✅ (SYSTEM ou ORG acessível) | BOLA: ORG RESTRICTED exige ACL ou ser criador (DR-EXB-004) |
| `updateExercise` | ✅ | ✅ | ✅ (criador ORG) | ❌ | ❌ | Cria nova ExerciseVersion (DR-EXB-001); `scope = SYSTEM` → apenas admin interno |
| `deleteExercise` | ✅ | ✅ | ✅ (criador ORG, sem referências) | ❌ | ❌ | Soft-delete; proibido se há referências históricas em training (INV-EXB-017) |
| `copyExerciseToOrg` | ✅ | ✅ | ✅ | ❌ | ❌ | Cria cópia ORG editável de exercício SYSTEM; criador da cópia = usuário que executa (DR-EXB-009) |
| `listExerciseVersions` | ✅ | ✅ | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | Visibilidade herdada do exercício principal |
| `getExerciseVersion` | ✅ | ✅ | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | Visibilidade herdada do exercício principal |
| `listExerciseRelations` | ✅ | ✅ | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | ✅ (se tem acesso ao exercício) | Relações visíveis para quem vê o exercício |
| `addExerciseRelation` | ✅ | ✅ | ✅ (criador do exercício from ou to) | ❌ | ❌ | Ambos os exercícios devem ser acessíveis ao usuário; relação reflexiva → 422 (INV-EXB-014) |
| `deleteExerciseRelation` | ✅ | ✅ | ✅ (criador do exercício from) | ❌ | ❌ | Coach só remove relações de exercícios que criou |
| `getExerciseAcl` | ✅ | ✅ | ✅ (criador do exercício) | ❌ | ❌ | Apenas criador e staff gerenciam ACL; visível apenas para quem pode gerenciar (DR-EXB-010) |
| `addExerciseAclEntry` | ✅ | ✅ | ✅ (criador do exercício) | ❌ | ❌ | Somente para exercícios ORG RESTRICTED; ACL em SYSTEM → 422 (INV-EXB-010) |
| `removeExerciseAclEntry` | ✅ | ✅ | ✅ (criador do exercício) | ❌ | ❌ | Criador não pode ser removido da própria ACL (INV-EXB-009, DR-EXB-010) |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-EXB-001 | Roles são atribuídos em `identity_access`; `exercises` não altera atribuição de roles | ADR-008 |
| PERM-EXB-002 | `athlete` e `member` têm acesso read-only ao catálogo de exercícios; nunca criam, editam ou deletam | DR-EXB-003, DR-EXB-004 |
| PERM-EXB-003 | Exercícios `scope = SYSTEM` são editáveis apenas por admin com papel curador interno HB Track; coaches lêem mas não editam | DR-EXB-009, INV-EXB-008 |
| PERM-EXB-004 | Coach (`scope = ORG`) é dono do exercício que criou: pode editar, deletar, configurar ACL e visibilidade independentemente de coordinator/admin negar | DR-EXB-010, INV-EXB-009 |
| PERM-EXB-005 | Edição de exercício ORG por outro coach da mesma organização → 403, salvo se estiver na ACL com permissão de edição | DR-EXB-004, INV-EXB-010 |
| PERM-EXB-006 | Soft-delete de exercício com referências históricas em `session_exercise` → 403 para qualquer role (preservação de integridade) | INV-EXB-017 |
| PERM-EXB-007 | ACL só existe para exercícios ORG RESTRICTED; tentar criar ACL em SYSTEM ou ORG_WIDE → 422 independente do role | INV-EXB-010 |
| PERM-EXB-008 | Adição de usuário à ACL que não pertença à mesma organização → 422 (isolamento multi-tenant) | INV-EXB-011 |
| PERM-EXB-009 | `admin` e `coordinator` têm visibilidade global sobre exercícios da organização; `coach` e `athlete` têm visibilidade filtrada por ACL/scope | ADR-008 |
| PERM-EXB-010 | Toda ação de write em exercício gera evento de auditoria consumido pelo módulo `audit` (DR-EXB-003 + MODULE_SCOPE_EXERCISES) | MODULE_SCOPE_EXERCISES.md |
