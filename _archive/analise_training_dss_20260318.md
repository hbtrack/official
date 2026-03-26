Análise Arquitetural — ARCH_DECISIONS_TRAINING.md
Módulo: training | Data: 2026-03-16 | Referência: docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md

> **Nota de governança de path:** `ARCH_DECISIONS_TRAINING.md` é tratado nesta análise como explicação consolidada / DSS (Decision Support Source) de módulo — **não** como artefato canônico soberano de módulo. As docs canônicas reconhecidas pela governança para `docs/hbtrack/modulos/<módulo>/` são: `README`, `MODULE_SCOPE`, `DOMAIN_RULES`, `INVARIANTS`, `STATE_MODEL`, `PERMISSIONS`, `ERRORS`, `UI_CONTRACT`, `SCREEN_MAP` e `TEST_MATRIX`. Arquivos fora dessas listas são não-soberanos por padrão, salvo promoção explícita. A precisão do conteúdo de `ARCH_DECISIONS_TRAINING.md` é aproveitada como fonte de raciocínio, mas as afirmações normativas precisam ser materializadas nas docs mínimas de módulo para ter efeito canônico.

Legenda de classificação:

C — Já coberto pelo canon
NO — Decisão nova obrigatória
NI — Decisão nova importante
HI — Hipótese ainda insuficiente
GO — Conflito com governança existente
Tabela Resumo
ID	Título	Classe	ADR necessário
TRAIN-DEC-001	training_session não é a unidade central	C	Não
TRAIN-DEC-002	Módulo orientado a decisão	C	Não
TRAIN-DEC-003	Analytics e IA só recomendam	C	Não
TRAIN-DEC-004	Sessão exige objetivo operacional	C	Não
TRAIN-DEC-005	Objetivo exige origem rastreável	NO	Não — requer DOMAIN_AXIOMS enum
TRAIN-DEC-006	Sessão publicada exige conteúdo mínimo	C	Não
TRAIN-DEC-007	execution_record exige contexto de prescrição	NO	Não — requer schema
TRAIN-DEC-008	planned vs actual é obrigatório	C	Não
TRAIN-DEC-009	Ajuste ao vivo exige motivo estruturado	NI	Não
TRAIN-DEC-010	Feedback é contextual, nunca solto	NO	Não — requer schema Fase 1
TRAIN-DEC-011	Revisão exige evidência de execução	C	Não
TRAIN-DEC-012	Restrição crítica bloqueia ou exige override	C	Não
TRAIN-DEC-013	Sessão COMPLETED é imutável	C	Não
TRAIN-DEC-014	Estados derivados não substituem dados-fonte	C	Não
TRAIN-DEC-015	Conversa técnica gera consequência operacional	C	Não
TRAIN-DEC-016	Dois loops: coletivo e individual	C	Não
TRAIN-DEC-017	Vídeo e playbook são objetos operacionais	NI	Sim — adendo ADR-021
TRAIN-DEC-018	Fricção adaptativa é princípio sistêmico	HI	Não
TRAIN-DEC-019	Aderência é entidade de primeira classe	NI	Não
TRAIN-DEC-020	Edição viva de sessão deve ser suportada	GO	Sim — adendo ADR-017
TRAIN-DEC-021	Continuidade interstaff	C	Não
TRAIN-DEC-022	training não entrega notificação diretamente	C	Não
TRAIN-DEC-023	Auditoria via módulo audit	C	Não
TRAIN-DEC-024	Restrições médicas são somente leitura	C	Não
TRAIN-DEC-025	identity_access governa; training aplica	C	Não
TRAIN-DEC-026	Status de sessão tem máquina fechada	C	Não (≡ ADR-017)
TRAIN-DEC-027	Atenção do treinador deve ser priorizada	NI	Não
TRAIN-DEC-028	Fases de implementação: 1, 2, 3	C	Não
TRAIN-DEC-029	Módulo training = HYBRID persistence	C	Não (≡ ADR-018)
TRAIN-DEC-030	Eventos append-only não eliminam CRUD	C	Não (≡ ADR-018)
TRAIN-DEC-031	session_templates e periodização são CRUD puros	C	Não (≡ ADR-018)
TRAIN-DEC-032	Separação: Domínio ≠ DTO ≠ ViewModel ≠ Props	C	Não (≡ ADR-019)
TRAIN-DEC-033	Domínio não moldado por UI nem provedores	C	Não (≡ ADR-019)
TRAIN-DEC-034	DTO não vaza internos de persistência	C	Não (≡ ADR-019)
TRAIN-DEC-035	ViewModel não oculta distinções canônicas	C	Não (≡ ADR-019)
TRAIN-DEC-036	Dados externos passam pela camada de ingestão	C	Não
TRAIN-DEC-037	observed_at e ingested_at são distintos	C	Não (≡ ADR-018)
TRAIN-DEC-038	Idempotência obrigatória para fatos ingeridos	C	Não (≡ ADR-018)
TRAIN-DEC-039	Wellness consumido por training é domínio sensível	C	Não (≡ ADR-010)
TRAIN-DEC-040	training não expõe sensíveis em endpoints genéricos	C	Não (≡ ADR-010)
TRAIN-DEC-041	Inferências de IA são consultivas	C	Não (≡ ADR-010 + ADR-015)
TRAIN-DEC-042	dropout_risk_signal é derivado	C	Não (≡ ADR-010 + FI-009)
TRAIN-DEC-043	Registros sensíveis sem armazenamento ad hoc	C	Não (≡ ADR-010)
TRAIN-DEC-044	Sessão híbrida: individualization_mode	NO	Não — requer contrato + DOMAIN_AXIOMS
TRAIN-DEC-045	planned vs actual dualidade embedded	C	Não (OD-TRAIN-003 resolvido)
TRAIN-DEC-046	analytics soberano de derived_signal	C	Não (OD-TRAIN-007 resolvido)
TRAIN-DEC-047	exercises é módulo soberano	C	Não (OD-TRAIN-001 resolvido + contratos)
TRAIN-DEC-048	Versionamento pedagógico explícito	C	Não (contratos gerados)
TRAIN-DEC-049	session_block é contrato obrigatório Fase 1	C	Não (contratos gerados)
Detalhamento por decisão
TRAIN-DEC-001 C — training_session não é a unidade central
Avaliação: Declaração de identidade arquitetural do módulo. A unidade soberana é o training_intervention_cycle; training_session é um artefato interno do ciclo. O backbone Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment orienta todos os contratos subsequentes.

Riscos: Sem esta declaração canonizada no módulo, agentes e implementações tendem a modelar o módulo como CRUD de sessão — o "degradation pattern" identificado explicitamente na decisão.

Impacto em artefatos canônicos: A declaração de identidade arquitetural precisa estar materializada em `MODULE_SCOPE_TRAINING.md` (identidade e escopo do módulo) e `DOMAIN_RULES_TRAINING.md` (backbone semântico Need → Objective → Prescription → Session → Execution → Response → Review → Adjustment). `ARCH_DECISIONS_TRAINING.md` serve como fonte de raciocínio (DSS consolidado) mas **não substitui** essas docs canônicas — TRAIN-DEC-001 só tem efeito normativo quando expresso nos artefatos soberanos do módulo. ADR-017 valida implicitamente ao tratar a sessão como componente do ciclo, mas a identidade do módulo precisa estar canonizada em `docs/hbtrack/modulos/training/`.

Necessidade de ADR: Não — é identidade de módulo, não decisão de plataforma. Escopo correto: `docs/hbtrack/modulos/training/MODULE_SCOPE_TRAINING.md`.

Bloqueios aplicáveis: Nenhum de contrato. Pendência de materialização nos artefatos canônicos de módulo.

TRAIN-DEC-002 C — Módulo orientado a decisão, não a cadastro
Avaliação: Extensão filosófica de TRAIN-DEC-001. Todo fluxo nasce de need_detected, goal_gap ou competitive_focus — não de formulário em branco. Fundamental para evitar abandono por "burocracia de preenchimento".

Riscos: Se não internalizado, a UX criará atalhos que permitem sessões sem propósito. Risco de produto, não de contrato.

Impacto em artefatos canônicos: session_objective como campo obrigatório antes de SCHEDULED (reforça TRAIN-DEC-006). Já capturado em INV-TRAIN-001. A orientação a decisão — e não a cadastro — é princípio de identidade do módulo e precisa estar declarada explicitamente em `DOMAIN_RULES_TRAINING.md`, pois é o tipo de afirmação que orienta interpretação futura de contratos e de boundary. Como DSS, `ARCH_DECISIONS_TRAINING.md` captura bem o raciocínio, mas a afirmação normativa só tem efeito canônico quando expressa no artefato soberano de módulo.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum de contrato. Pendência de materialização em `DOMAIN_RULES_TRAINING.md`.

TRAIN-DEC-003 C — Analytics e IA só recomendam; treinador decide
Avaliação: Plenamente coberto por FI-002, FI-008, FI-010, FI-017 (Inferências Globalmente Proibidas). ADR-015 (agent execution log) e ADR-010 (inferências de IA consultivas sobre dados sensíveis) formalizam o princípio de plataforma.

Riscos: Nenhum adicional — já possui múltiplas camadas de proteção via Forbidden Inferences.

Impacto em artefatos canônicos: O campo review_status: pending_human_review obrigatório em inferências de IA consumidas (TRAIN-DEC-041) precisa constar no schema de qualquer entidade que carregue sinais de IA.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-002, FI-008, FI-010, FI-017.

TRAIN-DEC-004 C — Sessão exige objetivo operacional
Avaliação: Coberto por INV-TRAIN-001 (sessão sem session_objective válido é inválida). A condição de PUBLISHED/SCHEDULED exigindo objetivo está em TRAIN-DEC-006 e ADR-017 (transições de estado).

Riscos: O schema de training_session.yaml precisa refletir o requisito — se session_objectives for opcional no schema, a invariante só é enforced em nível de aplicação.

Impacto em artefatos canônicos: training_session.yaml — field sessionObjectives deve ter validação condicional (obrigatório para transição SCHEDULED+). DOMAIN_AXIOMS deve conter enum de session_objective_origin (ver TRAIN-DEC-005).

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum imediato.

TRAIN-DEC-005 NO — Objetivo exige origem rastreável
Avaliação: Regra clara: todo session_objective deve referenciar exatamente uma origem: need_detected, competitive_focus, development_goal, ou manual_coach_rationale. FI-012 proíbe objective sem origem. Porém, o schema de session_objective não existe, e session_objective_origin não está em DOMAIN_AXIOMS.

Riscos: Sem enum fechado em DOMAIN_AXIOMS, CROSS_SPEC_ALIGNMENT_GATE bloqueará o schema quando criado. O campo de origem pode ser implementado como string livre, perdendo rastreabilidade.

Impacto em artefatos canônicos:

.contract_driven/DOMAIN_AXIOMS.json — adicionar enum session_objective_origin: ["NEED_DETECTED", "COMPETITIVE_FOCUS", "DEVELOPMENT_GOAL", "MANUAL_COACH_RATIONALE"]
contracts/schemas/training/session_objective.schema.json — criar (não existe)
contracts/openapi/components/schemas/training/session_objective.yaml — criar
Necessidade de ADR: Não — decisão de domínio de módulo, não de plataforma.

Bloqueios aplicáveis: CROSS_SPEC_ALIGNMENT_GATE — enum sem x-domain-enum-ref bloqueará quando schema for criado. §17 DoD — módulo não estará completo sem schema de session_objective.

TRAIN-DEC-006 C — Sessão publicada exige conteúdo mínimo
Avaliação: Integralmente coberto por ADR-017 (condições de transição DRAFT → SCHEDULED: "Dados mínimos presentes"). INV-TRAIN-005 e INV-TRAIN-018 formalizam os campos mínimos. TRAIN-DEC-026 reforça.

Riscos: O enforcement é lógica de aplicação (guard na transição de estado). O OpenAPI schema de training_session pode não refletir as condições condicionais — isso é aceitável para contratos HTTP, mas deve ser documentado como constraint de servidor.

Impacto em artefatos canônicos: Nenhum novo. O contrato existente em training.yaml para PATCH de sessão deve documentar o guard.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-007 NO — execution_record exige contexto de prescrição
Avaliação: execution_record é entidade central do núcleo operacional de Fase 1 — sem ela, planned vs actual (TRAIN-DEC-045) não funciona, e review_outcome (TRAIN-DEC-011) é inválida. INV-TRAIN-006 referencia execution_record mas a entidade não tem schema JSON nem OpenAPI component.

Riscos: Implementação sem schema gera drift entre domínio e contrato. Campo coach_rationale (obrigatório quando for improviso) pode surgir como string livre irrestrita sem validação. CROSS_SPEC_ALIGNMENT_GATE bloqueará na primeira implementação.

Impacto em artefatos canônicos:

contracts/schemas/training/execution_record.schema.json — criar (bloqueador §17 DoD)
contracts/openapi/components/schemas/training/execution_record.yaml — criar
contracts/openapi/paths/training.yaml — endpoints POST /training-sessions/{id}/execution-records (Fase 1)
.contract_driven/DOMAIN_AXIOMS.json — enum execution_type se diferente dos existentes
Necessidade de ADR: Não — decisão de schema de módulo.

Bloqueios aplicáveis: §17 DoD (módulo incompleto sem domain shape de entidade central de Fase 1). CROSS_SPEC_ALIGNMENT_GATE quando implementado.

TRAIN-DEC-008 C — planned vs actual é obrigatório
Avaliação: Plenamente coberto por TRAIN-DEC-045 (resolução formal de OD-TRAIN-003): planned_content_snapshot imutável na publicação + execution_records append-only. INV-TRAIN-007 formaliza a dualidade.

Riscos: planned_content_snapshot não está no schema atual de training_session.yaml. Sem ele, a dualidade existe na decisão mas não no contrato.

Impacto em artefatos canônicos: contracts/openapi/components/schemas/training/training_session.yaml — adicionar campo plannedContentSnapshot (capturado na transição para PUBLISHED; imutável após). Requer definição de tipo para o snapshot.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum imediato.

TRAIN-DEC-009 NI — Ajuste ao vivo exige motivo estruturado
Avaliação: Regra válida e necessária: todo live_session_adjustment, constraint_override, alternate_exercise, load_recalculation deve registrar motivo em campo estruturado (não texto livre irrestrito). As entidades são Fase 2. INV-TRAIN-008 referencia.

Riscos: Se os schemas de Fase 2 forem criados sem motivo estruturado obrigatório, a regra não terá enforcement. O "campo estruturado" precisa ser especificado: é um enum de razões ou texto livre com reason_code?

Impacto em artefatos canônicos: Nenhum imediato (Fase 2). Quando criados, os schemas de live_session_adjustment e constraint_override precisarão de reason_code com enum em DOMAIN_AXIOMS.

Necessidade de ADR: Não — regra de schema de módulo.

Bloqueios aplicáveis: CROSS_SPEC_ALIGNMENT_GATE (futuro — quando schemas de Fase 2 forem criados sem enum fechado para reason_code).

TRAIN-DEC-010 NO — Feedback é contextual, nunca solto
Avaliação: Princípio coberto por FI-011 (feedback_thread sem conversation_outcome) e OD-TRAIN-002 (resolvido: Fase 1 = reflexão estruturada com outcome). Porém, o schema de feedback_thread / athlete_reflection de Fase 1 não existe. O campo conversation_outcome não tem tipo definido. A reflexão estruturada de Fase 1 (OD-TRAIN-002) exige contrato antes da implementação.

Riscos: Implementação de Fase 1 sem schema cria entidade não contratualizada. feedback_thread pode se tornar texto livre não rastreável.

Impacto em artefatos canônicos:

contracts/schemas/training/feedback_thread.schema.json — criar (Fase 1 scope: reflexão estruturada com outcome obrigatório)
contracts/openapi/components/schemas/training/feedback_thread.yaml — criar
.contract_driven/DOMAIN_AXIOMS.json — enum feedback_context_type (sessão, bloco, objetivo, atleta, evidência) e conversation_outcome_type
Necessidade de ADR: Não — schema de módulo. OD-TRAIN-002 já resolve o scope.

Bloqueios aplicáveis: §17 DoD se feedback_thread for entidade de Fase 1. CROSS_SPEC_ALIGNMENT_GATE quando schema criado.

TRAIN-DEC-011 C — Revisão exige evidência de execução
Avaliação: Coberto por FI-018 (review_outcome sem entidade formal é inválida), INV-TRAIN-011, INV-TRAIN-012. O schema de review_outcome não existe (Fase 2).

Riscos: Revisão de sessão pode ocorrer sem entidade formal — apenas como nota de texto.

Impacto em artefatos canônicos: contracts/schemas/training/review_outcome.schema.json — criar (Fase 2). Nenhum imediato.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum para Fase 1.

TRAIN-DEC-012 C — Restrição crítica bloqueia ou exige override auditado
Avaliação: Integralmente coberto: FI-014 (prescrição a atleta com restrição sem override), FI-019 (restrição quebrada sem restriction_override formal), TRAIN-DEC-024 (boundary com medical), INV-TRAIN-021.

Riscos: restriction_override não tem schema formal (Fase 2). O mecanismo de override pode ser implementado ad hoc.

Impacto em artefatos canônicos: contracts/schemas/training/restriction_override.schema.json — criar (Fase 2). Campos: authorization_level, authorized_by, rationale, audit_event linkado.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-014, FI-019.

TRAIN-DEC-013 C — Sessão COMPLETED é imutável por edição destrutiva
Avaliação: Tripla cobertura: ADR-017 (COMPLETED = Não editável), ADR-018 (HYBRID — fatos históricos imutáveis), FI-007 (COMPLETED não pode ser mutada diretamente). Enforcement via state machine.

Riscos: Nenhum adicional.

Impacto em artefatos canônicos: Nenhum novo. O endpoint PATCH de sessão deve retornar 409/422 para sessões COMPLETED.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-007.

TRAIN-DEC-014 C — Estados derivados não substituem dados-fonte
Avaliação: Coberto por FI-009 (derived_signal não substitui/deleta dados-fonte), TRAIN-DEC-046 (analytics soberano), TRAIN-DEC-042 (dropout_risk_signal é derivado), INV-TRAIN-036.

Riscos: Nenhum adicional.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-009.

TRAIN-DEC-015 C — Conversa técnica gera consequência operacional
Avaliação: Coberto por FI-011 (feedback_thread sem conversation_outcome inválida) e OD-TRAIN-002 (resolvido). As entidades action_commitment, followup_check, conversation_outcome são Fase 3 (conversação multi-turno). Fase 1 cobre apenas reflexão estruturada com outcome (ver TRAIN-DEC-010).

Riscos: "Consequência operacional" é ampla — o que conta como consequência em Fase 1? Precisa ser especificado no schema de Fase 1 de feedback_thread.

Impacto em artefatos canônicos: Nenhum novo além do schema de feedback_thread (TRAIN-DEC-010). Entidades de Fase 3 não têm contratos.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-011.

TRAIN-DEC-016 C — Dois loops: coletivo e individual
Avaliação: TRAIN-DEC-044 resolve com o modelo individualization_mode — um único tipo de sessão com atributo de individualização. O modelo unificado é mais limpo do que dois tipos-entidade.

Riscos: individualization_mode não está no schema atual de training_session.yaml (ver TRAIN-DEC-044 → NO).

Impacto em artefatos canônicos: Dependente de TRAIN-DEC-044.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum direto.

TRAIN-DEC-017 NI — Vídeo e playbook são objetos operacionais, não anexos
Avaliação: A intenção é correta — mídia (video_clip, diagram, playbook_pattern, coaching_cue) deve ter contexto operacional vinculado a session_objective, session_block, exercise_variant, etc. Porém, ADR-021 (Media Delivery Boundary) foi emitido apenas para exercises. Não há política de mídia para training. Sem política, implementações podem: (a) embutir URLs transitórias no session_block, (b) replicar o objeto Exercise com mídia própria, (c) criar armazenamento ad hoc.

Riscos: Violação de ADR-021 por analogia — training adquirindo campos de mídia sem política explícita. Acoplamento de session_block a CDN/storage. Risco médio para Fase 2.

Impacto em artefatos canônicos:

docs/_canon/decisions/ADR-021-media-delivery-boundary.md — atualizar ou emitir ADR-022 para estender a política ao contexto training
Definir entidade coaching_media_ref (referência estável a asset de mídia, não binário)
Necessidade de ADR: Sim — ADR-021 adendo ou ADR-022 estendendo a media delivery boundary para training. Sem isso, ADR-021 §5 (critério de revisão de contrato) não cobre training.

Bloqueios aplicáveis: ADR-021 §5 se contratos de training adquirirem campos de mídia sem política formal. Aplicável para Fase 2 — não imediato.

TRAIN-DEC-018 HI — Fricção adaptativa é princípio sistêmico
Avaliação: O princípio é válido (estado normal → fluxo mínimo; risco/anomalia → sistema expande). Porém falta completamente: (1) definição de "estado normal" — quais campos indicam risco/anomalia? (2) quais perguntas são expandidas? (3) quem aciona a expansão (wellness? training? UI?). (4) qual é o protocolo de voltar ao fluxo mínimo? INV-TRAIN-025/026 são referenciadas mas não li o conteúdo — e mesmo que existam, a lógica de adaptação não está contrátil.

Riscos: Implementação ad hoc de "fricção" que não é testável ou auditável. A afirmação "questionário sem uso explícito downstream não é permitido" (TRAIN-DEC-018) não tem enforcement possível sem definição.

Impacto em artefatos canônicos: Nenhum — a decisão não está madura o suficiente para impactar artefatos.

Necessidade de ADR: Não — precisa primeiro de especificação de domínio suficiente para virar decisão formal.

Bloqueios aplicáveis: Nenhum para Fase 1. Para Fase 2, qualquer contrato que implemente "fricção adaptativa" precisará de lógica especificada.

TRAIN-DEC-019 NI — Aderência é entidade de primeira classe
Avaliação: A definição ampla de aderência (adherence_status, miss_reason, partial_completion, reschedule_window, consistency_streak, engagement_signal, dropout_risk_signal) é importante. Atenção: engagement_signal e dropout_risk_signal são soberanos de analytics (TRAIN-DEC-046) — portanto adherence no módulo training inclui apenas os dados-fonte, não os sinais derivados.

Riscos: Sem contrato, adherence pode ser implementado como campos avulsos em execution_record ou training_session, perdendo a identidade de entidade de primeira classe. miss_reason pode vir como string livre em vez de enum fechado.

Impacto em artefatos canônicos:

.contract_driven/DOMAIN_AXIOMS.json — enum miss_reason_type, adherence_status_type
contracts/schemas/training/adherence_record.schema.json — criar (Fase 2)
Necessidade de ADR: Não — schema de módulo.

Bloqueios aplicáveis: Nenhum para Fase 1. CROSS_SPEC_ALIGNMENT_GATE quando schema criado.

TRAIN-DEC-020 GO — Edição viva de sessão deve ser suportada
Avaliação: Esta decisão conflita latentemente com ADR-017. ADR-017 define IN_PROGRESS → Não (bloqueado) na coluna "Editável?". TRAIN-DEC-020 diz que live_session_adjustment, alternate_exercise, constraint_override, load_recalculation devem ser suportados durante a sessão — o que implica escrita em um estado que ADR-017 marca como bloqueado para edição.

A tensão não é irresolvível: ADR-017 provavelmente quer dizer que a estrutura do agregado (training_session principal) é imutável em IN_PROGRESS, mas registros de ajuste são novos objetos (append-only) — não edições destrutivas. Porém isso nunca foi formalizado e cria risco de interpretação divergente entre implementações.

Riscos: Um implementador lê ADR-017 ("IN_PROGRESS = Não editável") e bloqueia qualquer escrita na sessão. Outro lê TRAIN-DEC-020 e permite edição livre. Sem resolução formal, ambos estão "corretos" segundo documentos existentes. Duas fontes canônicas no mesmo nível dizem coisas incompatíveis — o bloqueio é formal e ativo, não preventivo.

Impacto em artefatos canônicos:

docs/_canon/decisions/ADR-017-training-session-state-machine.md — adicionar adendo formal distinguindo: "Não editável em IN_PROGRESS refere-se ao agregado estrutural de training_session. Registros de ajuste ao vivo (live_session_adjustment, alternate_exercise, constraint_override) são objetos append-only e seguem o padrão ADR-018 HYBRID — NÃO são edições destrutivas do agregado." Essa clarificação resolve o conflito sem criar novo ADR, mas precisa ser o primeiro artefato normativo atualizado antes de qualquer contrato de ajuste ao vivo.
Necessidade de ADR: Sim — adendo formal a ADR-017 é obrigatório. Sem ele, o conflito não tem resolução canônica e impede a abertura de qualquer endpoint de ajuste ao vivo.

Bloqueios aplicáveis: **BLOCKED_CONTRACT_CONFLICT** ativo entre ADR-017 e TRAIN-DEC-020 para qualquer implementação de ajuste ao vivo em IN_PROGRESS. O adendo a ADR-017 deve preceder a abertura dos contratos.

TRAIN-DEC-021 C — Continuidade interstaff é responsabilidade do módulo
Avaliação: OPEN-004 resolvido formalmente (2026-03-16): continuityNotes (string, maxLength 2000) em training_session para Fase 1. staff_handoff como entidade própria diferida para DEFER-TRAIN-P3-003.

Riscos: continuityNotes precisa estar no schema de training_session.yaml. Se não estiver, a resolução de OPEN-004 é apenas documental.

Impacto em artefatos canônicos: training_session.yaml — verificar se continuityNotes foi adicionado ao schema. Entidades de Fase 3 (observation_log, continuity_snapshot) sem contratos — correto.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-022 C — training não entrega notificação diretamente
Avaliação: Coberto por FI-004, INV-TRAIN-039, Boundary Map formal. O pattern training → emit notification_intent → notifications → entrega é canônico no Boundary Map do próprio documento.

Riscos: O formato de notification_intent não tem schema formal — pode ser implementado de forma inconsistente.

Impacto em artefatos canônicos: Schema de notification_intent é responsabilidade do módulo notifications, não de training.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-004.

TRAIN-DEC-023 C — Auditoria via módulo audit, não interna
Avaliação: Coberto por FI-005, INV-TRAIN-040, Boundary Map. Pattern: training → emit audit_event → audit.

Riscos: O schema de audit_event emitido por training não está especificado — implementação pode ser inconsistente com o que audit espera.

Impacto em artefatos canônicos: Schema de audit_event é responsabilidade do módulo audit.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-005.

TRAIN-DEC-024 C — Restrições médicas são somente leitura operacional
Avaliação: Coberto por FI-001, INV-TRAIN-014, INV-TRAIN-037, Boundary Map. medical é soberano; training consome read-only.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-001.

TRAIN-DEC-025 C — identity_access governa permissão; training aplica
Avaliação: Coberto por ADR-008 (authz strategy de plataforma), FI-006, INV-TRAIN-041.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-006.

TRAIN-DEC-026 C — Status de sessão tem máquina de estados fechada
Avaliação: ADR-017 é o canon de plataforma que promove, expande e resolve conflitos de TRAIN-DEC-026. A state machine de 7 estados está completamente formalizada.

Necessidade de ADR: Não — já é ADR-017.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-027 NI — Atenção do treinador deve ser finita e priorizada
Avaliação: attention_queue com campos obrigatórios severity, reason, target_entity é uma entidade de domínio sem schema. FI-013 proíbe items sem esses campos. INV-TRAIN-027 referencia. OPEN-005 menciona que INV-TRAIN-083 cria um item de baixa severidade na attention_queue — o que confirma que a entidade é Fase 1 (mesmo que limitada).

Riscos: INV-TRAIN-083 (Elastic Sum Rule) já gera items de attention_queue. Sem schema, o formato do item é ad hoc. FI-013 não pode ser enforced sem tipo definido.

Impacto em artefatos canônicos:

.contract_driven/DOMAIN_AXIOMS.json — enum attention_queue_severity (LOW, MEDIUM, HIGH, CRITICAL) e attention_queue_reason_code
contracts/schemas/training/attention_queue_item.schema.json — criar
contracts/openapi/components/schemas/training/attention_queue_item.yaml — criar
Necessidade de ADR: Não — schema de módulo.

Bloqueios aplicáveis: FI-013. INV-TRAIN-083 já produz items — schema bloqueador imediato para completar a implementação de TRAIN-DEC-049.

TRAIN-DEC-028 C — Fases de implementação: 1, 2, 3
Avaliação: Roadmap já integrado ao MODULE_DECISION_IR.json via DEFER-TRAIN-P2-* e DEFER-TRAIN-P3-*. O documento ARCH_DECISIONS_TRAINING.md documenta as capacidades por fase.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-029 C — Módulo training = HYBRID persistence
Avaliação: ADR-018 promove explicitamente TRAIN-DEC-029 e define os 10 critérios obrigatórios para classificar dado como append-only.

Necessidade de ADR: Não — já é ADR-018.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-030 C — Eventos append-only não eliminam o agregado CRUD
Avaliação: ADR-018 promove TRAIN-DEC-030. Importante: ADR-018 lista explicitamente session_block, session_objective como CRUD — não append-only.

Necessidade de ADR: Não — já é ADR-018.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-031 C — session_templates e planning_periodization são CRUD puros
Avaliação: ADR-018 promove TRAIN-DEC-031. Nota: arquivos mesocycle.yaml e microcycle.yaml aparecem como ?? (untracked) no git status — existem mas não foram commitados. Devem ser schemas de Fase 2.

Riscos: mesocycle.yaml e microcycle.yaml untracked podem conter tokens de template não resolvidos (PLACEHOLDER_RESIDUE_GATE).

Impacto em artefatos canônicos: Verificar e commitar os schemas de mesocycle/microcycle após validação de gates.

Necessidade de ADR: Não.

Bloqueios aplicáveis: PLACEHOLDER_RESIDUE_GATE (se contiverem tokens {{...}}). DERIVED_DRIFT_GATE (se adicionados sem recompilação de manifests).

TRAIN-DEC-032 a TRAIN-DEC-035 C — Separação de camadas
Avaliação: Quatro decisões integralmente promovidas para ADR-019 (Separação Estrita de Camadas — Domain / DTO / ViewModel / Props). ADR-019 cita explicitamente cada uma. O fluxo canônico obrigatório está definido.

Riscos: Nenhum canônico. O risco é de implementação (DTOs inflados, model impuro) — mitigado pelo ADR.

Necessidade de ADR: Não — já é ADR-019.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-036 C — Dados externos passam pela camada de ingestão
Avaliação: Coberto pela política de plataforma INGESTION_PROVIDER_CONTRACT.md (referenciada em ADR-018). Os campos obrigatórios de ingestão estão especificados na própria decisão.

Riscos: A camada de ingestão para training não tem contrato OpenAPI. source_type enum não está em DOMAIN_AXIOMS.

Impacto em artefatos canônicos: DOMAIN_AXIOMS.json — verificar se enum source_type existe para os valores listados (manual_coach_entry, csv_import, sensor_device, etc.).

Necessidade de ADR: Não.

Bloqueios aplicáveis: CROSS_SPEC_ALIGNMENT_GATE (futuro — quando endpoint de ingestão for criado com enum source_type sem x-domain-enum-ref).

TRAIN-DEC-037 C — observed_at e ingested_at são distintos
Avaliação: ADR-018 seção "Distinção obrigatória de timestamps" formaliza exatamente: "observed_at — quando o fato ocorreu no mundo real; ingested_at — quando o HB Track recebeu o registro."

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-038 C — Idempotência obrigatória para fatos ingeridos
Avaliação: ADR-018 critério 4 nos "Critérios obrigatórios para append-only": "Idempotência está definida (dedupe_key ou idempotency_key)."

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-039 a TRAIN-DEC-043 C — Governança de dados sensíveis
Avaliação: Grupo de 5 decisões integralmente coberto por ADR-010 (Classificação de Dados Sensíveis), atualizado em 2026-03-16 especificamente para incorporar TRAIN-DEC-039/040/041. ADR-010 define: sub-classes PHI esportivas (sensitive_health_adjacent, sensitive_psychological), níveis de access_classification (restricted_coaching, restricted_medical, public_aggregate), política de endpoints genéricos, autoridade consultiva de IA.

TRAIN-DEC-042: Coberto por FI-009 + ADR-010
TRAIN-DEC-043: Coberto por ADR-010 (PHI soberano de wellness; training referencia)
Riscos: Os campos de wellness que training referencia (como readiness_snapshot_ref) não têm schema formal em training ainda.

Necessidade de ADR: Não — já é ADR-010.

Bloqueios aplicáveis: ADR-010 enforcement via contrato (PHI_AUTHORIZED obrigatório para endpoints que expõem dados PHI).

TRAIN-DEC-044 NO — Sessão híbrida: individualization_mode
Avaliação: OPEN-001 resolvido formalmente. O modelo individualization_mode (COLLECTIVE_UNIFORM, COLLECTIVE_WITH_VARIANTS, INDIVIDUAL_ONLY) é a decisão correta e está documentada. Porém: (1) o enum não está em DOMAIN_AXIOMS.json, (2) o campo individualization_mode não está em training_session.yaml, (3) a entidade block_athlete_variant não tem schema.

Riscos: Implementação criará o campo como string livre. CROSS_SPEC_ALIGNMENT_GATE bloqueará. O modo COLLECTIVE_WITH_VARIANTS requer block_athlete_variant — implementação ad hoc sem schema.

Impacto em artefatos canônicos:

.contract_driven/DOMAIN_AXIOMS.json — adicionar enum individualization_mode: ["COLLECTIVE_UNIFORM", "COLLECTIVE_WITH_VARIANTS", "INDIVIDUAL_ONLY"]
contracts/openapi/components/schemas/training/training_session.yaml — adicionar campo individualizationMode com x-domain-enum-ref
contracts/schemas/training/training_session.schema.json — atualizar
contracts/openapi/components/schemas/training/block_athlete_variant.yaml — criar (Fase 2)
Recompilar manifests após DOMAIN_AXIOMS atualizado
Necessidade de ADR: Não — resolução de OPEN-001 já documentada.

Bloqueios aplicáveis: CROSS_SPEC_ALIGNMENT_GATE (enum sem x-domain-enum-ref). DERIVED_DRIFT_GATE (após atualização de DOMAIN_AXIOMS).

TRAIN-DEC-045 C — planned vs actual dualidade embedded
Avaliação: OD-TRAIN-003 resolvido formalmente. planned_content_snapshot (imutável na publicação) + execution_records (append-only). Comparação sempre query derivada. Granularidade de Fase 1: nível de sessão.

Riscos: planned_content_snapshot não está no schema atual de training_session.yaml. Sem ele, o snapshot de "o que foi planejado" não é capturado na publicação.

Impacto em artefatos canônicos: training_session.yaml — adicionar campo plannedContentSnapshot (write-once na transição PUBLISHED). Tipo: inline object ou referência a schema.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum imediato. Sem o campo, INV-TRAIN-007 não pode ser enforced.

TRAIN-DEC-046 C — analytics soberano de derived_signal
Avaliação: OD-TRAIN-007 resolvido formalmente. TRAIN-DEC-046 bem documentado: analytics produz, training consome read-only com proveniência completa (model_name, model_version, confidence_level, computed_at). Fase 2: trigger_event → analytics recalcula.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum.

TRAIN-DEC-047 C — exercises é módulo soberano
Avaliação: OD-TRAIN-001 resolvido. Contratos gerados: ExerciseId e ExerciseVersionId em CANONICAL_TYPE_REGISTRY, x-semantic-id em session_block.yaml. FI-020 e FI-021 formalizam as invariantes derivadas.

Necessidade de ADR: Não. ADR-021 complementa para boundary de mídia.

Bloqueios aplicáveis: FI-020, FI-021.

TRAIN-DEC-048 C — Versionamento pedagógico explícito
Avaliação: Contratos gerados. exercise_version.schema.json com append-only semântica (sem updatedAt). session_block.yaml com if/then para exerciseVersionId obrigatório quando exerciseId presente.

Necessidade de ADR: Não.

Bloqueios aplicáveis: FI-021.

TRAIN-DEC-049 C — session_block é contrato obrigatório Fase 1
Avaliação: Totalmente formalizado. Contratos gerados: session_block.yaml, session_block.schema.json, 6 endpoints em training.yaml. INV-TRAIN-083 (Elastic Sum Rule) formalizado e documentado no schema com comment.

Necessidade de ADR: Não.

Bloqueios aplicáveis: Nenhum — contratos existem e passaram pelos gates.

Síntese Executiva
Distribuição de classificações
Classe	Qtd	IDs
C Coberto pelo canon	38	001–004, 006, 008, 011–016, 021–026, 028–031, 032–035, 036–043, 045–049
NO Nova obrigatória	4	005, 007, 010, 044
NI Nova importante	5	009, 017, 019, 020*, 027
HI Hipótese insuficiente	1	018
GO Conflito de governança	1*	020
*TRAIN-DEC-020 é classificado como NI+GO — é uma decisão importante com conflito latente com ADR-017.

Ações bloqueadoras (executar antes de implementar Fase 1)
Prioridade	Ação	Decisão	Artefato
P0	Adicionar session_objective_origin ao DOMAIN_AXIOMS	TRAIN-DEC-005	.contract_driven/DOMAIN_AXIOMS.json
P0	Criar session_objective.schema.json e .yaml	TRAIN-DEC-005	contracts/schemas/training/, contracts/openapi/components/schemas/training/
P0	Criar execution_record.schema.json e .yaml	TRAIN-DEC-007	Idem
P0	Criar feedback_thread.schema.json e .yaml	TRAIN-DEC-010	Idem
P0	Adicionar individualization_mode ao DOMAIN_AXIOMS + training_session.yaml	TRAIN-DEC-044	DOMAIN_AXIOMS + training_session.yaml
P1	Adicionar nota a ADR-017 clarificando "não editável" vs ajustes ao vivo	TRAIN-DEC-020	ADR-017
P1	Criar attention_queue_item.schema.json + enums em DOMAIN_AXIOMS	TRAIN-DEC-027	DOMAIN_AXIOMS + schemas
P1	Adicionar plannedContentSnapshot a training_session.yaml	TRAIN-DEC-045	training_session.yaml
P2	Emitir adendo a ADR-021 para mídia em training	TRAIN-DEC-017	ADR-021 ou ADR-022
Decisões a diferir formalmente (Fase 2+)
Decisão	Entidade diferida	Fase
TRAIN-DEC-009	live_session_adjustment, constraint_override, alternate_exercise	2
TRAIN-DEC-011	review_outcome	2
TRAIN-DEC-012	restriction_override	2
TRAIN-DEC-017	video_clip, playbook_pattern, coaching_cue, diagram	2
TRAIN-DEC-019	adherence_record	2
TRAIN-DEC-027	attention_queue completa	2
TRAIN-DEC-018	Fricção adaptativa (especificar antes de implementar)	2/3
TRAIN-DEC-015	action_commitment, followup_check, conversação multi-turno	3
Conflito formal a resolver
**BLOCKED_CONTRACT_CONFLICT** ativo: ADR-017 classifica IN_PROGRESS como "Não (bloqueado)" para edição; TRAIN-DEC-020 exige suporte a live_session_adjustment durante a sessão. São duas fontes canônicas no mesmo nível com afirmações incompatíveis — o bloqueio é ativo e formalmente registrado. O conflito é resolvível com adendo a ADR-017 esclarecendo que "imutabilidade do agregado" ≠ "proibição de registros de ajuste append-only". O adendo a ADR-017 **precede obrigatoriamente** qualquer abertura de contrato ou endpoint de ajuste ao vivo.

