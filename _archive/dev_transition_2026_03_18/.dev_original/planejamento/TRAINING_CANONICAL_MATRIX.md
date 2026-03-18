# MATRIZ CANÔNICA DO MÓDULO TRAINING — HB TRACK

**Versão:** 1.0.0
**Status:** draft
**Módulo:** training
**Eixo soberano:** `need → objective → prescription → session → execution → response → review → adjustment`
**Data:** 2026-03-14
**Fonte primária:** `.dev/TREINOS.md`
**Benchmarks principais:** XPS Network, Smartabase, Teamworks AMS, BridgeAthletic, TeamBuildr, Sportlyzer, Handball.ai

---

## Enums Controlados

### decision_stage
`need | objective | prescription | session | execution | response | review | adjustment | module_identity | boundary | governance`

### decision_type
`business | boundary | lifecycle | authorization | integrity | audit`

### gate_class
`blocking | warning | documentation_only`

### automation_level
`fully_automatable | partially_automatable | manual_review_required`

### materializes_in (valores válidos)
`README | MODULE_SCOPE | DOMAIN_RULES | INVARIANTS | STATE_MODEL | PERMISSIONS | ERRORS | UI_CONTRACT | SCREEN_MAP | OpenAPI | Schema | Workflow | AsyncAPI`

---

## Bloco 1 — Identidade do Módulo

### TRAIN-DEC-001

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-001 |
| **decision_stage** | module_identity |
| **decision_type** | business |
| **decision_name** | Training é ciclo de intervenção, não agenda de sessões |
| **problem_real_world** | Módulo degradar para CRUD de sessão sem propósito, perdendo valor como motor de decisão operacional do treinador |
| **operational_value_unit** | training_intervention_cycle |
| **entity_owner** | training |
| **entities_touched** | training_intervention_cycle, training_session |
| **minimum_required_fields** | n/a — decisão de identidade arquitetural |
| **allowed_origin** | revisão arquitetural formal com aprovação CDD |
| **forbidden_origin** | inferência de agente sem decisão explícita, preferência de implementação |
| **allowed_actor** | arquiteto, líder técnico (por processo formal) |
| **forbidden_actor** | agente autônomo, desenvolvedor sem aprovação de governance |
| **preconditions** | — |
| **postconditions** | toda funcionalidade do módulo ancorável ao eixo soberano |
| **state_impact** | nenhum (decisão de identidade) |
| **events_emitted** | — |
| **invariants** | INV-TRAIN-001, INV-TRAIN-002, INV-TRAIN-003 |
| **boundary_rules** | training é orquestrador da intervenção; não é dono de analytics, medical, identity_access |
| **evidence_required** | MODULE_SCOPE e DOMAIN_RULES documentam eixo soberano |
| **gate_class** | blocking |
| **automation_level** | manual_review_required |
| **materializes_in** | README, MODULE_SCOPE, DOMAIN_RULES |

### TRAIN-DEC-002

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-002 |
| **decision_stage** | module_identity |
| **decision_type** | business |
| **decision_name** | training_intervention_cycle é o eixo soberano do módulo |
| **problem_real_world** | training_session ser modelada como entidade central, perdendo o ciclo completo de intervenção e tornando o módulo incapaz de representar o fluxo real do treinador |
| **operational_value_unit** | training_intervention_cycle |
| **entity_owner** | training |
| **entities_touched** | training_intervention_cycle, training_session, session_block, session_objective, need_detected, execution_record |
| **minimum_required_fields** | training_intervention_cycle: id, team_ref, objective_refs (min 1), status, created_by, created_at |
| **allowed_origin** | coach.action, authorized_staff.action |
| **forbidden_origin** | ai.autonomous_creation, system.autocreation sem coach authority |
| **allowed_actor** | coach_head, coach_assistant (com escopo limitado) |
| **forbidden_actor** | analytics, ai_agent sem validação do coach |
| **preconditions** | — |
| **postconditions** | training_session sempre referenciada por training_intervention_cycle |
| **state_impact** | training_intervention_cycle: OPEN → IN_PROGRESS → REVIEW → COMPLETED → ARCHIVED |
| **events_emitted** | intervention_cycle_created, intervention_cycle_completed |
| **invariants** | INV-TRAIN-001, INV-TRAIN-002 |
| **boundary_rules** | training_session não deve existir como entidade flutuante sem cycle_ref |
| **evidence_required** | Schema de training_session inclui intervention_cycle_ref como campo obrigatório |
| **gate_class** | blocking |
| **automation_level** | manual_review_required |
| **materializes_in** | MODULE_SCOPE, DOMAIN_RULES, Schema |

---

## Bloco 2 — Fluxo Operacional: Need → Objective

### TRAIN-DEC-003

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-003 |
| **decision_stage** | need |
| **decision_type** | business |
| **decision_name** | Necessidade exige origem rastreável |
| **problem_real_world** | Need detectada sem evidência causal gerar intervenções arbitrárias desconectadas do contexto competitivo ou de performance |
| **operational_value_unit** | need_detected |
| **entity_owner** | training |
| **entities_touched** | need_detected, analytics_signal (ref), scout_signal (ref), match_outcome (ref) |
| **minimum_required_fields** | source_type (enum), description, evidence_ref OR manual_coach_rationale, created_at |
| **allowed_origin** | analytics.signal, scout.signal, match.outcome, wellness.alert, medical.flag, coach.manual_observation |
| **forbidden_origin** | ai.autonomous_need_creation sem evidence_ref, system.placeholder |
| **allowed_actor** | coach_head, coach_assistant, system (quando gera signal baseado em dados reais) |
| **forbidden_actor** | ai_agent sem evidence_ref, agente sem validação de dados |
| **preconditions** | evidence_ref aponta para entidade válida no módulo de origem |
| **postconditions** | need_detected.status = OPEN, disponível para vinculação a objetivo |
| **state_impact** | need_detected: → OPEN → LINKED_TO_OBJECTIVE → DISMISSED |
| **events_emitted** | need_detected_created |
| **invariants** | INV-TRAIN-002, INV-TRAIN-031 |
| **boundary_rules** | evidence_ref pertence ao módulo soberano da evidência (analytics, scout, medical — Training apenas referencia) |
| **evidence_required** | need_detected com source_type e (evidence_ref OU manual_coach_rationale) — payload válido |
| **gate_class** | blocking |
| **automation_level** | partially_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-004

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-004 |
| **decision_stage** | objective |
| **decision_type** | business |
| **decision_name** | Objetivo exige necessidade vinculada ou rationale explícito do coach |
| **problem_real_world** | Objetivo de treino nascer de forma arbitrária, sem contexto de necessidade, tornando o ciclo de intervenção inrastreável |
| **operational_value_unit** | session_objective |
| **entity_owner** | training |
| **entities_touched** | session_objective, need_detected, development_goal |
| **minimum_required_fields** | description, success_criteria, ONE OF: need_detected_ref, competitive_focus_ref, development_goal_ref, manual_coach_rationale |
| **allowed_origin** | coach.action referenciando need_detected ou decidindo manualmente com rationale |
| **forbidden_origin** | session_objective sem qualquer vínculo de origem, ai.autonomous sem coach review |
| **allowed_actor** | coach_head, coach_assistant |
| **forbidden_actor** | athlete, system autônomo sem validação do coach |
| **preconditions** | need_detected_ref (se presente) deve estar no status OPEN ou LINKED_TO_OBJECTIVE |
| **postconditions** | need_detected.status → LINKED_TO_OBJECTIVE (se referenciada) |
| **state_impact** | need_detected: OPEN → LINKED_TO_OBJECTIVE |
| **events_emitted** | objective_created, need_linked_to_objective |
| **invariants** | INV-TRAIN-001, INV-TRAIN-002 |
| **boundary_rules** | development_goal pertence ao módulo de athletes/development; Training apenas referencia |
| **evidence_required** | session_objective com campo de origem preenchido (not null) |
| **gate_class** | blocking |
| **automation_level** | partially_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-005

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-005 |
| **decision_stage** | objective |
| **decision_type** | boundary |
| **decision_name** | IA e analytics só recomendam; treinador decide |
| **problem_real_world** | Automação usurpar a autoridade técnica do treinador, criando sessões ou objetivos sem validação humana e produzindo intervenções opacas |
| **operational_value_unit** | recommendation |
| **entity_owner** | analytics (sinal), training (decisão) |
| **entities_touched** | recommendation, need_detected, session_objective, training_session |
| **minimum_required_fields** | recommendation: source_module, evidence_ref, signal_type, status=PENDING_COACH_REVIEW |
| **allowed_origin** | analytics.output → recommendation → coach.explicit_accept → training.action |
| **forbidden_origin** | analytics.direct_session_creation, ai.session_mutation, ai.prescription_override |
| **allowed_actor** | system (para gerar recommendation), coach (para aceitar/rejeitar) |
| **forbidden_actor** | analytics como ator direto de mutação em Training |
| **preconditions** | recommendation tem status PENDING_COACH_REVIEW |
| **postconditions** | recommendation.status → ACCEPTED (com decision_rationale) OU DISMISSED |
| **state_impact** | recommendation: PENDING_COACH_REVIEW → ACCEPTED → materializes_as_need / DISMISSED |
| **events_emitted** | recommendation_generated, recommendation_accepted, recommendation_dismissed |
| **invariants** | INV-TRAIN-003, INV-TRAIN-004, INV-TRAIN-015, INV-TRAIN-038 |
| **boundary_rules** | analytics não pode alterar estado soberano de Training; apenas emite sinal |
| **evidence_required** | log de decision_rationale do coach presente quando recommendation é aceita |
| **gate_class** | blocking |
| **automation_level** | partially_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, PERMISSIONS, OpenAPI, AsyncAPI |

---

## Bloco 3 — Fluxo Operacional: Prescription → Session

### TRAIN-DEC-006

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-006 |
| **decision_stage** | session |
| **decision_type** | business |
| **decision_name** | Sessão exige objetivo operacional |
| **problem_real_world** | Sessão nascer como bloco de calendário vazio, sem propósito, tornando o módulo mero agendador |
| **operational_value_unit** | training_session |
| **entity_owner** | training |
| **entities_touched** | training_session, session_objective |
| **minimum_required_fields** | training_session: session_objective_ids (min 1 válido), intervention_cycle_ref |
| **allowed_origin** | coach.action com session_objective definido |
| **forbidden_origin** | criação de training_session sem session_objective |
| **allowed_actor** | coach_head, coach_assistant |
| **forbidden_actor** | athlete, sistema autônomo |
| **preconditions** | session_objective deve existir com campos mínimos válidos (ver DEC-004) |
| **postconditions** | training_session criada em status DRAFT com objetivo vinculado |
| **state_impact** | training_session: → DRAFT |
| **events_emitted** | training_session_created |
| **invariants** | INV-TRAIN-001 |
| **boundary_rules** | — |
| **evidence_required** | POST /training-sessions retorna 422 quando session_objective ausente |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-007

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-007 |
| **decision_stage** | session |
| **decision_type** | lifecycle |
| **decision_name** | Sessão publicada exige conteúdo mínimo treinável |
| **problem_real_world** | Atletas receberem sessão publicada sem objetivos, escopo, responsável ou blocos definidos |
| **operational_value_unit** | training_session |
| **entity_owner** | training |
| **entities_touched** | training_session, session_objective, session_block, identity_role |
| **minimum_required_fields** | session_objective_ids (min 1), team_scope_ref OR athlete_scope_refs (min 1), responsible_staff_ref, scheduled_start_at, scheduled_end_at, session_blocks (min 1) |
| **allowed_origin** | coach.explicit_publish_action |
| **forbidden_origin** | auto_publish, scheduled_auto_publish sem guard de conteúdo mínimo |
| **allowed_actor** | coach_head, coach_assistant (com permissão de publicação) |
| **forbidden_actor** | athlete, analytics, sistema autônomo |
| **preconditions** | status = DRAFT ou SCHEDULED; todos os campos mínimos presentes |
| **postconditions** | training_session.status = PUBLISHED; planned_content_snapshot gerado (imutável após este ponto) |
| **state_impact** | training_session: DRAFT → PUBLISHED |
| **events_emitted** | training_session_published |
| **invariants** | INV-TRAIN-001, INV-TRAIN-005, INV-TRAIN-018 |
| **boundary_rules** | identity_access valida permissão de publicação; Training aplica guard de conteúdo |
| **evidence_required** | POST /training-sessions/{id}/publish retorna 422 quando qualquer campo mínimo ausente |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, STATE_MODEL, OpenAPI |

### TRAIN-DEC-008

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-008 |
| **decision_stage** | session |
| **decision_type** | lifecycle |
| **decision_name** | Status de sessão tem transições válidas e fechadas |
| **problem_real_world** | Sessão saltar estados arbitrariamente (ex: DRAFT → COMPLETED), perdendo rastreabilidade e integridade operacional |
| **operational_value_unit** | training_session.status |
| **entity_owner** | training |
| **entities_touched** | training_session |
| **minimum_required_fields** | n/a — regra de transição |
| **allowed_origin** | ações autorizadas em cada estado |
| **forbidden_origin** | qualquer mutação direta de status fora das transições válidas |
| **allowed_actor** | coach_head (todas), coach_assistant (limitado), system (start, auto-complete com guards) |
| **forbidden_actor** | athlete, analytics, agente sem autorização |
| **preconditions** | transição a partir de estado válido |
| **postconditions** | novo status consistente com transição aplicada |
| **state_impact** | DRAFT → SCHEDULED\|PUBLISHED → IN_PROGRESS → COMPLETED; saídas: CANCELLED (de qualquer estado ativo), ARCHIVED (de COMPLETED) |
| **events_emitted** | training_session_status_changed |
| **invariants** | INV-TRAIN-017, INV-TRAIN-018, INV-TRAIN-019, INV-TRAIN-020 |
| **boundary_rules** | — |
| **evidence_required** | testes de máquina de estados com transições proibidas retornando 422 |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | STATE_MODEL, INVARIANTS, OpenAPI |

---

## Bloco 4 — Fluxo Operacional: Execution → Response

### TRAIN-DEC-009

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-009 |
| **decision_stage** | execution |
| **decision_type** | business |
| **decision_name** | Execução exige contexto de prescrição |
| **problem_real_world** | Registros de execução existirem soltos, sem referência à sessão ou bloco, tornando análise de planned vs actual impossível |
| **operational_value_unit** | execution_record |
| **entity_owner** | training |
| **entities_touched** | execution_record, training_session, session_block, prescription_line |
| **minimum_required_fields** | training_session_ref (obrigatório), session_block_ref OR prescription_line_ref OR improvised_rationale, executed_by, recorded_at |
| **allowed_origin** | coach.record, athlete.self_record (quando habilitado) |
| **forbidden_origin** | execution_record sem training_session_ref |
| **allowed_actor** | coach_head, coach_assistant, athlete (para próprio registro quando habilitado) |
| **forbidden_actor** | analytics, sistema sem contexto de sessão |
| **preconditions** | training_session_ref aponta para sessão em status PUBLISHED ou IN_PROGRESS |
| **postconditions** | execution_record criado; training_session transita para IN_PROGRESS no primeiro registro |
| **state_impact** | training_session: PUBLISHED → IN_PROGRESS (no primeiro execution_record) |
| **events_emitted** | execution_recorded |
| **invariants** | INV-TRAIN-006 |
| **boundary_rules** | — |
| **evidence_required** | POST /training-sessions/{id}/execution retorna 422 sem training_session_ref e sem contexto |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-010

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-010 |
| **decision_stage** | execution |
| **decision_type** | integrity |
| **decision_name** | Planned vs Actual é obrigatório em toda sessão executada |
| **problem_real_world** | Realizado sobrescrever planejado, destruindo evidência histórica e impossibilitando análise de aderência e efetividade |
| **operational_value_unit** | execution_record + training_session |
| **entity_owner** | training |
| **entities_touched** | training_session, execution_record, session_adjustment |
| **minimum_required_fields** | training_session: planned_content_snapshot (imutável pós-publicação); execution_record: completion_status, actual_load (nullable), improvised_rationale (quando delta) |
| **allowed_origin** | sistema (comparação automática) + coach/athlete (registro de realizado) |
| **forbidden_origin** | sobrescrita de planned_content_snapshot após publicação |
| **allowed_actor** | sistema (gerar comparação), coach (registrar desvio), athlete (registrar resposta) |
| **forbidden_actor** | qualquer agente com permissão de editar planned_content_snapshot após publicação |
| **preconditions** | training_session.status ≥ PUBLISHED |
| **postconditions** | planned_content e executed_content preservados separadamente e imutáveis após COMPLETED |
| **state_impact** | nenhuma transição — campo de integridade |
| **events_emitted** | planned_vs_actual_recorded |
| **invariants** | INV-TRAIN-007 |
| **boundary_rules** | — |
| **evidence_required** | teste de imutabilidade de planned_content_snapshot após publicação |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema |

### TRAIN-DEC-011

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-011 |
| **decision_stage** | execution |
| **decision_type** | business |
| **decision_name** | Ajuste ao vivo exige motivo estruturado |
| **problem_real_world** | Alterações de sessão durante execução sem rastreabilidade, impossibilitando análise de padrões de adaptação e continuidade interstaff |
| **operational_value_unit** | session_adjustment |
| **entity_owner** | training |
| **entities_touched** | session_adjustment, training_session, session_block |
| **minimum_required_fields** | adjustment_type (enum), original_value, new_value, reason_code (enum), reason_text, adjusted_by, adjusted_at |
| **allowed_origin** | coach.live_action, authorized_staff.live_action |
| **forbidden_origin** | auto_adjustment sem motivo, system.override sem autorização |
| **allowed_actor** | coach_head, coach_assistant, physical_trainer (no escopo de condicionamento) |
| **forbidden_actor** | athlete, analytics, sistema autônomo |
| **preconditions** | training_session.status = IN_PROGRESS ou PUBLISHED |
| **postconditions** | session_adjustment registrado; delta preservado no execution_record |
| **state_impact** | nenhuma transição de status — registro de ajuste |
| **events_emitted** | session_adjusted |
| **invariants** | INV-TRAIN-008 |
| **boundary_rules** | — |
| **evidence_required** | POST /training-sessions/{id}/adjustments retorna 422 sem reason_code |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-012

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-012 |
| **decision_stage** | response |
| **decision_type** | integrity |
| **decision_name** | Sessão concluída exige evidência mínima de resposta |
| **problem_real_world** | Sessão fechar como COMPLETED sem qualquer evidência, tornando o histórico inútil para análise futura |
| **operational_value_unit** | training_session (completion guard) |
| **entity_owner** | training |
| **entities_touched** | training_session, execution_record, coach_note, athlete_feedback |
| **minimum_required_fields** | mínimo de 1 de: attendance_record, post_session_note, athlete_rpe, coach_session_note, execution_record |
| **allowed_origin** | coach.complete_action, system.auto_close (com guard de evidência) |
| **forbidden_origin** | close_without_evidence, auto_complete sem verificação |
| **allowed_actor** | coach_head, coach_assistant |
| **forbidden_actor** | athlete (não pode completar sessão), sistema sem guard |
| **preconditions** | training_session.status = IN_PROGRESS; pelo menos 1 evidência de resposta presente |
| **postconditions** | training_session.status = COMPLETED; histórico imutável |
| **state_impact** | training_session: IN_PROGRESS → COMPLETED |
| **events_emitted** | training_session_completed |
| **invariants** | INV-TRAIN-009, INV-TRAIN-020 |
| **boundary_rules** | — |
| **evidence_required** | POST /training-sessions/{id}/complete retorna 422 sem evidência mínima |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, STATE_MODEL, OpenAPI |

---

## Bloco 5 — Fluxo Operacional: Review → Adjustment

### TRAIN-DEC-013

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-013 |
| **decision_stage** | review |
| **decision_type** | business |
| **decision_name** | Feedback é contextual e vinculado a entidade operacional |
| **problem_real_world** | Feedback técnico solto (sem âncora a sessão, objetivo, atleta ou evidência) sem valor operacional e aumentando ruído |
| **operational_value_unit** | feedback_thread |
| **entity_owner** | training |
| **entities_touched** | feedback_thread, training_session, session_block, session_objective, execution_record |
| **minimum_required_fields** | target_athlete_ref, created_by, content, PELO MENOS 1 DE: training_session_ref, session_block_ref, session_objective_ref, evidence_ref |
| **allowed_origin** | coach.action, authorized_staff.action |
| **forbidden_origin** | feedback sem qualquer anchor_ref |
| **allowed_actor** | coach_head, coach_assistant, physical_trainer, physiotherapist (no escopo) |
| **forbidden_actor** | analytics, sistema autônomo |
| **preconditions** | âncora referenciada deve existir e pertencer ao escopo do atleta-alvo |
| **postconditions** | feedback_thread criado com status OPEN, disponível para resposta do atleta |
| **state_impact** | feedback_thread: → OPEN → CLOSED |
| **events_emitted** | feedback_posted |
| **invariants** | INV-TRAIN-010, INV-TRAIN-028 |
| **boundary_rules** | — |
| **evidence_required** | POST /training-sessions/{id}/feedback retorna 422 sem anchor_ref |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-014

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-014 |
| **decision_stage** | review |
| **decision_type** | business |
| **decision_name** | Conversa técnica precisa gerar consequência operacional |
| **problem_real_world** | Troca conversacional decorativa sem produzir reflexão, compromisso, ação ou decisão — tornando o módulo um chat genérico |
| **operational_value_unit** | feedback_thread.conversation_outcome |
| **entity_owner** | training |
| **entities_touched** | feedback_thread |
| **minimum_required_fields** | conversation_outcome: enum(reflection, commitment, pending_action, followup, decision) — obrigatório no fechamento |
| **allowed_origin** | coach.close_thread_action |
| **forbidden_origin** | fechar thread sem conversation_outcome definido |
| **allowed_actor** | coach_head, coach_assistant |
| **forbidden_actor** | sistema autônomo (não pode fechar thread sem coach) |
| **preconditions** | feedback_thread.status = OPEN; athlete respondeu ou prazo de follow-up passou |
| **postconditions** | feedback_thread.status = CLOSED; conversation_outcome preenchido |
| **state_impact** | feedback_thread: OPEN → CLOSED |
| **events_emitted** | conversation_outcome_recorded |
| **invariants** | INV-TRAIN-028 |
| **boundary_rules** | — |
| **evidence_required** | PATCH /feedback-threads/{id}/close retorna 422 sem conversation_outcome |
| **gate_class** | blocking |
| **automation_level** | partially_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-015

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-015 |
| **decision_stage** | review |
| **decision_type** | audit |
| **decision_name** | Revisão de ciclo exige execução ou evidência equivalente |
| **problem_real_world** | Review_outcome existir sem base em dados reais de execução, tornando a decisão de ajuste especulativa |
| **operational_value_unit** | review_outcome (dentro de training_intervention_cycle) |
| **entity_owner** | training |
| **entities_touched** | training_intervention_cycle, execution_record, coach_note |
| **minimum_required_fields** | review: execution_ref OR post_session_report_ref OR equivalent_evidence_ref |
| **allowed_origin** | coach.review_action com evidence_ref |
| **forbidden_origin** | review_outcome sem evidência de execução |
| **allowed_actor** | coach_head, coach_assistant |
| **forbidden_actor** | analytics (pode fornecer sinal mas não decide review) |
| **preconditions** | ao menos 1 execution_record ou post_session_report vinculado ao ciclo |
| **postconditions** | review_outcome documentado com evidence_ref |
| **state_impact** | training_intervention_cycle: IN_PROGRESS → REVIEW → ADJUSTED\|COMPLETED |
| **events_emitted** | cycle_reviewed |
| **invariants** | INV-TRAIN-011 |
| **boundary_rules** | — |
| **evidence_required** | review_outcome com evidence_ref presente e válido |
| **gate_class** | warning |
| **automation_level** | manual_review_required |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema |

### TRAIN-DEC-016

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-016 |
| **decision_stage** | adjustment |
| **decision_type** | audit |
| **decision_name** | Sessão concluída é imutável por edição destrutiva |
| **problem_real_world** | Histórico de treino ser alterado retroativamente de forma destrutiva, perdendo evidência e rastreabilidade |
| **operational_value_unit** | training_session (post-COMPLETED) |
| **entity_owner** | training |
| **entities_touched** | training_session, audit_event |
| **minimum_required_fields** | correção via: audit_correction_record, correction_reason, corrected_by, original_snapshot |
| **allowed_origin** | coach.audit_correction_action com autorização elevada |
| **forbidden_origin** | direct_edit em campos históricos, hard_delete de sessão COMPLETED |
| **allowed_actor** | coach_head (com autorização de nível elevado), admin |
| **forbidden_actor** | qualquer agente sem autorização de correção auditada |
| **preconditions** | training_session.status = COMPLETED |
| **postconditions** | correção gera audit_event com original_snapshot preservado |
| **state_impact** | nenhuma transição — imutabilidade mantida |
| **events_emitted** | historical_record_corrected |
| **invariants** | INV-TRAIN-019, INV-TRAIN-020, INV-TRAIN-029 |
| **boundary_rules** | audit (soberano para correção versionada) |
| **evidence_required** | audit_event gerado com original_snapshot e correction_reason |
| **gate_class** | blocking |
| **automation_level** | manual_review_required |
| **materializes_in** | INVARIANTS, STATE_MODEL, PERMISSIONS, OpenAPI, AsyncAPI |

---

## Bloco 6 — Boundaries

### TRAIN-DEC-017

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-017 |
| **decision_stage** | boundary |
| **decision_type** | boundary |
| **decision_name** | Training consome medical; não soberaniza restrição médica |
| **problem_real_world** | Training criar ou editar restrição médica, causando conflito de soberania e risco clínico |
| **operational_value_unit** | restriction_profile (consumida de medical) |
| **entity_owner** | medical (soberano), training (consumidor read-only) |
| **entities_touched** | restriction_profile (ref), return_to_play_guard (ref) |
| **minimum_required_fields** | consumed_from=medical obrigatório em toda referência de restriction_profile no Training |
| **allowed_origin** | medical.update (escrita soberana); training.read (leitura operacional) |
| **forbidden_origin** | training.create/edit restriction_profile |
| **allowed_actor** | medical staff (escrita), qualquer ator de training (leitura) |
| **forbidden_actor** | coach escrevendo em restriction_profile |
| **preconditions** | — |
| **postconditions** | training consome restriction_profile como read-only operacional |
| **state_impact** | restriction_guard_triggered quando restriction_profile bloqueia prescrição |
| **events_emitted** | restriction_guard_triggered |
| **invariants** | INV-TRAIN-013, INV-TRAIN-014, INV-TRAIN-037 |
| **boundary_rules** | medical é soberano da restrição; Training aplica o guard operacional |
| **evidence_required** | todas as referências a restriction_profile no Training têm flag read-only e consumed_from=medical |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, OpenAPI |

### TRAIN-DEC-018

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-018 |
| **decision_stage** | boundary |
| **decision_type** | boundary |
| **decision_name** | Analytics recomenda; treinador decide no Training |
| **problem_real_world** | Analytics alterar estado soberano do Training sem comando do coach, automatizando decisões técnicas opacas |
| **operational_value_unit** | recommendation (sinal de analytics), training_session (decisão soberana) |
| **entity_owner** | analytics (sinal), training (decisão soberana) |
| **entities_touched** | recommendation, need_detected, training_session |
| **minimum_required_fields** | pipeline obrigatório: analytics.signal → training.need_detected → coach.decision → training.action |
| **allowed_origin** | analytics.output → training.consumption |
| **forbidden_origin** | analytics.direct_mutation_of_training_state |
| **allowed_actor** | analytics (geração de sinal), coach (decisão) |
| **forbidden_actor** | analytics como ator de mutação em Training |
| **preconditions** | recommendation.status = PENDING_COACH_REVIEW |
| **postconditions** | coach tomou decisão explícita sobre recommendation |
| **state_impact** | recommendation: PENDING → ACCEPTED\|DISMISSED |
| **events_emitted** | recommendation_accepted, recommendation_dismissed |
| **invariants** | INV-TRAIN-004, INV-TRAIN-015, INV-TRAIN-038 |
| **boundary_rules** | analytics consome eventos de Training; não escreve nele |
| **evidence_required** | nenhum caminho de API permite analytics alterar training_session diretamente |
| **gate_class** | blocking |
| **automation_level** | partially_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, PERMISSIONS, OpenAPI |

### TRAIN-DEC-019

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-019 |
| **decision_stage** | boundary |
| **decision_type** | boundary |
| **decision_name** | Notifications são intents emitidos; Training não entrega diretamente |
| **problem_real_world** | Training gerenciar infraestrutura de entrega de notificações, criando acoplamento forte e duplicação de responsabilidade |
| **operational_value_unit** | notification_intent |
| **entity_owner** | notifications (entrega soberana), training (intent emitter) |
| **entities_touched** | notification_intent |
| **minimum_required_fields** | intent: type, target_ref, trigger_event, priority, emitted_by=training |
| **allowed_origin** | training.event → notifications.module |
| **forbidden_origin** | training.direct_push, training.sms_direct, training.email_direct |
| **allowed_actor** | system (emitir intent baseado em eventos de Training) |
| **forbidden_actor** | Training como entregador direto de notificação |
| **preconditions** | training_event ocorreu (session_published, session_cancelled, feedback_posted, etc.) |
| **postconditions** | notification_intent emitido para módulo de notifications |
| **state_impact** | — |
| **events_emitted** | notification_intent_emitted |
| **invariants** | INV-TRAIN-039 |
| **boundary_rules** | notifications é módulo transversal soberano de entrega |
| **evidence_required** | nenhuma entrega direta de notificação no Training; apenas emissão de intent event |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, AsyncAPI |

### TRAIN-DEC-020

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-020 |
| **decision_stage** | boundary |
| **decision_type** | audit |
| **decision_name** | Audit é transversal; Training emite eventos estruturados |
| **problem_real_world** | Training manter log de auditoria informal interno, perdendo rastreabilidade centralizada e quebrando continuidade interstaff |
| **operational_value_unit** | audit_event |
| **entity_owner** | audit (soberano), training (emitter) |
| **entities_touched** | audit_event |
| **minimum_required_fields** | event: type, subject_ref, actor_ref, timestamp, payload_snapshot |
| **allowed_origin** | training.action → audit.event_emission |
| **forbidden_origin** | training.internal_audit_log, training.self_audit |
| **allowed_actor** | system (emitir eventos de auditoria baseado em ações de Training) |
| **forbidden_actor** | Training como repositório soberano de auditoria |
| **preconditions** | ação relevante ocorreu em Training (publish, adjust, cancel, complete, override, correction) |
| **postconditions** | audit_event capturado pelo módulo audit |
| **state_impact** | — |
| **events_emitted** | audit_event_emitted |
| **invariants** | INV-TRAIN-029, INV-TRAIN-040 |
| **boundary_rules** | audit é módulo transversal soberano; Training é emitter |
| **evidence_required** | audit_event gerado com todos os campos obrigatórios para cada ação relevante |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, AsyncAPI |

### TRAIN-DEC-021

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-021 |
| **decision_stage** | boundary |
| **decision_type** | authorization |
| **decision_name** | identity_access governa permissão; Training apenas aplica |
| **problem_real_world** | Training definir ou sobrescrever regras de permissão, fragmentando governança de acesso e criando inconsistências |
| **operational_value_unit** | permission_policy |
| **entity_owner** | identity_access (soberano), training (enforcement only) |
| **entities_touched** | identity_role (ref), permission_policy (ref) |
| **minimum_required_fields** | toda verificação de permissão no Training referencia identity_access como fonte |
| **allowed_origin** | identity_access.policy → training.enforcement |
| **forbidden_origin** | training.define_permission, training.override_role |
| **allowed_actor** | identity_access (definição), training (aplicação) |
| **forbidden_actor** | qualquer componente de Training definindo permissão de forma independente |
| **preconditions** | — |
| **postconditions** | todas as permissões em Training verificadas via identity_access |
| **state_impact** | — |
| **events_emitted** | — |
| **invariants** | INV-TRAIN-022, INV-TRAIN-041 |
| **boundary_rules** | identity_access é módulo transversal soberano de permissões |
| **evidence_required** | nenhuma permissão hardcoded em Training; todas por referência a identity_access |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | PERMISSIONS, DOMAIN_RULES, INVARIANTS |

---

## Bloco 7 — Governança

### TRAIN-DEC-022

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-022 |
| **decision_stage** | governance |
| **decision_type** | authorization |
| **decision_name** | Atleta inelegível bloqueia prescrição executável sem override auditado |
| **problem_real_world** | Atleta com restrição ativa receber prescrição executável sem guard, criando risco de agravamento de lesão |
| **operational_value_unit** | prescription_line + eligibility_guard |
| **entity_owner** | training (guard), medical (restriction source) |
| **entities_touched** | prescription_line, restriction_profile (ref), return_to_play_guard (ref), override_authorization |
| **minimum_required_fields** | guard verifica: restriction_profile.active, return_to_play_guard.active, availability_status |
| **allowed_origin** | system.eligibility_check antes de prescrição executável |
| **forbidden_origin** | prescrição sem verificação de elegibilidade |
| **allowed_actor** | system (guard), coach_head (override com autorização elevada e auditada) |
| **forbidden_actor** | athlete, coach_assistant (override de restrição médica) |
| **preconditions** | prescrição sendo criada para atleta específico |
| **postconditions** | se bloqueado: restriction_guard_triggered; se override: override_authorized emitido com responsible |
| **state_impact** | — |
| **events_emitted** | restriction_guard_triggered, override_authorized (se aplicável) |
| **invariants** | INV-TRAIN-021 |
| **boundary_rules** | restriction_profile consumido de medical (read-only) |
| **evidence_required** | prescrição para atleta com restrição ativa retorna 422 sem override; override gera audit_event |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, PERMISSIONS, OpenAPI |

### TRAIN-DEC-023

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-023 |
| **decision_stage** | governance |
| **decision_type** | integrity |
| **decision_name** | Derived signals não substituem fatos-fonte |
| **problem_real_world** | readiness_score, dropout_risk_signal ou engagement_signal sobrescreverem dados brutos, perdendo evidência original |
| **operational_value_unit** | derived_signal |
| **entity_owner** | training |
| **entities_touched** | execution_record, athlete_feedback, wellness_check (ref), derived_signal |
| **minimum_required_fields** | derived_signal: raw_data_ref (imutável), computed_at, algorithm_version |
| **allowed_origin** | system.computation sobre raw_data |
| **forbidden_origin** | derived_signal substituindo ou sobrescrevendo raw_data |
| **allowed_actor** | sistema (para computar sinais derivados) |
| **forbidden_actor** | qualquer agente com permissão de substituir raw_data por derived |
| **preconditions** | raw_data (respostas brutas, registros de execução) existem e são imutáveis |
| **postconditions** | derived_signal criado com raw_data_ref preservado e inalterado |
| **state_impact** | — |
| **events_emitted** | derived_signal_computed |
| **invariants** | INV-TRAIN-036 |
| **boundary_rules** | — |
| **evidence_required** | raw_data_ref presente e non-null em todo derived_signal; raw_data imutável após criação |
| **gate_class** | blocking |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema |

### TRAIN-DEC-024

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-024 |
| **decision_stage** | governance |
| **decision_type** | audit |
| **decision_name** | Atenção do treinador é finita e priorizada na fila de atenção |
| **problem_real_world** | attention_queue gerando ruído genérico sem severidade ou motivo, esgotando atenção do treinador e levando ao abandono do sistema |
| **operational_value_unit** | attention_queue_item |
| **entity_owner** | training |
| **entities_touched** | attention_queue_item |
| **minimum_required_fields** | severity_level (enum: critical\|high\|medium\|low), reason_code, target_entity_ref, created_at, resolved (boolean) |
| **allowed_origin** | system.guard_trigger, coach.manual_flag |
| **forbidden_origin** | alert_without_reason, blanket_notification, alert sem target_entity_ref |
| **allowed_actor** | system (triggers de guard), coach (flag manual) |
| **forbidden_actor** | qualquer agente criando alerta sem reason_code e severity_level |
| **preconditions** | evento real ocorreu (restriction triggered, athlete at_risk, objective overdue, etc.) |
| **postconditions** | item na attention_queue com severity e reason claros |
| **state_impact** | attention_queue_item: OPEN → RESOLVED |
| **events_emitted** | attention_queue_updated |
| **invariants** | INV-TRAIN-027 |
| **boundary_rules** | — |
| **evidence_required** | todo attention_queue_item tem severity_level, reason_code e target_entity_ref |
| **gate_class** | warning |
| **automation_level** | fully_automatable |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema, UI_CONTRACT |

### TRAIN-DEC-025

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-025 |
| **decision_stage** | governance |
| **decision_type** | business |
| **decision_name** | Fricção adaptativa no check-in do atleta |
| **problem_real_world** | Check-in longo e repetitivo para todo atleta todo dia gerando abandono do sistema |
| **operational_value_unit** | athlete_checkin (fluxo adaptativo) |
| **entity_owner** | training (trigger/display), wellness (data) |
| **entities_touched** | athlete_checkin, wellness_state (ref), restriction_profile (ref) |
| **minimum_required_fields** | checkin: athlete_ref, session_ref, state_summary (normal\|at_risk), extended_questions (presente apenas se at_risk) |
| **allowed_origin** | system.adaptive_logic baseado em wellness_state + restriction_profile |
| **forbidden_origin** | checkin_full_always, forced_long_checkin independente do estado |
| **allowed_actor** | athlete (resposta), system (lógica adaptativa) |
| **forbidden_actor** | coach forçando checkin longo para atletas em estado normal |
| **preconditions** | sessão publicada; atleta no escopo |
| **postconditions** | checkin registrado; se at_risk, alertas gerados em attention_queue |
| **state_impact** | — |
| **events_emitted** | checkin_submitted, attention_queue_updated (se at_risk) |
| **invariants** | INV-TRAIN-025, INV-TRAIN-026 |
| **boundary_rules** | wellness (dono do wellness_state); training (trigger e exibição do checkin) |
| **evidence_required** | variante mínima vs expandida de checkin verificada por teste; abandoned_rate monitorado |
| **gate_class** | warning |
| **automation_level** | fully_automatable |
| **materializes_in** | UI_CONTRACT, SCREEN_MAP, DOMAIN_RULES |

### TRAIN-DEC-026

| Campo | Valor |
|-------|-------|
| **decision_id** | TRAIN-DEC-026 |
| **decision_stage** | governance |
| **decision_type** | audit |
| **decision_name** | Raciocínio técnico sobrevive à troca de staff |
| **problem_real_world** | Conhecimento técnico acumulado perdido quando coach muda, forçando reconstrução de contexto e reduzindo qualidade das intervenções |
| **operational_value_unit** | continuity_snapshot, decision_rationale |
| **entity_owner** | training |
| **entities_touched** | continuity_snapshot, decision_rationale, staff_handoff, coach_note |
| **minimum_required_fields** | snapshot: session_ref OR cycle_ref, key_decisions, open_items, created_by, created_at |
| **allowed_origin** | coach.explicit_action, system.auto_snapshot_on_handoff |
| **forbidden_origin** | system discarding rationale on role_change |
| **allowed_actor** | coach_head, admin (handoff process) |
| **forbidden_actor** | sistema deletando decision_rationale na troca de staff |
| **preconditions** | staff_handoff ou mudança de responsável iminente |
| **postconditions** | continuity_snapshot preservado; novo responsável tem acesso ao contexto |
| **state_impact** | — |
| **events_emitted** | staff_handoff_recorded |
| **invariants** | INV-TRAIN-030, INV-TRAIN-031 |
| **boundary_rules** | — |
| **evidence_required** | continuity_snapshot presente antes de staff_handoff event; testes de non-deletion de rationale |
| **gate_class** | warning |
| **automation_level** | manual_review_required |
| **materializes_in** | DOMAIN_RULES, INVARIANTS, Schema |

---

## Resumo de Referências Cruzadas

### Invariantes → Decisões

| INV-ID | Nome Curto | Decisões |
|--------|-----------|---------|
| INV-TRAIN-001 | Sessão exige objetivo | DEC-002, DEC-004, DEC-006, DEC-007 |
| INV-TRAIN-002 | Objetivo exige origem rastreável | DEC-002, DEC-003, DEC-004 |
| INV-TRAIN-003 | Necessidade não cria sessão automaticamente | DEC-002, DEC-005 |
| INV-TRAIN-004 | IA só recomenda; treinador decide | DEC-005, DEC-018 |
| INV-TRAIN-005 | Sessão publicada exige conteúdo mínimo | DEC-007 |
| INV-TRAIN-006 | Execução referencia prescrição | DEC-009 |
| INV-TRAIN-007 | Planned vs Actual obrigatório | DEC-010 |
| INV-TRAIN-008 | Ajuste exige motivo estruturado | DEC-011 |
| INV-TRAIN-009 | Sessão concluída exige evidência | DEC-012 |
| INV-TRAIN-010 | Feedback contextual e vinculado | DEC-013 |
| INV-TRAIN-011 | Revisão exige evidência de execução | DEC-015 |
| INV-TRAIN-013 | Training não soberaniza atleta/equipe/restrição | DEC-017 |
| INV-TRAIN-014 | Restrição médica é read-only em Training | DEC-017 |
| INV-TRAIN-015 | Analytics não altera Training diretamente | DEC-005, DEC-018 |
| INV-TRAIN-017 | Status lifecycle fechado | DEC-008 |
| INV-TRAIN-018 | Sessão publicada não perde campos mínimos | DEC-007, DEC-008 |
| INV-TRAIN-019 | IN_PROGRESS sem hard delete | DEC-008, DEC-016 |
| INV-TRAIN-020 | COMPLETED é imutável por edição destrutiva | DEC-012, DEC-016 |
| INV-TRAIN-021 | Atleta inelegível bloqueado | DEC-022 |
| INV-TRAIN-022 | Variante individual respeita escopo/permissão | DEC-021 |
| INV-TRAIN-025 | Interação do atleta tem propósito downstream | DEC-025 |
| INV-TRAIN-026 | Fricção adaptativa obrigatória | DEC-025 |
| INV-TRAIN-027 | Atenção do treinador priorizada | DEC-024 |
| INV-TRAIN-028 | Conversa gera consequência operacional | DEC-013, DEC-014 |
| INV-TRAIN-029 | Decisões relevantes auditadas | DEC-016, DEC-020 |
| INV-TRAIN-030 | Justificativa sobrevive à troca de staff | DEC-016, DEC-026 |
| INV-TRAIN-031 | Origem de evidência preservada | DEC-003, DEC-026 |
| INV-TRAIN-036 | Derived signals não substituem fatos-fonte | DEC-023 |
| INV-TRAIN-037 | Training consome medical, não soberaniza | DEC-017 |
| INV-TRAIN-038 | Training mantém autoridade sobre analytics | DEC-018 |
| INV-TRAIN-039 | Notifications como intents, não entrega direta | DEC-019 |
| INV-TRAIN-040 | Audit via módulo transversal | DEC-020 |
| INV-TRAIN-041 | identity_access governa permissão | DEC-021 |

### Módulos de Boundary → Decisões

| Módulo | Tipo de Relação | Decisões Relevantes |
|--------|----------------|---------------------|
| medical | Training consome (read-only) | DEC-017, DEC-022 |
| analytics | Training consome sinais; treinador decide | DEC-005, DEC-018 |
| notifications | Training emite intents | DEC-019 |
| audit | Training emite eventos | DEC-016, DEC-020 |
| identity_access | Training aplica permissões | DEC-021 |
| wellness | Training consome estado de prontidão | DEC-025 |
| exercises | Training referencia biblioteca | DEC-001 (capacidade) |
| scout | Training consome sinais de scouting | DEC-003, DEC-005 |
| matches | Training consome outcome competitivo | DEC-003 |
| teams | Training referencia escopo humano/organizacional | DEC-007 |

### Gate Classes por Bloco

| gate_class | Quantidade | Decisões |
|-----------|-----------|---------|
| blocking | 19 | DEC-001 a DEC-013, DEC-016 a DEC-023 |
| warning | 4 | DEC-014 (parcial), DEC-015, DEC-024, DEC-025, DEC-026 |
| documentation_only | 0 | — |

---

*Matriz gerada em 2026-03-14 com base em `.dev/TREINOS.md`*
*Próximo artefato: `MODULE_DECISION_IR.json`*


# CHECKLISTA DE GAPS PARA MATRIZ CANÔNICA

Checklist dos gaps restantes da Matriz Canônica do Módulo Training. Aplique a correção necessária para deixar a Matriz deterministica.

---

**1. Nomes dos artefatos de superfície precisam bater exatamente com o canon real do repositório.**
Você usou coisas como:

* `MODULE_SCOPE`
* `DOMAIN_RULES`
* `STATE_MODEL`
* `OpenAPI`
* `Schema`

Isso está bom como classe de superfície, mas para geração determinística o pipeline vai precisar do path exato.

**CORREÇÃO**:

Tabela canônica de mapeamento `materializes_in` → path exato (relativo à raiz do repo):

| Surface type | Path canônico | Status |
|---|---|---|
| `README` | `docs/hbtrack/modulos/training/README.md` | existe |
| `MODULE_SCOPE` | `docs/hbtrack/modulos/training/MODULE_SCOPE_TRAINING.md` | existe |
| `DOMAIN_RULES` | `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md` | existe |
| `INVARIANTS` | `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` | existe |
| `STATE_MODEL` | `docs/hbtrack/modulos/training/STATE_MODEL_TRAINING.md` | **CRIAR** (template: `.contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md`) |
| `PERMISSIONS` | `docs/hbtrack/modulos/training/PERMISSIONS_TRAINING.md` | **CRIAR** (template: `.contract_driven/templates/modulos/PERMISSIONS_{{MODULE_NAME_UPPER}}.md`) |
| `ERRORS` | `docs/hbtrack/modulos/training/ERRORS_TRAINING.md` | **CRIAR** (template: `.contract_driven/templates/modulos/ERRORS_{{MODULE_NAME_UPPER}}.md`) |
| `UI_CONTRACT` | `docs/hbtrack/modulos/training/UI_CONTRACT_TRAINING.md` | **CRIAR** (template: `.contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md`) |
| `SCREEN_MAP` | `docs/hbtrack/modulos/training/SCREEN_MAP_TRAINING.md` | **CRIAR** (template: `.contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md`) |
| `OpenAPI` | `contracts/openapi/paths/training.yaml` | existe |
| `Schema` | `contracts/schemas/training/training_session.schema.json` | existe |
| `Workflow` | `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml` | existe |
| `AsyncAPI` | `contracts/asyncapi/messages/{event_name}.yaml` + `contracts/asyncapi/channels/{channel}.yaml` + `contracts/asyncapi/operations/{op}.yaml` | **CRIAR por evento** |

---

**2. `minimum_required_fields` ainda está em linguagem humana, não em binding tipado.**
Isso está correto para a matriz.
Mas significa que ainda falta uma etapa de transformação para:

* campo
* tipo semântico
* required
* nullable
* enum ref
* constraint ref

**CORREÇÃO**:

Substituir o texto livre de `minimum_required_fields` por tabela tipada com as colunas:

| field | semantic_type_ref | required | nullable | enum_ref | constraint_ref |

- Fonte dos tipos: `.dev/training.module_decision_ir.yaml` → `entities[*].fields[*]` (campos já têm `semantic_type_ref`, `required`, `nullable`, `unique_governance_id`)
- Fonte dos constraints: `contracts/schemas/training/training_session.schema.json` (validações JSON Schema por campo)

Exemplo aplicado (campos mínimos de `training_session` para criação — TRAIN-DEC-006):

| field | semantic_type_ref | required | nullable | enum_ref | constraint_ref |
|---|---|---|---|---|---|
| `id` | `core.id.uuid_v4` | `true` | `false` | — | `FLD-TRAINING-001` |
| `teamId` | `core.team.id` | `true` | `false` | — | `FLD-TRAINING-002` |
| `scheduledStartAt` | `core.time.timestamp_utc` | `true` | `false` | — | `FLD-TRAINING-003` |
| `state` | `training.state` | `true` | `false` | `training.state_enum` | `FLD-TRAINING-004` |

Aplicar o mesmo padrão a todas as decisions que hoje têm `minimum_required_fields` em prosa.

---

**3. `state_impact` ainda está semi-livre.**
Está ótimo para governança, mas ainda precisa ser normalizado para:

* `entity_ref`
* `initial_state`
* `allowed_transitions`
* `forbidden_transitions`
* `guards`

**CORREÇÃO**:

Substituir `state_impact` semi-livre pelo formato estruturado referenciando `STM-TRAINING-001`:

```
entity_ref: training.training_session   # STM-TRAINING-001 (.dev/training.module_decision_ir.yaml → state_models[0])
transition: {from_state} → {to_state}
guard_ref: {rule_ref} | none
```

- Estados válidos: `DRAFT | PLANNED | SCHEDULED | IN_PROGRESS | COMPLETED | CANCELLED`
- Transições permitidas: conforme `STM-TRAINING-001.allowed_transitions`
- Transições proibidas: conforme `STM-TRAINING-001.forbidden_transitions`
- Guards: conforme `STM-TRAINING-001.transition_guards` (ex.: `PLANNED→SCHEDULED` requer `training.rule.publication_preconditions_met`)

Exemplo aplicado (TRAIN-DEC-007 — publicação de sessão):

```
entity_ref: training.training_session (STM-TRAINING-001)
transition: DRAFT → SCHEDULED
guard_ref: training.rule.publication_preconditions_met
```

Decisions sem transição de estado devem registrar: `state_impact: none`.

---

**4. `events_emitted` ainda são nomes, não contratos de evento.**
Está correto para esta camada, mas ainda precisa virar evento tipado.

**CORREÇÃO**:

Para cada evento listado em `events_emitted`, criar o contrato em `contracts/asyncapi/messages/{event_name}.yaml` com o seguinte formato (baseado no existente `contracts/asyncapi/messages/training_attendance_marked.yaml`):

```yaml
name: {event_name}
title: {Title}
summary: {descrição do evento}
contentType: application/json
payload:
  $ref: ../components/schemas/{event_name}_payload.yaml
```

Referenciar no campo `events_emitted` pelo path relativo: `contracts/asyncapi/messages/{event_name}.yaml`

Eventos a contratar identificados nas decisions desta matriz:

| Evento | Decision | Path a criar |
|---|---|---|
| `training_session_created` | TRAIN-DEC-006 | `contracts/asyncapi/messages/training_session_created.yaml` |
| `training_session_published` | TRAIN-DEC-007 | `contracts/asyncapi/messages/training_session_published.yaml` |
| `training_session_status_changed` | TRAIN-DEC-008 | `contracts/asyncapi/messages/training_session_status_changed.yaml` |
| `execution_recorded` | TRAIN-DEC-009 | `contracts/asyncapi/messages/execution_recorded.yaml` |
| `training_session_completed` | TRAIN-DEC-011 | `contracts/asyncapi/messages/training_session_completed.yaml` |
| `cycle_reviewed` | TRAIN-DEC-014 | `contracts/asyncapi/messages/cycle_reviewed.yaml` |
| `restriction_guard_triggered` | TRAIN-DEC-017, TRAIN-DEC-021 | `contracts/asyncapi/messages/restriction_guard_triggered.yaml` |
| `notification_intent_emitted` | TRAIN-DEC-019 | `contracts/asyncapi/messages/notification_intent_emitted.yaml` |
| `audit_event_emitted` | TRAIN-DEC-020 | `contracts/asyncapi/messages/audit_event_emitted.yaml` |

Os demais eventos listados nas decisions devem seguir o mesmo padrão.

---

**5. `allowed_actor` / `forbidden_actor` e `allowed_origin` / `forbidden_origin` ainda precisam ser ligados ao modelo real de autorização e origem.**
Como decisão, está ótimo.
Como IR, ainda não.

**CORREÇÃO**:

**`allowed_actor` / `forbidden_actor`** — vincular ao RBAC do módulo `identity_access`:

Forma canônica: `identity_access.role.{role_name}`

| Valor atual na matriz | Referência canônica | Fonte |
|---|---|---|
| `coach_head` | `identity_access.role.coach_head` | `contracts/openapi/paths/identity_access.yaml` |
| `coach_assistant` | `identity_access.role.coach_assistant` | `contracts/openapi/paths/identity_access.yaml` |
| `athlete` | `identity_access.role.athlete` | `contracts/openapi/paths/identity_access.yaml` |
| `admin` | `identity_access.role.admin` | `contracts/openapi/paths/identity_access.yaml` |
| `physical_trainer` | `identity_access.role.physical_trainer` | `contracts/openapi/paths/identity_access.yaml` |
| `physiotherapist` | `identity_access.role.physiotherapist` | `contracts/openapi/paths/identity_access.yaml` |
| `system` | `training.system_actor` | ator interno ao módulo, sem papel RBAC externo |

**`allowed_origin` / `forbidden_origin`** — vincular ao módulo + capability + ação:

Forma canônica: `{module}.{capability_id}.{action}` (capabilities em `.dev/training.module_decision_ir.yaml` → `capabilities[*]`)

| Valor atual na matriz | Referência canônica |
|---|---|
| `coach.action` | `identity_access.role.coach_head` + `training.CAP-TRAINING-002.create` |
| `analytics.output` | `analytics.CAP-ANALYTICS-*.emit_signal` |
| `medical.update` | `medical.{CAP_ID}.update_restriction_profile` |
| `system.adaptive_logic` | `training.system_actor.adaptive_logic` |
| `training.action → audit.event_emission` | `training.system_actor.emit_audit_event` |
| `identity_access.policy → training.enforcement` | `identity_access.CAP-IAM-*.enforce_policy` |



