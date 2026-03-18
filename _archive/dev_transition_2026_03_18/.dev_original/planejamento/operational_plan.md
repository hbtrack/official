Avaliação Arquitetural — ARCH_DECISIONS_TRAINING.md (46 decisões)
Data de avaliação: 2026-03-16

Papel: Arquiteto HB Track

Referência: ARCH_DECISIONS_TRAINING.md (promoted_at 2026-03-15)

ESTADO GERAL
O módulo training tem uma base arquitetural sólida e coerente. O documento de 46 decisões está bem estruturado e internamente consistente. O trabalho desta sessão (ADR-017, wellness endpoints, periodization, schemas) já instalou parte não trivial. O problema principal não é a qualidade das decisões — é que a maioria ainda existe apenas como texto normativo sem correspondente canônico em invariantes, contrato ou schema.

CATEGORIA 1 — JÁ INSTALADAS (refletidas em artefatos canônicos)
Essas decisões estão efetivamente instaladas após o trabalho desta sessão:

Decisão	O que instalou	Artefato
TRAIN-DEC-026	FSM 7 estados + ADR-017	DOMAIN_AXIOMS.json, training_session.yaml, training.yaml
TRAIN-DEC-029/030/031	HYBRID classification, agregado CRUD + fatos append-only	Decisão documentada no ARCH_DECISIONS_TRAINING.md; boundary está claro
TRAIN-DEC-032/033/034/035	Separação Domain/DTO/ViewModel/Props	Política de arquitetura; refletida em como os schemas foram criados (sem internos de BD)
TRAIN-DEC-039/040	Wellness como domínio sensível; não exposto em endpoints genéricos	wellness_pre.yaml, wellness_post.yaml têm endpoints dedicados; campos em training_session.yaml não incluem campos sensíveis raw
TRAIN-DEC-044	individualization_mode como enum em sessão	Identificado — falta campo no schema (ver Cat. 2)
TRAIN-DEC-045	planned_content_snapshot imutável + execution_records append-only	Arquitetura definida; Fase 1 campos (durationPlannedMinutes, durationActualMinutes) existem no schema
TRAIN-DEC-046	analytics soberano de derived signals	Boundary documentado; training não tem campos de cálculo de sinal
TRAIN-DEC-022/023/024/025	Boundaries formais (notifications, audit, medical, identity_access)	Documentados; refletidos na tabela de boundaries
TRAIN-DEC-036/037/038	Camada de ingestão obrigatória; observed_at ≠ ingested_at; idempotência	Decisão documentada
TRAIN-DEC-041/042/043	IA consultiva; derived signals não são fonte primária; sem ad hoc sensível	Boundary documentado
Total instalado: ~18 decisões (39%) — em nível de documentação e/ou contrato parcial.

CATEGORIA 2 — INSTALAÇÃO IMEDIATA NECESSÁRIA (Fase 1 ativa)
Essas decisões têm impacto direto no contrato e schemas da Fase 1 e precisam ser instaladas agora:

2A — Campos ausentes em training_session.yaml
TRAIN-DEC-004/005 — Objetivo operacional obrigatório:

mainObjective existe no schema mas é string livre.
Falta: campo objectiveOrigin com enum canônico: NEED_DETECTED | COMPETITIVE_FOCUS | DEVELOPMENT_GOAL | MANUAL_COACH_RATIONALE (FI-012 proíbe objetivo sem origem)
Ação: Adicionar objectiveOrigin ao schema + invariante INV-TRAIN-002 verificável.
TRAIN-DEC-006 — Conteúdo mínimo para PUBLISHED:

teamId e createdByUserId existem, mas sessionType está como string livre sem validação de "coach_assignment" explícito.
Falta: constraint de guarda de publicação documentada em invariante contratual — atualmente INV-TRAIN-005/018 existem no INVARIANTS_TRAINING.md mas não há campo coachAssignmentId no schema.
Ação: Avaliar se createdByUserId serve como coachAssignmentId ou se são distintos. Se distintos, adicionar campo.
TRAIN-DEC-044 — individualization_mode:

O enum foi decidido (COLLECTIVE_UNIFORM | COLLECTIVE_WITH_VARIANTS | INDIVIDUAL_ONLY) mas não existe em training_session.yaml.
x-domain-enum-ref será necessário; portanto o enum precisa entrar em DOMAIN_AXIOMS.json também.
Ação: Adicionar individualization_mode como required ao schema + enum ao DOMAIN_AXIOMS.json + x-domain-enum-ref.
TRAIN-DEC-045 — planned_content_snapshot:

Fase 1 manda planned_duration_min vs actual_duration_min — ambos já existem (durationPlannedMinutes, durationActualMinutes). ✓
Falta campo plannedLoadTarget separado de plannedLoad (o schema tem plannedLoad que serve como planejado e actualLoadRecorded ainda não existe).
Ação: Adicionar actualLoadRecorded ao schema (integer, 0-32767) para completar a dualidade de Fase 1.
TRAIN-DEC-009/020 — Ajuste ao vivo e live editing:

Falta: deviationJustification existe no schema. ✓
planningDeviationFlag existe. ✓
Falta: liveAdjustmentReason como campo estruturado (enum), não texto livre.
Ação: Considerar se deviationJustification (string) é suficiente ou se precisa de enum de adjustmentReason.
TRAIN-DEC-027 — attention_queue com severity/reason/target:

Nenhum endpoint ou schema para attention_queue_item existe.
Fase 1 não requer atenção_queue completa (ver TRAIN-DEC-028: Fase 2 item).
Ação: Diferir para Fase 2. Documentar como open item.
2B — Enum ausente em DOMAIN_AXIOMS.json
Enum	Decisão	Valores
training_session_type	TRAIN-DEC-004	precisa ser definido ou mantido como string aberta — avaliar
individualization_mode	TRAIN-DEC-044	COLLECTIVE_UNIFORM, COLLECTIVE_WITH_VARIANTS, INDIVIDUAL_ONLY
objective_origin	TRAIN-DEC-005	NEED_DETECTED, COMPETITIVE_FOCUS, DEVELOPMENT_GOAL, MANUAL_COACH_RATIONALE
session_block_type	TRAIN-DEC-006	precisa ser definido para validar "bloco mínimo"
source_type	TRAIN-DEC-036	7 valores canônicos listados na decisão
restriction_override_authorization_level	FI-019	precisa ser definido para override auditado
Ação imediata: individualization_mode entra em DOMAIN_AXIOMS.json agora (bloqueia schema). Os demais são dependentes de entidades ainda não contratualizadas (Fase 1 vs Fase 2).

2C — Endpoints ausentes em Fase 1
Funcionalidade	Decisão	Status
POST /training-sessions/{id}/start (SESSION_STARTED event)	TRAIN-DEC-029	Ausente — necessário para HYBRID append-only
POST /training-sessions/{id}/complete (SESSION_COMPLETED event)	TRAIN-DEC-029	Ausente — necessário para transição IN_PROGRESS → COMPLETED
POST /training-sessions/{id}/cancel (motivo estruturado)	TRAIN-DEC-013	Ausente — apenas PATCH status existe; precisa de cancellationReason estruturado
POST /training-sessions/{id}/attendance (presence_registered)	TRAIN-DEC-029	Ausente — fato append-only de presença
GET /training-sessions/{id}/attendance	TRAIN-DEC-016	Ausente — loop coletivo de presença
Ação: Esses 5 endpoints são Fase 1 obrigatórios pelo TRAIN-DEC-028. O endpoint de wellness-pre/post foi adicionado — os de presença e lifecycle transitions são equivalentemente críticos.

CATEGORIA 3 — INVARIANTES PENDENTES (INV-TRAIN referenciadas mas não verificáveis via contrato)
O ARCH_DECISIONS_TRAINING.md referencia invariantes que precisam ser checadas no INVARIANTS_TRAINING.md. As seguintes são citadas em decisões Fase 1 e precisam ter enforcement contratual (campo obrigatório, enum fechado ou regra de validação):

INV	Decisão	Estado atual estimado	Ação
INV-TRAIN-001	TRAIN-DEC-001/002/004	Existe	Verificar se inclui objectiveOrigin
INV-TRAIN-002	TRAIN-DEC-002/005	Existe	Verificar cobertura de objectiveOrigin enum
INV-TRAIN-005	TRAIN-DEC-006	Existe	Verificar se cobre coachAssignmentId
INV-TRAIN-007	TRAIN-DEC-008/045	Existe	Verificar se especifica actualLoadRecorded como mandatório em COMPLETED
INV-TRAIN-008	TRAIN-DEC-009/020	Existe	Verificar se deviationJustification é obrigatório quando planningDeviationFlag=true
INV-TRAIN-035	TRAIN-DEC-016/044	Existe	Precisa ser atualizado para especificar individualization_mode
INV-TRAIN-036	TRAIN-DEC-014/046	Existe	Verificar especificação de boundary analytics
INV-TRAIN-039	TRAIN-DEC-022	Existe	Notificação via intent; sem endpoint direto
INV-TRAIN-040	TRAIN-DEC-023	Existe	Auditoria via evento; sem tabela interna
CATEGORIA 4 — FASE 2 (DIFERIR — não instalar agora)
Decisão	Capacidade	Por que diferir
TRAIN-DEC-017	Vídeo/playbook como objetos operacionais	TRAIN-DEC-028 Fase 2 explicitamente
TRAIN-DEC-018	Fricção adaptativa em check-ins	Depende de módulo wellness avançado
TRAIN-DEC-019	Aderência como entidade (dropout_risk_signal, engagement_signal)	Depende de TRAIN-DEC-046 (analytics Phase 2)
TRAIN-DEC-021	Continuidade interstaff (staff_handoff, continuity_snapshot)	TRAIN-DEC-028 Fase 3
TRAIN-DEC-027	attention_queue completa	TRAIN-DEC-028 Fase 2
OD-TRAIN-001	exercises como módulo separado	Open, sem contrato definido
OPEN-004	staff_handoff como entidade própria	Baixo impacto, Fase 3
OPEN-005	Tolerância de duração de blocos vs sessão	Bloqueia Fase 2, não Fase 1
CATEGORIA 5 — DECISÕES QUE PRECISAM DE ADR FORMAL NO SISTEMA
Essas decisões têm peso cross-module e deveriam ser promovidas para ADRs globais (não apenas módulo training):

Decisão	ADR sugerido	Razão
TRAIN-DEC-029	ADR-018: HYBRID persistence pattern	Aplicável a qualquer módulo com estado + fatos históricos
TRAIN-DEC-032	ADR-019: Layer separation (Domain/DTO/ViewModel/Props)	Política de plataforma, não módulo
TRAIN-DEC-036	ADR-020: Ingestion layer mandatory	Política de plataforma para dados externos
TRAIN-DEC-039	Faz parte ADR-010 (sensitive data policy)	Verificar se ADR-010 cobre sensitive_health_adjacent + restricted_coaching
TRAIN-DEC-041	Faz parte ADR-015 (agent execution log)	IA consultiva é princípio de plataforma
DECISÕES ABERTAS PENDENTES DE RESOLUÇÃO
ID	Questão	Impacto	Recomendação
OD-TRAIN-001	exercises como módulo separado ou submódulo	Médio — afeta session_block schema	Módulo separado; training só referencia exerciseId (UUID)
OD-TRAIN-002	feedback_thread: async vs reflexão estruturada	Baixo Fase 1	Fase 1: campo coachNotes / athleteReflection simples; Fase 3: multi-turno
OD-TRAIN-006	athlete_feedback: resposta única vs multi-turno	Baixo Fase 1	Idem OD-TRAIN-002
OPEN-004	staff_handoff: entidade própria vs campo	Baixo	Fase 3: coach_annotation como campo em training_session; staff_handoff como snapshot de Fase 3
OPEN-005	Tolerância duração blocos vs sessão total	Bloqueia INV-TRAIN-034	Definir regra: SUM(block.durationMinutes) ≤ session.durationPlannedMinutes * 1.1
PRIORIDADE DE INSTALAÇÃO — PRÓXIMAS AÇÕES
Bloco A — Instalar agora (unblocking Fase 1):

individualization_mode → DOMAIN_AXIOMS.json (enum) + training_session.yaml (campo required)
objectiveOrigin → DOMAIN_AXIOMS.json (enum objective_origin) + training_session.yaml (campo)
actualLoadRecorded → training_session.yaml (campo integer, par de plannedLoad)
Endpoints lifecycle: POST /{id}/start, POST /{id}/complete, POST /{id}/cancel, POST /{id}/attendance, GET /{id}/attendance → training.yaml
Verificar INVARIANTS_TRAINING.md — confirmar INV-TRAIN-007/008/035 estão atualizados pós-TRAIN-DEC-045/044
Bloco B — Instalar em paralelo (não bloqueiam Fase 1):

Promover TRAIN-DEC-029 para ADR-018 (HYBRID pattern)
Promover TRAIN-DEC-032 para ADR-019 (layer separation)
Verificar ADR-010 cobre as classes sensíveis de TRAIN-DEC-039
Bloco C — Diferir explicitamente:

Registrar OPEN-004, OPEN-005, OD-TRAIN-001 como decisões abertas formais no sistema de governança
Documentar Fase 2 e Fase 3 como escopo futuro com IDs de referência
VEREDICTO GERAL
O documento está completo e instalável como normativo. As 46 decisões são coerentes entre si, não há contradições internas e o alinhamento com o que foi construído nesta sessão é alto.

O gap real: 8 campos e 5 endpoints Fase 1 ausentes, mais 3 enums não canonizados no DOMAIN_AXIOMS. Tudo solucionável no Bloco A acima.


Bloco A concluído. Gates: 22/22 PASS.

O que foi instalado
DOMAIN_AXIOMS.json — 2 novos enums canônicos:

individualization_mode: COLLECTIVE_UNIFORM | COLLECTIVE_WITH_VARIANTS | INDIVIDUAL_ONLY (TRAIN-DEC-044)
objective_origin: NEED_DETECTED | COMPETITIVE_FOCUS | DEVELOPMENT_GOAL | MANUAL_COACH_RATIONALE (TRAIN-DEC-005)
training_session.yaml — 3 novos campos:

individualizationMode — required, x-domain-enum-ref: individualization_mode
objectiveOrigin — opcional, x-domain-enum-ref: objective_origin; obrigatório quando mainObjective está presente (INV semântica)
actualLoadRecorded — integer 0-32767; par canônico de plannedLoad (TRAIN-DEC-045 Fase 1)
training.yaml — 5 novos endpoints de Fase 1:

POST /{id}/start — transição para IN_PROGRESS + SESSION_STARTED fact
POST /{id}/complete — transição para COMPLETED + SESSION_COMPLETED fact + dualidade planejado/realizado obrigatória
POST /{id}/cancel — cancelamento estruturado com cancellationReason obrigatório
GET /{id}/attendance — lista presença (provisional até complete)
POST /{id}/attendance — registra presence_registered fact com status enum, source, correctionByUserId, observedAt
INVARIANTS_TRAINING.md:

INV-TRAIN-006 — atualizado para ADR-017 7 estados canônicos (era 5 estados legados)
INV-TRAIN-035 — atualizado para individualization_mode (TRAIN-DEC-044)
INV-TRAIN-082 — novo, preserva a constraint de template name unique (movida do 035)
Nota de workflow de estados — limpa a divergência LAC-001 (encerrada)
Arazzo — create_training_session_and_mark_attendance.arazzo.yaml atualizado: registerTrainingAttendance → recordSessionAttendance.

O que foi executado
Decisões formais registradas:

TRAIN-DEC-047 — exercises é módulo soberano; training referencia exercise_id + exercise_version_id
TRAIN-DEC-048 — Versionamento pedagógico explícito (Approach B): exercise_version append-only
OD-TRAIN-001 → fechada no MODULE_DECISION_IR.json (era a única open decision de fronteira que restava)
10 novos enums canônicos em DOMAIN_AXIOMS.json:
exercise_scope, exercise_visibility_mode, exercise_age_category, exercise_skill_level, exercise_primary_objective, exercise_game_phase, session_block_phase, exercise_physical_load, exercise_space_required, exercise_relation_type

Módulo exercises contratualizado — de casca vazia para pronto para implementação:

Artefato	O que entrega
MODULE_SCOPE_EXERCISES.md	Responsabilidades, boundaries, fora do escopo
DOMAIN_RULES_EXERCISES.md	10 regras de domínio (DR-EXB-001 a 010)
INVARIANTS_EXERCISES.md	18 invariantes (INV-EXB-001 a 018)
exercise_preview.yaml	DTO de listagem — scan de 15s (DR-EXB-008)
exercise.yaml	DTO completo com todos os atributos pedagógicos
exercise_version.yaml	Fato append-only de versão (TRAIN-DEC-048)
exercise_relation.yaml	Relação semântica tipada (progressão/regressão/variação/contraindicação)
exercises.yaml	14 endpoints: CRUD, versioning, copy-to-org, relations, ACL
Próximo passo natural: session_block — o contrato de composição da sessão (DEFER-TRAIN-P2-006, já desbloqueado), usando o enum session_block_phase agora canônico e referenciando exercise_version_id.

Avaliação Arquitetural — 14 Decisões para Liderança de Mercado
Papel: Arquiteto de Software — HB Track
Data: 2026-03-16
Base: MODULE_MAP.md (Princípio 2 — Monólito Modular), ARCH_DECISIONS_TRAINING.md (46 decisões), contratos Fase 1

Tabela de Veredicto Rápido
#	Decisão	Veredicto	Ação
1	"Workout Knowledge Graph"	Válida, terminologia errada	Rich schema no módulo exercises — sem graph DB
2	Workflow-first / 6 bounded contexts	Parcialmente já existe — conflito com Princípio 2	Remap para módulos canônicos
3	Multi-tenant + multi-persona day zero	Já decidida	Hierarquia federação-clube é nova — needs ADR
4	Conteúdo híbrido (canonical + user + institutional)	2 tiers existem. 3º tier é novo	Decidir INSTITUTIONAL scope
5	Search como capacidade estratégica	Não existe nenhuma decisão	Faceted/Postgres Fase 1; índice externo Fase 2
6	Training Session DSL	É o contrato de session_block	session_block schema + phase enum — DEFER-TRAIN-P2-006
7	Session Planner como motor transacional	Núcleo existe. Clonagem/versionamento são novos	Classificar por fase
8	Offline-first	Não existe. CONFLITA com contratos atuais	ADR de plataforma — Fase 2
9	Media engine desacoplado	INV-TRAIN-052 existe, ADR não	ADR de Media Delivery — módulo exercises
10	Versionamento pedagógico	Não existe — lacuna crítica de integridade	Necessita decisão formal imediata
11	Recomendação híbrida (rules + signals)	Alinhada com TRAIN-DEC-003/041/042	Fase 2 — regras de domínio primeiro
12	Telemetria de valor de produto	Não existe	Event taxonomy — Fase 2 analytics
13	Analytics longitudinal	Alinhada com TRAIN-DEC-046 + módulo analytics	Já na arquitetura
14	UX "coach-grade"	Alinhada com ADR-019 (lean DTOs)	Cache-control, ETags, preview DTO
Seção 1 — O que já está na arquitetura HB Track
Decisão 2 — Os bounded contexts JÁ SÃO os módulos canônicos
O documento sugere decompor em: Drill Library, Session Planner, Tactical Board, Athlete Feedback, Team Workspace, Training Analytics. Porém o MODULE_MAP.md e Princípio 2 já resolvem isso:

Bounded context sugerido	Módulo canônico HB Track
Drill Library	exercises (módulo separado, já existe)
Session Planner	training (núcleo do módulo)
Tactical Board	training (contexto interno) ou scout
Athlete Feedback	training + wellness (já delimitado)
Team Workspace	teams (módulo separado, já existe)
Training Analytics	analytics (módulo soberano, TRAIN-DEC-046)
A decomposição correta já existe. O que não existe é o conteúdo rico dentro de cada módulo — especialmente no módulo exercises, que hoje é um lookup simples.

Ação: não criar novos módulos. Enriquecer os módulos existentes.

OD-TRAIN-001 — Já resolvida pelo MODULE_MAP.md
MODULE_MAP.md linha 31 e fronteira crítica lines 59-60:

exercises é lookup; training é evento operacional.

OD-TRAIN-001 ("exercises como módulo separado ou submódulo") está implicitamente resolvida pelo mapa canônico. exercises é um módulo separado com dependência declarada: exercises → training. O que está faltando é o schema rico do módulo exercises, não a decisão de fronteira.

Decisões 3, 11, 13 — Totalmente alinhadas
Decisão 3 (multi-tenant): organizationId em todas as entidades, ADR-007/008 (auth/authz), RBAC com roles — base existe. O que é novo é hierarquia organizacional (federação > clube > equipe).
Decisão 11 (recomendação híbrida): TRAIN-DEC-003 ("IA só recomenda, treinador decide") + TRAIN-DEC-041/042 (IA consultiva). Filosofia idêntica.
Decisão 13 (analytics longitudinal): TRAIN-DEC-046 (analytics soberano), fronteiras wellness/medical/competitions definidas, HYBRID persistence (ADR-018). Já na arquitetura.
Seção 2 — Tensões Arquiteturais Críticas
Tensão 1 — "Knowledge Graph" vs. realidade do stack
O que é sugerido: exercises como grafo de conhecimento com relações semânticas — progressões, regressões, variações, contraindicações.

O problema: HB Track usa PostgreSQL como banco canônico (ARCHITECTURE.md). Um graph database (Neo4j, etc.) seria um segundo motor de persistência com operação separada, backups separados, transações não compartilhadas com o domínio principal.

Veredicto como arquiteto: os atributos ricos E as relações semânticas cabem perfeitamente em schema relacional. Relações entre drills (progressão, regressão, variação) são uma tabela de adjacência exercise_relation(from_id, to_id, relation_type). Atributos ricos são colunas estruturadas + JSONB para metadados flexíveis.

Decisão: exercício como objeto de domínio rico em PostgreSQL. A linguagem "Knowledge Graph" é metáfora de produto válida, não decisão tecnológica.

Tensão 2 — Decisão 8 (Offline-first) conflita com contratos atuais
Os contratos atuais não têm:

ETags / Last-Modified / If-None-Match em nenhum endpoint
Endpoint de delta sync (GET /training-sessions/changes-since?cursor=X)
Protocolo de resolução de conflitos (last-write-wins? CRDTs? versão vetorial?)
Semântica de fila offline para writes (presença, wellness_pre, ajustes ao vivo)
Offline-first é a decisão com maior impacto horizontal da lista inteira. Afeta todos os módulos, não só training. Implementar offline-first sem ADR de plataforma criaria contratos ad hoc incompatíveis entre módulos.

Decisão: Offline-first exige ADR de plataforma antes de qualquer implementação. Fase 2. Não é detalhe técnico — é mudança de contrato.

Tensão 3 — Decisão 10 (Versionamento pedagógico) expõe lacuna de integridade real
Esta é a tensão mais séria e menos óbvia. O problema:

INV-TRAIN-053 diz que exercício referenciado por sessão histórica não pode ser removido (soft-delete). Mas o que acontece quando o exercício é editado? O treinador do sub-12 que executou uma sessão em março ver o drill da forma como era em março, ou como ele é agora após uma correção editorial?

O contrato atual apenas guarda exerciseId em session_exercise. Se o exercício muda, a sessão histórica passa a refletir a nova versão — quebrando reprodutibilidade e auditoria pedagógica.

Há duas abordagens arquiteturais mutuamente exclusivas:

Abordagem	Trade-off
A — Snapshot no momento de uso (session_exercise guarda snapshot dos atributos relevantes do drill na data de execução)	Correto para auditoria. Aumenta tamanho de armazenamento. Snapshot pode ficar obsoleto se intencionalmente diferente da versão atual.
B — Versioning explícito no exercises module (cada drill tem version_id; session_exercise referencia exercise_id + version_id)	Correto para rastreabilidade. Requer sistema de versionamento no módulo exercises. Permite upgrade intencional de sessão para nova versão de drill.
Decisão como arquiteto: a Abordagem B é superior porque permite que o treinador opte por atualizar uma sessão-template para usar a versão corrigida do drill, enquanto sessões executadas permanecem imutáveis na versão usada. Mas requer que o módulo exercises implemente versionamento semântico de objetos de domínio.

Esta decisão bloqueia o design do schema de exercises e precisa ser tomada antes de qualquer implementação do módulo.

Tensão 4 — Decisão 4 (3º tier de conteúdo: INSTITUTIONAL)
A arquitetura atual de exercises tem dois escopos: SYSTEM (plataforma) e ORG (clube). A Decisão 4 propõe um terceiro: INSTITUTIONAL (federações, parceiros licenciados).

Impacto em invariantes existentes (INV-TRAIN-047 a 053): todas assumem o modelo de dois escopos. Um terceiro escopo exige:

Quem pode criar conteúdo INSTITUTIONAL? (federação autenticada? curador HB Track com role especial?)
Quem pode ver? (qualquer organização? somente organizações filiadas?)
Quem pode editar? (apenas o criador institucional? equipe editorial HB Track como intermediária?)
Qual a política de licenciamento/pricing? (gratuito, premium, por filiação?)
Estas perguntas têm resposta de domínio, não de tecnologia. Sem respostas, o escopo INSTITUTIONAL vira um placeholder sem governança.

Seção 3 — Classificação por Fase
Fase 1 — Implementar agora (desbloqueiam roadmap)
1. Schema rico do módulo exercises (Decisão 1)

O módulo exercises existe mas não tem schema OpenAPI. Este é o maior gap. O schema precisa de:


ageCategory: enum (sub-12 | sub-14 | sub-16 | sub-18 | adult)
skillLevel: enum (iniciante | intermediário | avançado | elite)
primaryObjective: enum (técnico | tático | físico | decision-making | misto)
gamePhase: enum (ataque-posicional | defesa-posicional | transição-ofensiva | transição-defensiva | bola-parada)
sessionPhase: enum (aquecimento | ativação | técnica | tomada-de-decisão | tática | jogo-reduzido | retorno-à-calma)
complexity: integer(1..5)
physicalLoad: enum (baixo | médio | alto | máximo)
minAthletes / maxAthletes: integer
spaceRequired: enum (meia-quadra | quadra-inteira | área-reduzida | sem-quadra)
materials: array[enum]
estimatedDurationMinutes: integer
Relações semânticas (Fase 1 apenas diretas):


exercise_relation(from_exercise_id, to_exercise_id, relation_type: progressão|regressão|variação)
2. Resolução de OD-TRAIN-001 — registrar formalmente que exercises é módulo separado, per MODULE_MAP.md.

3. session_block schema (Decisão 6 — DEFER-TRAIN-P2-006 já desbloqueado)

A fase da sessão é conhecimento de domínio do handebol que deve entrar em DOMAIN_AXIOMS.json como enum session_block_phase:


WARMUP | ACTIVATION | TECHNICAL | DECISION_MAKING | TACTICAL | REDUCED_GAME | COOLDOWN
4. Preview DTO de exercício (Decisão 14 — coach-grade UX)

O endpoint de listagem de exercícios deve retornar uma representação mínima (15 segundos de scan):


id, name, sessionPhase, ageCategory, estimatedDurationMinutes, physicalLoad,
thumbnailUrl, primaryObjective — SEM description longa, SEM relations, SEM fullMedia
Representação completa apenas em GET /exercises/{id}.

Fase 2 — Implementar após base do módulo exercises
5. Versionamento de exercícios (Decisão 10 — crítico para integridade)

Antes de qualquer sessão histórica ser registrada com referência a um exercício, a política de versionamento deve estar decidida. Fase 2 porque bloqueia a reprodutibilidade histórica mas não impede a operação básica da Fase 1 enquanto os exercícios ainda são poucos e sem revisões.

6. Busca facetada estruturada (Decisão 5)

Fase 1: filtros simples em Postgres (WHERE + índices compostos). Fase 2: FTS (pg_trgm ou Meilisearch) + facets + ranking contextual. Busca semântica/vetorial: Fase 3.

7. Session clonagem + template reuso sazonal (Decisão 7)

Session planner transacional está na Fase 1. Clonagem de sessão, comparação de versões, reuso sazonal de template são Fase 2.

8. Recomendação contextual (Decisão 11)

Primeiro ciclo: rule engine baseado nos atributos do exercício + contexto da sessão (categoria, objetivo, fase do microciclo). Sem ML. Fase 2.

9. Offline-first (Decisão 8) — após ADR de plataforma

Protocolo: delta sync endpoint (GET /sync/changes?cursor=ISO-8601-timestamp, por módulo), ETags em GETs, fila local de writes com idempotency key. Exige ADR antes de qualquer implementação.

10. Media delivery desacoplado (Decisão 9)

ADR separando metadados pedagógicos de assets de mídia. Múltiplas representações (thumbnail, clip curto, vídeo completo, diagrama, PDF) com CDN configurável. Fase 2 porque Fase 1 pode usar YouTube links (INV-TRAIN-052 já permite youtube_link).

11. Telemetria de produto (Decisão 12)

Event taxonomy orientada a outcome (DrillViewed, SessionBuiltFromTemplate, etc.). Integração com módulo analytics. Fase 2.

Fase 3 — Quando escala ou organização justificar
12. Hierarquia organizacional (Decisão 3 — federação > clube)

Multi-tenant está na Fase 1. A hierarquia federation como super-organização requer mudança no modelo de permissão (ADR-008 extended). Fase 3.

13. Conteúdo INSTITUTIONAL (Decisão 4 — 3º tier)

Após definição de governança editorial, licenciamento e modelo comercial. Fase 3.

14. Busca semântica / vetorial (Decisão 5 parte 2)

Embeddings de drills + busca por contexto natural ("variação de 6:0 com foco em saída de ponta"). Fase 3 quando tiver volume de dados para treinar ou usar embeddings pré-treinados de qualidade.

Seção 4 — Decisões que Precisam de Resolução Formal Antes da Implementação
Estas são bloqueantes. Implementar qualquer coisa sem elas cria dívida arquitetural que não é amortizável.

BLOQ-01 — Política de versionamento de exercícios (Decisão 10)

Pergunta: session_exercise armazena snapshot dos atributos do drill OU referencia exercise_id + version_id?

Recomendação: exercise_id + version_id (Abordagem B). session_exercise é append-only (ADR-018); guardar a versão usada é coerente com imutabilidade histórica. O módulo exercises implementa exercise_versions como tabela append-only.

BLOQ-02 — Política de offline-first (Decisão 8)

Pergunta: qual é o protocolo de sync? Quem é a fonte de verdade em conflito? O que é sincronizável e o que é apenas online?

Recomendação: ADR de plataforma antes de qualquer endpoint de sync. Proposta inicial: leitura offline-first (cache de sessão + exercícios favoritos); writes online com retry queue local; nenhuma resolução de conflito em Fase 2 — last-write-wins com timestamp; conflitos são logados como atenção na attention_queue.

BLOQ-03 — Conteúdo INSTITUTIONAL: modelo de governança

Pergunta: quem cria, quem aprova, quem vê, como é licenciado?

Recomendação: não implementar em Fase 1 ou Fase 2. O escopo SYSTEM cobre o catálogo curado HB Track. Parcerias institucionais são modelo comercial, não decisão técnica — devem seguir o processo de ADR quando o modelo de negócio estiver definido.

BLOQ-04 — OD-TRAIN-001: registrar resolução formal

Ação imediata: registrar em MODULE_DECISION_IR.json e ARCH_DECISIONS_TRAINING.md que OD-TRAIN-001 está resolvida pelo MODULE_MAP.md. exercises é módulo separado. training só referencia exerciseId + exerciseVersionId (após BLOQ-01). Isso desbloqueará o design do schema do módulo exercises.

Seção 5 — Próximos Passos Concretos
Em ordem de dependência:


1. Resolver BLOQ-01 (política de versionamento de exercícios)
   → Define o campo exercise_version_id em session_exercise
   → Habilita o design completo do módulo exercises

2. Resolver BLOQ-04 (fechar OD-TRAIN-001 formalmente)
   → Registrar decisão no IR

3. Contratar módulo exercises (schema rico — Decisão 1)
   → exercise.yaml com todos os atributos de domínio
   → exercise_relation.yaml (progressão/regressão/variação)
   → exercise_media.yaml (tipos de representação)
   → exercise_version.yaml (append-only, ADR-018)
   → Endpoints: GET /exercises (lista com preview DTO), GET /exercises/{id}
     POST /exercises, PATCH /exercises/{id}, POST /exercises/{id}/relations
     GET /exercises/{id}/versions

4. Contratar session_block (Decisão 6 — DEFER-TRAIN-P2-006 desbloqueado)
   → session_block_phase enum em DOMAIN_AXIOMS.json
   → session_block.yaml (phase, exerciseId, exerciseVersionId, durationMinutes,
     intensity, blockObjective, order_index)
   → Aplicar INV-TRAIN-083 (Elastic Sum Rule) no design do schema

5. ADR-020: offline-first protocol (BLOQ-02)
   → ADR de plataforma: delta sync, ETags, conflict policy, fila de writes

6. ADR-021: media delivery e exercise versioning
   → Formalizar separação de assets e política de versionamento pedagógico
Síntese Arquitetural
Das 14 decisões propostas, o HB Track já tem resposta arquitetural para 7 delas nos artefatos canônicos existentes (Decisões 2, 3, 11, 13, 14 e partes de 6 e 7). A questão não é ausência de visão — é ausência de schema rico no módulo exercises, que é o substrato sobre o qual Decisões 1, 4, 5, 6, 7, 9, 10 e 12 dependem.

O maior risco de implementação não é tecnológico. É começar a colocar código antes de decidir a política de versionamento de exercícios (BLOQ-01). Uma sessão histórica que perde reprodutibilidade após uma correção editorial é um problema de integridade de dados que não tem conserto retroativo sem migração destrutiva.

O segundo maior risco é usar a linguagem "Workout Knowledge Graph" como justificativa para introduzir um graph database. Não há nada nessas 14 decisões que requeira tecnologia além do PostgreSQL com schema bem modelado para Fase 1 e Fase 2.