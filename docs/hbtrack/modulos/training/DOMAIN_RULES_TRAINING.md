---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "domain-rules"
---

# DOMAIN_RULES_TRAINING.md

## Objetivo
Registrar as regras de negócio do módulo `training`.

## Fonte do domínio
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md` (HBR-014: Treino Orientado à Modalidade)
- OpenAPI e schemas do módulo
- Invariantes documentadas em `INVARIANTS_TRAINING.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-TRAIN-001 | Sessões só podem ser criadas por treinadores ou coordenadores | `TrainingSession` | RBAC + SYSTEM_SCOPE.md | Atores: Treinador (nível 3), Coordenador (nível 2) |
| DR-TRAIN-002 | Soma dos percentuais de foco (7 campos `focus_*_pct`) deve ser ≤ 120 | `TrainingSession` | Regra de produto | Permite sessões híbridas sem ultrapassar limite de consistência |
| DR-TRAIN-003 | Valores individuais de foco, quando presentes, devem estar em [0..100] | `TrainingSession` | Regra de produto | Validação de range por campo |
| DR-TRAIN-004 | Wellness pré-treino só pode ser submetido até 2h antes de `session_at` | `WellnessPre` | Regra de produto | Garante coleta "pré" com antecedência suficiente |
| DR-TRAIN-005 | Wellness pós-treino só pode ser editado até 24h após criação | `WellnessPost` | Regra de produto | Permite correção breve mas impede edições tardias |
| DR-TRAIN-006 | Sessões com `session_at` > 60 dias no passado são somente leitura | `TrainingSession` | Regra de produto | Estabilidade histórica e integridade de analytics |
| DR-TRAIN-007 | Janela de edição de sessão depende de papel e estado (ver INV-TRAIN-004) | `TrainingSession` | Regra de produto + RBAC | Autor: até 10min antes; Superior: até 24h após |

## Regras derivadas da modalidade
| ID | Regra derivada do handebol | Regra de produto | Referência em HANDBALL_RULES_DOMAIN.md |
|---|---|---|---|
| DR-TRAIN-H01 | Treino de handebol organiza-se por posições específicas | Sistema deve suportar classificação de exercícios por posição-alvo (goleiro, pontas, armadores, pivô) | HBR-014 |
| DR-TRAIN-H02 | Treino de handebol organiza-se por fases do jogo | Sistema deve suportar classificação de exercícios por fase (ataque organizado, contra-ataque, defesa fechada, transição) | HBR-014 |
| DR-TRAIN-H03 | Categorias etárias determinam volume e intensidade | Sistema deve vincular sessões a categorias (mini-handebol, infantil, juvenil, júnior, adulto) | HBR-014 |
| DR-TRAIN-H04 | Periodização segue estrutura: temporada → bloco → semana → sessão | Sistema deve suportar 4 níveis de periodização (macrociclo, mesociclo, microciclo, sessão) | HBR-014 |

## Prioridade de verdade
1. Regra oficial do esporte quando aplicável (HBR-014)
2. Regra global do sistema (GLOBAL_INVARIANTS.md)
3. Regra do módulo (esta seção)
4. Comportamento da implementação

## Regras proibidas
- Não inferir regra de negócio a partir de UI isolada
- Não inferir regra de negócio a partir de dado histórico sem contrato
- Não inferir comportamento público sem respaldo em documentação do módulo

---

## Regras de negócio — decisões arquiteturais (atualizado 2026-03-16)

> **Materializadas a partir de ARCH_DECISIONS_TRAINING.md (DSS). Data: 2026-03-16.**

### Backbone operacional (TRAIN-DEC-001, TRAIN-DEC-002)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-008 | A unidade soberana é `training_intervention_cycle`, não `training_session`. Toda sessão pertence a um ciclo de intervenção. | TRAIN-DEC-001 |
| DR-TRAIN-009 | Toda sessão deve nascer de `need_detected`, `goal_gap` ou `competitive_focus`. O sistema exige propósito antes de duração. | TRAIN-DEC-002 |
| DR-TRAIN-010 | Analytics e IA produzem apenas `recommendations` ou `signals`. Nunca materializam `training_session` diretamente. Ato explícito de treinador autorizado é obrigatório. | TRAIN-DEC-003 |

### Sessão e objetivos (TRAIN-DEC-004, TRAIN-DEC-005, TRAIN-DEC-006)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-011 | Toda `training_session` deve possuir pelo menos um `SessionObjective` válido. Sessão sem objetivo operacional é inválida. | TRAIN-DEC-004 |
| DR-TRAIN-012 | Todo `SessionObjective` deve declarar `origin` como um de: `NEED_DETECTED`, `COMPETITIVE_FOCUS`, `DEVELOPMENT_GOAL`, `MANUAL_COACH_RATIONALE`. Objetivo sem origem é dado incompleto. | TRAIN-DEC-005 |
| DR-TRAIN-013 | Quando `origin = MANUAL_COACH_RATIONALE`, o campo `originNotes` é obrigatório (mínimo 10 caracteres). | TRAIN-DEC-005 |
| DR-TRAIN-014 | Sessão só pode transitar para `PUBLISHED` ou `SCHEDULED` se possuir: `team_scope` e/ou `athlete_scope`, pelo menos um `SessionObjective`, horário/data, pelo menos um bloco, e `coach_assignment`. Sem esses campos, status máximo é `DRAFT`. | TRAIN-DEC-006 |

### Execução e planned vs actual (TRAIN-DEC-007, TRAIN-DEC-008, TRAIN-DEC-009)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-015 | `ExecutionRecord` não pode existir como objeto solto. Deve apontar para `sessionId` (obrigatório) e opcionalmente `blockId` e/ou `prescriptionLineId`. | TRAIN-DEC-007 |
| DR-TRAIN-016 | Se for improviso documentado, `ExecutionRecord` deve carregar `coachRationale` de ajuste ao vivo. | TRAIN-DEC-007 |
| DR-TRAIN-017 | Todo `ExecutionRecord` preserva `plannedContent` e `actualContent` separadamente. `plannedContent` nunca é sobrescrito por `actualContent`. | TRAIN-DEC-008 |
| DR-TRAIN-018 | Todo ajuste ao vivo (`LIVE_ADJUSTMENT`, `CONSTRAINT_OVERRIDE`, `ALTERNATE_EXERCISE`, `LOAD_RECALCULATION`) deve registrar `adjustmentReasonType` em campo estruturado — não texto livre irrestrito. | TRAIN-DEC-009 |
| DR-TRAIN-019 | `LIVE_ADJUSTMENT` e `CONSTRAINT_OVERRIDE` exigem adicionalmente `coachRationale` (mínimo 5 caracteres). | TRAIN-DEC-009 |

### Feedback e conversas técnicas (TRAIN-DEC-010, TRAIN-DEC-015)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-020 | Todo `FeedbackThread` deve referenciar pelo menos um contexto operacional: sessão, bloco, objetivo, atleta, evidência ou grupo. Feedback sem contexto é rejeitado. | TRAIN-DEC-010 |
| DR-TRAIN-021 | Toda conversa técnica relevante deve produzir `conversationOutcome` — um de: `REFLECTION_DOCUMENTED`, `COMMITMENT_MADE`, `FOLLOWUP_SCHEDULED`, `DECISION_RECORDED`, `PENDING_FOLLOWUP`. Conversa sem consequência operacional é rejeitada. | TRAIN-DEC-015 |
| DR-TRAIN-022 | `FOLLOWUP_SCHEDULED` exige `followUpAt`. `COMMITMENT_MADE` exige `commitmentText`. `DECISION_RECORDED` exige `decisionText`. | TRAIN-DEC-015 |

### Revisão e evidência (TRAIN-DEC-011)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-023 | Não pode haver `review_outcome` sem pelo menos um `ExecutionRecord` ou `post_session_report` equivalente. Revisão sem evidência é inválida. | TRAIN-DEC-011 |
| DR-TRAIN-024 | Ajuste futuro de plano deve derivar de revisão documentada ou de decisão manual justificada do coach. | TRAIN-DEC-011 |

### Elegibilidade e restrições críticas (TRAIN-DEC-012)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-025 | Atleta com restrição médica ativa, indisponibilidade severa ou `return_to_play_guard` não pode receber prescrição executável sem `override` explícito, autorizado e auditado via módulo `audit`. | TRAIN-DEC-012 |

### Imutabilidade e integridade (TRAIN-DEC-013, TRAIN-DEC-014)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-026 | Sessão `COMPLETED` é imutável por edição destrutiva. Alterações históricas exigem correção auditada e versionada. | TRAIN-DEC-013 |
| DR-TRAIN-027 | Sessões em `IN_PROGRESS` não podem ser excluídas fisicamente — apenas cancelamento lógico com trilha é permitido. | TRAIN-DEC-013 |
| DR-TRAIN-028 | Campos derivados (`readiness_score`, `dropout_risk_signal`, `engagement_signal`) nunca substituem os dados-fonte originais. A fonte primária de verdade é sempre o dado coletado. | TRAIN-DEC-014 |

### Dois loops explícitos (TRAIN-DEC-016)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-029 | O módulo opera dois ciclos separados: **coletivo** (`team_training_cycle`: calendário, presença, comunicação de equipe) e **individual** (`individual_development_cycle`: carga, readiness, progressão, restrição). | TRAIN-DEC-016 |
| DR-TRAIN-030 | Toda `training_session` deve declarar `individualizationMode` explicitamente: `COLLECTIVE_UNIFORM`, `COLLECTIVE_WITH_VARIANTS` ou `INDIVIDUAL_ONLY`. | TRAIN-DEC-016, TRAIN-DEC-044 |

### Dados externos e ingestão (TRAIN-DEC-036, TRAIN-DEC-037, TRAIN-DEC-038)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-031 | Dados externos passam pela camada de ingestão antes de entrar no domínio `training`. | TRAIN-DEC-036 |
| DR-TRAIN-032 | `observed_at` (quando o fato ocorreu) é distinto de `ingestedAt` (quando foi registrado no sistema). Ambos devem ser preservados. | TRAIN-DEC-037 |
| DR-TRAIN-033 | Idempotência é obrigatória para fatos ingeridos. Campo `idempotencyKey` permite reprocessamento seguro. | TRAIN-DEC-038 |

### Governança de dados sensíveis (TRAIN-DEC-039 a TRAIN-DEC-043)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-034 | Dados de wellness consumidos por `training` são domínio sensível (LGPD). Acesso por staff fora do self-only exige `data_access_log`. | TRAIN-DEC-039 |
| DR-TRAIN-035 | `training` não expõe detalhes sensíveis de wellness em endpoints genéricos. | TRAIN-DEC-040 |
| DR-TRAIN-036 | Inferências de IA sobre estado do atleta são sempre consultivas — nunca bloqueantes nem determinísticas por si sós. | TRAIN-DEC-041 |
| DR-TRAIN-037 | `dropout_risk_signal` é derivado — nunca fonte primária. Não pode substituir dados de resposta do atleta. | TRAIN-DEC-042 |

### Fila de atenção — atenção finita (TRAIN-DEC-027)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-038 | Todo item de `AttentionQueueItem` deve ter: `severity` explícito, `reasonCode` estruturado, `targetEntityType` e `targetEntityId` identificados. Itens sem esses campos são rejeitados. | TRAIN-DEC-027 |
| DR-TRAIN-039 | A violação da Elastic Sum Rule (INV-TRAIN-083) produz item de severidade `LOW` na fila de atenção quando dentro da tolerância, e rejeita a operação (422) quando fora. | TRAIN-DEC-027, INV-TRAIN-083 |

### Fronteiras de módulo (TRAIN-DEC-022 a TRAIN-DEC-025, TRAIN-DEC-046, TRAIN-DEC-047)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-040 | `training` não entrega notificação diretamente. Emite `notification_intent` para o módulo `notifications`. | TRAIN-DEC-022 |
| DR-TRAIN-041 | `training` registra fatos auditáveis enviando eventos ao módulo `audit`. Não mantém trilha informal interna. | TRAIN-DEC-023 |
| DR-TRAIN-042 | `training` consome `restriction_profile` e `return_to_play_guard` do módulo `medical` como somente leitura. Não cria nem edita verdade clínica. | TRAIN-DEC-024 |
| DR-TRAIN-043 | `identity_access` é fonte soberana de autorização. `training` aplica a policy — não a redefine. | TRAIN-DEC-025 |
| DR-TRAIN-044 | `analytics` é soberano de `derived_signal`. `training` consome sinais derivados como read-only. | TRAIN-DEC-046 |
| DR-TRAIN-045 | `exercises` é módulo soberano. `training` referencia exclusivamente `exercise_id + exercise_version_id` — nunca embute `Exercise`. Sessão histórica preserva `exercise_version_id` imutavelmente. | TRAIN-DEC-047, TRAIN-DEC-048 |

### Persistência híbrida (TRAIN-DEC-029, TRAIN-DEC-030, TRAIN-DEC-031)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-046 | O módulo `training` usa persistência HYBRID: eventos append-only para fatos de execução + CRUD para entidades de planejamento. | TRAIN-DEC-029 |
| DR-TRAIN-047 | Eventos append-only não eliminam o agregado CRUD da sessão. Os dois coexistem. | TRAIN-DEC-030 |
| DR-TRAIN-048 | `session_templates` e `planning_periodization` são CRUD puros — sem append-only. | TRAIN-DEC-031 |
| DR-TRAIN-049 | `session_block` é contrato obrigatório de Fase 1 — DSL operacional da sessão com campos `phase`, `orderIndex`, `durationMinutes`, `intensity` e referência a `exerciseId` + `exerciseVersionId`. Sessão `PUBLISHED` deve ter pelo menos um `session_block`. `phase` usa enum `session_block_phase`; `intensity` usa enum `session_block_intensity`. INV-TRAIN-083 aplicado. | TRAIN-DEC-049 |

## Nota sobre conflito ativo (TRAIN-DEC-020)

> 🚫 **BLOCKED_CONTRACT_CONFLICT:** ADR-017 classifica `IN_PROGRESS` como "Não (bloqueado)" na coluna "Editável?", mas TRAIN-DEC-020 exige suporte a `live_session_adjustment`, `alternate_exercise`, `constraint_override` e `load_recalculation` durante sessão `IN_PROGRESS`. Nenhum endpoint de ajuste ao vivo pode ser aberto antes de adendo formal em ADR-017 distinguindo imutabilidade do agregado de registros append-only. O adendo a ADR-017 precede a abertura de qualquer contrato de ajuste ao vivo.

---

### Regras operacionais—mitigações adversariais (adicionadas 2026-03-17)

#### Performance (A4)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-050 | Validação de soma `focus_*_pct` é executada **em memória no servidor** sobre os campos do payload+estado atual — nunca via agregação DB por sessão. Latência esperada < 1ms. Se o benchmark de 1k sessões concorrentes exceder 50ms P95, o campo `focus_sum` deve ser desnormalizado (campo computado no modelo). | Performance + RC-2 |

#### Fronteiras de módulo reforçadas (A5)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-051 | Todo endpoint que altera estado de `training_session` (`publish`, `unpublish`, `start`, `complete`, `cancel`, `archive`) deve validar explicitamente o papel do ator via `identity_access` antes de executar a transição. Endpoints de somente leitura validam acesso (autenticação), mas não papel. Ausência de validação de papel é bloqueada por `TRAINING_FORBIDDEN_ACTOR` (403). | A5, DR-TRAIN-043, INV-TRAIN-098 |
| DR-TRAIN-052 | O módulo `training` não pode registrar nem atualizar `restriction_profile`, `return_to_play_guard` ou qualquer entidade clínica soberana do módulo `medical`. O endpoint `POST /{id}/ineligibility-declaration` cria uma **declaração operacional de inelegibilidade** (domínio training) — não confundir com restrição clínica. A declaração de inelegibilidade aponta para a restrição médica como referência, mas não a replica nem a altera. | A5, DR-TRAIN-042, INV-TRAIN-097 |
| DR-TRAIN-053 | Módulo `analytics` não pode alterar estado de `training_session`. Analytics consome dados de training via eventos (read). Qualquer chamada de analytics a endpoints de escrita de training (`PATCH`, `POST /{id}/complete` etc.) deve retornar 403 — validação de papel via `identity_access`. | A5, DR-TRAIN-044, INV-TRAIN-098 |

#### Convenção de nomenclatura (M5)

| ID | Regra | Decisão |
|---|---|---|
| DR-TRAIN-054 | **Convenção canônica status vs. state:** (a) em código (Python, SQL, API, schemas JSON) usar sempre **`status`** para o campo que armazena o estado FSM; (b) em documentação de contrato (STATE_MODEL, ADR, INVARIANTS) usar **`state`** ou **`estado`** ao descrever a FSM; (c) `DECISION_IR.yaml` e outros artefatos de contrato usam `state_model` e `states` — consistente com nomenclatura de FSM. Nunca inverter nos dois contextos. Refactoramento que violar esta convenção requer revisão de contrato antes de merge. | M5 |

---

## Regras de HB Pro Coach (Virtual Assistant Chat)

| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-TRAIN-COACH-01 | HB Pro Coach respostas sempre sobre handebol/treino. Tópicos permitidos: exercício (movimento, propósito, segurança), técnica de jogo (posição, arremesso, defesa), wellness (sono, nutrição, descanso, frequência), feedback histórico (treinos faltados, comentários passados), formações táticas | `athlete_chat_message` | D-UI-21 | Resposta a off-topic retorna redirecionamento educado, nunca erro/rejeição agressiva |
| DR-TRAIN-COACH-02 | HB Pro Coach rejeita palavrões e off-topic (política, assuntos aleatórios) com resposta padrão educada: "Sou coach de handebol. Posso ajudar com exercícios, treino, wellness ou feedback. O que quer saber?" | `athlete_chat_message` | D-UI-21 | Flags internas: `isOffTopicRejection=true` (para auditoria). Nunca rejeição agressiva. |
| DR-TRAIN-COACH-03 | HB Pro Coach entende e responde com fluência completa a linguagem natural informal de atletas (vc, pq, oq, taum, msm, etc). **NUNCA aponta ou corrige erros de digitação** — isso gera frustração. Comunica de forma elevadora: "Vejo seu comprometimento!", "Ótima pergunta!" | `athlete_chat_message` | D-UI-21 | Inclusividade + motivação são prioridade máxima. Sem flags de typo. |
| DR-TRAIN-COACH-04 | Conversa responde ao age-group (U10, U12, U14, U16, U18, ADULT) — linguagem e complexidade adaptadas. U10/U12 usam linguagem mais simples, de incentivo lúdico; ADULTO usa linguagem técnica e orientada a performance | `athlete_chat_conversation` | D-UI-21 | Campo `athleteAgeGroup` deve ser preenchido na conversação para contexto |
| DR-TRAIN-COACH-05 | Coach virtual oferece treino compensatório após atleta perder sessão ou solicitar objetivo específico. Atleta vê **preview**: nome + duração + objetivos (sem blocos, sem local/data). Coach encaminha sugestão **completa** (com blocos de exercícios detalhados) ao **treinador da equipe** via AsyncAPI | `training_suggestion` | D-UI-21, UIF-006 | Reduz atrito de atleta + Coach-in-Loop garantido pelo treinador (não pelo chat) |
| DR-TRAIN-COACH-06 | **Quem aprova/rejeita é o Treinador da Equipe (não o coach virtual).** Treinador recebe notificação assíncrona com sugestão completa + contexto de wellness do atleta. Janela de aprovação: até 24h. Aprovação → treino aparece em "Sessões Agendadas" com status "Aprovado por [Nome do Treinador]". Rejeição → atleta notificado + sugestões alternativas | `training_suggestion`, AsyncAPI event | D-UI-21, UIF-006 | Coach virtual não autoriza. Segurança clínico-técnica fica com treinador responsável |
| DR-TRAIN-COACH-07 | Max 1 sugestão de treino em estado `pending_approval` por atleta por vez. Novo pedido do atleta antes de resposta do treinador retorna mensagem: "Você já tem uma sugestão aguardando aprovação de seu treinador. Aguarde!" (409 Conflict) | `training_suggestion` | D-UI-21 | Previne spam + evita sobrecarga de notificação do treinador |
| DR-TRAIN-COACH-08 | Feature Store engineering: Coach consulta dados históricos via `ai_ingestion` (treinos, wellness, medical, analytics) e calcula features (fatigue_score, performance_gap, injury_status). Regras especializadas em handebol (se fatigue > 7 E performance_gap.velocity > 15% ENTÃO focus = [técnica, recuperação]) geram sugestões determinísticas por posição + categoria etária. Resposta sempre contextualizada em dados reais do atleta — nunca genérica. Falha de dados → retorna resposta padrão: "Desculpa, não consegui acessar seus dados de treino agora. Tente novamente!" | `generateCoachResponse` endpoint | D-UI-21, G-06 | Garante inteligência contextual baseada em Feature Store, não LLM genérico |
| DR-TRAIN-COACH-09 | Conversa de chat é somente-leitura (archived=true) se: (a) atleta a fecha manualmente, (b) inatividade > 30 dias. Conversas arquivadas não deletadas — consultáveis em auditoria e relatórios | `athlete_chat_conversation` | Necessidade audit | Garante rastreabilidade histórica |

---

## Prioridade de verdade (revisada)

