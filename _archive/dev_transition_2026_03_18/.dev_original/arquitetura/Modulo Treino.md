# Módulo Training — Especificação Pós-Implementação das Decisões Arquiteturais

**Status:** Previsão pós-implementação de `ARCH-DEC-TRAIN.md`
**Data:** 2026-03-15
**Autor:** Principal Software Architect — HB Track
**Fontes normativas:**
- `.dev/arquitetura/ARCH-DEC-TRAIN.md` (TRAIN-DEC-001 a TRAIN-DEC-046)
- `.dev/MODULE_DECISION_IR.json` (promovido)
- `docs/hbtrack/modulos/training/CONTRACT_TRAINING.md` v1.1.0
- `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md`
- `contracts/openapi/paths/training.yaml`
- `contracts/schemas/training/training_session.schema.json`
- `contracts/workflows/training/`

> **Modo estrito:** Este documento não inventa contratos, endpoints, enums, eventos, transições de estado, permissões, comportamento de UI, integrações externas nem regras de handebol sem base normativa explícita nos artefatos listados acima.

---

## Sumário

1. [Decisão Arquitetural Mãe](#1-decisão-arquitetural-mãe)
2. [O que existe no módulo training](#2-o-que-existe-no-módulo-training)
3. [O que NÃO existe no módulo training](#3-o-que-não-existe-no-módulo-training)
4. [Serviços e Responsabilidade Normativa](#4-serviços-e-responsabilidade-normativa)
5. [Fluxos dos usuários no frontend](#5-fluxos-dos-usuários-no-frontend)

---

## 1. Decisão Arquitetural Mãe

> **O módulo `training` não é uma agenda de sessões. É um motor de decisão operacional do treinador que transforma contexto competitivo e dados do elenco em intervenção treinável, coordenada e executável.**
>
> A unidade de valor é o ciclo completo:
> `Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment`
>
> Toda decisão de contrato, schema, boundary e implementação deve ser avaliada contra essa definição. Se uma decisão reduz o módulo a CRUD de sessão, ela está errada.

*Fonte: TRAIN-DEC-001, TRAIN-DEC-002 e Decisão Arquitetural Mãe em ARCH-DEC-TRAIN.md*

---

## 2. O que existe no módulo training

### 2.1 Identidade e Unidade Soberana

| Atributo | Valor |
|---|---|
| **Nome do módulo** | `training` |
| **Unidade soberana** | `training_intervention_cycle` |
| **Backbone operacional** | `need` → `objective` → `prescription` → `session` → `execution` → `response` → `review` → `adjustment` |
| **Benchmark principal** | XPS Network / Sideline Sports |
| **Benchmark ecossistema** | Smartabase, Teamworks AMS, Kitman Labs, Catapult |
| **Benchmark prescrição** | BridgeAthletic, TeamBuildr |
| **Benchmark operação** | Sportlyzer |
| **Benchmark semântico handebol** | Handball.ai |

*Fonte: MODULE_DECISION_IR.json → module_identity; TRAIN-DEC-001*

### 2.2 Entidades Soberanas

Todas as entidades abaixo são de propriedade exclusiva do módulo `training`. Identificadores públicos seguem formato `uuid_v4`.

| Entidade | Descrição operacional | Fase | Tipo de persistência |
|---|---|---|---|
| `training_intervention_cycle` | Unidade soberana do módulo. Envolve o ciclo causal completo desde a necessidade detectada até o ajuste pós-revisão. | 1 | CRUD |
| `training_session` | Artefato interno do ciclo. Sessão de treino de equipe ou individual, com campo `individualization_mode`. | 1 | CRUD (estado) + append-only (fatos) |
| `session_block` | Bloco estrutural da sessão com exercícios, tarefas ou prescrições. Suporta `block_athlete_variant`. | 1 | CRUD |
| `session_objective` | Objetivo técnico da sessão ou do ciclo. Exige origem rastreável obrigatória. | 1 | CRUD |
| `prescription_line` | Linha individual de prescrição dentro de um bloco. | 1 | CRUD |
| `execution_record` | Registro de execução factual. Deve apontar para `training_session`, `session_block` ou `prescription_line`. | 1 | Append-only |
| `session_adjustment` | Ajuste ao vivo durante a sessão. Exige `reason_code` estruturado. | 1 | Append-only |
| `need_detected` | Necessidade de treino identificada com origem rastreável. | 1 | CRUD |
| `feedback_thread` | Thread de feedback técnico contextual. Jamais solta — sempre vinculada. | 1 | CRUD |
| `coach_note` | Observação qualitativa do treinador vinculada a sessão ou atleta. | 1 | Append-only |
| `attention_queue_item` | Item da fila de atenção priorizada. Exige `severity_level` + `reason_code` + `target_entity_ref`. | 1 | CRUD |
| `decision_rationale` | Justificativa técnica documentada de decisão (aceite/descarte de recomendação, ajuste de ciclo, override). | 1 | Append-only |
| `training_recommendation` | Objeto intermediário advisory entre módulos externos e o treinador. Soberano do `training`; exige revisão explícita do coach. | 1 | CRUD |
| `review_outcome` | Evidência formal de fechamento de revisão do ciclo. Obrigatório para encerrar ciclo. | 1 | CRUD |
| `restriction_override` | Exceção formal e auditada ao bloqueio de restrição médica. Autorizada apenas por `coach_head`. | 1 | CRUD |
| `attendance_record` | Registro oficial de presença de atleta na sessão. Fato histórico após consolidação. | 1 | Append-only |
| `athlete_feedback` | Resposta estruturada do atleta à thread de feedback. `response_content` obrigatório. | 1 | CRUD |
| `continuity_snapshot` | Estado operacional capturado em ponto no tempo para continuidade de staff. Suporta `staff_handoff`. | 3 | CRUD |

*Fonte: MODULE_DECISION_IR.json → entities; TRAIN-DEC-007, TRAIN-DEC-010, TRAIN-DEC-011, TRAIN-DEC-019, TRAIN-DEC-021, TRAIN-DEC-044*

### 2.3 Entidades Referenciadas (não-soberanas)

| Entidade | Módulo soberano | O que `training` consome | Modo de acesso |
|---|---|---|---|
| `readiness_snapshot_ref` | `wellness` | Resultado do check-in contextual pré-sessão | Read-only; `training` orquestra o momento operacional e consome apenas a referência |
| `derived_signal` | `analytics` | `readiness_score`, `dropout_risk_signal`, `engagement_signal` com proveniência completa | Read-only; Fase 2: via trigger → analytics recalcula → `training` consome atualizado |

*Fonte: TRAIN-DEC-024, TRAIN-DEC-046, OD-TRAIN-005 (resolvido)*

### 2.4 Máquinas de Estado

#### `training_session` — LIFECYCLE-TRAINING-SESSION

```
DRAFT ──→ SCHEDULED ──→ PUBLISHED ──→ IN_PROGRESS ──→ COMPLETED ──→ ARCHIVED
  │              │             │             │
  └──────────────┴─────────────┴──→ CANCELLED ←──┘
```

| De | Para | Trigger | Guards |
|---|---|---|---|
| `DRAFT` | `SCHEDULED` | `coach.schedule_action` | `scheduled_start_at` presente |
| `DRAFT` | `PUBLISHED` | `coach.publish_action` | INV-TRAIN-005: team_scope, session_objective, data/hora, bloco mínimo, coach_assignment |
| `SCHEDULED` | `PUBLISHED` | `coach.publish_action` | INV-TRAIN-005 fields all present |
| `PUBLISHED` | `IN_PROGRESS` | primeiro `execution_record` ou `coach.start_action` | — |
| `IN_PROGRESS` | `COMPLETED` | `coach.complete_action` | Evidência de execução presente (INV-TRAIN-009) |
| `DRAFT`/`SCHEDULED`/`PUBLISHED`/`IN_PROGRESS` | `CANCELLED` | `coach.cancel_action` | Cancelamento lógico apenas; sem hard delete (INV-TRAIN-019) |
| `COMPLETED` | `ARCHIVED` | `system.archival_policy` | — |

**Transições proibidas:** `DRAFT → COMPLETED`, `DRAFT → IN_PROGRESS`, `SCHEDULED → IN_PROGRESS` (sem publicação), `COMPLETED → qualquer estado editável`, `ARCHIVED → qualquer estado`.

*Fonte: TRAIN-DEC-026, TRAIN-DEC-013*

#### `training_intervention_cycle` — LIFECYCLE-INTERVENTION-CYCLE

```
OPEN → IN_PROGRESS → REVIEW → ADJUSTED → IN_PROGRESS (retomada)
                           → COMPLETED → ARCHIVED
```

| De | Para | Trigger |
|---|---|---|
| `OPEN` | `IN_PROGRESS` | Primeira sessão publicada |
| `IN_PROGRESS` | `REVIEW` | `coach.initiate_review` |
| `REVIEW` | `ADJUSTED` | `review_outcome` registrado com ajuste |
| `ADJUSTED` | `IN_PROGRESS` | Retomada do ciclo ajustado |
| `REVIEW` | `COMPLETED` | `review_outcome` registrado com encerramento |
| `COMPLETED` | `ARCHIVED` | Política de arquivamento do sistema |

#### `need_detected`

```
OPEN → LINKED_TO_OBJECTIVE → (DISMISSED)
OPEN → DISMISSED
```

#### `feedback_thread`

```
OPEN → CLOSED
```
Guard: `conversation_outcome` presente (INV-TRAIN-028). **`CLOSED → OPEN` proibido.**

#### `training_recommendation`

```
PENDING_COACH_REVIEW → ACCEPTED / DISMISSED / EXPIRED
```
Guard para `ACCEPTED`: `decision_rationale` obrigatório.

#### `restriction_override`

```
AUTHORIZED → EXPIRED (sistema: expires_at atingido)
AUTHORIZED → REVOKED (admin: revogação auditada)
```

*Fonte: MODULE_DECISION_IR.json → state_models*

### 2.5 Capacidades por Fase

#### Fase 1 — Núcleo operacional obrigatório (MVP)

| Capacidade | Descrição |
|---|---|
| Detecção de Necessidade | Registrar `need_detected` com origem rastreável (analytics, partida, foco competitivo, observação manual) |
| Definição de Objetivo Técnico | Transformar necessidade em `session_objective` com critérios de sucesso e referência à `need_detected` |
| Planejamento de Ciclo e Periodização | Estruturar `training_intervention_cycle` no contexto de temporada, microciclo e fase competitiva |
| Criação e Publicação de Sessão | Criar DRAFT, montar blocos, aplicar guards de validação e publicar |
| Prescrição de Exercícios e Tarefas | Estruturar `session_block` com `prescription_line` e `block_athlete_variant` |
| Gestão de Readiness e Restrições com Override Auditado | Consumir `readiness_snapshot_ref` de Wellness e `restriction_profile` de Medical; emitir `restriction_override` quando necessário |
| Execução e Adesão | Registrar `execution_record`, `session_adjustment`, `attendance_record` |
| Feedback Contextual | Produzir `feedback_thread` vinculada a sessão/bloco/objetivo/atleta; encerrar com `conversation_outcome` |
| Revisão e Ajuste do Ciclo | Registrar `review_outcome` com decisão; gerar `decision_rationale` |
| Revisão de Recomendação sob Autoridade do Treinador | Receber `training_recommendation`, registrar aceite ou descarte explícito |
| Override de Restrição sob Auditoria | Autorizar `restriction_override` com nível de autorização e trilha via `audit` |
| Fila de Atenção (parcial) | Criar e resolver `attention_queue_item` com `severity_level` + `reason_code` + `target_entity_ref` |

#### Fase 2 — Precisão e contexto expandido

| Capacidade | Descrição |
|---|---|
| Vídeo e Playbook Contextual | `video_clip`, `diagram`, `playbook_pattern`, `coaching_cue` vinculáveis a objetivo/bloco/exercício/erro/feedback |
| Variantes por atleta expandidas | `block_athlete_variant` com cobertura completa por atleta no modo `COLLECTIVE_WITH_VARIANTS` |
| Fila de atenção completa | Todos os triggers automatizados de `attention_queue_item` |
| Guards de return-to-play avançados | Lógica de progressão de retorno esportivo integrada à prescrição |
| `planned vs actual` avançado | Granularidade a nível de bloco e drill por atleta |
| `derived_signal` com trigger | `training` emite `trigger_event` → `analytics` recalcula → `training` consome sinal atualizado |

#### Fase 3 — Inteligência e continuidade

| Capacidade | Descrição |
|---|---|
| Feedback conversacional estruturado | `feedback_thread` multi-turno com `athlete_reflection`, `action_commitment`, `followup_check`, `conversation_outcome` |
| Risco de abandono | Consumo de `dropout_risk_signal` (soberano do analytics) como referência consultiva |
| Recomendações automáticas assistidas | Sugestão de sessão/microciclo por IA com revisão obrigatória do coach |
| Continuidade interstaff avançada | `continuity_snapshot`, `staff_handoff`, `decision_rationale` histórico para transições de staff |

*Fonte: TRAIN-DEC-028, MODULE_DECISION_IR.json → module_identity.phase_scope*

### 2.6 Casos de Uso da API

| ID | Goal | Atores | Fase |
|---|---|---|---|
| UC-TRAIN-001 | Criar ciclo de intervenção de treino | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-002 | Criar sessão de treino (DRAFT) | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-003 | Publicar sessão de treino | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-004 | Iniciar execução de sessão | `coach_head`, `coach_assistant`, sistema | 1 |
| UC-TRAIN-005 | Registrar execução de bloco/prescrição | `coach_head`, `coach_assistant`, `athlete` (limitado) | 1 |
| UC-TRAIN-006 | Registrar ajuste ao vivo | `coach_head`, `coach_assistant`, `physical_trainer` | 1 |
| UC-TRAIN-007 | Completar sessão de treino | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-008 | Cancelar sessão | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-009 | Criar feedback contextual (thread) | `coach_head`, `coach_assistant`, `physical_trainer`, `physiotherapist` | 1 |
| UC-TRAIN-010 | Fechar thread de feedback com outcome | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-011 | Criar/detectar necessidade de treino | `coach_head`, `coach_assistant`, sistema (com evidência) | 1 |
| UC-TRAIN-012 | Listar sessões de treino (filtrado por ciclo, equipe, status, data) | `coach_head`, `coach_assistant`, `analyst` (read-only) | 1 |
| UC-TRAIN-013 | Consultar detalhe de sessão | `coach_head`, `coach_assistant`, `athlete` (sessões próprias), `analyst` | 1 |
| UC-TRAIN-014 | Consultar snapshot de prontidão do atleta antes da sessão (proxy Wellness) | `coach_head`, `coach_assistant`, `athlete` (via redirect wellness) | 1 |
| UC-TRAIN-015 | Consultar fila de atenção do treinador | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-016 | Revisar (aceitar/descartar) recomendação de treino | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-017 | Registrar resultado de revisão do ciclo | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-018 | Criar override de restrição (exceção auditada) | `coach_head` (exclusivo) | 1 |
| UC-TRAIN-019 | Resolver item da fila de atenção | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-020 | Registrar assiduidade da sessão | `coach_head`, `coach_assistant` | 1 |
| UC-TRAIN-021 | Registrar resposta do atleta ao feedback | `athlete` | 1 |

*Fonte: MODULE_DECISION_IR.json → api_use_cases*

### 2.7 Eventos Emitidos e Consumidos

#### Emitidos por `training`

| ID | Nome do evento | Trigger |
|---|---|---|
| EVT-TRAIN-001 | `training_intervention_cycle_created` | POST /training-intervention-cycles |
| EVT-TRAIN-002 | `training_session_created` | POST /training-sessions |
| EVT-TRAIN-003 | `training_session_published` | POST /training-sessions/{id}/publish |
| EVT-TRAIN-004 | `training_session_status_changed` | Qualquer transição de status |
| EVT-TRAIN-005 | `training_session_completed` | POST /training-sessions/{id}/complete |
| EVT-TRAIN-006 | `training_session_cancelled` | POST /training-sessions/{id}/cancel |
| EVT-TRAIN-007 | `execution_recorded` | POST /training-sessions/{id}/execution-records |
| EVT-TRAIN-008 | `session_adjusted` | POST /training-sessions/{id}/adjustments |
| EVT-TRAIN-009 | `feedback_posted` | POST /feedback-threads |
| EVT-TRAIN-010 | `conversation_outcome_recorded` | PATCH /feedback-threads/{id}/close |
| EVT-TRAIN-011 | `need_detected_created` | POST /needs-detected |
| EVT-TRAIN-012 | `need_linked_to_objective` | `need_detected.status` → `LINKED_TO_OBJECTIVE` |
| EVT-TRAIN-013 | `restriction_guard_triggered` | Verificação de elegibilidade falha para atleta |
| EVT-TRAIN-014 | `override_authorized` | `coach_head` autoriza override de restrição |
| EVT-TRAIN-015 | `attention_queue_updated` | Novo item criado ou resolvido |
| EVT-TRAIN-016 | `notification_intent_emitted` | Eventos significativos: publish, cancel, complete, feedback |
| EVT-TRAIN-017 | `audit_event_emitted` | Todas as decisões: publish, adjust, cancel, complete, override, review |
| EVT-TRAIN-018 | `staff_handoff_recorded` | Mudança de `responsible_staff_ref` em ciclo ativo |
| EVT-TRAIN-019 | `checkin_submitted` | POST /training-sessions/{id}/checkin |
| EVT-TRAIN-020 | `planned_vs_actual_recorded` | `training_session` completada com `execution_records` |
| EVT-TRAIN-021 | `training_recommendation_created` | `training_recommendation` recebida de módulo externo |
| EVT-TRAIN-022 | `training_recommendation_accepted` | PATCH /training-recommendations/{id}/review (status=ACCEPTED) |
| EVT-TRAIN-023 | `training_recommendation_dismissed` | PATCH /training-recommendations/{id}/review (status=DISMISSED) |
| EVT-TRAIN-024 | `review_outcome_recorded` | POST /training-intervention-cycles/{id}/review-outcomes |
| EVT-TRAIN-025 | `restriction_override_created` | POST /restriction-overrides |
| EVT-TRAIN-026 | `restriction_override_expired` | Sistema: `expires_at` atingido |

#### Consumidos por `training`

| ID | Módulo de origem | Nome do evento | Uso em `training` |
|---|---|---|---|
| EVT-EXT-001 | `wellness` | `wellness_checkin_submitted` | Atualiza contexto de prontidão; dispara `attention_queue_item` se necessário |
| EVT-EXT-002 | `medical` | `medical_restriction_changed` | Atualiza `restriction_profile`; pode gerar `attention_queue_item` ou bloquear prescrição |
| EVT-EXT-003 | `analytics` | `analytics_recommendation_generated` | Cria `training_recommendation` para revisão do coach |
| EVT-EXT-004 | `scout` | `scout_signal_generated` | Gera `need_detected` ou alimenta `training_recommendation` |
| EVT-EXT-005 | `matches` | `match_completed` | Gera `need_detected` ou alimenta `training_recommendation` |

*Fonte: MODULE_DECISION_IR.json → events; TRAIN-DEC-022*

### 2.8 Papéis e Permissões

`identity_access` é a fonte soberana de política de autorização. `training` aplica as decisões — não as define. Identidade humana e roster de staff são soberanos do módulo `users/staff_directory`.

| Papel | Capacidades em `training` |
|---|---|
| `coach_head` | CRUD completo de sessão, publicar, cancelar, completar, ajuste ao vivo, `restriction_override` (exclusivo), fechar `feedback_thread`, criar/revisar ciclo, aceitar/descartar `training_recommendation`, criar `review_outcome`, revogar override, resolver `attention_queue_item` |
| `coach_assistant` | Criar rascunho de sessão, atualizar rascunho, publicar (escopo atribuído), adicionar blocos/prescrições, criar `feedback_thread`, registrar execução, consultar prontidão, aceitar/descartar recomendação, criar `review_outcome`, resolver `attention_queue_item` |
| `physical_trainer` | Criar blocos de condicionamento, adicionar prescrições de força/condicionamento, registrar execução de condicionamento, consultar prontidão, criar `feedback_thread` (no escopo) |
| `physiotherapist` | Ler `restriction_profile`, ler `return_to_play_guard`, criar `feedback_thread` (no escopo), consultar prontidão |
| `athlete` | Visualizar sessões próprias, submeter check-in (orquestrado por training, executado via Wellness), registrar execução própria, responder `feedback_thread` atribuída, consultar histórico próprio |
| `analyst` | Leitura de todos os dados de treino, emitir sinais de analytics como `training_recommendation` (via módulo `analytics`) |
| `admin` | Arquivar sessões, gerenciar `staff_handoff`, autorizar `audit_correction` |

*Fonte: MODULE_DECISION_IR.json → permissions; TRAIN-DEC-025*

### 2.9 Modelo de Persistência

O módulo `training` adota arquitetura **HYBRID** de persistência (TRAIN-DEC-029).

| Tipo | Entidade / Fato |
|---|---|
| **CRUD** | `training_session` (estado operacional), `session_block`, `session_objective`, `prescription_line` |
| **CRUD** | `training_intervention_cycle`, `need_detected`, `training_recommendation`, `feedback_thread`, `attention_queue_item`, `restriction_override`, `review_outcome` |
| **CRUD** | `session_templates`, `planning_periodization` (artefatos de configuração — TRAIN-DEC-031) |
| **Append-only** | `execution_record`, `session_adjustment`, `coach_note` |
| **Append-only** | `attendance_record` (`presence_registered`) após consolidação |
| **Append-only** | `decision_rationale` (raciocínio técnico histórico) |
| **Snapshot imutável** | `planned_content_snapshot` — capturado na publicação da sessão; nunca sobrescrito |

**`planned vs actual`:** `planned_content_snapshot` é imutável após publicação. `execution_records` acumulam o realizado. Comparação é sempre query derivada — nunca campo armazenado (TRAIN-DEC-045).
- Fase 1: granularidade de sessão (`planned_duration_min` vs `actual_duration_min`; `planned_load_target` vs `actual_load_recorded`).
- Fase 2: granularidade de bloco/drill/atleta.

*Fonte: TRAIN-DEC-029, TRAIN-DEC-030, TRAIN-DEC-031, TRAIN-DEC-045*

### 2.10 Mapa de Boundaries Formais

| Módulo | Relação | `training` consome | `training` emite | Soberania |
|---|---|---|---|---|
| `wellness` | Consome | `readiness_snapshot_ref`, `wellness_state summary`, `readiness_score` | `session_context_ref` (âncora de check-in) | `wellness` soberano sobre `athlete_checkin`; `training` consome referência (TRAIN-DEC-024, OD-TRAIN-005) |
| `medical` | Consome | `restriction_profile`, `return_to_play_guard`, `availability_status` | — | `medical` soberano; `training` read-only (TRAIN-DEC-024) |
| `analytics` | Consome sinais | `training_recommendation`, `analytics_signal` | Eventos de sessão e execução (triggers para recálculo) | `analytics` soberano sobre sinais derivados; `training` soberano sobre decisões (TRAIN-DEC-003, TRAIN-DEC-046) |
| `scout` | Consome sinais | `scout_signal`, foco competitivo | — | `scout` soberano; `training` consome como gatilho (TRAIN-DEC-003) |
| `exercises` | Referencia | Definições de exercícios, `playbook_items`, `media_assets` | — | `exercises` soberano sobre biblioteca; `training` governa uso contextual |
| `teams` | Referencia | Roster de equipe, elegibilidade de atletas, atribuições de staff | — | `teams` soberano; `training` usa para resolução de escopo |
| `seasons` | Referencia | Contexto de temporada, fase competitiva, âncora de periodização | — | `seasons` soberano; `training` referencia para periodização |
| `matches` | Consome evento | `match_completed`, sinais de resultado | — | `matches` soberano; `training` consome como gatilho de `need_detected` |
| `users/staff_directory` | Referencia | Perfil de atleta, diretório de staff, roster | — | `users/staff_directory` soberano sobre identidade humana; `training` reference-only |
| `identity_access` | Aplica política | `permission_policy`, definições de papéis | — | `identity_access` governa; `training` aplica (TRAIN-DEC-025) |
| `notifications` | Emite intents | — | `notification_intent_emitted` | `notifications` soberano sobre entrega; `training` emite apenas intenções (TRAIN-DEC-022) |
| `audit` | Emite eventos | — | `audit_event_emitted` | `audit` soberano como repositório; `training` é emissor apenas (TRAIN-DEC-023) |
| `reports` | Emite dados | — | Eventos de sessão, `execution_record`, `planned_vs_actual` | `reports` agrega; não governa `training` |

---

## 3. O que NÃO existe no módulo training

### 3.1 Inferências Globalmente Proibidas (FI-001 a FI-019)

| # | Inferência proibida | Decisão |
|---|---|---|
| FI-001 | `training` criar ou atualizar registros médicos (`restriction_profile`, `return_to_play_guard`) | TRAIN-DEC-024 |
| FI-002 | `analytics` ou IA criar, atualizar ou deletar `training_session`, `session_block` ou `prescription_line` diretamente | TRAIN-DEC-003 |
| FI-003 | `training` ser dono soberano de `athlete`, `team`, `season` ou `competition` — apenas referência | MODULE_DECISION_IR |
| FI-004 | `training` entregar notificações diretamente — apenas emitir `notification_intent` | TRAIN-DEC-022 |
| FI-005 | `training` manter log de auditoria próprio — apenas emitir eventos estruturados para `audit` | TRAIN-DEC-023 |
| FI-006 | `training` definir regras de permissão — apenas aplicar decisões de `identity_access` | TRAIN-DEC-025 |
| FI-007 | `training_session` com status `COMPLETED` ser mutada diretamente — correções apenas via `audit_correction` versionada | TRAIN-DEC-013 |
| FI-008 | `recommendation` de analytics auto-materializar como sessão sem ação explícita do coach | TRAIN-DEC-003 |
| FI-009 | `derived_signal` substituir ou deletar dados-fonte brutos | TRAIN-DEC-014, TRAIN-DEC-042 |
| FI-010 | `need_detected` criar automaticamente `training_session` sem ação explícita do coach | TRAIN-DEC-002 |
| FI-011 | `feedback_thread` ser encerrada sem `conversation_outcome` | TRAIN-DEC-010 |
| FI-012 | `session_objective` existir sem origem (`need_ref`, `competitive_focus_ref`, `development_goal_ref` ou `manual_coach_rationale`) | TRAIN-DEC-005 |
| FI-013 | `attention_queue_item` ser criada sem `severity_level` + `reason_code` + `target_entity_ref` | TRAIN-DEC-027 |
| FI-014 | Atleta com restrição ativa receber prescrição executável sem `restriction_override` autorizado + `audit_event` | TRAIN-DEC-012 |
| FI-015 | `training` ser dono da verdade de check-in do atleta — soberano do módulo `wellness` | OD-TRAIN-005 |
| FI-016 | `identity_access` ser tratado como dono de identidade humana — soberano é `users/staff_directory` | MODULE_DECISION_IR |
| FI-017 | `training_recommendation` contornar revisão explícita do coach — proibida auto-materialização | TRAIN-DEC-003 |
| FI-018 | Revisão existir sem entidade formal `review_outcome` — revisões implícitas são inválidas | TRAIN-DEC-011 |
| FI-019 | Restrição ser quebrada sem `restriction_override` formal com `authorization_level` + auditoria | TRAIN-DEC-012 |

### 3.2 O que estruturalmente não existe no módulo

| O que não existe | Substituto vigente |
|---|---|
| `training_session` como unidade central do módulo | Unidade soberana é `training_intervention_cycle`; `training_session` é artefato interno do ciclo |
| Sessão sem objetivo operacional explícito | Toda sessão publicada exige pelo menos um `session_objective` válido |
| Objetivo sem origem rastreável | `session_objective` sem origem é dado incompleto; estado máximo é `DRAFT` |
| Automação direta de prescrição por IA | IA produz `training_recommendation`; coach decide e materializa |
| Entrega direta de notificações | `training` emite `notification_intent`; `notifications` entrega |
| Trilha de auditoria interna | `training` emite `audit_event`; `audit` é repositório soberano |
| `training` criando dados clínicos | `medical` soberano; read-only para `training` |
| `athlete_checkin` soberano do `training` | Soberano do módulo `wellness`; `training` consome `readiness_snapshot_ref` |
| Dois tipos-entidade para sessão coletiva vs individual | `training_session` única com `individualization_mode` (TRAIN-DEC-044) |
| Comparação `planned vs actual` como campo armazenado | Query derivada de `planned_content_snapshot` + `execution_records` (TRAIN-DEC-045) |
| `derived_signal` calculado internamente | Soberano do módulo `analytics`; `training` consome com proveniência (TRAIN-DEC-046) |
| Feedback conversacional genérico / chatbot | `feedback_thread` sempre contextual e vinculada; Fase 3 para multi-turno |
| Gestão de roster de atletas ou equipes | Soberano do módulo `teams` |
| Analytics, KPIs, dashboards de performance | Módulo `analytics` |
| Gestão de partidas, resultados ou escalações | Módulo `matches` |
| Cadastro de exercícios no catálogo global | Módulo `exercises` |
| Gestão de lesões ou tratamentos médicos | Módulo `medical` |
| Hard delete de sessões em execução ou encerradas | Cancelamento lógico; imutabilidade após `COMPLETED` |
| Estados `pending_review` e `readonly` na máquina de estados | Substituídos: `COMPLETED` → `ARCHIVED`; revisão via `review_outcome` formal |
| `WellnessPre` e `WellnessPost` como entidades soberanas de `training` | Após OD-TRAIN-005: `wellness` soberano; `training` consome `readiness_snapshot_ref` |

> **Nota sobre divergência com estado pré-decisional:** O CONTRACT_TRAINING.md v1.1.0 registra entidades `WellnessPre` e `WellnessPost` e a máquina de estados `(draft, scheduled, in_progress, pending_review, readonly)` como estado operacional anterior. A OD-TRAIN-005 (resolvida em 2026-03-15) e TRAIN-DEC-026 superscedem esse estado. Após implementação das decisões arquiteturais, a nova máquina de estados de 7 estados e o boundary de Wellness prevalecem.

---

## 4. Serviços e Responsabilidade Normativa

Após as implementações, o módulo `training` organiza-se nos seguintes serviços de domínio internos.

---

### 4.1 Serviço de Ciclo de Intervenção

**Responsabilidade:** Gerenciar ciclo de vida de `training_intervention_cycle` e coordenar o backbone `Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment`.

| Operação | Invariantes | Notas |
|---|---|---|
| Criar ciclo | INV-TRAIN-001, INV-TRAIN-002 | Exige `responsible_staff_ref`; conectado a `team_ref` |
| Associar `session_objective` | INV-TRAIN-002 | Origem obrigatória: `need_ref`, `competitive_focus_ref`, `development_goal_ref` ou `manual_coach_rationale` |
| Transicionar estado do ciclo | LIFECYCLE-INTERVENTION-CYCLE | Transições fechadas; OPEN → IN_PROGRESS exige primeira sessão publicada |
| Registrar `review_outcome` | INV-TRAIN-011, INV-TRAIN-012 | Sem evidência de execução, revisão é inválida |
| Registrar `decision_rationale` | INV-TRAIN-008 | Toda decisão de ajuste exige motivo estruturado |
| Emitir `staff_handoff_recorded` | INV-TRAIN-030 | Ao mudar `responsible_staff_ref` em ciclo ativo |

**Boundary:** Consome `team_ref` e `season_ref` como referência. Não gerencia roster nem temporada.

---

### 4.2 Serviço de Necessidade e Recomendação

**Responsabilidade:** Gerenciar `need_detected` e `training_recommendation`. Garantir que analytics e IA sejam advisory — jamais decisores.

| Operação | Invariantes | Notas |
|---|---|---|
| Criar `need_detected` | INV-TRAIN-001, INV-TRAIN-002 | `source_type` canônico obrigatório |
| Receber `training_recommendation` | FI-008, FI-017 | Status inicial: `PENDING_COACH_REVIEW`; auto-materialização proibida |
| Registrar aceite de recomendação | INV-TRAIN-003 | Exige `decision_rationale` |
| Registrar descarte de recomendação | INV-TRAIN-003 | Exige motivo documentado |
| Expirar recomendação | LIFECYCLE-TRAINING-RECOMMENDATION | Sistema: `expires_at` atingido |

**Boundary:** Consome eventos de `analytics`, `scout`, `matches` como triggers. Analytics e IA nunca criam nem editam sessões diretamente.

---

### 4.3 Serviço de Sessão e Prescrição

**Responsabilidade:** Gerenciar ciclo de vida de `training_session`, `session_block` e `prescription_line`. Aplicar guards de publicação e `individualization_mode`.

| Operação | Invariantes | Notas |
|---|---|---|
| Criar sessão (DRAFT) | INV-TRAIN-004 | `session_type` obrigatório; `standalone = true` exige ausência de `microcycle_id` |
| Publicar sessão | INV-TRAIN-005, TRAIN-DEC-006 | Campos mínimos obrigatórios: `team_scope`/`athlete_scope`, `session_objective`, data/hora, bloco mínimo, `coach_assignment` |
| Definir `individualization_mode` | TRAIN-DEC-044 | `COLLECTIVE_UNIFORM`, `COLLECTIVE_WITH_VARIANTS` (com `block_athlete_variant`), `INDIVIDUAL_ONLY` |
| Editar sessão | INV-TRAIN-004 | Autor: até 10 min antes de `session_at`; Superior: até 24h após `ended_at` |
| Bloquear edição histórica | INV-TRAIN-005 | `session_at` > 60 dias bloqueia toda edição |
| Cancelar sessão | TRAIN-DEC-013, INV-TRAIN-019 | Cancelamento lógico; sem hard delete |
| Completar sessão | INV-TRAIN-009 | Exige evidência de execução |
| Imutabilizar sessão `COMPLETED` | TRAIN-DEC-013, INV-TRAIN-019 | Correções via `audit_correction` versionada |
| Capturar `planned_content_snapshot` | TRAIN-DEC-045 | Ao publicar; imutável após publicação |

**Ingestão de dados externos:** Dados via importação ou feeds externos devem passar por normalização canônica com `source_type`, `source_system`, `source_record_id`, `ingested_at`, `observed_at` (distintos — TRAIN-DEC-037), `confidence_level`, `normalization_version`, `sensitivity_class`, `access_classification` (TRAIN-DEC-036, TRAIN-DEC-038).

---

### 4.4 Serviço de Execução e Adesão

**Responsabilidade:** Registrar execução factual, ajustes ao vivo e presença. Preservar dualidade planejado/realizado. Gerenciar aderência como entidade de primeira classe.

| Operação | Invariantes | Notas |
|---|---|---|
| Registrar `execution_record` | INV-TRAIN-006, TRAIN-DEC-007 | Deve apontar para `training_session`, `session_block` ou `prescription_line`. Improviso: exige `coach_rationale` |
| Registrar ajuste ao vivo | TRAIN-DEC-009, INV-TRAIN-008 | `reason_code` estruturado obrigatório em todo `live_session_adjustment`, `alternate_exercise`, `constraint_override`, `load_recalculation` |
| Consolidar presença | INV-TRAIN-016, TRAIN-DEC-008 | `attendance_record` append-only após consolidação |
| Preservar `planned vs actual` | TRAIN-DEC-008, TRAIN-DEC-045 | `planned_content_snapshot` nunca sobrescrito; comparação é query derivada |
| Registrar aderência | TRAIN-DEC-019 | `adherence_status`, `miss_reason`, `partial_completion`, `reschedule_window`, `consistency_streak` são entidades do domínio |
| Consumir `dropout_risk_signal` | TRAIN-DEC-042, TRAIN-DEC-046 | Sinal derivado — soberano do `analytics`; `training` consome read-only |

**Dados sensíveis:** `readiness_score`, estado emocional e fadiga classificados como `sensitive_health_adjacent` ou `sensitive_psychological`. Acesso exige `need-to-know` operacional e `access_classification: restricted_coaching`. Proibido em endpoints genéricos de listagem (TRAIN-DEC-039, TRAIN-DEC-040).

---

### 4.5 Serviço de Feedback e Conversação

**Responsabilidade:** Gerenciar `feedback_thread`, `athlete_feedback` e `coach_note`. Garantir que feedback produza consequência operacional.

| Operação | Invariantes | Notas |
|---|---|---|
| Criar `feedback_thread` | TRAIN-DEC-010, INV-TRAIN-010 | Deve ser vinculada a sessão, bloco, objetivo, evidência ou atleta. Feedback solto é inválido |
| Registrar resposta do atleta | TRAIN-DEC-015 | `response_content` obrigatório; `wellness_reflection_ref` opcional |
| Fechar thread | TRAIN-DEC-015, INV-TRAIN-028 | `conversation_outcome` obrigatório; `CLOSED → OPEN` proibido |
| Registrar `coach_note` | INV-TRAIN-008, INV-TRAIN-009 | Observação qualitativa histórica; append-only |
| Privacidade de conversas IA | CONTRACT_TRAINING §3.6 | Conteúdo de conversas IA com atleta NÃO pode ser exposto ao treinador; apenas métricas agregadas |

**Fase 1:** Resposta única estruturada e `conversation_outcome` obrigatório. **Fase 3:** Multi-turno com `athlete_reflection`, `action_commitment`, `followup_check`.

---

### 4.6 Serviço de Atenção e Alerta

**Responsabilidade:** Gerenciar `attention_queue_item`. Garantir que a atenção do treinador seja finita e priorizada.

| Operação | Invariantes | Notas |
|---|---|---|
| Criar `attention_queue_item` | TRAIN-DEC-027, INV-TRAIN-027 | Exige obrigatoriamente: `severity_level` + `reason_code` + `target_entity_ref` |
| Resolver item | TRAIN-DEC-027 | Campos obrigatórios: `resolved_by`, `resolution_action`, `resolution_reason` |
| Filtrar fila por severidade | TRAIN-DEC-027 | Fila sempre exibida filtrada; sem fila plana |
| Emitir `notification_intent` | TRAIN-DEC-022 | Alertas críticos geram intent para `notifications` |

---

### 4.7 Serviço de Readiness e Elegibilidade

**Responsabilidade:** Intermediar consumo de prontidão (wellness) e restrições (medical). Gerenciar `restriction_override`.

| Operação | Invariantes | Notas |
|---|---|---|
| Consultar `readiness_snapshot_ref` | TRAIN-DEC-024, OD-TRAIN-005 | Proxy via Wellness (UC-TRAIN-014); `training` não persiste check-in |
| Verificar restrição médica | TRAIN-DEC-012, INV-TRAIN-014 | `restriction_profile` e `return_to_play_guard` de `medical`; read-only |
| Bloquear prescrição por restrição ativa | FI-014, INV-TRAIN-021 | Sem `restriction_override`: atleta bloqueado não recebe prescrição executável |
| Criar `restriction_override` | TRAIN-DEC-012, FI-019 | Exclusivo de `coach_head`; exige `authorization_level` + trilha de auditoria |
| Expirar/revogar override | LIFECYCLE-RESTRICTION-OVERRIDE | Sistema expira; admin revoga com auditoria |
| Inferência IA sobre estado do atleta | TRAIN-DEC-041 | `review_status: pending_human_review` por padrão; não pode ser operacionalizada sem revisão humana |

---

### 4.8 Serviço de Continuidade Interstaff (Fase 3)

**Responsabilidade:** Preservar raciocínio técnico e contexto de intervenção através de mudanças de staff.

| Entidade | Responsabilidade | Fase |
|---|---|---|
| `decision_rationale` | Justificativa técnica preservada (append-only) | 1 |
| `coach_annotation` | Observações qualitativas do treinador | 1 |
| `staff_handoff` | Pacote de contexto para transição de staff | 3 |
| `continuity_snapshot` | Estado operacional em ponto no tempo | 3 |

*Fonte: TRAIN-DEC-021, INV-TRAIN-030*

---

### 4.9 Adaptadores de Boundary

**Responsabilidade:** Normalizar mensagens de módulos externos. Toda ingestão passa por normalização canônica (TRAIN-DEC-036).

| Adaptador | Módulo | Direção | Função |
|---|---|---|---|
| `WellnessAdapter` | `wellness` | Consome | Consome `readiness_snapshot_ref`; orquestra momento de check-in contextual |
| `MedicalAdapter` | `medical` | Consome | Lê `restriction_profile`, `return_to_play_guard`; aciona guards de prescrição |
| `AnalyticsAdapter` | `analytics` | Bidirecional | Consome sinais como `training_recommendation`; Fase 2: emite triggers de recálculo |
| `ScoutAdapter` | `scout` | Consome | Consome `scout_signal` como gatilho de `need_detected` |
| `MatchesAdapter` | `matches` | Consome | Consome `match_completed` como gatilho de `need_detected` |
| `NotificationsAdapter` | `notifications` | Emite | Emite `notification_intent_emitted` — não entrega diretamente |
| `AuditAdapter` | `audit` | Emite | Emite `audit_event_emitted` para todas as decisões auditáveis |
| `ReportsAdapter` | `reports` | Emite | Expõe `reportable_facts` (eventos de sessão, execução, `planned_vs_actual`) |

---

### 4.10 Separação de Camadas (Arquitetura Interna)

O módulo `training` observa separação estrita e não-intercambiável de camadas (TRAIN-DEC-032 a TRAIN-DEC-035):

```
Provedor/Entrada
→ Contrato de Ingestão (normalização canônica)
→ Modelo de Domínio   (invariantes, ciclo de vida, regras — não moldado por UI nem provedores)
→ DTO de API          (contrato de transporte versionável; não expõe internos de BD)
→ ViewModel           (composição e formatação de tela; não colapsa status canônicos)
→ Props de Componente UI (limite mínimo de renderização)
→ UI Renderizada
```

**Proibido:**
- DTO expor estrutura de tabelas de junção, soft-delete ou formato bruto de event store.
- DTO carregar strings de apresentação (`"Amanhã às 08:00"`) — pertencem ao ViewModel.
- ViewModel colapsar distinções canônicas de status (`DRAFT`, `SCHEDULED`, `PUBLISHED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`) em campo genérico `"active"` quando a UI ainda precisa das distinções.

---

## 5. Fluxos dos usuários no frontend

Os fluxos abaixo descrevem como os atores acessam o sistema via frontend após as implementações das decisões arquiteturais. Normalizados pelo `MODULE_DECISION_IR.json → ui_flows`.

---

### UF-TRAIN-001 — Detectar e registrar necessidade

**Ator:** `coach_head`
**Trigger:** Sinal de analytics, resultado de partida ou observação do treinador

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador visualiza sinal ou observação no painel | `attention_queue_item` ou sinal externo | Sinal vem de `analytics`, `scout` ou `matches` como input advisory apenas |
| 2 | Treinador cria `need_detected` com `source_type` e `evidence_ref` | `need_detected` | Origem rastreável obrigatória (FI-012 se omitida) |
| 3 | Necessidade aparece na fila de planejamento com status `OPEN` | `need_detected` | Estado inicial OPEN |

**Resultado:** `need_detected` registrada com origem rastreável, pronta para ser vinculada a um objetivo.

---

### UF-TRAIN-002 — Criar ciclo e definir objetivo

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** `need_detected` com status `OPEN` ou foco competitivo identificado

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador abre painel de planejamento | `training_intervention_cycle` | Visualiza ciclos existentes e necessidades abertas |
| 2 | Treinador cria `training_intervention_cycle` | `training_intervention_cycle` | Status inicial: `OPEN` |
| 3 | Treinador cria `session_objective` vinculado à necessidade | `session_objective`, `need_detected` | `need_detected.status` → `LINKED_TO_OBJECTIVE`; objetivo sem origem é inválido |
| 4 | Ciclo aparece no quadro de planejamento | `training_intervention_cycle` | Status: `OPEN`; aguarda primeira sessão publicada |

**Resultado:** Ciclo criado com objetivo técnico rastreável conectado à necessidade.

---

### UF-TRAIN-003 — Montar e publicar sessão

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** Ciclo `IN_PROGRESS` ou nova sessão necessária

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador cria sessão (DRAFT) com `sessionType`, data/hora e `team_scope` | `training_session` | Status: `DRAFT`; `individualization_mode` definido |
| 2 | Treinador adiciona `session_block` com `prescription_line` | `session_block`, `prescription_line` | `block_athlete_variant` disponível no modo `COLLECTIVE_WITH_VARIANTS` |
| 3 | Sistema verifica campos mínimos para publicação | `training_session` | INV-TRAIN-005: `team_scope`, `session_objective`, data, bloco mínimo, `coach_assignment` |
| 4 | Treinador consulta prontidão e restrições (opcional) | `readiness_snapshot_ref`, `restriction_profile` | Proxy via Wellness e Medical; treinador ajusta prescrição se necessário |
| 5 | Treinador publica sessão | `training_session` | Status: `DRAFT` → `PUBLISHED`; `planned_content_snapshot` capturado e imutável |
| 6 | Atletas e staff notificados | `notification_intent_emitted` → `notifications` | `training` emite intent; `notifications` entrega |

**Resultado:** Sessão publicada com conteúdo mínimo validado, snapshot planejado imutável, notificações emitidas.

---

### UF-TRAIN-004 — Revisar prontidão antes da execução

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** Sessão publicada, aproximando-se de `scheduled_start_at`

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador abre painel de prontidão da sessão | `readiness_snapshot_ref` | Estado de wellness da equipe do módulo `wellness` (read-only) |
| 2 | Treinador visualiza restrições médicas ativas | `restriction_profile`, `return_to_play_guard` | Dados de `medical` (read-only); atletas com bloqueio sinalizados |
| 3 | Treinador verifica fila de atenção | `attention_queue_item` | Items filtrados por severidade |
| 4 | Treinador ajusta sessão ao vivo se necessário | `session_adjustment` | `reason_code` obrigatório (TRAIN-DEC-009) |

**Resultado:** Treinador inicia a sessão com visão completa do estado da equipe e restrições vigentes.

---

### UF-TRAIN-005 — Fluxo de prontidão pré-treino (boundary wellness)

**Ator:** `athlete`
**Trigger:** Sessão publicada e aproximando-se do horário de início

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Atleta abre a sessão no app | `training_session` | Visualiza sessão publicada atribuída |
| 2 | `training` abre contexto e solicita prontidão ao módulo `wellness` | `readiness_snapshot_ref` | `training` orquestra o momento; `wellness` coleta e retorna a referência |
| 3 | Estado normal → fluxo mínimo; flag `at_risk` → perguntas expandidas | `readiness_snapshot_ref` | Princípio TRAIN-DEC-018: fricção adaptativa |
| 4 | Confirmação mostrada ao atleta | — | `training` consome `readiness_snapshot_ref`; `wellness` é soberano |

**Resultado:** `readiness_snapshot_ref` disponível para o treinador. `training` não persiste o check-in.

---

### UF-TRAIN-006 — Executar sessão e registrar ao vivo

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** Sessão `IN_PROGRESS`

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador visualiza plano da sessão (snapshot imutável) | `training_session`, `session_block`, `prescription_line` | `planned_content_snapshot` como referência; não editável |
| 2 | Treinador marca blocos como executados | `execution_record` | Fato append-only; deve apontar para `session_block` ou `prescription_line` |
| 3 | Treinador aplica ajuste ao vivo com `reason_code` se necessário | `session_adjustment` | `live_session_adjustment`, `alternate_exercise`, `constraint_override`, `load_recalculation` — todos exigem `reason_code` |
| 4 | Sistema preserva dualidade planejado/realizado | `planned_content_snapshot` + `execution_records` | `planned` nunca sobrescrito; comparação é query derivada |

**Resultado:** Fatos de execução registrados append-only; histórico causal preservado.

---

### UF-TRAIN-007 — Completar sessão e registrar resposta

**Ator:** `coach_head`, `coach_assistant` + `athlete`
**Trigger:** Execução da sessão encerrada

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador confirma presença de atletas | `attendance_record` | Fato append-only após consolidação (INV-TRAIN-016) |
| 2 | Treinador registra `coach_note` pós-sessão | `coach_note` | Observação histórica; append-only |
| 3 | Atletas registram RPE e `athlete_feedback` | `athlete_feedback` | `response_content` obrigatório |
| 4 | Sistema verifica guards antes de completar | `training_session` | Evidência de execução obrigatória (INV-TRAIN-009) |
| 5 | Treinador completa sessão | `training_session` | Status: `IN_PROGRESS` → `COMPLETED`; `planned_vs_actual_recorded` emitido |
| 6 | Sessão `COMPLETED` torna-se imutável | `training_session` | Correções via `audit_correction` versionada (TRAIN-DEC-013) |

**Resultado:** Sessão encerrada com evidência; resposta do atleta registrada; fatos históricos imutáveis.

---

### UF-TRAIN-008 — Dar feedback contextual ao atleta

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** Sessão completada ou observação de performance específica

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador seleciona atleta e âncora o feedback | `feedback_thread` | Vinculado a sessão, bloco, objetivo ou evento de avaliação (TRAIN-DEC-010) |
| 2 | Atleta recebe notificação | `notification_intent_emitted` → `notifications` | `training` emite intent; entrega via `notifications` |
| 3 | Atleta reflete e responde | `athlete_feedback` | `response_content` obrigatório |
| 4 | Treinador fecha thread com `conversation_outcome` | `feedback_thread` | `conversation_outcome` obrigatório — sem ele, thread não pode ser encerrada (FI-011) |

**Resultado:** Feedback contextual com consequência operacional documentada.

---

### UF-TRAIN-009 — Revisar ciclo e ajustar plano

**Ator:** `coach_head`
**Trigger:** Múltiplas sessões executadas no ciclo

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador abre resumo do ciclo com `planned vs actual` | `training_intervention_cycle`, `planned_content_snapshot`, `execution_records` | Comparação é query derivada (TRAIN-DEC-045); Fase 1: granularidade de sessão |
| 2 | Treinador revisa evidências de execução | `execution_record`, `coach_note`, `session_adjustment` | Sem evidência: revisão é inválida (TRAIN-DEC-011) |
| 3 | Treinador cria `decision_rationale` | `decision_rationale` | Justificativa técnica; append-only |
| 4 | Treinador registra `review_outcome` com decisão | `review_outcome` | Decisão obrigatória: continuar, escalar, modificar ou encerrar ciclo |
| 5 | Ciclo transiciona conforme decisão | `training_intervention_cycle` | `REVIEW → ADJUSTED` ou `REVIEW → COMPLETED` |

**Resultado:** Revisão formal com evidência; `review_outcome` como entidade de fechamento; `decision_rationale` preservado para continuidade de staff.

---

### UF-TRAIN-010 — Gerenciar fila de atenção

**Ator:** `coach_head`, `coach_assistant`
**Trigger:** Acesso diário ou notificação de alerta

| Passo | Entidade tocada | Observação |
|---|---|---|
| 1 | Treinador abre fila de atenção filtrada por severidade | `attention_queue_item` | Items sem os 3 campos obrigatórios nunca chegam à fila (TRAIN-DEC-027) |
| 2 | Treinador revisa contexto do item | `attention_queue_item` | Contexto: atleta, severidade, `reason_code`, entidade alvo |
| 3 | Treinador toma ação | `session_adjustment`, `feedback_thread` ou encaminhamento | Ação registrada na resolução |
| 4 | Treinador marca item como resolvido | `attention_queue_item` | Campos obrigatórios: `resolved_by`, `resolution_action`, `resolution_reason` |

**Resultado:** Fila de atenção gerenciada com resolução rastreável; atenção do treinador gerenciada como recurso finito.

---

## Referência rápida de decisões implementadas

| TRAIN-DEC | Resumo | Impacto principal |
|---|---|---|
| 001 | `training_session` não é unidade central | Unidade soberana = `training_intervention_cycle` |
| 002 | Módulo orientado a decisão | Toda sessão nasce de necessidade/objetivo rastreável |
| 003 | Analytics/IA apenas recomendam | `training_recommendation` exige revisão explícita do coach |
| 004 | Sessão exige objetivo operacional | Sessão sem `session_objective` é inválida |
| 005 | Objetivo exige origem rastreável | `session_objective` sem origem é dado incompleto |
| 006 | Sessão publicada exige conteúdo mínimo | 5 campos mínimos obrigatórios para transitar de DRAFT |
| 007 | `execution_record` exige contexto | Deve apontar para sessão, bloco ou prescription_line |
| 008 | `planned vs actual` obrigatório | `planned_content_snapshot` imutável; comparação é query derivada |
| 009 | Ajuste ao vivo exige motivo estruturado | `reason_code` obrigatório em toda modificação ao vivo |
| 010 | Feedback é contextual, nunca solto | `feedback_thread` obrigatoriamente vinculada |
| 011 | Revisão exige evidência de execução | `review_outcome` sem evidência é inválido |
| 012 | Restrição crítica bloqueia ou exige override auditado | `restriction_override` exclusivo de `coach_head` + auditoria |
| 013 | `COMPLETED` é imutável | Correções via `audit_correction` versionada |
| 014 | Estados derivados não substituem dados-fonte | `readiness_score` etc. são recalculáveis |
| 015 | Conversa técnica gera consequência operacional | `conversation_outcome` obrigatório |
| 016 | Dois loops explícitos | Loop coletivo (`team_training_cycle`) + Loop individual (`individual_development_cycle`) |
| 017 | Vídeo/playbook são objetos operacionais | Vinculáveis a objetivo/bloco/exercício/feedback (Fase 2) |
| 018 | Fricção adaptativa é princípio | Check-in mínimo no estado normal; expandido em risco |
| 019 | Aderência é entidade de primeira classe | `adherence_status`, `miss_reason`, `dropout_risk_signal` como domínio |
| 020 | Edição viva de sessão suportada | `live_session_adjustment`, `alternate_exercise`, `constraint_override`, `load_recalculation` |
| 021 | Continuidade interstaff é responsabilidade do módulo | `decision_rationale`, `staff_handoff`, `continuity_snapshot` |
| 022 | `training` não entrega notificação diretamente | Emite `notification_intent` → `notifications` entrega |
| 023 | Auditoria via módulo `audit` | Emite `audit_event` → `audit` soberano |
| 024 | Dados médicos são somente leitura | `medical` soberano; `training` consome read-only |
| 025 | `identity_access` governa; `training` aplica | Sem hardcoded permissions |
| 026 | Máquina de estados fechada | 7 estados; transições proibidas explícitas |
| 027 | Atenção do treinador é finita | `attention_queue_item` exige `severity` + `reason` + `target_entity` |
| 028 | Fases 1, 2, 3 | Escopo progressivo sem supermodelagem |
| 029–031 | Persistência HYBRID | CRUD para estado operacional; append-only para fatos históricos |
| 032–035 | Separação estrita de camadas | Domínio ≠ DTO ≠ ViewModel ≠ Props UI |
| 036–038 | Camada de ingestão canônica | Dados externos normalizados; `observed_at` ≠ `ingested_at` |
| 039–043 | Governança de dados sensíveis | Wellness/readiness: `sensitive_health_adjacent`; IA: consultiva |
| 044 | Sessão híbrida via `individualization_mode` | Um tipo único de entidade; OPEN-001 resolvido |
| 045 | `planned vs actual` embedded | OPEN-002/OD-TRAIN-003 resolvidos |
| 046 | `analytics` soberano de `derived_signal` | OD-TRAIN-007 resolvido |

---

*Gerado em: 2026-03-15 | Papel: Principal Software Architect — HB Track*
*Fontes: ARCH-DEC-TRAIN.md (TRAIN-DEC-001 a 046), MODULE_DECISION_IR.json, CONTRACT_TRAINING.md v1.1.0, INVARIANTS_TRAINING.md, DOMAIN_RULES_TRAINING.md, contracts/openapi/paths/training.yaml*
