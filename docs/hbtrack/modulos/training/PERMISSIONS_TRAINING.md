---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
domain_rules_ref: "./DOMAIN_RULES_TRAINING.md"
invariants_ref: "./INVARIANTS_TRAINING.md"
updated_at: "2026-03-31"
---

# PERMISSIONS_TRAINING.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autorização (TRAIN-DEC-025, DR-TRAIN-043).
> Este artefato **documenta** como `training` aplica a policy — não a redefine.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `listTrainingSessions` | ✅ | ✅ | ✅ | ✅ (próprias) | ❌ | athlete vê somente sessões às quais pertence |
| `createTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | DR-TRAIN-001 |
| `getTrainingSessionById` | ✅ | ✅ | ✅ | ✅ (própria) | ❌ | BOLA: athlete só acessa sessão em que está incluído |
| `updateTrainingSession` | ✅ | ✅ | ✅ (autor) | ❌ | ❌ | Janela temporal por papel — INV-TRAIN-004 |
| `deleteTrainingSession` | ✅ | ✅ | ❌ | ❌ | ❌ | Apenas admin/coordinator podem excluir |
| `publishTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | Requer conteúdo mínimo (DR-TRAIN-014) |
| `unpublishTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | PUBLISHED → SCHEDULED; INV-TRAIN-017 |
| `startTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | SCHEDULED/PUBLISHED → IN_PROGRESS; INV-TRAIN-017 |
| `completeTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | IN_PROGRESS → COMPLETED; INV-TRAIN-017 |
| `cancelTrainingSession` | ✅ | ✅ | ✅ | ❌ | ❌ | Qualquer estado pré-terminal |
| `archiveTrainingSession` | ✅ | ✅ | ❌ | ❌ | ❌ | COMPLETED → ARCHIVED; automático 60d ou manual admin/coordinator |
| `listSessionBlocks` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | — |
| `addSessionBlock` | ✅ | ✅ | ✅ | ❌ | ❌ | Sessão não pode estar em estado terminal |
| `getSessionBlock` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | — |
| `updateSessionBlock` | ✅ | ✅ | ✅ | ❌ | ❌ | Sessão não pode estar em estado terminal |
| `deleteSessionBlock` | ✅ | ✅ | ✅ | ❌ | ❌ | Sessão não pode estar em estado terminal |
| `reorderSessionBlocks` | ✅ | ✅ | ✅ | ❌ | ❌ | Sessão não pode estar em estado terminal |
| `listSessionAttendance` | ✅ | ✅ | ✅ | ✅ (própria) | ❌ | athlete vê somente própria presença |
| `recordSessionAttendance` | ✅ | ✅ | ✅ | ❌ | ❌ | — |
| `submitWellnessPre` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | athlete envia wellness de si mesmo; bloqueado se NOW ≥ session_at - 2h (INV-TRAIN-002) |
| `getWellnessPre` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | BOLA por atleta; staff acessa todos |
| `updateWellnessPre` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | Janela temporal INV-TRAIN-002 |
| `submitWellnessPost` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | Requer sessão IN_PROGRESS ou COMPLETED; INV-TRAIN-003 |
| `getWellnessPost` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | BOLA por atleta; staff acessa todos |
| `updateWellnessPost` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | Janela temporal INV-TRAIN-003 |
| `listExecutionRecords` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | — |
| `createExecutionRecord` | ✅ | ✅ | ✅ | ❌ | ❌ | Requer sessão IN_PROGRESS |
| `getExecutionRecord` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | — |
| `listFeedbackThreads` | ✅ | ✅ | ✅ | ✅ (própria) | ❌ | BOLA: athlete vê threads que lhe dizem respeito |
| `createFeedbackThread` | ✅ | ✅ | ✅ | ✅ (sobre si) | ❌ | Requer contexto operacional vinculado (DR-TRAIN-019) |
| `listSessionObjectives` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | — |
| `createSessionObjective` | ✅ | ✅ | ✅ | ❌ | ❌ | Requer origin e ObjectiveType válidos |
| `listAttentionQueueItems` | ✅ | ✅ | ✅ | ❌ | ❌ | Fila técnica — não exposta a athletes |
| `resolveAttentionQueueItem` | ✅ | ✅ | ✅ | ❌ | ❌ | Marca item como resolvido após ação corretiva |
| `dismissAttentionQueueItem` | ✅ | ✅ | ✅ | ❌ | ❌ | Descarta item sem ação (ex.: falso positivo) |
| `escalateAttentionQueueItem` | ✅ | ✅ | ✅ | ❌ | ❌ | Escala item para coordinator/medical; gera notificação |
| `listRecommendations` | ✅ | ✅ | ✅ | ✅ (própria sessão) | ❌ | Recomendações DSS para a sessão |
| `acceptRecommendation` | ✅ | ✅ | ✅ | ❌ | ❌ | Coach aceita recomendação DSS; aplica ajuste |
| `dismissRecommendation` | ✅ | ✅ | ✅ | ❌ | ❌ | Coach descarta recomendação DSS com justificativa |
| `submitIneligibilityDeclaration` | ✅ | ✅ | ✅ | ✅ (própria) | ❌ | Declara atleta inelegível para sessão (restrição médica ou auto-reporte) |
| `getIneligibilityStatus` | ✅ | ✅ | ✅ | ✅ (próprio) | ❌ | Consulta status de inelegibilidade do atleta na sessão |
| `closeFeedbackThread` | ✅ | ✅ | ✅ | ❌ | ❌ | Encerra thread de feedback — somente staff (DR-TRAIN-019) |
| `getLoadChart` | ✅ | ✅ | ✅ | ✅ (próprio time) | ❌ | Dados agregados de carga e prontidão; athlete vê apenas dados de si no time |
| `listChatMessages` | ✅ | ✅ | ✅ | ✅ (própria conversa) | ❌ | BOLA: athlete acessa apenas conversas em que é participante |
| `submitTrainingSuggestion` | ✅ | ✅ | ❌ | ✅ | ❌ | Athlete envia sugestão ao coach; coach não envia sugestão a si mesmo |
| `listMesocycles` | ✅ | ✅ | ✅ | ✅ (leitura) | ❌ | — |
| `createMesocycle` | ✅ | ✅ | ✅ | ❌ | ❌ | — |
| `getMesocycleById` | ✅ | ✅ | ✅ | ✅ (leitura) | ❌ | — |
| `updateMesocycle` | ✅ | ✅ | ✅ | ❌ | ❌ | — |
| `listMicrocycles` | ✅ | ✅ | ✅ | ✅ (leitura) | ❌ | — |
| `createMicrocycle` | ✅ | ✅ | ✅ | ❌ | ❌ | — |
| `getMicrocycleById` | ✅ | ✅ | ✅ | ✅ (leitura) | ❌ | — |
| `updateMicrocycle` | ✅ | ✅ | ✅ | ❌ | ❌ | — |

---

## Regras de contexto cross-operação

| ID | Regra | Ref |
|---|---|---|
| PERM-TRAIN-001 | Roles são atribuídos em `identity_access`; `training` não altera atribuição de roles | TRAIN-DEC-025, DR-TRAIN-043 |
| PERM-TRAIN-002 | `athlete` nunca acessa dados de wellness de outro atleta | DR-TRAIN-034, DR-TRAIN-035; BOLA |
| PERM-TRAIN-003 | Staff acessa wellness de atletas em contexto de time; deve registrar `data_access_log` (LGPD) | DR-TRAIN-034 |
| PERM-TRAIN-004 | Janela de edição de sessão: `coach` (autor) até 10min antes de `session_at`; `coordinator`/`admin` até 24h após `ended_at` | INV-TRAIN-004 |
| PERM-TRAIN-005 | Sessão > 60 dias é somente leitura para todos os roles | INV-TRAIN-005 |
| PERM-TRAIN-006 | Override de restrição médica exige role com `OVERRIDE_RESTRICTION` permission — role padrão não pode fazer override sem permissão explícita auditada | INV-TRAIN-092, DR-TRAIN-025 |
| PERM-TRAIN-007 | ACL de exercício ORG: apenas o treinador criador pode alterar `visibility_mode` e gerenciar ACL | INV-TRAIN-EXB-ACL-004 |
| PERM-TRAIN-008 | Coach com exercício ORG `restricted` sem ACL → 403 ao tentar usar em sessão | INV-TRAIN-EXB-ACL-007, INV-TRAIN-065 |
| PERM-TRAIN-009 | `admin` e `coordinator` são globais no contexto do time; `coach` e `athlete` precisam de atribuição explícita por time+temporada | ADR-008 |
