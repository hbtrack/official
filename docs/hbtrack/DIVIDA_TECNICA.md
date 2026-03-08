Matriz — MUDANÇA → ARQUIVOS/CÓDIGO IMPACTADOS → TIPO DE IMPACTO → EVIDÊNCIA
MUDANÇA	ARQUIVOS / CÓDIGO IMPACTADOS	TIPO DE IMPACTO	EVIDÊNCIA
Estabelecer precedência normativa spec-driven do módulo	Hb Track - Backend/docs/ssot/schema.sql, services do backend, openapi.json, Hb Track - Frontend/src/api/generated/*, src/lib/api/*, docs PRD/flows/screens	Governança / arquitetura / resolução de conflito	A ordem normativa é DB > Services > OpenAPI > FE Generated > FE Manual/Adapter > PRD/Flows/Screens. 

INVARIANTS_TRAINING

 

TRAINING_FRONT_BACK_CONTRACT


Tornar o contrato FE↔BE determinístico e obrigatório	TRAINING_FRONT_BACK_CONTRACT.md, Hb Track - Backend/docs/ssot/openapi.json, routers/schemas do backend, Hb Track - Frontend/src/api/generated/*	Contrato / integração FE-BE	O documento define endpoints, operationIds, shapes mínimos, tipos canônicos, erros, gaps e a materialização via OpenAPI + generator. 

TRAINING_FRONT_BACK_CONTRACT


Obrigar pipeline CONTRACT_SYNC_FE quando contrato mudar	Backend real, openapi.json, baseline OpenAPI, src/api/generated/*, telas FE impactadas, validação runtime	Processo de entrega / sincronização obrigatória	O fluxo obrigatório é: backend → regenerar OpenAPI → lint spec → diff spec → regenerar client → migrar telas → validar runtime → só então declarar paridade. 

TRAINING_FRONT_BACK_CONTRACT


Proibir edição manual do cliente FE gerado	Hb Track - Frontend/src/api/generated/*	Regra de implementação FE	O cliente gerado é derivado e “não pode ser editado manualmente”. 

TRAINING_FRONT_BACK_CONTRACT

 

TRAINING_FRONT_BACK_CONTRACT


Rebaixar src/lib/api/* a adapter subordinado	Hb Track - Frontend/src/lib/api/*, hooks e componentes que ainda usem camada manual	Refactor arquitetural FE	A documentação define que o FE deve preferir src/api/generated/* e que src/lib/api/* não define contrato. 

TRAINING_FRONT_BACK_CONTRACT

 

TRAINING_FRONT_BACK_CONTRACT


Formalizar ferramentas oficiais do pipeline	Redocly CLI, oasdiff, OpenAPI Generator, Schemathesis	Toolchain / gates	Ferramentas oficiais explícitas: OPENAPI_SPEC_QUALITY, CONTRACT_DIFF_GATE, GENERATED_CLIENT_SYNC, RUNTIME CONTRACT VALIDATION. 

TRAINING_FRONT_BACK_CONTRACT

 

TRAINING_FRONT_BACK_CONTRACT


Congelar mudanças contratuais sem spec sincronizada	openapi.json, baseline OpenAPI, FE gerado, código FE/BE afetado	Gate de qualidade / bloqueio de merge lógico	SPEC_FREEZE_RULE: nenhuma mudança FE/BE que afete contrato é válida sem openapi.json atualizado, validado e sincronizado. 

TRAINING_FRONT_BACK_CONTRACT


Exigir baseline de contrato para diff de breaking change	contracts/openapi/baseline/openapi_baseline.json	Governança de versionamento de contrato	SPEC_VERSIONING exige spec anterior aceita preservada para comparação. 

TRAINING_FRONT_BACK_CONTRACT


Obrigar materialização backend real antes de declarar conclusão	schema/constraints, models, services, routers, Pydantic/FastAPI	Backend / entrega real	O _INDEX.md define: primeiro materializar backend real, depois validar subset, depois sync FE se necessário, depois TRUTH_BE. 

_INDEX

 

_INDEX


Fixar o escopo de persistência do módulo treino	training_sessions, training_session_exercises, wellness_pre, wellness_post, attendance, training_cycles, training_microcycles, session_templates, exercises, exercise_tags, exercise_favorites, exercise_media, exercise_acl, training_analytics_cache, team_wellness_rankings, training_alerts, training_suggestions	Banco de dados / domínio	O escopo normativo explicita as entidades e tabelas lógicas do módulo. 

INVARIANTS_TRAINING


Alinhar invariantes a testes canônicos do backend	Hb Track - Backend/tests/training/invariants/* e código de domínio correspondente	Regra de negócio / cobertura de teste	O documento alinha INV-TRAIN-### ao conjunto de testes canônicos. 

INVARIANTS_TRAINING

 

INVARIANTS_TRAINING


Expandir o módulo com FASE_3 real: presença avançada, pending queue, visão atleta, pós-treino, IA coach, wellness obrigatório, gamificação e IA treinador	Backend e FE ligados a attendance, pending queue, athlete view, ai coach, wellness gates	Novas capabilities / expansão funcional	As invariantes v1.3.0 adicionam 28 regras para FASE_3 nesses domínios. 

INVARIANTS_TRAINING


Mudar default de visibilidade dos exercícios ORG para restricted	Persistência/modelo/regras de ACL do banco de exercícios	Regra de negócio / banco / backend	A decisão normativa registrada muda o default de org_wide para restricted. 

INVARIANTS_TRAINING


Implementar telas normativas e seus estados mínimos (loading, empty, data, error)	Hb Track - Frontend/src/app/(admin)/training/* e rotas protected de atleta	Frontend / UX funcional	As telas são SSOT normativo e devem consumir cliente gerado; exemplo: agenda /training/agenda com query params normativos e estados de UI explícitos. 

TRAINING_SCREENS_SPEC

 

TRAINING_SCREENS_SPEC


Implementar/considerar 25 telas do módulo treino	Agenda, editor, relatórios, planning, exercícios, analytics, rankings, wellness athlete, pending queue, telas atleta/IA	Frontend / cobertura de superfície	O índice de telas registra 25 entradas, com status EVIDENCIADO, PARCIAL, HIPOTESE e GAP. 

TRAINING_SCREENS_SPEC


Implementar os fluxos normativos, sem deixar flows redefinirem contrato	Fluxos do usuário, mas contrato continua no OpenAPI/contract doc	UX / processo / disciplina documental	O flow document não define endpoint/schema; se o fluxo exigir mudança de contrato, ela deve ocorrer primeiro no contrato e na spec. 

TRAINING_USER_FLOWS


Fixar wellness athlete pages como self-only, sem seleção de atleta	/athlete/wellness-pre/[sessionId], /athlete/wellness-post/[sessionId], payloads correlatos	Regra funcional / segurança / FE-BE	Changelog registra regra self-only explícita e mapeamento FE→payload. 

TRAINING_USER_FLOWS

 

TRAINING_SCREENS_SPEC


Normatizar comportamento degradado de export sem worker	Export PDF / LGPD routers, modal de export, backend de export	Backend + FE / resiliência operacional	Screens e contract registram decisão normativa de estado degradado sem worker. 

TRAINING_SCREENS_SPEC

 

TRAINING_FRONT_BACK_CONTRACT


Implementar e/ou sincronizar pending queue	Backend de pendências, training_pending_items, service de pending, página /training/pending-queue	Backend / banco / frontend	AR backlog registra migration attendance.preconfirm + training_pending_items, service de pending e tela pending queue evidenciada. 

AR_BACKLOG_TRAINING

 

TRAINING_SCREENS_SPEC


Migrar hooks e componentes do FE para cliente gerado	api-instance.ts, useSessions.ts, useSessionTemplates.ts, useCycles.ts, useMicrocycles.ts, useExercises.ts, modais e clients de treino	Refactor FE / convergência OpenAPI	O backlog registra migração para generated client, singletons de API e componentes de sessão/exercício. 

AR_BACKLOG_TRAINING


Tornar a evidência válida dependente de TRUTH_BE com banco real	Reset DB, migrations, seed, pytest real, scans de no-mocks	Testes / gate de aceite	A matriz de testes diz que, se SSOT mudar, a mudança deve ser ancorada; TRUTH test falhou → corrigir produto real; NO_MOCKS_GLOBAL é pré-condição; sync FE não substitui backend validado. 

TEST_MATRIX_TRAINING

 

TEST_MATRIX_TRAINING


Exigir atualização mínima do SSOT após cada tipo de mudança	INVARIANTS_TRAINING.md, TRAINING_FRONT_BACK_CONTRACT.md, TRAINING_USER_FLOWS.md, TRAINING_SCREENS_SPEC.md, TEST_MATRIX_TRAINING.md, AR_BACKLOG_TRAINING.md	Governança documental / rastreabilidade	_INDEX.md define qual SSOT atualizar conforme a natureza da mudança. 

_INDEX


Declarar o módulo como concluído em FASE_2 + FASE_3 REAL, mas com itens pós-DONE fora do bloqueio atual	Estado do módulo, backlog, roadmap, superfícies ainda GAP/HIPÓTESE	Estado de produto / leitura correta do done	_INDEX.md declara DONE_TRAINING_ATINGIDO, 80 ARs e FE migration completa; screens ainda mostram itens PARCIAL, HIPOTESE e GAP em superfícies específicas. 

_INDEX

 

TRAINING_SCREENS_SPEC