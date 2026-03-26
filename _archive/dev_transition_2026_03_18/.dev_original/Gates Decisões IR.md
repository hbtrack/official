# Gates — Decisões IR: Análise de Cobertura (`training`)

## Top 5 patches — melhor custo-benefício

| # | Patch |
|---|-------|
| 1 | Resolver semanticamente `subject_ref`, `primary_entities`, `entities_touched`, `request_entity`, `response_entity` |
| 2 | Exigir `relations.to/from` como entidades (`entity_id` / `external_entity_ref`), nunca nome de coluna/FK |
| 3 | Validar `payload_refs` contra fields reais, projections formais ou `event_schema` declarado |
| 4 | Detectar aliases semânticos concorrentes (naming drift intra-IR) |
| 5 | Implementar `IR_REGISTRY_DRIFT` contra `MODULE_SOURCE_AUTHORITY_MATRIX`, axioms e snapshots promovidos |

---

## A — Referências implícitas não resolvidas

Código primário: `IR_UNKNOWN_REGISTRY_REF`

| Problema real do IR | Código que deveria pegar | Por que hoje não pega | Patch conceitual no gate |
|---|---|---|---|
| `capabilities.primary_entities` cita `athlete_feedback`, `staff_handoff`, `restriction_profile_ref`, `wellness_state_ref` sem entidade/modelo formal no IR | `IR_UNKNOWN_REGISTRY_REF` | O check atual só olha `registry_ref` / `ref_module` explícitos; não resolve strings semânticas em `primary_entities` | Expandir resolução semântica para `primary_entities`, exigindo que cada item aponte para `entities[]` local, registry canônico, ou `external_ref` formal |
| `rules.subject_ref` cita objetos não modelados: `recommendation`, `athlete_checkin`, `derived_signal`, `notification_intent`, `audit_event`, `permission_policy` | `IR_UNKNOWN_REGISTRY_REF` | `subject_ref` não entra na validação forte de referência | Validar `subject_ref` contra catálogo canônico: entidade local, boundary object formal, event contract formal ou registry externo explícito |
| `formal_check_hint` menciona `review_outcome`, `attendance_record`, `athlete_rpe`, `audit_correction` sem definição formal | `IR_UNKNOWN_REGISTRY_REF` ou novo subtipo semântico | O gate não parseia referências implícitas dentro do texto de `formal_check_hint` | Criar parser leve de tokens semânticos em `formal_check_hint`, com allowlist de termos livres e validação de objetos formais mencionados |
| `ui_flows.entities_touched` inclui `athlete_checkin` e `athlete_feedback`, mas essas entidades não existem em `entities[]` | `IR_UNKNOWN_REGISTRY_REF` | `entities_touched` não é resolvido semanticamente | Validar `entities_touched` contra `entities[]` + boundary registries |
| `relations.to` aponta para nome de campo (`exercise_ref`, `team_ref`, `season_ref`, `restriction_profile_ref`) em vez de entidade alvo | `IR_RELATION_WITHOUT_OWNERSHIP` ou novo check específico | O gate checa presença de ownership/delete_policy, mas não semântica do alvo | Exigir que `relations.from` e `relations.to` apontem para `entity_id` ou `external_entity_ref`, nunca para nome de coluna/FK |
| `REL-TRAIN-006` usa `to: exercise_ref` em vez da entidade soberana do módulo `exercises` | `IR_UNKNOWN_REGISTRY_REF` + novo check de relation target | `exercise_ref` é tratado como string qualquer, não resolvida | Validar que relações cross-module usem `external_entity_ref: exercises.exercise` ou sintaxe canônica equivalente |
| `decision_rationale.subject_type` inclui `recommendation`, mas `recommendation` não existe como entidade/modelo formal | `IR_UNKNOWN_REGISTRY_REF` | `subject_type` enum não é validado semanticamente | Validar enums que representam tipos de objetos contra entidades/boundaries formais |
| `INV-TRAIN-004` e integrações pressupõem um objeto `recommendation` não modelado | `IR_UNKNOWN_REGISTRY_REF` | O gate não cruza rules/integrations/events com inventário de objetos formais | Criar verificação cross-block: todo objeto operacional citado em 2+ superfícies deve existir como entidade, DTO, event schema ou external object |
| `CAP-TRAIN-009.forbidden_behavior` menciona `review_outcome`, que não existe | `IR_UNKNOWN_REGISTRY_REF` | Texto livre em `forbidden_behavior` não é semantizado | Parse opcional de termos estruturados em `forbidden_behavior` ou regra de glossário formal obrigatório |
| `permissions.roles.admin.capabilities` inclui `manage_staff_handoff`, mas `staff_handoff` não é entidade/modelo formal | `IR_UNKNOWN_REGISTRY_REF` | Capabilities RBAC não são reconciliadas com objetos reais | Validar capabilities contra catálogo de actions/resources materializáveis |
| `integrations.analytics.data_provided_to_training` inclui `recommendation` não modelado | `IR_UNKNOWN_REGISTRY_REF` | `integrations.*.data_provided_to_training` não é validado semanticamente | Validar objetos de integração contra catálogo local/external formal |
| `forbidden_inference_global` cita `audit_correction`, `notification_intent`, `readiness_score`, `dropout_risk_signal` sem objeto formal | `IR_UNKNOWN_REGISTRY_REF` | Lista global é tratada como texto livre | Validar termos estruturados em `forbidden_inference_global` quando estiverem em formato de objeto de domínio |

---

## B — Payload / event schema sem reconciliação com o modelo

Código primário: `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE`

| Problema real do IR | Código que deveria pegar | Por que hoje não pega | Patch conceitual no gate |
|---|---|---|---|
| `api_use_cases.request_entity` / `response_entity` apontam para DTOs inexistentes: `training_session_create`, `training_session_detail`, `attention_queue_item_list` | `IR_API_USE_CASE_INCOMPLETE` | Hoje o gate só verifica presença do campo, não sua resolução real | Exigir que `request_entity` / `response_entity` apontem para DTO formal, projection formal ou entidade canônica existente |
| O IR assume DTOs, eventos derivados e projeções, mas não define nenhum bloco formal de `dto_models`, `event_schemas` ou `projections` | `IR_API_USE_CASE_INCOMPLETE` + `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Os checks aceitam shape mínimo sem exigir artefatos intermediários | Introduzir blocos opcionais obrigatórios por aplicabilidade: `dto_models`, `event_schemas`, `projections` |
| `feedback_posted` emite `anchor_ref`, mas `feedback_thread` não tem esse campo | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | O check atual só garante trigger/payload mínimo, não reconcilia payload com modelo | Validar cada `payload_ref` contra campos reais, projections formais ou payload schemas declarados |
| `conversation_outcome_recorded` emite `closed_by`, mas `feedback_thread` não possui `closed_by` | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Mesmo motivo acima | Exigir alinhamento `payload_refs` ↔ campos/modelos/event schemas |
| `training_session_cancelled` emite `cancel_reason`, mas `training_session` não modela `cancel_reason` | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Mesmo motivo acima | Obrigar projection formal de evento quando payload não vier diretamente da entidade |
| `training_session_status_changed` emite `previous_status` e `actor_ref`, mas não estão modelados em `training_session` | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | O gate não diferencia campo persistido de campo de envelope/evento | Permitir payload derivado apenas se houver `event_schema` ou `payload_mapping` formal |
| `need_linked_to_objective` emite `session_objective_ref`, mas a entidade `need_detected` tem `linked_objective_ref` | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Não há reconciliação nominal entre payload e modelo | Checar mismatch nominal e exigir alias/formal mapping quando payload usar nome diferente do campo |
| `planned_vs_actual_recorded` emite `planned_content_snapshot_ref`, mas o campo modelado é `planned_content_snapshot` | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Não há validação fina de nome/ref | Validar sufixos `_ref` apenas quando o campo realmente existir como referência |
| `events.consumed.analytics_recommendation_generated` diz que cria `recommendation`, mas esse objeto não existe formalmente | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` + `IR_UNKNOWN_REGISTRY_REF` | O gate não cruza evento consumido com objeto de materialização declarado | Exigir `materializes_object_ref` ou `affects_object_ref` resolvido canonicamente |
| `events.emitted.override_authorized` pressupõe `override_reason` e `audit_event_ref`, mas não há `restriction_override` modelado | `IR_EVENT_MODEL_INCOMPLETE_WHEN_EVENTS_APPLICABLE` | Payload não é reconciliado com entidade/DTO/event schema | Exigir schema de evento quando payload não vier de entidade persistida |

---

## C — Aliases semânticos e naming drift

Código primário: `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK`

| Problema real do IR | Código que deveria pegar | Por que hoje não pega | Patch conceitual no gate |
|---|---|---|---|
| Aliases concorrentes para o mesmo conceito: `training_intervention_cycle`, `training_cycle_ref`, `cycle_ref`, `training_cycle` | `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK` | O check atual não detecta alias semântico, apenas derived formula | Implementar detector de alias/collision semântica com canonical naming por conceito |
| `attention_queue_item.target_entity_type` usa `training_cycle`, enquanto a entidade real é `training_intervention_cycle` | `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK` ou `IR_UNKNOWN_REGISTRY_REF` | Enums semânticos não são reconciliados com entidades canônicas | Validar enums de tipo-entidade contra catálogo canônico de entity kinds |
| `coach_note` usa `training_cycle_ref`, enquanto outras partes usam `intervention_cycle_ref` / `cycle_ref` | `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK` | Falta detecção de naming drift interno | Checar consistência de nomes de referência intra-IR por conceito |
| `UC-TRAIN-014` usa `athlete_checkin`, embora `OD-TRAIN-005` recomende que check-in pertença a `Wellness` | `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK` | O check atual só cobre campos `derived` sem fórmula | Adicionar regra de soberania pendente: se um objeto aparece em API/UI/rules e sua soberania ainda está ambígua ou externa, falhar sem `external_owner` / `handoff_contract` |
| `OD-TRAIN-005` deixa soberania do check-in em aberto, mas API/UI/rules/eventos já tratam o fluxo como materializado em 3+ superfícies | `IR_OPEN_DECISION_BLOCKING` ou `IR_NON_DETERMINISTIC_MATERIALIZATION_RISK` | A decisão está `blocking: false`, então não barra; e o risco não é detectado | Criar regra: decisão não-blocking vira erro se um conceito ainda ambíguo já estiver materializado em 3+ superfícies |

---

## D — Surface mapping e drift contra registries canônicos

Códigos primários: `IR_SURFACE_MAPPING_INCOMPLETE` · `IR_REGISTRY_DRIFT`

| Problema real do IR | Código que deveria pegar | Por que hoje não pega | Patch conceitual no gate |
|---|---|---|---|
| `surface_mapping` usa `TRAIN-DEC-*`, mas `open_decisions` usa `OD-TRAIN-*`; não há evidência de que os IDs batem | `IR_SURFACE_MAPPING_INCOMPLETE` | Hoje só checa presença de `artifact_path/target`, não integridade referencial dos IDs | Validar que todo `decision_id` citado em `surface_mapping` exista no inventário real de decisões |
| `surface_mapping` referencia faixas como `TRAIN-DEC-001 through TRAIN-DEC-026`, mas essas decisões não existem formalmente no IR | `IR_SURFACE_MAPPING_INCOMPLETE` | O gate não expande nem resolve ranges textuais | Exigir lista explícita de IDs ou parser que expanda ranges e valide cada ID |
| Não há comparação do IR com registries externos — nomes, boundaries e soberania podem divergir do canônico | `IR_REGISTRY_DRIFT` | Declarado, mas nunca emitido | Implementar diff do IR contra `MODULE_SOURCE_AUTHORITY_MATRIX`, axioms, registries semânticos e snapshots promovidos |
