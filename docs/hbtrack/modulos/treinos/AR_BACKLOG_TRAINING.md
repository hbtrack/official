# AR_BACKLOG_TRAINING.md — Backlog de ARs (Materialização) do Módulo TRAINING

Status: ATIVO
Versão: v4.3.0
Tipo de Documento: AR Materialization Backlog (**apenas ARs** — sem gate, sem roadmap)  
Módulo: TRAINING  
Fase: FASE_2 (PRD v2.2 — 2026-02-20) + DEC-TRAIN-* (2026-02-25) + FASE_3 (2026-02-27)  
Autoridade: NORMATIVO_OPERACIONAL  
Owners:
- Arquitetura (Arquiteto): Codex (Arquiteto v2.4.0)
- Execução (Executor): (a definir)
- Auditoria/Testes: (a definir)

Última revisão: 2026-03-09  
Próxima revisão recomendada: N/A — TRUTH SUITE 0 failed/skipped/xfailed atingido  

> Changelog v4.3.0 (2026-03-09) — Batch REC-03/04/05: Planejamento AR-TRAIN-REC-03, AR-TRAIN-REC-04, AR-TRAIN-REC-05:
> - AR-TRAIN-REC-03 adicionada ao backlog (AR_274, Class A+G, Status BACKLOG) — Ledger de Sessao + Scheduler SKIP LOCKED.
> - AR-TRAIN-REC-04 adicionada ao backlog (AR_275, Class A+G, Status BACKLOG) — Superficie UI/Flows/Screens reconciliada.
> - AR-TRAIN-REC-05 adicionada ao backlog (AR_276, Class A, Status BACKLOG) — Sunset final rotas legadas /publish+/close.
> - Tabela de ARs: 3 linhas adicionadas.

> Changelog v4.2.0 (2026-03-09) — Batch REC-02: Planejamento AR-TRAIN-REC-02:
> - AR-TRAIN-REC-02 adicionada ao backlog (AR_273, Class A+G, Status BACKLOG).
> - Tabela de ARs: 1 linha adicionada AR-TRAIN-REC-02 (dependencia AR_271+AR_272).

> Changelog v4.1.0 (2026-03-09) — Batch REC-02: Sync documental pós-REC-01:
> - AR-TRAIN-REC-01 READY->VERIFICADO (hb seal 271, 2026-03-09).
> - Tabela de ARs: AR-TRAIN-REC-01 status atualizado para VERIFICADO.
> - Detalhe §8 AR-TRAIN-REC-01: Status Final atualizado para VERIFICADO.
> - Tabela de ARs: 1 linha adicionada AR-TRAIN-087 (AR_272, EM_EXECUCAO).

> Changelog v4.0.0 (2026-03-09) — Batch REC-01: Reconciliação documental base (AR-TRAIN-REC-01):
> - Lote 26 adicionado: AR-TRAIN-REC-01 (G+A) — Reconciliação canônica: eliminar PUBLISHED/CLOSED/_publish/_close de TRAINING_SCOPE_REGISTRY.yaml + TRAINING_PERF_LIMITS.json + _INDEX.md; promover lifecycle draft->scheduled->in_progress->pending_review->readonly; renomear 'limits'->'operations' em PERF_LIMITS.
> - Tabela de ARs: 1 linha adicionada AR-TRAIN-REC-01 (AR_271).
> - Detalhe §8: seção AR-TRAIN-REC-01 adicionada.

> Changelog v3.9.0 (2026-03-08) — Batch 35 DONE_CONTRACT implementation (AR-TRAIN-081..086):
> - Lote 25 adicionado: AR-TRAIN-081 (G) — Registrar DONE_CONTRACT_TRAINING.md na cadeia canônica: _INDEX.md v1.8.0 + entry 6b.
> - Lote 25 adicionado: AR-TRAIN-082 (A) — Criar TRAINING_SCOPE_REGISTRY.yaml: 13 CORE + 7 EXTENDED + 2 EXPERIMENTAL.
> - Lote 25 adicionado: AR-TRAIN-083 (A) — Criar TRAINING_STATE_MACHINE.yaml: 5 entidades stateful CORE.
> - Lote 25 adicionado: AR-TRAIN-084 (A) — Criar TRAINING_PERF_LIMITS.json: 16 itens CORE com SLOs baseline.
> - Lote 25 adicionado: AR-TRAIN-085 (A) — Criar traceability_training_core.csv skeleton: 9 headers, 0 dados.
> - Lote 25 adicionado: AR-TRAIN-086 (G) — Sync documental pós-Batch 35.
> - Tabela de ARs: 6 linhas adicionadas AR-TRAIN-081..086.
> - Detalhe §8: seções AR-TRAIN-081..086 adicionadas.
> - DONE_CONTRACT_TRAINING.md implementado (Batch 35 completo).
> - Lote 24 adicionado: AR-TRAIN-079 (D/E) — trainingAlertsSuggestionsApi singleton + TRAINING_FRONT_BACK_CONTRACT.md §5.10 DIVERGENTE→IMPLEMENTADO + useSuggestions.ts deferred CAP-001.
> - Lote 24 adicionado: AR-TRAIN-080 (G) — Sync documental pós-Batch 34.
> - Tabela de ARs: 2 linhas adicionadas AR-TRAIN-079..080.
> - Detalhe §8: seções AR-TRAIN-079..080 adicionadas.
> - FE_MIGRATION_COMPLETE = TRUE (100% endpoints canônicos; useSuggestions.ts deferred a CAP-001).

> Changelog v3.7.0 (2026-03-07) — Batch 33 FE migration + BE fix + documental sync (AR-TRAIN-072..078):
> - Lote 23 adicionado: AR-TRAIN-072 (D) — api-instance.ts: 9 singletons + fix interceptor.
> - Lote 23 adicionado: AR-TRAIN-073 (D) — Migrar useSessions + useSessionTemplates para cliente gerado.
> - Lote 23 adicionado: AR-TRAIN-074 (D) — Migrar componentes session para generated client.
> - Lote 23 adicionado: AR-TRAIN-075 (D) — Migrar useCycles + useMicrocycles + useExercises.
> - Lote 23 adicionado: AR-TRAIN-076 (D) — Migrar exercise components + training-phase3.ts.
> - Lote 23 adicionado: AR-TRAIN-077 (B) — Fix DEC-TRAIN-004 export-pdf 503 → 202.
> - Lote 23 adicionado: AR-TRAIN-078 (G) — Sync documental pós-Batch 33.
> - Tabela de ARs: 7 linhas adicionadas AR-TRAIN-072..078.
> - Detalhe §8: seções AR-TRAIN-072..078 adicionadas.
> - FE_MIGRATION_COMPLETE = TRUE (exceto useSuggestions.ts — DIVERGENTE_DO_SSOT pendente).

> Changelog v3.6.0 (2026-03-06) — Batch 32 sync documental (AR-TRAIN-070/071):
> - Lote 22 adicionado: AR-TRAIN-070 (T) — testes impl GET/PATCH wellness por ID (CONTRACT-031/032/037/038).
> - Lote 22 adicionado: AR-TRAIN-071 (G) — sync documental pós-Batch 31+32.
> - Tabela de ARs: 2 linhas adicionadas AR-TRAIN-070/071.
> - Detalhe §8: seções AR-TRAIN-070 e AR-TRAIN-071 adicionadas.

> Changelog v3.5.1 (2026-03-06) — Doc hygiene (spec-driven):
> - DONE_GATE tratado como evidência derivada (`_reports/training/DONE_GATE_TRAINING.md`), não SSOT.
> - Removidas referências a artefatos inexistentes (Done Gate versionado / Batch Plan) como exigência normativa.
> - Ajustadas referências para `TEST_MATRIX_TRAINING.md` (norma) e `_reports/training/*` (evidência).

> Changelog v3.5.0 (2026-03-06) - Batch 31 BE stubs fix (AR-TRAIN-069):
> - Lote 21 adicionado: AR-TRAIN-069 (B) — BE: implementar GET/PATCH wellness-pre e wellness-post por ID (fix stubs 501).
> - Tabela de ARs: 1 linha adicionada AR-TRAIN-069.
> - Detalhe §8: secao AR-TRAIN-069 adicionada.

> Changelog v3.4.0 (2026-03-06) - Batch 30 FE Refactor (AR-TRAIN-068):
> - Lote 20 adicionado: AR-TRAIN-068 (M) — Refactor FE Wellness Pre/Pos para cliente gerado.
> - Tabela de ARs: 1 linha adicionada AR-TRAIN-068.
> - Detalhe §8: secao AR-TRAIN-068 adicionada.

> Changelog v3.3.0 (2026-03-05) — Batch 29 TRUTH SUITE Residuals (AR-TRAIN-063..067):
> - Lote 19 adicionado: AR-TRAIN-063 (T/G), AR-TRAIN-064 (B), AR-TRAIN-065 (B/E), AR-TRAIN-066 (T), AR-TRAIN-067 (G) — todos VERIFICADO.
> - Tabela de ARs: 5 linhas adicionadas AR-TRAIN-063..067.
> - Detalhe §8: seções AR-TRAIN-063..067 adicionadas.
> - Meta-objetivo Batch 29 atingido: 0 xfailed, 0 skipped, 0 LEGACY_INVALID.

> Changelog v3.2.0 (2026-03-05) — NO_MOCKS_GLOBAL + RESPOSTA_A_FALHA:
> - §1: bloco `RESPOSTA A FALHA DE TRUTH TEST` adicionado — procedimento obrigatório para agentes quando TRUTH TEST falha; proibição de alterar testes para simular comportamento.
> - Sem alteração de status de nenhuma AR.

> Changelog v3.1.0 (2026-03-04) — SSOT_PATCH_NO_STUBS_AI (Governança IA Coach):
> - §1 Classes: adicionada Regra NO_STUBS (IA Core) `[NORMATIVO]` — proíbe `unittest.mock`/`MagicMock` no production code de `ai_coach_service.py`.
> - Changelogs v2.1.0, v2.2.0: linguagem "stubs IA Coach" → "símbolos determinísticos" (reclassificação histórica).
> - Descritores de lotes 12/13 (AR-TRAIN-046, AR-TRAIN-048): "stubs" → "símbolos determinísticos".
> - Nenhuma AR alterada em status ou funcionalidade; patch é exclusivamente normativo/documental.

> Changelog v3.0.0 (2026-03-04) — Reestruturação de responsabilidades:
> - **Este arquivo** agora contém SOMENTE ARs (backlog, tabela de status, templates).
> - **TEST_MATRIX_TRAINING.md**: critérios de DONE, PASS/FAIL, classificação BLOQUEANTE/NAO_BLOQUEANTE e gates TRUTH (SSOT operacional vigente).
> - **TRAINING_ROADMAP.md**: auditoria AS-IS, gaps, mapa evidência vs hipótese, decisões arquiteturais (extraído de §0..§3).
> - Removidas: §0 (AS-IS), §1 (evidência/hipótese), §2 (gaps), §3 (decisões), §7b (classificação gate), §9 (PASS/FAIL).

> Changelog v2.9.1 (2026-03-04) — Patch SSOT_PATCH_TRAINING_DONE (reclassificação NON_BLOCKING):
> - Adicionada §7b: Classificação Gate — identifica ARs NON_BLOCKING (classe G) vs BLOCKING.
> - 11 ARs de classe G reclassificadas como NON_BLOCKING (DOCUMENTATION_ONLY / DERIVED_ARTIFACT).
> - Não altera status VERIFICADO de nenhuma AR; não altera funcionalidade, testes, invariantes ou contratos.

> Changelog v2.9.0 (2026-03-04) — AR_246/AR-TRAIN-062 (Batch 28 — Sync pós-Batch 27):
> - AR-TRAIN-060 (G): VERIFICADO (AR_244, hb seal 2026-03-04).
> - AR-TRAIN-061 (T): VERIFICADO (AR_245, hb seal 2026-03-04).
> - AR-TRAIN-062 (G): PENDENTE — Sync Backlog + TEST_MATRIX §9 pós-Batch 27.

> Changelog v2.8.0 (2026-03-04) — AR_244-245/AR-TRAIN-060-061 (Batch 27 — Opção C: Governance+Contracts):
> - AR-TRAIN-060 (G): PENDENTE → VERIFICADO — Governance: Kanban retroativo Batches 23-26 (AR_244).
> - AR-TRAIN-061 (T): PENDENTE → VERIFICADO — Contract tests: CONTRACT-TRAIN-074/075 wellness-rankings (AR_245).

> Changelog v2.7.0 (2026-03-04) — AR_243/AR-TRAIN-059 (Batch 26 — Sync pós-Batch 26):
> - AR-TRAIN-052 (M): VERIFICADO — Frontend Hard Sync v1.3.0 (AR_236, hb seal Batch 23).
> - AR-TRAIN-053 (G): VERIFICADO — Sync §9 TEST_MATRIX entry AR-TRAIN-052 (AR_237, hb seal Batch 24).
> - AR-TRAIN-054 (G): VERIFICADO — Sync §5 FASE_3 18 INVs FAIL/ERROR→PASS + v3.1.0 (AR_238, hb seal Batch 25).
> - AR-TRAIN-055 (E): VERIFICADO — PATCH /attendance/pending-items resolve (AR_239, hb seal Batch 26).
> - AR-TRAIN-056 (E): VERIFICADO — PATCH apply-draft + POST justify-suggestion AI Coach (AR_240, hb seal Batch 26).
> - AR-TRAIN-057 (E): VERIFICADO — GET wellness-content-gate BE endpoint (AR_241, hb seal Batch 26).
> - AR-TRAIN-058 (M): VERIFICADO — FE corrigir URLs training-phase3.ts (AR_242, hb seal Batch 26).
> - AR-TRAIN-059 (G): VERIFICADO — Sync TEST_MATRIX + BACKLOG pós-Batch 26 (AR_243).
> - AR-TRAIN-050/051: PENDENTE→VERIFICADO retroativo (AR_231/AR_232 já selados; tabela estava desatualizada).

> Changelog v2.4.0 (2026-03-03) — Arquiteto (Batch 21/22 planejados; AR-TRAIN-043 obsoleta):
> - AR-TRAIN-043: EM_EXECUCAO → OBSOLETO (Contexto mudou pós-Batches 17-20; escopo de sync §5 TEST_MATRIX extraído para AR-TRAIN-050; Done Gate formal coberto por AR-TRAIN-051).
> - AR-TRAIN-050 (G): ADICIONADA — Sync §5 TEST_MATRIX_TRAINING.md: 11 itens (INV-079/080/081 NOT_RUN→PASS + INV-018/035/058/059/063/064/076/EXB-ACL-006 FAIL/ERROR→PASS) refletindo AR-TRAIN-046 + AR-TRAIN-049 VERIFICADOS.
> - AR-TRAIN-051 (G): ADICIONADA — Done Gate §10 final pós-Batch 21: declaração formal Done + bump versão matriz v2.2.0→v3.0.0 + §10/§0 preenchidos (substitui AR-TRAIN-043 com escopo atualizado).

> Changelog v2.3.0 (2026-03-03) — Arquiteto (Sync Batches 14-20: status das ARs executadas):
> - AR-TRAIN-035..042: PENDENTE → VERIFICADO (AR_214..221, hb seal 2026-03-03 — Batches 14/15: contratos P0 + DEC + Flows P1 + Screens).
> - AR-TRAIN-043: PENDENTE → EM_EXECUCAO (AR_222 Done Gate §10 — suite verde não atingida ainda; 124 FAILs em AR_222).
> - AR-TRAIN-044: PENDENTE → VERIFICADO (AR_225, hb seal 2026-03-03 — Fix async fixtures Batch 17).
> - AR-TRAIN-045: PENDENTE → VERIFICADO (AR_226, hb seal 2026-03-03 — Fix DB fixture setup).
> - AR-TRAIN-046: PENDENTE → VERIFICADO (AR_227, hb seal 2026-03-03 — Fix import stubs ai_coach_service).
> - AR-TRAIN-047: PENDENTE → REJEITADO (AR_228, 🔴 REJEITADO — fix residuais substituído por AR-TRAIN-049).
> - AR-TRAIN-048: PENDENTE → VERIFICADO (AR_229, hb seal 2026-03-03 — Sync app layer modelos/serviços/stubs Batch 19).
> - AR-TRAIN-049: PENDENTE → VERIFICADO (AR_230, hb seal 2026-03-03 — Fix 6 FAILs + 10 ERRORs residuais Batch 20).

> Changelog v2.2.0 (2026-03-03) — Arquiteto (Batch 19 — Sincronização em Lote: app/ desbloqueada via GOVERNED_ROOTS.yaml `UNLOCKED_FOR_SYNC_BATCH_19`):
> - DECISÃO HUMANA: Batch Sync Strategy — corrigir app/models/ + app/services/ para eliminar desalinhamento SSOT (contrato v1.3.0 + invariantes v1.5.0).
> - AR-TRAIN-048 (A/E): Sync app layer — modelos (UniqueConstraint/FK INV-010/035/036/054), serviços (assinaturas contrato), símbolos determinísticos IA Coach — `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion` (GAP-CONTRACT-6/7). *(Nota: o termo "stubs" usado originalmente referia-se a implementações ausentes, NÃO a mocks de teste — ver RH-06/NO_STUBS em TEST_MATRIX_TRAINING.md §5d)*

> Changelog v2.1.0 (2026-03-03) — Arquiteto (Batch 18 — fix FAILs de test-layer pré-existentes Batch 13):
> - DECISÃO HUMANA (Opção A): Criar Batch 18 para zerar os 109 FAILs + 31 ERRORs residuais da suite tests/training/.
> - AR-TRAIN-044 (T): Fix async fixtures — `@pytest.fixture` → `@pytest_asyncio.fixture` (~23+ FAILs, 7 arquivos).
> - AR-TRAIN-045 (T): Fix DB fixture setup — `category_id` NOT NULL + FK `team_registrations` (~57+ ERROs, múltiplos arquivos).
> - AR-TRAIN-046 (T): Fix símbolos determinísticos ausentes em ai_coach_service (3 ERRORs de coleta: `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`) — implementações reais de motor determinístico interno, **não** mocks de teste.
> - AR-TRAIN-047 (T): Fix residuais mistos + validação done gate (suite verde 0 FAILs).

> Changelog v2.0.0 (2026-03-03) — Arquiteto (Batches 12-16 — §10 como gate formal):
> - DECISÃO HUMANA: §10 de TEST_MATRIX_TRAINING.md é o critério formal de aceitação do módulo TRAINING (não "norte ideal").
> - Dessincronia detectada: ~40 invariantes na Matrix marcadas PENDENTE, mas testes já existem no filesystem (criados ARs 144-167).
> - Adicionadas AR-TRAIN-032..043 (Batches 12-16) para satisfazer §10 integral.
> - AR-TRAIN-032 (G): Sync TEST_MATRIX §5 — ~40 INV PENDENTE → COBERTO onde arquivo de teste já existe.
> - AR-TRAIN-033 (T): Criar 6 testes realmente ausentes: INV-053/060/061/062/EXB-ACL-005/007.
> - AR-TRAIN-034 (T): Executar todos NOT_RUN + evidências formais.
> - AR-TRAIN-035..039 (E): Testes de contrato por domínio (5 ARs, ~105 contratos P0 ausentes).
> - AR-TRAIN-040 (T): DEC tests automatizados (11 DEC: DEC-TRAIN-001..004 + EXB-* + RBAC-*).
> - AR-TRAIN-041 (T): Flows P1 evidências MANUAL_GUIADO (13 flows).
> - AR-TRAIN-042 (T): Screens smoke tests MANUAL_GUIADO (25 telas).
> - AR-TRAIN-043 (G): Done Gate §10 final — sync TEST_MATRIX v2.0.0 completo.
> - Também adicionadas linhas 024..031 na tabela-resumo §7 (estavam ausentes por serem adicionadas pós v1.2.0).

> Changelog v1.9.0 (2026-03-02) — Arquiteto (pós hb seal 199):
> - AR-TRAIN-023 PENDENTE → VERIFICADO (AR_199 hb seal 2026-03-02)
> - Todos os 23 AR-TRAIN-* do backlog estão agora VERIFICADO. Batch 8 concluído.

> Changelog v1.8.0 (2026-03-02) — AR_198:
> - AR-TRAIN-022 PENDENTE → VERIFICADO (AR_197 hb seal 2026-03-02)
> - AR-TRAIN-023 adicionada: Governança sync TEST_MATRIX_TRAINING.md §9 pós-Batch 7

> Changelog v1.7.0 (2026-03-02):
> - AR-TRAIN-022 (G) adicionada ao Lote 6 (Governança): Sync INVARIANTS_TRAINING.md — 31 invariantes GAP/PARCIAL/DIVERGENTE → IMPLEMENTADO
> - Dependências: AR-TRAIN-011..021 todas VERIFICADO (2026-03-01)

> Changelog v1.5.0 (2026-02-26):  
> - AR_151 ✅ SUCESSO (MicrocycleOutsideMesoError + overlap guard — eb88236)  
> - AR_152 ✅ SUCESSO (tests INV-054..057 — 4 arquivos, 10 test cases — eb88236)  
> - AR_153 ✅ SUCESSO (migration 0067: attendance.preconfirm + training_pending_items — eb88236)  
> - AR_154 ✅ SUCESSO (attendance_service.py: set_preconfirm + close_session_attendance — eb88236)  
>   - **DECISÃO DEC-INV-065**: Item 3 (guard SessionHasPendingItemsError) NÃO implementado — INV-TRAIN-065 é autoritativo: "sistema DEVE permitir encerrar" com pending items virando fila (INV-066). Contradição AR vs INV resolvida em favor da invariante canônica. AR_155 implementa o pending queue (INV-066).  
> - Selagem pendente (HUMANO): AR_151, AR_152, AR_153, AR_154 → `hb seal 151 152 153 154`  
> - AR_155 → PRÓXIMA (training_pending_service.py + RBAC atleta — INV-066/067)  

> Changelog v1.4.0 (2026-02-26):  
> - ARs de implementação materializadas: AR_143-161 (commit `c65c969`, planos `ar_train_invariants_installation.json` + `ar_train_invariants_implementation.json`)  
> - AR_150 ✅ VERIFICADO+sealed (guards INV-054/INV-057, commit `236bfb6`)  
> - **INCIDENTE**: Testador destruiu Fase A via `git restore .` antes do `hb seal` — AR_143-148 precisam de REDO  
>   - AR_143 tinha sido verificada pelo Testador (hash `e57e1b35` ✅ SUCESSO) mas output `training_invariants_coverage_report.md` foi destruído  
>   - AR_144-148: Executor tinha implementado (exit 0), mas Testador não chegou a verificar  
> - **ATUALIZAÇÃO 2026-02-27**: Fase C (AR_153-158), Fase D (AR_159-161) CONCLUÍDAS com SUCESSO/VERIFICADO  
> - Kanban atualizado com seção `## 10. Cards — Domínio TRAINING — Implementação Invariantes`  

> Changelog v1.3.0 (2026-02-27):  
> - FASE_3: Adicionado Lote 5 com AR-TRAIN-015..021 (ciclos, sessão, presença oficial, pending queue, visão atleta, pós-treino, IA coach)  
> - AR-TRAIN-001 progresso: materialização parcial via AR_126..130 (Step18 UUID convergence, commit 869e061)  
> - INV-TRAIN-EXB-ACL-001 AMENDADA: default `org_wide` → `restricted` (consistência com INV-TRAIN-060)  
> - Novos alvos SSOT: INV-TRAIN-054..081, FLOW-TRAIN-016..021, SCREEN-TRAIN-022..025, CONTRACT-TRAIN-096..105  
> - Novos GAPs implícitos: ciclos hierarchy, presença oficial, IA coach (a detalhar em §2 se necessário)  

> Changelog v1.2.0 (2026-02-26):  
> - Adicionada Authority Matrix (separação Arquiteto/Executor/Testador)  
> - Adicionada convenção de Classification Tags  

> Changelog v1.1.0 (2026-02-25):  
> - DEC-TRAIN-001..004 movidas de PENDENTES para RESOLVIDAS  
> - Adicionadas DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001 como RESOLVIDAS  
> - AR-TRAIN-003/004 atualizadas com ACs de self-only e mapeamento FE→payload  
> - AR-TRAIN-007 atualizada com endpoint canônico CONTRACT-TRAIN-076  
> - AR-TRAIN-008/009 atualizadas com estado degradado sem worker  
> - Adicionadas AR-TRAIN-011..014 para Banco de Exercícios (scope/ACL/media/RBAC)  
> - Adicionados GAP-TRAIN-EXB-001..003  

Dependências:
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
- `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
- `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

Documentos separados (ver arquivo próprio):
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — critérios de evidência, TRUTH_BE, BLOCKING/NON_BLOCKING, PASS/FAIL
- `docs/hbtrack/modulos/treinos/TRAINING_ROADMAP.md` — features futuras, gaps e decisões arquiteturais

---

## REGRA DE LEITURA HISTÓRICA (NORMATIVO)

Os changelogs históricos deste arquivo não governam a execução atual quando conflitam com:
- `_INDEX.md`
- `TEST_MATRIX_TRAINING.md`
- `TRAINING_FRONT_BACK_CONTRACT.md`

Regras:
- Nenhuma instrução histórica de mock/stub, evidência manual/guiada ou sincronização antiga pode ser usada como protocolo operacional vigente.
- Para execução corrente, prevalecem:
  - `TRUTH_BE`
  - `NO_MOCKS_GLOBAL`
  - `API_SYNC_REQUIRED`
  - `GENERATED_CLIENT_SYNC`
  - `CONTRACT_SYNC_FE`

---

## Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | PRD + SSOT + Decisões humanas (DEC-*) |
| Escrita normativa | **Arquiteto** — criar, priorizar, definir escopo, ACs, dependências |
| Escrita de execução | **Executor** — atualizar status da AR em execução + evidências técnicas |
| Escrita de validação | **Testador** — atualizar status de validação/verificação da AR |
| Proposta de alteração | Qualquer papel → via GAP ou DEC ao Arquiteto |
| Precedência em conflito | Arquiteto (escopo/ACs) > Executor (implementação) > Testador (validação) |

---

## Convenção de Tags (Classification)

Cada item (AR-*, GAP-*, DEC-*, EVID-*, HIP-*) neste documento recebe classificação:

| Tag | Significado |
|---|---|
| `[NORMATIVO]` | AR/Regra aprovada que DEVE ser materializada. |
| `[DESCRITIVO-AS-IS]` | Evidência do estado atual do repo. |
| `[HIPOTESE]` | Expectativa do PRD não evidenciada. |
| `[GAP]` | Lacuna identificada. |

---

## Resposta a Falha de TRUTH TEST (NORMATIVO)

> **Se TRUTH TEST falhar: o agente DEVE corrigir o produto real** (código/rotas/serviços/invariantes/UI) até o teste passar. É **proibido** alterar o teste para simular comportamento (mock/stub/monkeypatch/patch). Nenhuma exceção sem AR aprovada pelo Arquiteto.

**Procedimento padrão (4 passos obrigatórios):**

1. **Reproduzir falha** com o TRUTH command:
   ```bash
   python scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && pytest -q tests/training/ 2>&1 | tee /tmp/truth_run.txt
   ```
2. **Corrigir o produto** (código de produção, não o teste): identificar a causa no código/rota/serviço/invariante e corrigir.
3. **Rodar TRUTH novamente** até `0 failed`:
   ```bash
   python scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && pytest -q tests/training/
   ```
4. **Registrar evidência mínima:**
   - Saída pytest (`X passed, 0 failed`)
   - RH-09a: `rg` retornando exit 1 = 0 matches
   - RH-09b: `rg` retornando exit 1 = 0 matches

> Se a falha persistir após correção do produto, abrir nova AR com classe `T` ou `E` conforme escopo. Não marcar como PASS enquanto `pytest` retornar `FAILED`.

**Aplicação:** `EVID-*` = `[DESCRITIVO-AS-IS]`. `HIP-*` = `[HIPOTESE]`. `GAP-*` = `[GAP]`. `AR-*` com ACs aprovados = `[NORMATIVO]`. `DEC-*` = `[NORMATIVO]` quando resolvida.

> **Auditoria AS-IS, Gaps e Decisões Arquiteturais** → ver [TRAINING_ROADMAP.md](TRAINING_ROADMAP.md)

---

## 0) Objetivo (Normativo)

Decompor a materialização do módulo TRAINING em ARs pequenas, rastreáveis, testáveis e auditáveis, com:
- alvos SSOT explícitos (`INV/FLOW/SCREEN/CONTRACT`),
- ACs binários,
- estratégia de validação (incluindo tentativa de violação para invariantes bloqueantes),
- ordem e dependências.

---

## 1) Classes de AR (Padrão)

- **A** — Banco/Persistência
- **B** — Regras de Domínio/Services
- **C** — Cálculo/Derivados/Determinismo
- **D** — Frontend/UX
- **E** — Contrato Front-Back / integração
- **T** — Testes/Gates/Paridade
- **G** — Governança/Sync documental *(não conta para DONE_FASE_3_REAL)*
- **M** — Manutenção / Hard Sync FE (stubs/tipos) *(stubs pré-implementação não contam para DONE_FASE_3_REAL)*

> **Tag `[FASE_3_REAL]`**: aplicada a ARs de **implementação funcional** de FASE_3 (classes A/B/D/E com entregaveis operáveis).  
> ARs com tag `[FASE_3_SYNC]` são de sincronização documental ou stubs — **não entram** no cálculo `DONE_FASE_3_REAL_ATINGIDO`.  
> Regra de cálculo completa em `TEST_MATRIX_TRAINING.md` (seção `DONE_TRAINING_ATINGIDO`).

> **Regra NO_STUBS (IA Core) `[NORMATIVO]`:** ARs que tocam `ai_coach_service.py` ou módulos de decisão da IA DEVEM implementar lógica determinística real. Uso de `unittest.mock` / `MagicMock` no **código de produção** desses módulos é **PROIBIDO**. `RecognitionApproved`, `CoachSuggestionDraft` e `JustifiedSuggestion` são classes concretas de motor determinístico — não mocks. Ver RH-06/NO_STUBS em `TEST_MATRIX_TRAINING.md` (§5d) e evidências em `_reports/training/` quando aplicável.

---

## 2) Ordem sugerida (lotes)

### Lote 1 — Núcleo bloqueante (E/B/T)
1. AR-TRAIN-001 (E) — Convergir IDs UUID em Step18
2. AR-TRAIN-002 (B) — Corrigir implementação Step18 (alerts/suggestions)
3. AR-TRAIN-003 (D) — Corrigir Wellness FE (endpoints + payload)
4. AR-TRAIN-004 (B/E) — Corrigir wellness self-only (athlete_id) e simplificar payload
5. AR-TRAIN-005 (D) — Materializar presenças (justified + batch)

### Lote 2 — Paridade analytics/rankings (B/E/D)
6. AR-TRAIN-006 (B/C) — Corrigir cálculo e contratos de rankings wellness
7. AR-TRAIN-007 (D) — Corrigir Rankings/TopPerformers FE para UUID e endpoint canônico (`CONTRACT-TRAIN-076`)

### Lote 3 — Exports e gates (E/T/D)
8. AR-TRAIN-008 (E) — Reabilitar routers de export + atualizar OpenAPI SSOT + estado degradado sem worker
9. AR-TRAIN-009 (D) — Conectar ExportPDFModal ao backend reabilitado + estado degradado
10. AR-TRAIN-010A (T) — Testes/Gates: migrar refs `_generated` → `docs/ssot`
10b. AR-TRAIN-010B (T) — Testes de contrato/cobertura (workstream) — ver dependências

### Lote 4 — Banco de Exercícios (A/B/E/D) — novo pós DEC-TRAIN-EXB-*
11. AR-TRAIN-011 (A) — Materializar schema exercises (scope, visibility_mode) + tabelas exercise_acl e exercise_media
12. AR-TRAIN-012 (B/E) — Implementar guards de escopo SYSTEM/ORG + RBAC "Treinador" + service de ACL
13. AR-TRAIN-013 (B/E) — Implementar endpoints ACL + copy SYSTEM→ORG + visibilidade
14. AR-TRAIN-014 (D) — Materializar UI scope/visibility/ACL/mídia no exercise-bank FE

### Lote 5 — FASE_3: Ciclos, Presença oficial, Visão atleta, IA (A/B/E/D) `[FASE_3_REAL]`

> **Tag: `[FASE_3_REAL]`** — Todas as 7 ARs deste lote (AR-TRAIN-015..021) são implementação funcional FASE_3.  
> Contam para `DONE_FASE_3_REAL_ATINGIDO`. Status: todas VERIFICADO (AR_169..246, Batches 0..27).

15. AR-TRAIN-015 (A/B) `[FASE_3_REAL]` — Schema + Service ciclos hierarchy (macro→meso→micro)
16. AR-TRAIN-016 (B/E) `[FASE_3_REAL]` — Sessão standalone + mutabilidade + order_index exercícios
17. AR-TRAIN-017 (B/E) `[FASE_3_REAL]` — Presença oficial (pre-confirm atleta + closure treinador + pending)
18. AR-TRAIN-018 (D/E) `[FASE_3_REAL]` — UI fila de pendências (pending queue treinador)
19. AR-TRAIN-019 (D/E) `[FASE_3_REAL]` — Visão pré-treino atleta + wellness content gate
20. AR-TRAIN-020 (B/E) `[FASE_3_REAL]` — Pós-treino conversacional + feedback imediato
21. AR-TRAIN-021 (B/E) `[FASE_3_REAL]` — IA coach (drafts, chat, justificativas, privacidade)

### Lote 6 — Governança: Sync INVARIANTS_TRAINING.md (G)
22. AR-TRAIN-022 (G) — Sync INVARIANTS_TRAINING.md: promover 31 itens GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO com evidência ARs 011..021

> **Nota (v1.x.0 → v1.9.0):** ARs 023-031 foram adicionadas em patches posteriores como Batches 7-11 (fix FAILs críticos, evidências P0 de flows/contracts, Done Gate v1.8.0). Todas estão VERIFICADO. Ver detalhes nas seções §8 correspondentes.

### Lote 7 — Cobertura §10: Matrix Sync + 6 testes ausentes + run NOT_RUN (G/T)
32. AR-TRAIN-032 (G) — Sync §5 TEST_MATRIX: ~40 INV PENDENTE → COBERTO onde teste já existe no filesystem
33. AR-TRAIN-033 (T) — Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007

### Lote 8 — Cobertura §10: Executar NOT_RUN + evidências (T)
34. AR-TRAIN-034 (T) — Executar todos NOT_RUN (INV + EXB) + gerar evidências formais

### Lote 9 — Contratos P0 automatizados por domínio (E/T)
35. AR-TRAIN-035 (E) — Contract tests: Sessions CRUD (CONTRACT-001..012)
36. AR-TRAIN-036 (E) — Contract tests: Teams + Attendance (CONTRACT-013..028)
37. AR-TRAIN-037 (E) — Contract tests: Wellness pre/post (CONTRACT-029..039)
38. AR-TRAIN-038 (E) — Contract tests: Ciclos/Exercises/Analytics/Export (CONTRACT-040..095)
39. AR-TRAIN-039 (E) — Contract tests: IA Coach + Athlete view (CONTRACT-096/101..105)

### Lote 10 — DEC tests + Flows P1 + Screens (T)
40. AR-TRAIN-040 (T) — DEC tests automatizados (DEC-TRAIN-001..004, EXB-*, RBAC-*)
41. AR-TRAIN-041 (T) — Flows P1 evidências MANUAL_GUIADO (FLOW-007..016/019..021)
42. AR-TRAIN-042 (T) — Screens smoke tests MANUAL_GUIADO (SCREEN-001..025)

### Lote 11 — Done Gate §10 final (G)
43. AR-TRAIN-043 (G) — Done Gate §10: sync TEST_MATRIX v2.0.0 + full suite verde + declaração final

### Lote 12 — Batch 18: Fix FAILs de test-layer (T)
44. AR-TRAIN-044 (T) — Fix async fixtures: `@pytest.fixture` → `@pytest_asyncio.fixture` (~23+ tests, 7 arquivos)
45. AR-TRAIN-045 (T) — Fix DB fixture setup: `category_id` NOT NULL + FK `team_registrations` (~57+ ERROs setup)
46. AR-TRAIN-046 (T) — Fix símbolos determinísticos ausentes em ai_coach_service (`RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`) — ERRORs de coleta INV-079/080/081
47. AR-TRAIN-047 (T) — Fix residuais mistos + validação done gate (0 FAILs suite completa)

### Lote 13 — Batch 19: Sincronização em Lote app layer (A/E)
48. AR-TRAIN-048 (A/E) — Sync app/models/ (constraints INV-010/035/036/054) + app/services/ (assinaturas contrato v1.3.0) + símbolos determinísticos IA Coach (implementações reais de `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion`)

### Lote 14 — Batch 20: Fix residuais test-layer pós-Batch 18/19 (T)
49. AR-TRAIN-049 (T) — Fix 6 FAILs + 10 ERRORs residuais em tests/training/invariants/ (test_018_route, test_035, test_058, test_059, test_063, test_064, test_076, test_acl_006)

### Lote 15 — Batch 21: Sync §5 TEST_MATRIX pós-Batches 17-20 (G)
50. AR-TRAIN-050 (G) — Sync §5 TEST_MATRIX_TRAINING.md: 11 itens (INV-079/080/081: NOT_RUN→PASS; INV-018/035/058/059/063/064/076/EXB-ACL-006: FAIL/ERROR→PASS) refletindo AR-TRAIN-046 + AR-TRAIN-049 VERIFICADOS

### Lote 16 — Batch 22: Done Gate §10 formal pós-Batch 21 (G) [substitui AR-TRAIN-043 OBSOLETA]
51. AR-TRAIN-051 (G) — Done Gate §10 final: declaração formal Done + bump TEST_MATRIX v2.2.0→v3.0.0 + §10/§0 preenchidos + §9 entry AR-TRAIN-051

### Lote 17 — Batches 23-26: FASE_3 FE sync + BE endpoints + doc sync (M/E/G)
52. AR-TRAIN-052 (M) — Frontend Hard Sync v1.3.0: tipos UUID/standalone + stubs CONTRACT-096..105 + AICoach justification (AR_236, Batch 23)
53. AR-TRAIN-053 (G) — Sync §9 TEST_MATRIX: entry AR-TRAIN-052 VERIFICADO pós-Batch 23 (AR_237, Batch 24)
54. AR-TRAIN-054 (G) — Sync §5 FASE_3: 18 INVs FAIL/ERROR→2026-03-04 + v3.1.0 + §9 entries AR-TRAIN-053/054 (AR_238, Batch 25)
55. AR-TRAIN-055 (E) `[FASE_3_REAL]` — BE: PATCH /attendance/pending-items/{item_id}/resolve (AR_239, Batch 26)
56. AR-TRAIN-056 (E) `[FASE_3_REAL]` — BE: PATCH /ai/coach/draft/{draft_id}/apply + POST /ai/coach/justify-suggestion (AR_240, Batch 26)
57. AR-TRAIN-057 (E) `[FASE_3_REAL]` — BE: GET /athlete/wellness-content-gate/{session_id} (AR_241, Batch 26)
58. AR-TRAIN-058 (M) `[FASE_3_REAL]` — FE: corrigir URLs training-phase3.ts — CONTRACT-097/101/102/103/104 (AR_242, Batch 26)
59. AR-TRAIN-059 (G) `[FASE_3_SYNC]` — Sync TEST_MATRIX §8/§9 + BACKLOG pós-Batch 26 + v3.2.0 (AR_243, Batch 26)

### Lote 18 — Batch 27: Governance Sync + Contract tests (G/T)
60. AR-TRAIN-060 (G) `[FASE_3_SYNC]` — Governance: Kanban retroativo Batches 23-26 (AR_244, Batch 27) ✅ VERIFICADO
61. AR-TRAIN-061 (T) — Contract tests: CONTRACT-TRAIN-074/075 wellness-rankings (AR_245, Batch 27) ✅ VERIFICADO
62. AR-TRAIN-062 (G) `[FASE_3_SYNC]` — Sync Backlog + TEST_MATRIX §9 pós-Batch 27 (AR_246, Batch 28) ✅ VERIFICADO

### Lote 19 — Batch 29: TRUTH SUITE Residuals (T/B/G)
63. AR-TRAIN-063 (T/G) — Fase 0+1: TRUTH SUITE dupla + triage 4 buckets (AR_247, Batch 29) ✅ VERIFICADO
64. AR-TRAIN-064 (B) — Fix user.organization_id not a column (unblock xfail INV-148) (AR_248, Batch 29) ✅ VERIFICADO
65. AR-TRAIN-065 (B/E) — Fix 4 SKIP em test_058 e test_059 (AR_249, Batch 29) ✅ VERIFICADO
66. AR-TRAIN-066 (T) `[NO_MOCKS_GLOBAL]` — Converter 9 LEGACY_INVALID para TRUTH (AR_250, Batch 29) ✅ VERIFICADO
67. AR-TRAIN-067 (G) `[FASE_3_SYNC]` — Sync documental pós-Batch 29: Backlog + TEST_MATRIX + DONE_GATE(relatório) + Kanban (AR_251, Batch 29) ✅ VERIFICADO

---

## 3) Tabela resumo do backlog de ARs

| AR ID | Classe | Prioridade | Objetivo | Alvos SSOT | Dependências | Status |
|---|---|---|---|---|---|---|
| AR-TRAIN-001 | E | ALTA | Tipar IDs Step18 como UUID e alinhar contrato | CONTRACT-TRAIN-077..085, INV-TRAIN-014 | - | VERIFICADO |
| AR-TRAIN-002 | B | ALTA | Tornar Step18 funcional com schema SSOT | INV-TRAIN-014, INV-TRAIN-023 | AR-TRAIN-001 | VERIFICADO |
| AR-TRAIN-003 | D | ALTA | Corrigir Wellness FE (paths + payload schema + self-only sem athlete_id) | FLOW-TRAIN-005/006, SCREEN-TRAIN-018/019, CONTRACT-TRAIN-029..039 | - | VERIFICADO |
| AR-TRAIN-004 | B/E | ALTA | Corrigir wellness self-only (athlete_id inferido do token) e payload mínimo + mapeamento FE→payload | INV-TRAIN-002/003/026, CONTRACT-TRAIN-029..039 | AR-TRAIN-003 | VERIFICADO |
| AR-TRAIN-005 | D | ALTA | Materializar UI de presenças (justified + batch) | FLOW-TRAIN-004, SCREEN-TRAIN-020, CONTRACT-TRAIN-025..028 | - | VERIFICADO |
| AR-TRAIN-006 | B/C/E | MEDIA | Corrigir rankings wellness (cálculo + response_model) | CONTRACT-TRAIN-073..075, INV-TRAIN-036/027 | AR-TRAIN-004 | VERIFICADO |
| AR-TRAIN-007 | D | MEDIA | Corrigir Rankings/TopPerformers FE (UUID + endpoint canônico CONTRACT-TRAIN-076) | SCREEN-TRAIN-014/015, CONTRACT-TRAIN-073..076 | AR-TRAIN-006 | VERIFICADO |
| AR-TRAIN-008 | E | MEDIA | Reabilitar exports + atualizar OpenAPI SSOT + estado degradado sem worker | CONTRACT-TRAIN-086..090, INV-TRAIN-012/025 | - | VERIFICADO |
| AR-TRAIN-009 | D | MEDIA | Conectar ExportPDFModal (polling + history + rate limit + estado degradado) | FLOW-TRAIN-012, SCREEN-TRAIN-013, CONTRACT-TRAIN-086..089 | AR-TRAIN-008 | VERIFICADO |
| AR-TRAIN-010A | T | ALTA | Testes/Gates: migrar refs `_generated` → `docs/ssot` | INV-TRAIN-008/020/021/030/031/040/041, TEST_MATRIX_TRAINING | - | VERIFICADO |
| AR-TRAIN-010B | T | ALTA | Testes de contrato/cobertura (workstream) | INV-TRAIN-013/024, CONTRACT-TRAIN-073..075, CONTRACT-TRAIN-077..085, TEST_MATRIX_TRAINING | AR-TRAIN-001..009 | VERIFICADO |
| AR-TRAIN-011 | A | ALTA | Materializar schema exercises (scope, visibility_mode) + exercise_acl + exercise_media | INV-TRAIN-047..053, INV-TRAIN-EXB-ACL-001/006 | - | VERIFICADO |
| AR-TRAIN-012 | B/E | ALTA | Guards de escopo SYSTEM/ORG + RBAC "Treinador" + service ACL + visibilidade | INV-TRAIN-048/051, INV-TRAIN-EXB-ACL-002..005/007 | AR-TRAIN-011 | VERIFICADO |
| AR-TRAIN-013 | B/E | MEDIA | Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade | CONTRACT-TRAIN-091..095, INV-TRAIN-EXB-ACL-001..007 | AR-TRAIN-012 | VERIFICADO |
| AR-TRAIN-014 | D | MEDIA | UI scope/visibility/ACL/mídia no exercise-bank FE | SCREEN-TRAIN-010/011, FLOW-TRAIN-009 | AR-TRAIN-013 | VERIFICADO |
| AR-TRAIN-015 | A/B | ALTA | Schema + Service ciclos hierarchy (macro→meso→micro) | INV-TRAIN-054..056, FLOW-TRAIN-008 | - | VERIFICADO |
| AR-TRAIN-016 | B/E | ALTA | Sessão standalone + mutabilidade + order_index exercícios | INV-TRAIN-057..059 | - | VERIFICADO |
| AR-TRAIN-017 | B/E | ALTA | Presença oficial (pre-confirm + closure + pending) | INV-TRAIN-063..066, FLOW-TRAIN-017, SCREEN-TRAIN-023, CONTRACT-TRAIN-097/098 | - | VERIFICADO |
| AR-TRAIN-018 | D/E | ALTA | UI fila de pendências (pending queue treinador) | INV-TRAIN-066/067, FLOW-TRAIN-018, SCREEN-TRAIN-023, CONTRACT-TRAIN-099/100 | AR-TRAIN-017 | VERIFICADO |
| AR-TRAIN-019 | D/E | ALTA | Visão pré-treino atleta + wellness content gate | INV-TRAIN-068/069/071/076/078, FLOW-TRAIN-016/021, SCREEN-TRAIN-022, CONTRACT-TRAIN-096/105 | AR-TRAIN-017 | VERIFICADO |
| AR-TRAIN-020 | B/E | MEDIA | Pós-treino conversacional + feedback imediato | INV-TRAIN-070/077 | AR-TRAIN-019 | VERIFICADO |
| AR-TRAIN-021 | B/E | MEDIA | IA coach (drafts, chat, justificativas, privacidade) | INV-TRAIN-072..075/079..081, FLOW-TRAIN-019/020, SCREEN-TRAIN-024/025, CONTRACT-TRAIN-101..104 | AR-TRAIN-020 | VERIFICADO |
| AR-TRAIN-022 | G | ALTA | Sync INVARIANTS_TRAINING.md: promover 31 itens GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO | INV-TRAIN-013/014/023/024/025/047..053/EXB-ACL-001..007/054..062/079..081 | AR-TRAIN-011..021 | VERIFICADO |
| AR-TRAIN-023 | G | ALTA | Sync TEST_MATRIX_TRAINING.md §9: AR-TRAIN-001..022 PENDENTE→VERIFICADO + desbloquear 7 INV + 9 CONTRACT | TEST_MATRIX_TRAINING.md §9/§5/§8 | AR-TRAIN-001/002/010A/022 | VERIFICADO |
| AR-TRAIN-024 | B | ALTA | Fix INV-001 test_invalid_case_2 — pytest assertion correto | INV-TRAIN-001, TEST_MATRIX_TRAINING | AR-TRAIN-010A | VERIFICADO |
| AR-TRAIN-025 | B | ALTA | Fix INV-008 schema_path: 3 .parent → 4 .parent | INV-TRAIN-008, TEST_MATRIX_TRAINING | AR-TRAIN-010A | VERIFICADO |
| AR-TRAIN-026 | B | ALTA | Fix INV-030 schema_path: 3 .parent → 4 .parent | INV-TRAIN-030, TEST_MATRIX_TRAINING | AR-TRAIN-010A | VERIFICADO |
| AR-TRAIN-027 | B | ALTA | Fix INV-032 6 async fixtures (pytest-asyncio) | INV-TRAIN-032, TEST_MATRIX_TRAINING | AR-TRAIN-010A | VERIFICADO |
| AR-TRAIN-028 | B | MEDIA | Fix CONTRACT-077-085 router path: 3 .parent → 4 .parent | CONTRACT-TRAIN-077..085 | AR-TRAIN-002 | VERIFICADO |
| AR-TRAIN-029 | E | ALTA | Flow P0 evidence MANUAL_GUIADO: FLOW-TRAIN-001..006/017/018 | FLOW-TRAIN-001..006/017/018 | AR-TRAIN-024..028 | VERIFICADO |
| AR-TRAIN-030 | B | ALTA | Contract P0 tests automatizados: CONTRACT-TRAIN-097..100 | CONTRACT-TRAIN-097..100 | AR-TRAIN-017/018/029 | VERIFICADO |
| AR-TRAIN-031 | G | ALTA | Done Gate v1.8.0: sync TEST_MATRIX §5/§6/§8/§9, declaração DONE | TEST_MATRIX_TRAINING.md §5/§6/§8/§9 | AR-TRAIN-024..030 | VERIFICADO |
| AR-TRAIN-032 | G | ALTA | Sync §5 TEST_MATRIX: ~40 INV PENDENTE→COBERTO onde teste já existe no filesystem | TEST_MATRIX_TRAINING.md §5/§0 | AR-TRAIN-031 | VERIFICADO |
| AR-TRAIN-033 | T | ALTA | Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007 | INV-TRAIN-053/060/061/062/EXB-ACL-005/007 | AR-TRAIN-032 | VERIFICADO |
| AR-TRAIN-034 | T | ALTA | Executar todos NOT_RUN + evidências formais em TEST_MATRIX | TEST_MATRIX_TRAINING.md §5 | AR-TRAIN-033 | VERIFICADO |
| AR-TRAIN-035 | E | ALTA | Contract tests: Sessions CRUD (CONTRACT-001..012) | CONTRACT-TRAIN-001..012 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-036 | E | ALTA | Contract tests: Teams + Attendance (CONTRACT-013..028) | CONTRACT-TRAIN-013..028 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-037 | E | ALTA | Contract tests: Wellness pre/post (CONTRACT-029..039) | CONTRACT-TRAIN-029..039 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-038 | E | MEDIA | Contract tests: Ciclos/Exercises/Analytics/Export (CONTRACT-040..095) | CONTRACT-TRAIN-040..095 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-039 | E | MEDIA | Contract tests: IA Coach + Athlete view (CONTRACT-096/101..105) | CONTRACT-TRAIN-096/101..105 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-040 | T | ALTA | DEC tests automatizados (DEC-TRAIN-001..004 + EXB-* + RBAC-*) | TEST_MATRIX_TRAINING.md §5b | AR-TRAIN-033 | VERIFICADO |
| AR-TRAIN-041 | T | MEDIA | Flows P1 evidências MANUAL_GUIADO (13 flows P1: FLOW-007..016/019..021) | FLOW-TRAIN-007..016/019..021 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-042 | T | MEDIA | Screens smoke tests MANUAL_GUIADO (25 telas: SCREEN-001..025) | SCREEN-TRAIN-001..025 | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-043 | G | ALTA | Done Gate §10 final: sync TEST_MATRIX v2.0.0 + full suite verde + declaração Done | TEST_MATRIX_TRAINING.md §10/§0/§9 | AR-TRAIN-034..042 | OBSOLETO |
| AR-TRAIN-044 | T | ALTA | Fix async fixtures: `@pytest.fixture` → `@pytest_asyncio.fixture` (~23+ tests, 7 arquivos) | tests/training/invariants/ | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-045 | T | ALTA | Fix DB fixture setup: `category_id` NOT NULL + FK `team_registrations` (~57+ ERROs setup) | tests/training/invariants/ | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-046 | T | ALTA | Fix import stubs ausentes em ai_coach_service (3 ERRORs coleta: INV-079/080/081) | tests/training/invariants/ | AR-TRAIN-034 | VERIFICADO |
| AR-TRAIN-047 | T | ALTA | Fix residuais mistos + validação done gate (0 FAILs suite completa) | tests/training/invariants/ | AR-TRAIN-044..046 | REJEITADO |
| AR-TRAIN-048 | A/E | CRÍTICA | Sync app/models/ (constraints INV-010/035/036/054) + app/services/ (assinaturas contrato v1.3.0) + stubs IA Coach | app/models/, app/services/, openapi.json | AR-TRAIN-044..047 | VERIFICADO |
| AR-TRAIN-049 | T | CRÍTICA | Fix 6 FAILs + 10 ERRORs residuais em tests/training/invariants/ (test_018_route, 035, 058, 059, 063, 064, 076, acl_006) | tests/training/invariants/ | AR-TRAIN-048 | VERIFICADO |
| AR-TRAIN-050 | G | ALTA | Sync §5 TEST_MATRIX_TRAINING.md: 11 itens (INV-079/080/081 NOT_RUN→PASS; INV-018/035/058/059/063/064/076/EXB-ACL-006 FAIL/ERROR→PASS) | TEST_MATRIX_TRAINING.md §5 | AR-TRAIN-046/049 | VERIFICADO |
| AR-TRAIN-051 | G | ALTA | Done Gate §10 final: declaração formal Done + bump TEST_MATRIX→v3.0.0 + §10/§0/§9 preenchidos | TEST_MATRIX_TRAINING.md §10/§0/§9 | AR-TRAIN-050 | VERIFICADO |
| AR-TRAIN-052 | M | ALTA | Frontend Hard Sync v1.3.0 — tipos UUID/standalone + stubs CONTRACT-096..105 + AICoach justification | Hb Track - Frontend/src/ (5 arquivos) | AR-TRAIN-021/051 | VERIFICADO |
| AR-TRAIN-053 | G | MEDIA | Sync §9 TEST_MATRIX: entry AR-TRAIN-052 VERIFICADO pós-Batch 23 | TEST_MATRIX_TRAINING.md §9 | AR-TRAIN-052 | VERIFICADO |
| AR-TRAIN-054 | G | ALTA | Sync §5 FASE_3: 18 INVs FAIL/ERROR→PASS + v3.1.0 + §9 entries | TEST_MATRIX_TRAINING.md §0/§5/§9 | AR-TRAIN-052/053 | VERIFICADO |
| AR-TRAIN-055 | E | ALTA | BE: PATCH /attendance/pending-items/{item_id}/resolve | app/api/v1/routers/attendance.py | AR-TRAIN-017 | VERIFICADO |
| AR-TRAIN-056 | E | ALTA | BE: PATCH apply-draft + POST justify-suggestion AI Coach | app/api/v1/routers/ai_coach.py, app/services/ai_coach_service.py | AR-TRAIN-021 | VERIFICADO |
| AR-TRAIN-057 | E | ALTA | BE: GET /athlete/wellness-content-gate/{session_id} | app/api/v1/routers/athlete_training.py | AR-TRAIN-019 | VERIFICADO |
| AR-TRAIN-058 | M | ALTA | FE: corrigir URLs training-phase3.ts — CONTRACT-097/101/102/103/104 | Hb Track - Frontend/src/lib/api/training-phase3.ts | AR-TRAIN-055/056/057 | VERIFICADO |
| AR-TRAIN-059 | G | ALTA | Sync TEST_MATRIX §8/§9 + BACKLOG pós-Batch 26 + bump v3.2.0 | TEST_MATRIX_TRAINING.md, AR_BACKLOG_TRAINING.md | AR-TRAIN-055..058 | VERIFICADO |
| AR-TRAIN-060 | G | ALTA | Governance Sync: Kanban retroativo Batches 23-26 | docs/hbtrack/Hb Track Kanban.md | AR-TRAIN-059 | VERIFICADO |
| AR-TRAIN-061 | T | MEDIA | Contract tests: CONTRACT-TRAIN-074/075 wellness-rankings | tests/training/contracts/, TEST_MATRIX_TRAINING.md | AR-TRAIN-060, AR-TRAIN-006 | VERIFICADO |
| AR-TRAIN-062 | G | ALTA | Sync Backlog AR-TRAIN-060/061 VERIFICADO + TEST_MATRIX §9 + Batch 28 | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md | AR-TRAIN-061 | VERIFICADO |
| AR-TRAIN-063 | T/G | ALTA | Fase 0+1: TRUTH SUITE dupla + triage 4 buckets | `_reports/training/DONE_GATE_TRAINING.md` (RH-08 baseline 610p/4s/1xf/0f) | AR-TRAIN-062 | VERIFICADO |
| AR-TRAIN-064 | B | ALTA | Fix user.organization_id not a column (unblock xfail test_inv_train_148) | Hb Track - Backend/app/services/exercise_acl_service.py | AR-TRAIN-063 | VERIFICADO |
| AR-TRAIN-065 | B/E | ALTA | Fix 4 SKIP em test_inv_train_058 e test_inv_train_059 | tests/training/invariants/test_inv_train_058_*.py, test_inv_train_059_*.py | AR-TRAIN-063 | VERIFICADO |
| AR-TRAIN-066 | T | ALTA | Converter 9 LEGACY_INVALID para TRUTH (NO_MOCKS_GLOBAL) | tests/training/invariants/ (9 arquivos) | AR-TRAIN-065 | VERIFICADO |
| AR-TRAIN-067 | G | ALTA | Sync documental pós-Batch 29: Backlog + TEST_MATRIX + DONE_GATE (relatório) + Kanban | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, `_reports/training/DONE_GATE_TRAINING.md`, Hb Track Kanban.md | AR-TRAIN-066 | VERIFICADO |
| AR-TRAIN-068 | M | MEDIA | Refactor FE Wellness Pre/Pos: migrar WellnessPreForm+WellnessPostForm para cliente gerado (src/api/generated) | src/api/generated/api-instance.ts, WellnessPreForm.tsx, WellnessPostForm.tsx, AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md | AR-TRAIN-067 | VERIFICADO |
| AR-TRAIN-069 | B | ALTA | BE: implementar GET/PATCH wellness-pre e wellness-post por ID (fix stubs 501) | app/api/v1/routers/wellness_pre.py, app/api/v1/routers/wellness_post.py, app/services/wellness_pre_service.py, app/services/wellness_post_service.py, AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md | AR-TRAIN-068 | VERIFICADO |
| AR-TRAIN-070 | T | ALTA | Testes impl GET/PATCH wellness por ID (CONTRACT-031/032/037/038) | tests/training/contracts/test_contract_train_029_039_wellness.py, AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md | AR-TRAIN-069 | VERIFICADO |
| AR-TRAIN-071 | G | ALTA | Sync documental pós-Batch 31+32: BACKLOG v3.6.0 + TEST_MATRIX v4.2.0 + Kanban Batch 32 + _INDEX v1.5.0 | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md, docs/hbtrack/modulos/treinos/_INDEX.md | AR-TRAIN-070 | VERIFICADO |
| AR-TRAIN-072 | D | ALTA | api-instance.ts: 9 singletons + fix interceptor (cyclesApi, microcyclesApi, sessionTemplatesApi, exercisesApi, exerciseTagsApi, exerciseFavoritesApi, athleteTrainingApi, aiCoachApi, attendanceApi) | Hb Track - Frontend/src/api/generated/api-instance.ts | AR-TRAIN-071 | VERIFICADO |
| AR-TRAIN-073 | D | ALTA | Migrar useSessions + useSessionTemplates para cliente gerado (trainingApi, sessionTemplatesApi) | src/lib/hooks/useSessions.ts, src/hooks/useSessionTemplates.ts | AR-TRAIN-072 | VERIFICADO |
| AR-TRAIN-074 | D | ALTA | Migrar componentes session para generated client (9 componentes) | ConfiguracoesClient.tsx, CreateTemplateModal.tsx, EditTemplateModal.tsx, EditSessionModal.tsx, CreateSessionModal.tsx, CreateTrainingModal.tsx, OverviewTab.tsx, StatsTab.tsx, TrainingsTab.tsx | AR-TRAIN-073 | VERIFICADO |
| AR-TRAIN-075 | D | ALTA | Migrar useCycles + useMicrocycles + useExercises para cliente gerado | src/lib/hooks/useCycles.ts, useMicrocycles.ts, src/hooks/useExercises.ts | AR-TRAIN-074 | VERIFICADO |
| AR-TRAIN-076 | D | ALTA | Migrar exercise components + training-phase3.ts para cliente gerado | ExerciseACLModal.tsx, ExerciseVisibilityToggle.tsx, src/lib/api/training-phase3.ts | AR-TRAIN-075 | VERIFICADO |
| AR-TRAIN-077 | B | ALTA | Fix DEC-TRAIN-004 export-pdf 503 → 202 (exports.py degraded mode) | Hb Track - Backend/app/api/v1/routers/exports.py | AR-TRAIN-076 | VERIFICADO |
| AR-TRAIN-078 | G | ALTA | Sync documental pós-Batch 33: BACKLOG v3.7.0 + TEST_MATRIX v4.3.0 + Kanban Batch 33 + _INDEX v1.6.0 | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md, docs/hbtrack/modulos/treinos/_INDEX.md | AR-TRAIN-077 | VERIFICADO |
| AR-TRAIN-079 | D/E | ALTA | trainingAlertsSuggestionsApi singleton + TRAINING_FRONT_BACK_CONTRACT.md §5.10 DIVERGENTE→IMPLEMENTADO + useSuggestions.ts deferred CAP-001 | Hb Track - Frontend/src/api/generated/api-instance.ts, docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md | AR-TRAIN-078 | VERIFICADO |
| AR-TRAIN-080 | G | ALTA | Sync documental pós-Batch 34: BACKLOG v3.8.0 + TEST_MATRIX v4.4.0 + Kanban Batch 34 + _INDEX v1.7.0 | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md, docs/hbtrack/modulos/treinos/_INDEX.md | AR-TRAIN-079 | VERIFICADO |
| AR-TRAIN-081 | G | ALTA | DONE_CONTRACT_TRAINING.md registrado na cadeia canônica: _INDEX.md v1.8.0 + entry 6b | docs/hbtrack/modulos/treinos/_INDEX.md | AR-TRAIN-080 | VERIFICADO |
| AR-TRAIN-082 | A | ALTA | TRAINING_SCOPE_REGISTRY.yaml criado: 13 CORE + 7 EXTENDED + 2 EXPERIMENTAL | docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml | AR-TRAIN-081 | VERIFICADO |
| AR-TRAIN-083 | A | ALTA | TRAINING_STATE_MACHINE.yaml criado: 5 entidades stateful CORE | docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml | AR-TRAIN-082 | VERIFICADO |
| AR-TRAIN-084 | A | ALTA | TRAINING_PERF_LIMITS.json criado: 16 itens CORE com SLOs baseline | docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json | AR-TRAIN-083 | VERIFICADO |
| AR-TRAIN-085 | A | ALTA | traceability_training_core.csv criado como skeleton: 9 headers, 0 dados | docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv | AR-TRAIN-084 | VERIFICADO |
| AR-TRAIN-086 | G | ALTA | Sync documental pós-Batch 35: BACKLOG v3.9.0 + TEST_MATRIX v4.5.0 + Kanban Batch 35 + _INDEX v1.8.0 | AR_BACKLOG_TRAINING.md, TEST_MATRIX_TRAINING.md, Hb Track Kanban.md, docs/hbtrack/modulos/treinos/_INDEX.md | AR-TRAIN-085 | VERIFICADO |
| AR-TRAIN-REC-01 | G+A | ALTA | Reconciliacao: eliminar PUBLISHED/CLOSED/publish/close dos 3 artefatos de base + lifecycle canonico draft->scheduled->in_progress->pending_review->readonly + renomear 'limits'->'operations' em PERF_LIMITS | docs/hbtrack/modulos/treinos/_INDEX.md, TRAINING_SCOPE_REGISTRY.yaml, TRAINING_PERF_LIMITS.json | AR-TRAIN-086 (AR_270) VERIFICADO | VERIFICADO |
| AR-TRAIN-087 | G | ALTA | Sync documental pos-REC-01: BACKLOG v4.1.0 + TEST_MATRIX v4.6.0 + Kanban VERIFICADO | docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md, docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md, docs/hbtrack/Hb Track Kanban.md | AR-TRAIN-REC-01 (AR_271) VERIFICADO | EM_EXECUCAO |
| AR-TRAIN-REC-02 | A+G | ALTA | Reconciliacao contratual: TRAINING_FRONT_BACK_CONTRACT.md + OpenAPI /schedule+/finalize + cliente FE gerado | docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md, Hb Track - Backend/app/schemas/training_sessions.py, Hb Track - Backend/app/services/training_session_service.py, Hb Track - Backend/app/api/v1/routers/training_sessions.py, Hb Track - Backend/docs/ssot/openapi.json, Hb Track - Frontend/src/api/generated/api.ts, tests/training/state_machine/ | AR-TRAIN-REC-01 (AR_271) VERIFICADO + AR-TRAIN-087 (AR_272) | BACKLOG |
| AR-TRAIN-REC-03 | A+G | ALTA | Ledger de Sessao + Scheduler SKIP LOCKED + provas de imutabilidade (tabelas training_session_plans, training_session_adjustments, celery SKIP LOCKED) | Hb Track - Backend/alembic/versions, Hb Track - Backend/docs/ssot/schema.sql, Hb Track - Backend/app/models/training_session_plan.py, Hb Track - Backend/app/models/training_session_adjustment.py, Hb Track - Backend/app/core/celery_tasks.py, Hb Track - Backend/app/services/training_session_service.py, tests/training/side_effects/*, tests/training/state_machine/*, tests/training/invariants/* | AR-TRAIN-REC-02 (AR_273) VERIFICADO | BACKLOG |
| AR-TRAIN-REC-04 | A+G | ALTA | Superficie TRAINING reconciliada: TRAINING_USER_FLOWS.md (lexical purge /publish+/close), TRAINING_SCREENS_SPEC.md, traceability_training_core.csv preenchida, FE 3 secoes lifecycle | docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md, docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md, docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv, Hb Track - Frontend/src/app/*/training/sessions, Hb Track - Frontend/src/app/*/training/agenda | AR-TRAIN-REC-03 (AR_274) VERIFICADO | BACKLOG |
| AR-TRAIN-REC-05 | A | ALTA | Sunset final: remover stubs /publish+/close do router BE + openapi.json + cliente FE gerado | Hb Track - Backend/app/api/v1/routers/training_sessions.py, Hb Track - Backend/docs/ssot/openapi.json, Hb Track - Frontend/src/api/generated/api.ts | AR-TRAIN-REC-04 (AR_275) VERIFICADO | BACKLOG |

> **Critérios de classificação (BLOQUEANTE/NAO_BLOQUEANTE)** → ver `TEST_MATRIX_TRAINING.md` (definições + matriz §5)  
> **Regra de cálculo de DONE_FASE_3_REAL_ATINGIDO**: contar apenas ARs com tag `[FASE_3_REAL]`. ARs `[FASE_3_SYNC]` (classe G/M de sync documental e stubs) **não contam**.

---

## 4) Template completo por AR (obrigatório)

> Abaixo, cada AR já vem pré-preenchida para execução por agentes (Executor/Testador).

### AR-TRAIN-001 — Convergir IDs UUID em Step18 (alerts/suggestions)

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_126 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_126/executor_main.log
**Classe:** E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Tornar o contrato Step18 coerente com o DB SSOT, trocando IDs em path para UUID (team_id/alert_id/suggestion_id) e atualizando OpenAPI SSOT.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-014

**Flows:**
- FLOW-TRAIN-015

**Screens:**
- SCREEN-TRAIN-021

**Contracts:**
- CONTRACT-TRAIN-077..085

#### 8.2 Tipo de mudança esperada
- [ ] API / Contrato
- [ ] Documentação MCP (ajuste)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** -

#### 8.4 Escopo de leitura (READ)
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/docs/ssot/openapi.json`
- `Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py`
- `Hb Track - Backend/app/models/training_alert.py`
- `Hb Track - Backend/app/models/training_suggestion.py`

#### 8.5 Escopo de escrita (WRITE)
- `Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py`
- `Hb Track - Backend/docs/ssot/openapi.json` (regenerar/atualizar)
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md` (ajuste se necessário)

#### 8.6 Fora do escopo / MUST NOT
- Não alterar schema do banco nesta AR.
- Não implementar UI.

#### 8.7 Acceptance Criteria (AC)
##### AC-001
**PASS:** OpenAPI SSOT define `team_id`, `alert_id`, `suggestion_id` como `string(uuid)` nas rotas Step18.  
**FAIL:** Qualquer um permanecer como `integer`.

##### AC-002
**PASS:** Rotas Step18 aceitam UUID em runtime (sem erro de validação do FastAPI).  
**FAIL:** 422 por tipo inválido ao passar UUID.

#### 8.8 Estratégia de validação
**validation_command (preferencial):**
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_014_overload_alert_threshold.py
```

**Tentativa de violação:**
- Chamar endpoint Step18 com UUID em path; esperado: não falhar por parse/type.

#### 8.9 Evidências esperadas
- [ ] diff de router + OpenAPI SSOT atualizado
- [ ] output de teste/validação

---

### AR-TRAIN-002 — Corrigir Step18 (services/queries) para SSOT atual

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_175 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_175/executor_main.log
**Classe:** B  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Fazer Step18 (alerts/suggestions) operar sobre `training_alerts`/`training_suggestions` (UUID) e produzir listagens e ações apply/dismiss funcionais.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-014
- INV-TRAIN-023

**Contracts:**
- CONTRACT-TRAIN-077..085

#### 8.3 Dependências
- AR-TRAIN-001

#### 8.7 AC binário
##### AC-001
**PASS:** `dismiss` de alert/suggestion atualiza `dismissed_at/applied_at` no registro correto (UUID).  
**FAIL:** 404 indevido ou update em registro incorreto.

##### AC-002
**PASS:** `GET active/pending` retorna lista vazia ou itens válidos sem erro SQL.  
**FAIL:** exceção por mismatch de tipo (UUID/int) ou consulta em coluna inexistente.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py
```

---

### AR-TRAIN-003 — Corrigir Wellness FE (paths + payload)

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_169 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_169/executor_main.log
**Classe:** D  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Alinhar `src/lib/api/wellness.ts` e formulários athlete ao contrato SSOT (`/wellness-pre|/wellness-post`), ao payload mínimo canônico e ao modelo self-only (sem `athlete_id` no payload do atleta).

#### 8.1 Alvos SSOT
**Flows:**
- FLOW-TRAIN-005
- FLOW-TRAIN-006

**Screens:**
- SCREEN-TRAIN-018
- SCREEN-TRAIN-019

**Contracts:**
- CONTRACT-TRAIN-029..039

**Decisões incorporadas:**
- DEC-TRAIN-001 (self-only: atleta não envia `athlete_id`)
- DEC-TRAIN-002 (mapeamento UI→payload canônico)

#### 8.4 READ
- `Hb Track - Frontend/src/lib/api/wellness.ts`
- `Hb Track - Frontend/src/components/training/wellness/*`
- `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`

#### 8.5 WRITE
- `Hb Track - Frontend/src/lib/api/wellness.ts`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`
- `Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx`

#### 8.7 AC binário
##### AC-001
**PASS:** `submitWellnessPre(sessionId, data)` faz POST em `/api/v1/wellness-pre/training_sessions/{sessionId}/wellness_pre`.  
**FAIL:** POST para `/wellness_pre` ou 404 por path incorreto.

##### AC-002
**PASS:** Form de wellness pré coleta `sleep_hours` e envia payload compatível com DB (`fatigue_pre`/`stress_level` etc).  
**FAIL:** payload sem `sleep_hours` ou com campos incompatíveis sem mapeamento.

##### AC-003 (DEC-TRAIN-001)
**PASS:** Form de wellness pré/pós do atleta NÃO envia `athlete_id` no payload; backend infere do token.  
**FAIL:** payload contém campo `athlete_id` enviado pelo frontend atleta.

##### AC-004 (DEC-TRAIN-002)
**PASS:** Existe tabela documentada de mapeamento FE→payload canônico (UI slider → campo DB) no contrato.  
**FAIL:** Mapeamento ausente ou incompleto.

#### 8.8 Validação
- Typecheck/build do FE (comando conforme toolchain do repo).
- Tentativa de violação: preencher após deadline deve produzir bloqueio (INV-TRAIN-002).

---

### AR-TRAIN-004 — Corrigir wellness self-only (athlete_id) e payload mínimo (backend)

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_176 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_176/executor_main.log
**Classe:** E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Garantir que endpoints wellness aceitam payload mínimo (sem `organization_id/created_by_membership_id`) e que atleta opera self-only com `athlete_id` inferido do token (DEC-TRAIN-001).

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-002
- INV-TRAIN-003
- INV-TRAIN-026

**Contracts:**
- CONTRACT-TRAIN-029..039

#### 8.3 Dependências
- AR-TRAIN-003

#### 8.7 AC binário
##### AC-001
**PASS:** Atleta autenticado consegue submeter wellness sem informar `organization_id` e sem escolher `athlete_id` de terceiros.  
**FAIL:** 422 exigindo campos que o server pode inferir, ou permissões allow indevido.

##### AC-002
**PASS:** Staff lendo wellness de outros atletas registra `data_access_logs` (LGPD).  
**FAIL:** ausência de log em acesso staff.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_026_lgpd_access_logging.py
```

---

### AR-TRAIN-005 — Materializar presenças (UI) com `justified`

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_171 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_171/executor_main.log
**Classe:** D  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Integrar UI de presenças ao módulo training (tab no editor ou página) suportando `present|absent|justified` e batch save.

#### 8.1 Alvos SSOT
**Flows:**
- FLOW-TRAIN-004

**Screens:**
- SCREEN-TRAIN-020

**Contracts:**
- CONTRACT-TRAIN-025..028

**Invariantes:**
- INV-TRAIN-030

#### 8.7 AC binário
##### AC-001
**PASS:** UI permite marcar `justified` e exigir `reason_absence` (UX), sem violar `ck_attendance_absent_reason_null`.  
**FAIL:** UI envia `reason_absence` com `absent` ou não permite `justified`.

##### AC-002
**PASS:** Batch save envia payload válido e atualiza estatísticas.  
**FAIL:** erro 409/422 por payload inválido.

---

### AR-TRAIN-006 — Corrigir rankings wellness (backend) + tipar response_model

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_177 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_177/executor_main.log
**Classe:** B  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Tornar `/analytics/wellness-rankings*` determinístico no schema SSOT (UUIDs, team_registrations, attendance.presence_status) e com response_model no OpenAPI.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-036
- INV-TRAIN-027

**Contracts:**
- CONTRACT-TRAIN-073..075

#### 8.7 AC binário
##### AC-001
**PASS:** Endpoint retorna `team_id` UUID e taxas coerentes com `attendance(present|justified)` (definir regra) e `wellness_pre/post`.  
**FAIL:** uso de campos/tabelas legadas (`Attendance.present`, `Athlete.active`, `TeamMembership` para atletas).

---

### AR-TRAIN-007 — Corrigir Rankings/TopPerformers FE para UUID + endpoint canônico

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_178 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_178/executor_main.log
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Ajustar FE para tratar `team_id`/`athlete_id` como UUID strings e consumir endpoint canônico `CONTRACT-TRAIN-076` para top performers no FE principal (DEC-TRAIN-003).

#### 8.1 Alvos SSOT
**Screens:**
- SCREEN-TRAIN-014
- SCREEN-TRAIN-015

**Contracts:**
- CONTRACT-TRAIN-073..076

#### 8.7 AC binário
##### AC-001
**PASS:** `TopPerformersClient` não usa `parseInt` e funciona com UUID.  
**FAIL:** erro por `NaN`/type mismatch.

---

### AR-TRAIN-008 — Reabilitar exports + atualizar OpenAPI SSOT

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_179 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_179/executor_main.log
**Classe:** E  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Incluir routers de export no agregador v1, atualizar `docs/ssot/openapi.json` e implementar estado degradado explícito quando worker/Celery não estiver ativo (DEC-TRAIN-004).

#### 8.1 Alvos SSOT
**Contracts:**
- CONTRACT-TRAIN-086..090

**Invariantes:**
- INV-TRAIN-012
- INV-TRAIN-025

#### 8.7 AC binário
##### AC-001
**PASS:** OpenAPI SSOT passa a conter `/analytics/export-pdf`, `/analytics/exports*` e `/athletes/me/export-data`.  
**FAIL:** rotas continuam ausentes após reabilitar include_router.

##### AC-002 (DEC-TRAIN-004)
**PASS:** Endpoint de export retorna estado degradado explícito (ex.: `{"status": "unavailable", "reason": "worker_not_active"}`) quando worker/Celery não está ativo.  
**FAIL:** Endpoint aceita job sem worker e simula polling fake.

---

### AR-TRAIN-009 — Conectar ExportPDFModal (polling + history + rate limit + estado degradado)

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_180 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_180/executor_main.log
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Fazer o modal de export consumir endpoints reabilitados, apresentar evidência de job concluído e exibir estado degradado explícito quando worker indisponível (DEC-TRAIN-004).

#### 8.1 Alvos SSOT
**Screen:**
- SCREEN-TRAIN-013

**Contracts:**
- CONTRACT-TRAIN-086..089

**Invariantes:**
- INV-TRAIN-012

---

### AR-TRAIN-010A — Testes/Gates: SSOT path (migrar `_generated` → `docs/ssot`)

**Status:** VERIFICADO (2026-02-28)
> Promovido por Kanban+evidência: AR_173 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_173/executor_main.log
**Classe:** T  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Ajustar testes para SSOT atual (`docs/ssot`) removendo dependência de `docs/_generated/*`.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-008
- INV-TRAIN-020
- INV-TRAIN-021
- INV-TRAIN-030
- INV-TRAIN-031
- INV-TRAIN-040
- INV-TRAIN-041

#### 8.7 AC binário
##### AC-001
**PASS:** suite `Hb Track - Backend/tests/training/invariants/*` não depende de `docs/_generated/*`.  
**FAIL:** testes falham por arquivo inexistente.

---

### AR-TRAIN-010B — Testes de Contrato/Cobertura: contratos críticos (workstream)

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_195 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_195/executor_main.log
**Classe:** T  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Cobrir contratos críticos sem schema no OpenAPI e consolidar cobertura no `TEST_MATRIX_TRAINING`.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-013
- INV-TRAIN-024

**Contracts:**
- CONTRACT-TRAIN-073..075
- CONTRACT-TRAIN-077..085

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-001..009

#### 8.7 AC binário
##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` referencia `AR-TRAIN-010B` para os itens em escopo (ex.: `INV-TRAIN-013/024`).  
**FAIL:** Itens em escopo permanecem sem AR relacionada na matriz.

---

### AR-TRAIN-011 — Materializar schema exercises (scope, visibility_mode) + exercise_acl + exercise_media

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_181 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log
**Classe:** A  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Adicionar campos `scope`, `visibility_mode`, `created_by_user_id` à tabela `exercises` e criar tabelas `exercise_acl` e `exercise_media` com constraints conforme invariantes.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-047 (scope válido)
- INV-TRAIN-049 (ORG single org)
- INV-TRAIN-050 (favorite unique)
- INV-TRAIN-052 (media type+ref válidos)
- INV-TRAIN-EXB-ACL-001 (visibility_mode válido)
- INV-TRAIN-EXB-ACL-006 (ACL unique per exercise+user)

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001
- DEC-TRAIN-EXB-001B

#### 8.4 READ
- `Hb Track - Backend/docs/ssot/schema.sql`
- `Hb Track - Backend/app/models/exercise.py`

#### 8.5 WRITE
- `Hb Track - Backend/alembic/versions/` (nova migration)
- `Hb Track - Backend/app/models/exercise.py` (acrescentar campos)
- `Hb Track - Backend/app/models/exercise_acl.py` (novo)
- `Hb Track - Backend/app/models/exercise_media.py` (novo)
- `Hb Track - Backend/docs/ssot/schema.sql` (regenerar)

#### 8.6 MUST NOT
- Não alterar schema de outras tabelas.
- Não implementar services/endpoints nesta AR (apenas schema+models).

#### 8.7 AC binário
##### AC-001
**PASS:** Migration cria `exercises.scope` (enum SYSTEM|ORG), `exercises.visibility_mode` (enum org_wide|restricted, default restricted), `exercises.created_by_user_id` (FK).  
**FAIL:** Campos ausentes ou sem constraint.

##### AC-002
**PASS:** Tabela `exercise_acl` existe com `(exercise_id FK, user_id FK)` e constraint unique.  
**FAIL:** Tabela ausente.

##### AC-003
**PASS:** Tabela `exercise_media` existe com `(exercise_id FK, media_type, reference)` e constraints de validação.  
**FAIL:** Tabela ausente.

#### 8.8 Validação
```bash
cd "Hb Track - Backend" && alembic upgrade head && python -c "from app.models.exercise import Exercise; print('OK')"
```

---

### AR-TRAIN-012 — Guards de escopo SYSTEM/ORG + RBAC "Treinador" + service ACL + visibilidade

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_182 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_182/executor_main.log
**Classe:** B/E  
**Prioridade:** ALTA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Implementar guards de escopo (SYSTEM imutável, ORG org-bound), filtro de visibilidade (org_wide+restricted+ACL), RBAC explícito "Treinador", e service de ACL com validação anti-cross-org.

#### 8.1 Alvos SSOT
**Invariantes:**
- INV-TRAIN-048 (SYSTEM imutável)
- INV-TRAIN-051 (catálogo respeita org)
- INV-TRAIN-EXB-ACL-002 (ACL apenas em restricted)
- INV-TRAIN-EXB-ACL-003 (anti-cross-org)
- INV-TRAIN-EXB-ACL-004 (autoridade do criador + RBAC)
- INV-TRAIN-EXB-ACL-005 (criador acesso implícito)
- INV-TRAIN-EXB-ACL-007 (ACL não retroquebra sessão)

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001

#### 8.3 Dependências
- AR-TRAIN-011

#### 8.5 WRITE
- `Hb Track - Backend/app/services/exercise_service.py` (guards scope, visibility, creator)
- `Hb Track - Backend/app/services/exercise_acl_service.py` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** PATCH/DELETE em exercício `SYSTEM` por usuário da organização retorna 403.  
**FAIL:** Edição permitida.

##### AC-002
**PASS:** Listagem de exercícios para usuário da org X retorna apenas `SYSTEM` + `ORG` da org X, respeitando `visibility_mode` e ACL.  
**FAIL:** Exercícios de org Y visíveis.

##### AC-003
**PASS:** Adicionar user de org Y à ACL de exercício org X retorna 400/422 (validação anti-cross-org).  
**FAIL:** ACL aceita user cross-org.

##### AC-004
**PASS:** Treinador B (não criador) tenta alterar `visibility_mode` ou ACL de exercício de treinador A → 403.  
**FAIL:** Alteração permitida.

##### AC-005 (RBAC)
**PASS:** Guard de criação/edição de exercício ORG verifica papel RBAC explícito "Treinador" (identificador no contrato, não inferência genérica).  
**FAIL:** Guard usa verificação genérica ou ausente.

---

### AR-TRAIN-013 — Endpoints ACL + copy SYSTEM→ORG + toggle visibilidade

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_183 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_183/executor_main.log
**Classe:** B/E  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Expor endpoints de ACL (listar/adicionar/remover), toggle de `visibility_mode`, e cópia de exercício SYSTEM→ORG no router de exercises.

#### 8.1 Alvos SSOT
**Contracts:**
- CONTRACT-TRAIN-091 (PATCH visibility)
- CONTRACT-TRAIN-092 (GET ACL)
- CONTRACT-TRAIN-093 (POST ACL)
- CONTRACT-TRAIN-094 (DELETE ACL user)
- CONTRACT-TRAIN-095 (POST copy-to-org)

**Invariantes:**
- INV-TRAIN-EXB-ACL-001..007
- INV-TRAIN-047, INV-TRAIN-048

#### 8.3 Dependências
- AR-TRAIN-012

#### 8.5 WRITE
- `Hb Track - Backend/app/api/v1/routers/exercises.py` (novos endpoints)
- `Hb Track - Backend/docs/ssot/openapi.json` (regenerar)

#### 8.7 AC binário
##### AC-001
**PASS:** `POST /exercises/{id}/copy-to-org` cria cópia ORG de exercício SYSTEM com `scope=ORG` e `created_by_user_id` do solicitante.  
**FAIL:** Cópia em exercício já ORG ou altera o original SYSTEM.

##### AC-002
**PASS:** `PATCH /exercises/{id}/visibility` aceita `org_wide|restricted` apenas para ORG por criador.  
**FAIL:** Aceita para SYSTEM ou por não-criador.

##### AC-003
**PASS:** `POST /exercises/{id}/acl` adiciona user da mesma org e retorna 201.  
**FAIL:** Aceita user cross-org ou em exercício sem `restricted`.

---

### AR-TRAIN-014 — UI scope/visibility/ACL/mídia no exercise-bank FE

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_184 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_184/executor_main.log
**Classe:** D  
**Prioridade:** MEDIA  
**Fase:** FASE_2  
**Objetivo da AR (1 frase):** Materializar no FE: indicador de escopo (SYSTEM/ORG), toggle de visibilidade, UI de ACL, ação "duplicar para ORG", preview de mídia e permissões RBAC "Treinador".

#### 8.1 Alvos SSOT
**Screens:**
- SCREEN-TRAIN-010
- SCREEN-TRAIN-011

**Flows:**
- FLOW-TRAIN-009

**Contracts:**
- CONTRACT-TRAIN-053..062, CONTRACT-TRAIN-091..095

**Decisões incorporadas:**
- DEC-TRAIN-EXB-001, DEC-TRAIN-EXB-001B, DEC-TRAIN-EXB-002, DEC-TRAIN-EXB-RBAC-001

#### 8.3 Dependências
- AR-TRAIN-013

#### 8.5 WRITE
- `Hb Track - Frontend/src/app/(admin)/training/exercise-bank/*`
- `Hb Track - Frontend/src/components/training/exercises/*`

#### 8.7 AC binário
##### AC-001
**PASS:** Card de exercício exibe badge `SYSTEM` ou `ORG` e ação "Duplicar para Meu Banco" quando SYSTEM.  
**FAIL:** Escopo não visível ou ação de duplicar ausente.

##### AC-002
**PASS:** Exercício ORG exibe toggle `org_wide|restricted` visível apenas para o criador (role Treinador).  
**FAIL:** Toggle visível para todos ou em exercício SYSTEM.

##### AC-003
**PASS:** Em modo `restricted`, UI exibe lista de ACL (usuários) + botão de compartilhar (busca de usuários da org).  
**FAIL:** ACL sem UI ou permitindo users cross-org.

##### AC-004
**PASS:** Preview de mídia (imagens, vídeos, links) funcional nos modais de detalhes.  
**FAIL:** Mídia não renderizada.

---

### AR-TRAIN-015 — Schema + Service ciclos hierarchy (macro→meso→micro)

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_189 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_189/executor_main.log
**Classe:** A/B  
**Prioridade:** ALTA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Garantir que ciclos macro→meso→micro tenham hierarquia FK obrigatória (INV-054), meso overlap permitido (INV-055) e micro contido em meso (INV-056).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-054, INV-TRAIN-055, INV-TRAIN-056  
**Flows:** FLOW-TRAIN-008  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** -

#### 8.5 WRITE
- `Hb Track - Backend/app/models/training_cycle.py` (FK hierarchy)
- `Hb Track - Backend/app/services/training_cycle_service.py` (validação containment)

#### 8.7 AC binário
##### AC-001
**PASS:** Micro-ciclo sem `mesocycle_id` válido é rejeitado (FK enforced).  
**FAIL:** Criação aceita micro sem meso.

##### AC-002
**PASS:** Micro-ciclo com datas fora do range do meso é rejeitado pelo service.  
**FAIL:** Micro fora do intervalo aceito.

##### AC-003
**PASS:** Dois meso-ciclos com overlap temporal no mesmo macro são aceitos.  
**FAIL:** Overlap rejeitado indevidamente.

---

### AR-TRAIN-016 — Sessão standalone + mutabilidade + order_index exercícios

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_190 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_190/executor_main.log
**Classe:** B/E  
**Prioridade:** ALTA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Garantir que sessão suporte flag `standalone` explícito (INV-057), estrutura mutável até close (INV-058) e `order_index` contíguo/único em exercícios (INV-059).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-057, INV-TRAIN-058, INV-TRAIN-059  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** -

#### 8.5 WRITE
- `Hb Track - Backend/app/services/training_session_service.py` (standalone flag + mutable guard)
- `Hb Track - Backend/app/services/session_exercise_service.py` (order_index validation)

#### 8.7 AC binário
##### AC-001
**PASS:** Sessão sem micro-ciclo requer `is_standalone=true`; sessão em ciclo requer `is_standalone=false`.  
**FAIL:** Flag inconsistente aceito.

##### AC-002
**PASS:** PATCH em sessão `closed` retorna 409/403 (estrutura imutável após close).  
**FAIL:** Sessão fechada permite edição de exercícios.

##### AC-003
**PASS:** `order_index` dos exercícios é contíguo (1,2,3...) e unique por sessão; reorder mantém contiguidade.  
**FAIL:** Gaps ou duplicatas em `order_index`.

---

### AR-TRAIN-017 — Presença oficial (pre-confirm + closure + pending)

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_185 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_185/executor_main.log
**Classe:** B/E  
**Prioridade:** ALTA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Implementar presença oficial: pré-confirmação do atleta (não oficial, INV-063), presença oficial no fechamento pelo treinador (INV-064), inconsistências viram pending (INV-065/066).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-063, INV-TRAIN-064, INV-TRAIN-065, INV-TRAIN-066  
**Flows:** FLOW-TRAIN-017  
**Screens:** SCREEN-TRAIN-023 (parcial)  
**Contracts:** CONTRACT-TRAIN-097, CONTRACT-TRAIN-098  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** -

#### 8.5 WRITE
- `Hb Track - Backend/app/services/attendance_service.py` (pre-confirm + official at closure)
- `Hb Track - Backend/app/api/v1/routers/attendance.py` (novos endpoints pre-confirm/close)
- `Hb Track - Backend/app/models/pending_item.py` (novo — fila de pendências)

#### 8.7 AC binário
##### AC-001
**PASS:** Pré-confirmação do atleta gera registro `is_official=false`; não altera status oficial.  
**FAIL:** Pré-confirmação cria presença oficial.

##### AC-002
**PASS:** Fechamento da sessão pelo treinador gera registros oficiais; divergências viram itens pending.  
**FAIL:** Fechamento ignora inconsistências sem gerar pending.

##### AC-003
**PASS:** Atleta que pré-confirmou mas treinador marcou ausente gera pending com ambas as versões.  
**FAIL:** Discrepância silenciada.

---

### AR-TRAIN-018 — UI fila de pendências (pending queue treinador)

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_186 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_186/executor_main.log
**Classe:** D/E  
**Prioridade:** ALTA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Materializar UI de fila de pendências para o treinador resolver discrepâncias de presença, com colaboração do atleta sem poder de validação (INV-066/067).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-066, INV-TRAIN-067  
**Flows:** FLOW-TRAIN-018  
**Screens:** SCREEN-TRAIN-023  
**Contracts:** CONTRACT-TRAIN-099, CONTRACT-TRAIN-100  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-017

#### 8.5 WRITE
- `Hb Track - Frontend/src/app/(admin)/training/pending-queue/*` (novo)
- `Hb Track - Frontend/src/lib/api/pending.ts` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** Treinador vê lista de itens pending filtráveis por sessão/atleta/data.  
**FAIL:** Fila não renderizada ou sem filtros.

##### AC-002
**PASS:** Atleta pode enviar justificativa/evidência ao item pending, mas NÃO pode validar/fechar.  
**FAIL:** Atleta consegue resolver o item por conta própria.

##### AC-003
**PASS:** Treinador resolve item pending com novo `presence_status` final e justificativa.  
**FAIL:** Resolução não atualiza attendance oficial.

---

### AR-TRAIN-019 — Visão pré-treino atleta + wellness content gate

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_187 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_187/executor_main.log
**Classe:** D/E  
**Prioridade:** ALTA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Permitir que atleta visualize treino antes da sessão (INV-068/069), com bloqueio de conteúdo completo se wellness obrigatório não preenchido (INV-071/076/078).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-068, INV-TRAIN-069, INV-TRAIN-071, INV-TRAIN-076, INV-TRAIN-078  
**Flows:** FLOW-TRAIN-016, FLOW-TRAIN-021  
**Screens:** SCREEN-TRAIN-022  
**Contracts:** CONTRACT-TRAIN-096, CONTRACT-TRAIN-105  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-017

#### 8.5 WRITE
- `Hb Track - Backend/app/api/v1/routers/athlete_training.py` (novo — preview endpoint)
- `Hb Track - Backend/app/services/wellness_gate_service.py` (novo — content gate)
- `Hb Track - Frontend/src/app/(athlete)/training/[sessionId]/*` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** Atleta vê preview do treino (exercícios, horário, objetivos) antes da sessão.  
**FAIL:** 404 ou conteúdo inacessível.

##### AC-002
**PASS:** Atleta sem wellness pré preenchido recebe `wellness_blocked=true` e vê conteúdo reduzido.  
**FAIL:** Conteúdo completo sem wellness.

##### AC-003
**PASS:** Mídia de exercícios (vídeo/imagem) acessível ao atleta na visão de preview.  
**FAIL:** Mídia bloqueada para atleta.

##### AC-004
**PASS:** Tela de progresso exige compliance wellness (INV-078).  
**FAIL:** Progresso visível sem compliance.

---

### AR-TRAIN-020 — Pós-treino conversacional + feedback imediato

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_191 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_191/executor_main.log
**Classe:** B/E  
**Prioridade:** MEDIA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Implementar coleta pós-treino conversacional (INV-070) com feedback imediato do coach virtual (INV-077).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-070, INV-TRAIN-077  
**Flows:** FLOW-TRAIN-020 (parcial)  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-019

#### 8.5 WRITE
- `Hb Track - Backend/app/services/post_training_service.py` (novo)
- `Hb Track - Backend/app/api/v1/routers/post_training.py` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** Atleta pode submeter feedback pós-treino via interface conversacional (não apenas formulário).  
**FAIL:** Interface pós-treino é formulário estático sem conversação.

##### AC-002
**PASS:** Coach virtual gera feedback imediato baseado nos dados da sessão + wellness.  
**FAIL:** Feedback ausente ou genérico sem dados da sessão.

---

### AR-TRAIN-021 — IA coach (drafts, chat, justificativas, privacidade)

**Status:** VERIFICADO (2026-03-01)
> Promovido por Kanban+evidência: AR_192 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_192/executor_main.log
**Classe:** B/E  
**Prioridade:** MEDIA  
**Fase:** FASE_3  
**Objetivo da AR (1 frase):** Implementar IA coach: sugestões como rascunhos (INV-075/080), chat atleta (INV-072/073), conteúdo educativo independente (INV-074), justificativas obrigatórias (INV-081), privacidade (INV-079).

#### 8.1 Alvos SSOT
**Invariantes:** INV-TRAIN-072, INV-TRAIN-073, INV-TRAIN-074, INV-TRAIN-075, INV-TRAIN-079, INV-TRAIN-080, INV-TRAIN-081  
**Flows:** FLOW-TRAIN-019, FLOW-TRAIN-020  
**Screens:** SCREEN-TRAIN-024, SCREEN-TRAIN-025  
**Contracts:** CONTRACT-TRAIN-101, CONTRACT-TRAIN-102, CONTRACT-TRAIN-103, CONTRACT-TRAIN-104  

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-020

#### 8.5 WRITE
- `Hb Track - Backend/app/services/ai_coach_service.py` (novo)
- `Hb Track - Backend/app/api/v1/routers/ai_coach.py` (novo)
- `Hb Track - Frontend/src/app/(athlete)/ai-chat/[sessionId]/*` (novo)
- `Hb Track - Frontend/src/components/training/AICoachDraftModal.tsx` (novo)

#### 8.7 AC binário
##### AC-001
**PASS:** Sugestão IA para treinador é rascunho (`draft=true`) que requer aprovação explícita (INV-075/080).  
**FAIL:** Sugestão aplicada automaticamente sem aprovação.

##### AC-002
**PASS:** Chat IA com atleta não contém conteúdo íntimo/sensível (INV-073/079).  
**FAIL:** IA retorna dados de wellness/médicos de outros atletas.

##### AC-003
**PASS:** Conteúdo educativo funciona mesmo sem dados históricos do atleta (INV-074).  
**FAIL:** Conteúdo educativo requer histórico preexistente.

##### AC-004
**PASS:** Sugestão IA ao treinador inclui justificativa baseada em dados (INV-081).  
**FAIL:** Sugestão sem justificativa ou com justificativa genérica.

##### AC-005
**PASS:** IA trata sugestões como orientações não-obrigatórias (INV-072 — "not an order").  
**FAIL:** Sugestão apresentada como obrigatória.

---

### AR-TRAIN-022 — Sync INVARIANTS_TRAINING.md: promover GAP/PARCIAL/DIVERGENTE → IMPLEMENTADO

**Status:** VERIFICADO (2026-03-02)
> **Evidência:** AR_197 (hb seal 2026-03-02) — docs/hbtrack/evidence/AR_197/executor_main.log
**Classe:** G (Governança documental)
**Prioridade:** ALTA
**Fase:** Governança pós-Batch 3..5
**Objetivo da AR (1 frase):** Atualizar INVARIANTS_TRAINING.md promovendo 31 invariantes de GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO com evidência rastreável das ARs 011..021 já verificadas, bumpando versão para v1.5.0.

#### 8.1 Alvos SSOT
**Invariantes (31 itens):**
- INV-TRAIN-013 (PARCIAL → IMPLEMENTADO, evidência: AR_195 testes)
- INV-TRAIN-014 (DIVERGENTE_DO_SSOT → IMPLEMENTADO, evidência: AR_175 UUID fix)
- INV-TRAIN-023 (DIVERGENTE_DO_SSOT → IMPLEMENTADO, evidência: AR_175/176 UUID+self-only)
- INV-TRAIN-024 (PARCIAL → IMPLEMENTADO, evidência: AR_195 testes WS)
- INV-TRAIN-025 (PARCIAL → IMPLEMENTADO, evidência: AR_179/180 exports reabilitados)
- INV-TRAIN-047..053 (GAP → IMPLEMENTADO, evidência: AR_181 schema + AR_182 guards)
- INV-TRAIN-EXB-ACL-001..007 (GAP → IMPLEMENTADO, evidência: AR_181/182/183)
- INV-TRAIN-054..056 (GAP → IMPLEMENTADO, evidência: AR_189 ciclos hierarchy)
- INV-TRAIN-057 (GAP → IMPLEMENTADO, evidência: AR_190 standalone guard)
- INV-TRAIN-058..059 (PARCIAL → IMPLEMENTADO, evidência: AR_190 order_index)
- INV-TRAIN-060..062 (GAP → IMPLEMENTADO, evidência: AR_182/183 visibility+copy)
- INV-TRAIN-079..081 (GAP → IMPLEMENTADO, evidência: AR_192 IA coach)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-011, AR-TRAIN-012, AR-TRAIN-013, AR-TRAIN-014, AR-TRAIN-015, AR-TRAIN-016, AR-TRAIN-020, AR-TRAIN-021 (todas VERIFICADO)

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` (único arquivo; somente campos `status:` e `note:` dos 31 blocos yaml listados + header versão v1.5.0 + changelog)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/` (nenhum arquivo de código)
- `Hb Track - Frontend/` (nenhum arquivo de código)
- `docs/ssot/` (somente leitura para evidência)

#### 8.7 AC binário
##### AC-001
**PASS:** `INVARIANTS_TRAINING.md` não contém `status: GAP`, `status: PARCIAL` nem `status: DIVERGENTE_DO_SSOT` em nenhum bloco yaml de invariante (verificado via regex `(?m)^status:\s*(GAP|PARCIAL|DIVERGENTE_DO_SSOT)`).
**FAIL:** Algum dos 31 itens ainda contém status não-IMPLEMENTADO.

##### AC-002
**PASS:** Versão do documento atualizada para v1.5.0 com changelog v1.5.0 descrevendo os 31 itens promovidos.
**FAIL:** Versão não atualizada.

##### AC-003
**PASS:** Cada invariante promovido tem `note:` com rastreabilidade da AR de origem (ex.: `Promovido por Kanban+evidencia: AR_181 (hb seal 2026-03-01)`).
**FAIL:** Promoção sem nota de rastreabilidade.

---

### AR-TRAIN-023 — Sync TEST_MATRIX_TRAINING.md §9 pós-Batch 3..7

**Status:** VERIFICADO (2026-03-02)
> **Evidência:** AR_199 (hb seal 2026-03-02) — docs/hbtrack/evidence/AR_199/executor_main.log
**Classe:** G (Governança documental)
**Prioridade:** ALTA
**Fase:** Governança pós-Batch 3..7
**Objetivo da AR (1 frase):** Sincronizar TEST_MATRIX_TRAINING.md §9 promovendo AR-TRAIN-001/002/003/004/005/010A/010B/022 de PENDENTE → VERIFICADO; desbloquear INV-TRAIN-008/020/021/030/031/040/041 (BLOQUEADO→COBERTO) e CONTRACT-TRAIN-077..085 (BLOQUEADO→COBERTO); atualizar summary §0; bump versão v1.5.1 → v1.6.0.

#### 8.1 Alvos SSOT
**TEST_MATRIX_TRAINING.md:**
- §9: AR-TRAIN-001/002/003/004/005/010A/010B — PENDENTE → VERIFICADO (evidências confirmadas via Kanban)
- §9: AR-TRAIN-022 — adicionar entrada VERIFICADO (AR_197 hb seal 2026-03-02)
- §5: INV-TRAIN-008/020/021/030/031/040/041 — BLOQUEADO → COBERTO (dep: AR-TRAIN-010A VERIFICADO)
- §8: CONTRACT-TRAIN-077..085 — BLOQUEADO → COBERTO (dep: AR-TRAIN-001/002 VERIFICADO)
- §0: atualizar contadores (BLOQUEADO → 0; COBERTO +16)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-001 VERIFICADO, AR-TRAIN-002 VERIFICADO, AR-TRAIN-010A VERIFICADO, AR-TRAIN-022 VERIFICADO

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (único arquivo)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/` (nenhum arquivo de código)
- `Hb Track - Frontend/` (nenhum arquivo de código)
- Qualquer outro SSOT além de TEST_MATRIX_TRAINING.md
- **NÃO executar pytest** — execução de testes é escopo de AR futura

#### 8.7 AC binário
##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` contém `Versão: v1.6.0`.
**FAIL:** Versão não atualizada.

##### AC-002
**PASS:** §9 não contém nenhuma linha com `AR-TRAIN-00[12345]` ou `AR-TRAIN-010[AB]` com status PENDENTE.
**FAIL:** Alguma das 7 entradas ainda PENDENTE.

##### AC-003
**PASS:** AR-TRAIN-022 presente em §9 como VERIFICADO.
**FAIL:** AR-TRAIN-022 ausente ou não VERIFICADO.

##### AC-004
**PASS:** INV-TRAIN-008/020/021/030/031/040/041 não aparecem como BLOQUEADO.
**FAIL:** Algum item ainda BLOQUEADO.

##### AC-005
**PASS:** CONTRACT-TRAIN-077..085 não aparecem como BLOQUEADO.
**FAIL:** Algum contrato ainda BLOQUEADO.

---

### AR-TRAIN-024 — Fix INV-001: test_invalid_case_2 expected constraint name errado

**Status:** PENDENTE
**Classe:** T (Correção de teste)
**Prioridade:** CRÍTICA
**Fase:** Batch 9 — Fix FAILs críticos
**Objetivo da AR (1 frase):** Corrigir em test_inv_train_001_focus_sum_constraint.py a string de expected constraint name na função test_invalid_case_2__negative_focus de ck_training_sessions_focus_total_sum para ck_training_sessions_focus_attack_positional_range (o DB dispara range-check antes de sum-check em valores negativos).

#### 8.1 Alvos SSOT
- `INV-TRAIN-001` — test passa → status COBERTO, Últ.Execução atualizada

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** nenhuma

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_001_focus_sum_constraint.py`
- `_reports/training/TEST-TRAIN-INV-001.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` (nenhuma mudança de produto)
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py` = 0 FAILs, 0 ERRORs.
**FAIL:** Teste ainda FAIL ou ERROR.

---

### AR-TRAIN-025 — Fix INV-008: schema_path com 3 .parent (deve ser 4)

**Status:** PENDENTE
**Classe:** T (Correção de teste)
**Prioridade:** CRÍTICA
**Fase:** Batch 9 — Fix FAILs críticos
**Objetivo da AR (1 frase):** Corrigir em test_inv_train_008_soft_delete_reason_pair.py a definição de schema_path adicionando um .parent extra para que o path resolva para Hb Track - Backend/docs/ssot/schema.sql (existente) em vez de tests/docs/ssot/schema.sql (inexistente).

#### 8.1 Alvos SSOT
- `INV-TRAIN-008` — test passa → status COBERTO, Últ.Execução atualizada

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** nenhuma

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py`
- `_reports/training/TEST-TRAIN-INV-008.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py` = 0 FAILs, 0 ERRORs.
**FAIL:** Teste ainda FAIL ou ERROR.

---

### AR-TRAIN-026 — Fix INV-030: schema_path com 3 .parent (deve ser 4)

**Status:** PENDENTE
**Classe:** T (Correção de teste)
**Prioridade:** CRÍTICA
**Fase:** Batch 9 — Fix FAILs críticos
**Objetivo da AR (1 frase):** Mesma causa raiz do AR-TRAIN-025 (INV-008): corrigir em test_inv_train_030_attendance_correction_fields.py o schema_path com .parent extra para apontar para o schema.sql correto.

#### 8.1 Alvos SSOT
- `INV-TRAIN-030` — test passa → status COBERTO, Últ.Execução atualizada

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** nenhuma (paralela a AR-TRAIN-025)

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py`
- `_reports/training/TEST-TRAIN-INV-030.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_030_attendance_correction_fields.py` = 0 FAILs, 0 ERRORs.
**FAIL:** Teste ainda FAIL ou ERROR.

---

### AR-TRAIN-027 — Fix INV-032: async fixtures com @pytest.fixture (deve ser @pytest_asyncio.fixture)

**Status:** PENDENTE
**Classe:** T (Correção de teste)
**Prioridade:** CRÍTICA
**Fase:** Batch 9 — Fix FAILs críticos
**Objetivo da AR (1 frase):** Corrigir em test_inv_train_032_wellness_post_rpe.py os 6 fixtures async que usam @pytest.fixture (incompatível com pytest-asyncio modo strict) para @pytest_asyncio.fixture, adicionando import pytest_asyncio.

#### 8.1 Alvos SSOT
- `INV-TRAIN-032` — test passa → status COBERTO, Últ.Execução atualizada

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** nenhuma

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_032_wellness_post_rpe.py`
- `_reports/training/TEST-TRAIN-INV-032.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py` = 0 FAILs, 0 ERRORs, 0 PytestUnraisableExceptionWarning async.
**FAIL:** Teste ainda contém FAIL, ERROR ou warning de async fixture.

---

### AR-TRAIN-028 — Fix CONTRACT-077-085: ROUTER_PATH com 3 .parent (deve ser 4)

**Status:** PENDENTE
**Classe:** T (Correção de teste)
**Prioridade:** CRÍTICA
**Fase:** Batch 9 — Fix FAILs críticos
**Objetivo da AR (1 frase):** Corrigir em test_contract_train_077_085_alerts_suggestions.py a definição de ROUTER_PATH adicionando .parent extra para que o path resolva para Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py (existente) em vez de tests/app/... (inexistente).

#### 8.1 Alvos SSOT
- `CONTRACT-TRAIN-077..085` — test passa → Últ.Execução atualizada (evidência renovada)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** nenhuma (paralela às demais do Batch 9)

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py`
- `_reports/training/TEST-TRAIN-CONTRACT-077-085.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py` = 0 FAILs, 0 ERRORs.
**FAIL:** Teste ainda FAIL ou ERROR.

---

### AR-TRAIN-029 — Flow P0 evidence: FLOW-TRAIN-001..006 + 017 + 018 (MANUAL_GUIADO)

**Status:** PENDENTE
**Classe:** D (Documentação / Evidência)
**Prioridade:** ALTA
**Fase:** Batch 10 — Cobrir evidências P0 restantes
**Objetivo da AR (1 frase):** Criar 8 arquivos de evidência MANUAL_GUIADO para os flows P0 PENDENTE (FLOW-TRAIN-001..006 + 017 + 018) e atualizar TEST_MATRIX_TRAINING.md §6 marcando-os como COBERTO com evidência linkada.

#### 8.1 Alvos SSOT
- `FLOW-TRAIN-001/002/003/004/005/006/017/018` — status PENDENTE → COBERTO em §6 da TEST_MATRIX

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-024/025/026/027/028 VERIFICADO (Batch 9 completo)

#### 8.5 WRITE
- `_reports/training/TEST-TRAIN-FLOW-001.md`
- `_reports/training/TEST-TRAIN-FLOW-002.md`
- `_reports/training/TEST-TRAIN-FLOW-003.md`
- `_reports/training/TEST-TRAIN-FLOW-004.md`
- `_reports/training/TEST-TRAIN-FLOW-005.md`
- `_reports/training/TEST-TRAIN-FLOW-006.md`
- `_reports/training/TEST-TRAIN-FLOW-017.md`
- `_reports/training/TEST-TRAIN-FLOW-018.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§6)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/` (nenhum arquivo de produto)
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** Existem 8 arquivos `_reports/training/TEST-TRAIN-FLOW-00[1-6].md` + `TEST-TRAIN-FLOW-017.md` + `TEST-TRAIN-FLOW-018.md` com conteúdo MANUAL_GUIADO (não vazios, contêm seção de resultado PASS).
**FAIL:** Algum arquivo ausente ou vazio.

##### AC-002
**PASS:** TEST_MATRIX_TRAINING.md §6 mostra FLOW-TRAIN-001/002/003/004/005/006/017/018 com status COBERTO e evidência linkada.
**FAIL:** Algum flow ainda PENDENTE no §6.

---

### AR-TRAIN-030 — Contract P0 tests: CONTRACT-TRAIN-097..100 (pre-confirm, close, pending-items)

**Status:** PENDENTE
**Classe:** T (Teste novo) + G (sync TEST_MATRIX)
**Prioridade:** ALTA
**Fase:** Batch 10 — Cobrir evidências P0 restantes
**Objetivo da AR (1 frase):** Criar test_contract_train_097_100_presence_pending.py com testes de contrato para os 4 endpoints P0 PENDENTE (097/098/099/100), executar, gerar evidência e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- `CONTRACT-TRAIN-097/098/099/100` — status PENDENTE → COBERTO em §8 da TEST_MATRIX

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-017 VERIFICADO, AR-TRAIN-018 VERIFICADO, AR-TRAIN-029 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_097_100_presence_pending.py`
- `_reports/training/TEST-TRAIN-CONTRACT-097-100.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_097_100_presence_pending.py` = 0 FAILs, 0 ERRORs.
**FAIL:** Arquivo não existe, FAIL ou ERROR.

##### AC-002
**PASS:** TEST_MATRIX_TRAINING.md §8 mostra CONTRACT-TRAIN-097/098/099/100 com status COBERTO e evidência linkada.
**FAIL:** Algum contrato ainda PENDENTE no §8.

---

### AR-TRAIN-031 — Done Gate: sync TEST_MATRIX v1.8.0 + validar §10

**Status:** PENDENTE
**Classe:** G (Governança / Done Gate)
**Prioridade:** CRÍTICA
**Fase:** Batch 11 — Done Gate módulo TRAINING
**Objetivo da AR (1 frase):** Sincronizar TEST_MATRIX_TRAINING.md para v1.8.0 (§9 + §5 + §8 + §6 finais), rodar smoke suite dos 5 testes corrigidos, e produzir _reports/training/DONE_GATE_TRAINING.md declarando satisfação dos critérios §10.

#### 8.1 Alvos SSOT
- `TEST_MATRIX_TRAINING.md` — v1.7.0 → v1.8.0; §9 contém AR-TRAIN-024..030; §5/§6/§8 sincronizados; §0 contadores atualizados

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-024/025/026/027/028/029/030 todos VERIFICADO

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
- `_reports/training/DONE_GATE_TRAINING.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/`
- `Hb Track - Frontend/`
- Não criar novos testes nesta AR — apenas sync documental + smoke run

#### 8.7 AC binário
##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` contém `Versão: v1.8.0`.
**FAIL:** Versão não atualizada.

##### AC-002
**PASS:** §9 contém entries para AR-TRAIN-024..031 (ou até 030 conforme execução real).
**FAIL:** Alguma AR do Batch 9-10 ausente.

##### AC-003
**PASS:** `_reports/training/DONE_GATE_TRAINING.md` existe com declaração de Done Gate e lista dos critérios §10 satisfeitos.
**FAIL:** Arquivo ausente ou incompleto.

##### AC-004
**PASS:** Smoke pytest (5 testes: INV-001/008/030/032 + CONTRACT-077-085) = 0 FAILs.
**FAIL:** Qualquer FAIL no smoke.

---

### AR-TRAIN-032 — Sync §5 TEST_MATRIX: ~40 INV PENDENTE → COBERTO

**Status:** VERIFICADO (AR_211 — hb seal 2026-03-03)
**Classe:** G
**Prioridade:** ALTA
**Fase:** Batch 12 — Cobertura §10 (Dessincronia Matrix)
**Objetivo da AR (1 frase):** Atualizar TEST_MATRIX_TRAINING.md §5 para refletir o estado real do filesystem: ~40 invariantes marcadas PENDENTE cuja suite de teste já existe (criada pelas ARs 144-167 nos Batches 3-8).

#### 8.1 Alvos SSOT
- `TEST_MATRIX_TRAINING.md` — §5 (status INV), §0 (contadores), §9 (entry AR-TRAIN-032)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-031 VERIFICADO

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque
- `Hb Track - Frontend/`
- Não criar código nesta AR — apenas sync documental

#### 8.7 AC binário
##### AC-001
**PASS:** §5 da TEST_MATRIX não contém mais nenhuma linha com `PENDENTE` para INV cujo arquivo de teste existe em `Hb Track - Backend/tests/training/`.
**FAIL:** Ainda existem linhas PENDENTE para INV com arquivo de teste presente.

##### AC-002
**PASS:** §0 contadores atualizados refletem a real distribuição COBERTO/NOT_RUN/PENDENTE.
**FAIL:** Contadores divergem do estado real.

##### AC-003
**PASS:** §9 contém entry para AR-TRAIN-032 com status VERIFICADO.
**FAIL:** Entry ausente.

---

### AR-TRAIN-033 — Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007

**Status:** VERIFICADO (AR_212 — hb seal 2026-03-03)
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 12 — Cobertura §10 (6 testes faltantes)
**Objetivo da AR (1 frase):** Criar os 6 únicos arquivos de teste de invariante que realmente não existem no filesystem após a revisão de dessincronia.

#### 8.1 Alvos SSOT
- INV-TRAIN-053 (soft delete exercise não quebra sessões históricas)
- INV-TRAIN-060 (exercício ORG default visibility restricted)
- INV-TRAIN-061 (exercício SYSTEM copy → ORG, não edita original)
- INV-TRAIN-062 (exercise_visibility_mode required for session add)
- INV-TRAIN-EXB-ACL-005 (criador tem acesso implícito independente da ACL)
- INV-TRAIN-EXB-ACL-007 (mudança de ACL/visibilidade não invalida leitura histórica)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-032 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_062_exercise_visibility_required.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§5: status COBERTO para os 6 INV)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque em código de produto
- `Hb Track - Frontend/`

#### 8.7 AC binário
##### AC-001
**PASS:** Os 6 arquivos de teste existem com pelo menos 1 test case cada que testa a violação da invariante (assert de exceção ou status 4xx).
**FAIL:** Qualquer arquivo ausente ou sem test case de violação.

##### AC-002
**PASS:** `pytest tests/training/invariants/test_inv_train_053*.py tests/training/invariants/test_inv_train_060*.py tests/training/invariants/test_inv_train_061*.py tests/training/invariants/test_inv_train_062*.py tests/training/invariants/test_inv_train_exb_acl_005*.py tests/training/invariants/test_inv_train_exb_acl_007*.py` = 0 FAILs / 0 ERRORs.
**FAIL:** Qualquer FAIL ou ERROR.

---

### AR-TRAIN-034 — Executar todos NOT_RUN + evidências formais

**Status:** EM_EXECUCAO (AR_213 — Batch 13 planejado 2026-03-03)
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 13 — Execução NOT_RUN
**Objetivo da AR (1 frase):** Executar os ~60 testes marcados como COBERTO/NOT_RUN no §5 da TEST_MATRIX, capturar evidências de execução em _reports/training/evidence_run_batch13.txt e atualizar os status.

#### 8.1 Alvos SSOT
- `TEST_MATRIX_TRAINING.md` §5 — todas as linhas NOT_RUN → COBERTO com Últ.Execução preenchida

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-033 VERIFICADO

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
- `_reports/training/evidence_run_batch13.txt` (output pytest)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** §5 da TEST_MATRIX não contém mais nenhuma linha com status `NOT_RUN`.
**FAIL:** Ainda existem linhas NOT_RUN.

##### AC-002
**PASS:** `_reports/training/evidence_run_batch13.txt` existe com output pytest mostrando 0 FAILs para os testes executados.
**FAIL:** Arquivo ausente ou mostra FAILs.

---

### AR-TRAIN-035 — Contract tests: Sessions CRUD (CONTRACT-001..012)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_214 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_214/executor_main.log
**Classe:** E
**Prioridade:** ALTA
**Fase:** Batch 14 — Contratos P0
**Objetivo da AR (1 frase):** Criar arquivo de testes de contrato para os 12 contratos do domínio Sessões de Treino e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- CONTRACT-TRAIN-001..012 (Sessions CRUD: criar, listar, detalhar, publicar, fechar, duplicar, restaurar)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_001_012_sessions_crud.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8: CONTRACT-001..012)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_001_012_sessions_crud.py` = 0 FAILs.
**FAIL:** Qualquer FAIL ou ERROR.

##### AC-002
**PASS:** TEST_MATRIX §8 mostra CONTRACT-001..012 = COBERTO com evidência linkada.
**FAIL:** Algum contrato ainda PENDENTE.

---

### AR-TRAIN-036 — Contract tests: Teams + Attendance (CONTRACT-013..028)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_215 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_215/executor_main.log
**Classe:** E
**Prioridade:** ALTA
**Fase:** Batch 14 — Contratos P0
**Objetivo da AR (1 frase):** Criar arquivo de testes de contrato para contratos de Teams e Attendance e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- CONTRACT-TRAIN-013..028 (Teams/equipes + Attendance/presenças com justified/batch)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_013_028_teams_attendance.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8: CONTRACT-013..028)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_013_028_teams_attendance.py` = 0 FAILs.
**FAIL:** Qualquer FAIL ou ERROR.

---

### AR-TRAIN-037 — Contract tests: Wellness pre/post (CONTRACT-029..039)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_216 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_216/executor_main.log
**Classe:** E
**Prioridade:** ALTA
**Fase:** Batch 14 — Contratos P0
**Objetivo da AR (1 frase):** Criar arquivo de testes de contrato para os contratos de Wellness pré/pós treino e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- CONTRACT-TRAIN-029..039 (Wellness pre + post: payload, self-only, mapeamento FE→backend)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_029_039_wellness.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8: CONTRACT-029..039)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_029_039_wellness.py` = 0 FAILs.
**FAIL:** Qualquer FAIL ou ERROR.

---

### AR-TRAIN-038 — Contract tests: Ciclos/Exercises/Analytics/Export (CONTRACT-040..095)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_217 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_217/executor_main.log
**Classe:** E
**Prioridade:** MEDIA
**Fase:** Batch 14 — Contratos P0
**Objetivo da AR (1 frase):** Criar arquivos de testes de contrato para os contratos de Ciclos, Exercícios, Analytics e Export (excluindo 073-075/077-085/091-095 que já têm teste) e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- CONTRACT-TRAIN-040..072 (Ciclos, microciclos, session exercises, session-templates)
- CONTRACT-TRAIN-076 (top performers endpoint canônico)
- CONTRACT-TRAIN-086..090 (exports e estado degradado)
- CONTRACT-TRAIN-091..095 (ACL exercícios)
**Nota:** CONTRACT-073..075 e 077..085 já têm testes (test_contract_train_073_075.py e test_contract_train_077_085.py).

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_040_072_ciclos_exercises.py`
- `Hb Track - Backend/tests/training/contracts/test_contract_train_086_095_exports_acl.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** Todos os novos arquivos de contrato: 0 FAILs no pytest.
**FAIL:** Qualquer FAIL ou ERROR.

---

### AR-TRAIN-039 — Contract tests: IA Coach + Athlete view (CONTRACT-096/101..105)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_218 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_218/executor_main.log
**Classe:** E
**Prioridade:** MEDIA
**Fase:** Batch 14 — Contratos P0
**Objetivo da AR (1 frase):** Criar arquivo de testes de contrato para IA Coach e visão do atleta e atualizar TEST_MATRIX §8.

#### 8.1 Alvos SSOT
- CONTRACT-TRAIN-096 (GET /athlete/training-sessions/{session_id}/preview)
- CONTRACT-TRAIN-101..105 (IA coach: drafts, chat, feedback, wellness-gate atleta)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§8: CONTRACT-096/101..105)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py` = 0 FAILs.
**FAIL:** Qualquer FAIL ou ERROR.

---

### AR-TRAIN-040 — DEC tests automatizados (DEC-TRAIN-001..004 + EXB-* + RBAC-*)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_219 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_219/executor_main.log
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 15 — DEC/Flows/Screens
**Objetivo da AR (1 frase):** Criar testes automatizados para os 11 DECs do módulo TRAINING que ainda não têm teste de violação formal, e atualizar TEST_MATRIX §5b.

#### 8.1 Alvos SSOT
- DEC-TRAIN-001 (wellness self-only — athlete_id do token, nunca do payload)
- DEC-TRAIN-002 (wellness UX sliders mapeados ao payload canônico)
- DEC-TRAIN-003 (top performers: CONTRACT-076 canônico no FE)
- DEC-TRAIN-004 (exports: estado degradado sem worker, sem polling fake)
- DEC-TRAIN-EXB-001/001B (scope SYSTEM/ORG + visibility org_wide/restricted)
- DEC-TRAIN-EXB-002 (categorias/tags personalizadas por treinador)
- DEC-TRAIN-EXB-RBAC-001 (Treinador como papel RBAC explícito)
- DEC-INV-065 (encerramento de sessão permite pendências, não bloqueia)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-033 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_dec_train_001_004_wellness_exports.py`
- `Hb Track - Backend/tests/training/invariants/test_dec_train_exb_rbac_scope_acl.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` (§5b)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** Todos os DEC tests: 0 FAILs no pytest.
**FAIL:** Qualquer FAIL ou ERROR.

##### AC-002
**PASS:** TEST_MATRIX §5b mostra status COBERTO para todos os DECs testados.
**FAIL:** Algum DEC ainda PENDENTE.

---

### AR-TRAIN-041 — Flows P1 evidências MANUAL_GUIADO (13 flows P1)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_220 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_220/executor_main.log
**Classe:** T
**Prioridade:** MEDIA
**Fase:** Batch 15 — DEC/Flows/Screens
**Objetivo da AR (1 frase):** Criar evidências MANUAL_GUIADO para os 13 flows P1 restantes não cobertos no Batch 10, e atualizar TEST_MATRIX §6.

#### 8.1 Alvos SSOT
- FLOW-TRAIN-007 (banco de exercícios scope/ACL)
- FLOW-TRAIN-008 (planejamento ciclos macro→meso→micro)
- FLOW-TRAIN-009 (criar/compartilhar exercício ORG)
- FLOW-TRAIN-010 (copiar exercício SYSTEM→ORG)
- FLOW-TRAIN-011 (analytics team summary)
- FLOW-TRAIN-012 (export PDF analytics)
- FLOW-TRAIN-013 (rankings top performers)
- FLOW-TRAIN-014 (session templates)
- FLOW-TRAIN-015 (step18 alertas/sugestões)
- FLOW-TRAIN-016 (visão atleta pré-treino + wellness gate)
- FLOW-TRAIN-019 (IA coach draft)
- FLOW-TRAIN-020 (IA coach chat feedback)
- FLOW-TRAIN-021 (pós-treino conversacional)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `_reports/training/TEST-TRAIN-FLOW-007.md` até `TEST-TRAIN-FLOW-021.md` (13 arquivos)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` §6

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** 13 arquivos de evidência existem com conteúdo MANUAL_GUIADO (descrição de passos + resultado observado).
**FAIL:** Qualquer arquivo ausente ou vazio.

##### AC-002
**PASS:** TEST_MATRIX §6: FLOW-007..016/019..021 com status COBERTO e evidência linkada.
**FAIL:** Algum flow ainda PENDENTE.

---

### AR-TRAIN-042 — Screens smoke tests MANUAL_GUIADO (25 telas)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_221 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_221/executor_main.log
**Classe:** T
**Prioridade:** MEDIA
**Fase:** Batch 15 — DEC/Flows/Screens
**Objetivo da AR (1 frase):** Criar evidências MANUAL_GUIADO de smoke test para as 25 telas do módulo TRAINING e atualizar TEST_MATRIX §7.

#### 8.1 Alvos SSOT
- SCREEN-TRAIN-001..025 (todas as telas do módulo TRAINING)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `_reports/training/TEST-TRAIN-SCREEN-001.md` até `TEST-TRAIN-SCREEN-025.md`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` §7

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** 25 arquivos de evidência existem com descrição de smoke (título da tela, rota, estado visual observado, PASS/FAIL).
**FAIL:** Qualquer arquivo ausente.

##### AC-002
**PASS:** TEST_MATRIX §7: SCREEN-001..025 com status COBERTO ou NOT_APPLICABLE (se tela não existe ainda).
**FAIL:** Alguma tela ainda PENDENTE sem nota.

---

### AR-TRAIN-043 — Done Gate §10 final: sync TEST_MATRIX v2.0.0

**Status:** OBSOLETO (2026-03-03)
> Substituída por AR-TRAIN-051 (Batch 22) com escopo atualizado. Contexto mudou significativamente pós-Batches 17-20: (a) sync §5 TEST_MATRIX extraído para AR-TRAIN-050 (Batch 21); (b) versão-alvo da matriz passa de v2.0.0 para v3.0.0; (c) AC-005 suite verde agora satisfatível via resultado AR_230. AR_222 (execução associada) encerrada sem selo — não tomar mais ações sobre ela.
**Classe:** G
**Prioridade:** ALTA
**Fase:** Batch 16 — Done Gate §10
**Objetivo da AR (1 frase):** Sincronizar TEST_MATRIX_TRAINING.md para v2.0.0 com todos os §10 formalmente satisfeitos, §9 atualizado com AR-TRAIN-032..043, e emitir declaração de Done Gate §10.

#### 8.1 Alvos SSOT
- `TEST_MATRIX_TRAINING.md` — v1.8.0 → v2.0.0
  - §0: contadores finais (COBERTO: todos INV/FLOW/CONTRACT/SCREEN em escopo)
  - §9: entries AR-TRAIN-032..043
  - §10: todos os checkboxes marcados ✅

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034..042 todos VERIFICADO

#### 8.5 WRITE
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
- `_reports/training/DONE_GATE_TRAINING_v2.md` (declaração Done Gate §10 completo)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque
- Não criar novos testes nesta AR — apenas sync documental

#### 8.7 AC binário
##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` contém `Versão: v2.0.0`.
**FAIL:** Versão não atualizada.

##### AC-002
**PASS:** §10 da TEST_MATRIX tem todos os checkboxes PASS marcados (todos os critérios formais satisfeitos).
**FAIL:** Qualquer checkbox PASS não marcado.

##### AC-003
**PASS:** §9 contém entries para AR-TRAIN-024..043.
**FAIL:** Alguma AR ausente.

##### AC-004
**PASS:** `_reports/training/DONE_GATE_TRAINING_v2.md` existe com lista explícita dos critérios §10 satisfeitos e assinatura do Arquiteto.
**FAIL:** Arquivo ausente ou incompleto.

##### AC-005
**PASS:** `pytest tests/training/ -q` = 0 FAILs (full suite verde).
**FAIL:** Qualquer FAIL na suite completa de training.

---

### AR-TRAIN-044 — Fix async fixtures: @pytest.fixture → @pytest_asyncio.fixture

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_225 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_225/executor_main.log
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 18 — Fix FAILs de test-layer
**Objetivo da AR (1 frase):** Substituir `@pytest.fixture` por `@pytest_asyncio.fixture` em todos os testes de training com coroutines async, eliminando o TypeError `missing required argument 'globals' (pos 2)`.

#### 8.1 Alvos SSOT
- INV-TRAIN-024 (`test_inv_train_024_websocket_broadcast.py`)
- INV-TRAIN-031 (`test_inv_train_031_derive_phase_focus.py`)
- INV-TRAIN-034 (`test_inv_train_034_wellness_pre_sleep_quality.py`)
- INV-TRAIN-035 (`test_inv_train_035_session_templates_unique_name.py`)
- INV-TRAIN-036 (`test_inv_train_036_wellness_rankings_unique.py`)
- INV-TRAIN-037 (`test_inv_train_037_cycle_dates.py`)
- INV-TRAIN-070 (`test_inv_train_070_post_conversational.py`)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_024_websocket_broadcast.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_031_derive_phase_focus.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_070_post_conversational.py`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque
- Não criar novos testes — apenas corrigir o decorador

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_024_websocket_broadcast.py tests/training/invariants/test_inv_train_031_derive_phase_focus.py tests/training/invariants/test_inv_train_034_wellness_pre_sleep_quality.py tests/training/invariants/test_inv_train_035_session_templates_unique_name.py tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py tests/training/invariants/test_inv_train_037_cycle_dates.py tests/training/invariants/test_inv_train_070_post_conversational.py -q --tb=no` = 0 FAILs, 0 ERRORs.
**FAIL:** Qualquer FAIL ou ERROR nestes arquivos.

##### AC-002
**PASS:** Nenhum arquivo listado em §8.5 contém `@pytest.fixture` em posição de async coroutine (grep clean).
**FAIL:** Grep encontra fixture async sem `pytest_asyncio`.

---

### AR-TRAIN-045 — Fix DB fixture setup: category_id NOT NULL + FK team_registrations

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_226 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_226/executor_main.log
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 18 — Fix FAILs de test-layer
**Objetivo da AR (1 frase):** Corrigir fixtures de setup de banco que falham por `category_id` NOT NULL e FK `team_registrations.athlete_id`, adicionando os campos obrigatórios ou criando os registros dependentes corretos.

#### 8.1 Alvos SSOT
- INV-TRAIN-011 (`test_inv_train_011_deviation_rules.py`)
- INV-TRAIN-013 (`test_inv_train_013_gamification_badge_rules.py`)
- INV-TRAIN-020 (`test_inv_train_020_cache_invalidation_trigger.py`)
- INV-TRAIN-021 (`test_inv_train_021_internal_load_trigger.py`)
- INV-TRAIN-028 (`test_inv_train_028_focus_sum_constraint.py`)
- INV-TRAIN-029 (`test_inv_train_029_edit_blocked_after_in_progress.py`)
- INV-TRAIN-050 (`test_inv_train_050_*` — exercise_favorites)
- INV-TRAIN-052 (`test_inv_train_052_*` — exercise_media)
- INV-TRAIN-058 (`test_inv_train_058_*` — session_structure_mutable)
- INV-TRAIN-059 (`test_inv_train_059_*` — exercise_order_contiguous)
- INV-TRAIN-063 (`test_inv_train_063_*` — preconfirm)
- INV-TRAIN-064 (`test_inv_train_064_*`)
- INV-TRAIN-076 (`test_inv_train_076_*` — wellness_content_gate)
- INV-TRAIN-148 (`test_inv_train_148_exercise_bank_services.py`)
- INV-TRAIN-EXB-ACL-006 (`test_inv_train_exb_acl_006_*`)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/` (arquivos listados nos alvos SSOT)
- `Hb Track - Backend/tests/training/conftest.py` (se fixtures compartilhadas precisarem de `category_id`)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque
- Não alterar schema de DB — apenas corrigir fixtures de teste

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_011_deviation_rules.py tests/training/invariants/test_inv_train_013_gamification_badge_rules.py tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py tests/training/invariants/test_inv_train_021_internal_load_trigger.py tests/training/invariants/test_inv_train_028_focus_sum_constraint.py tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py -q --tb=no` = 0 FAILs, 0 ERRORs.
**FAIL:** Qualquer FAIL ou ERROR nestes arquivos.

##### AC-002
**PASS:** `pytest tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py tests/training/invariants/test_inv_train_052_exercise_media.py tests/training/invariants/test_inv_train_058_session_structure_mutable.py tests/training/invariants/test_inv_train_148_exercise_bank_services.py -q --tb=no` = 0 FAILs, 0 ERRORs.
**FAIL:** Qualquer FAIL ou ERROR nestes arquivos.

---

### AR-TRAIN-046 — Fix import stubs ausentes em ai_coach_service (INV-079/080/081)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_227 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_227/executor_main.log
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 18 — Fix FAILs de test-layer
**Objetivo da AR (1 frase):** Adicionar stubs/mocks ou corrigir os imports em `test_inv_train_079/080/081` que importam `RecognitionApproved`, `CoachSuggestionDraft` e `JustifiedSuggestion` de `app.services.ai_coach_service` — classes inexistentes no módulo atual.

#### 8.1 Alvos SSOT
- INV-TRAIN-079 (`test_inv_train_079_individual_recognition_no_intimate_leak.py`)
- INV-TRAIN-080 (`test_inv_train_080_ai_coach_draft_only.py`)
- INV-TRAIN-081 (`test_inv_train_081_ai_suggestion_requires_justification.py`)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-034 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/test_inv_train_079_individual_recognition_no_intimate_leak.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/services/ai_coach_service.py` — NÃO adicionar classes reais ao produto; usar mock/stub local nos tests se classes não existem
- Não alterar lógica de produto

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_079_individual_recognition_no_intimate_leak.py tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py -q --tb=no` = 0 FAILs, 0 ERRORs (sem ImportError).
**FAIL:** Qualquer ERROR de coleta ou FAIL.

---

### AR-TRAIN-047 — Fix residuais mistos + validação done gate (0 FAILs suite completa)

**Status:** REJEITADO (AR_228 🔴 REJEITADO — substituido por AR-TRAIN-049/AR_230)
**Classe:** T
**Prioridade:** ALTA
**Fase:** Batch 18 — Fix FAILs de test-layer
**Objetivo da AR (1 frase):** Corrigir FAILs residuais não cobertos por AR-TRAIN-044..046 (arquivos: `test_inv_train_010`, `_018`, `_019`, `_054`, `_057`, `_065`, `_066`, `_067`) e validar que a suite completa atinge 0 FAILs.

#### 8.1 Alvos SSOT
- INV-TRAIN-010 (`test_inv_train_010_wellness_post_uniqueness.py`)
- INV-TRAIN-018 (`test_inv_train_018_training_session_microcycle_status.py`)
- INV-TRAIN-019 (`test_inv_train_019_training_session_audit_logs.py`)
- INV-TRAIN-054 (`test_inv_train_054_standalone_session.py`)
- INV-TRAIN-057 (`test_inv_train_057_session_within_microcycle.py`)
- INV-TRAIN-065 (`test_inv_train_065_close_pending_guard.py`)
- INV-TRAIN-066 (`test_inv_train_066_pending_items.py`)
- INV-TRAIN-067 (`test_inv_train_067_athlete_pending_rbac.py`)

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-044 VERIFICADO, AR-TRAIN-045 VERIFICADO, AR-TRAIN-046 VERIFICADO

#### 8.5 WRITE
- `Hb Track - Backend/tests/training/invariants/` (arquivos listados nos alvos SSOT)

#### 8.6 FORBIDDEN
- `Hb Track - Backend/app/` — zero toque

#### 8.7 AC binário
##### AC-001
**PASS:** `pytest tests/training/ -q --tb=no` = 0 FAILs, 0 ERRORs (suite completa verde).
**FAIL:** Qualquer FAIL ou ERROR na suite.

---
### AR-TRAIN-048 — Sincronização em Lote: Transposição do SSOT para a App Layer

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_229 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_229/executor_main.log  
**Classe:** A/E  
**Prioridade:** CRÍTICA  
**Módulo:** TRAINING  
**Lote:** 13 (Batch 19)  
**Objetivo:** Eliminar desalinhamento entre `app/` e o contrato v1.3.0 + INV v1.5.0, aplicando correções determinísticas em modelos (constraints/FKs), serviços (assinaturas) e stubs de IA Coach.

#### 8.0 Descrição
Alinhamento em 3 zonas de impacto:
1. **Modelos** — adicionar UniqueConstraint/FK onde INV exige (INV-010: wellness_post unicidade; INV-035: rankings weekly_unique; INV-036: attendance FK athlete_id; INV-054: training_cycle FK hierarchy)
2. **Serviços** — sincronizar assinaturas de `exercise_service.update_exercise` para aceitar `(exercise_id, data: dict, organization_id)` conforme CONTRACT-TRAIN-091..095; aplicar `visibility_mode` default=`restricted` em `exercise.py` (INV-TRAIN-060)
3. **Stubs IA Coach** — adicionar `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion` como dataclasses mínimas em `ai_coach_service.py` para eliminar ImportError de coleta nos testes 079/080/081

**Restrição:** Não alterar lógica de testes (`tests/`) — esta AR toca apenas `app/`.

#### 8.1 Alvos SSOT
- `INVARIANTS_TRAINING.md` — INV-TRAIN-010, 035, 036, 054, 060
- `TRAINING_FRONT_BACK_CONTRACT.md` v1.3.0 — CONTRACT-TRAIN-091..095
- `TRAINING_CLOSSARY.yaml` — campos canônicos de `Athlete` (athlete_name, birth_date)

#### 8.5 WRITE (máximo 10 itens)
- `Hb Track - Backend/app/models/athlete.py`
- `Hb Track - Backend/app/models/exercise.py`
- `Hb Track - Backend/app/models/training_session.py`
- `Hb Track - Backend/app/models/attendance.py`
- `Hb Track - Backend/app/models/training_cycle.py`
- `Hb Track - Backend/app/services/exercise_service.py`
- `Hb Track - Backend/app/services/ai_coach_service.py`
- `Hb Track - Backend/app/services/attendance_service.py`
- `Hb Track - Backend/docs/ssot/openapi.json`

#### 8.6 FORBIDDEN
- `Hb Track - Backend/tests/` — zero toque (esta AR não corrige testes)
- `Hb Track - Frontend/` — zero toque
- Qualquer arquivo `app/` não listado explicitamente no §8.5

#### 8.7 AC binário

##### AC-001
**PASS:** `app/models/athlete.py` contém campos `athlete_name` (string) e `birth_date` (date) alinhados ao Glossário canônico.  
**FAIL:** Campo `athlete_name` ou `birth_date` ausente; ou campo divergente do Glossário.

##### AC-002
**PASS:** `app/models/exercise.py` declara `visibility_mode` com `server_default='restricted'` (INV-TRAIN-060).  
**FAIL:** `server_default` ausente ou diferente de `'restricted'`.

##### AC-003
**PASS:** `app/services/exercise_service.py` → método `update_exercise` aceita assinatura `(self, exercise_id, data: dict, organization_id)` ou equivalente com Pydantic Schema (CONTRACT-TRAIN-091..095).  
**FAIL:** Assinatura divergente do contrato v1.3.0.

##### AC-004
**PASS:** `app/services/ai_coach_service.py` exporta os 3 stubs: `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion` (dataclasses ou classes mínimas importáveis).  
**FAIL:** Qualquer um dos 3 ausente ou não importável.

##### AC-005
**PASS:** `python -m pytest tests/training/invariants/test_inv_train_079*.py tests/training/invariants/test_inv_train_080*.py tests/training/invariants/test_inv_train_081*.py -q --tb=short` = 0 ERRORs de coleta.  
**FAIL:** Qualquer `ImportError` ou `ERROR` de coleta nos 3 arquivos.

#### 8.8 validation_command
```
cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1 | tail -5
```

#### 8.9 rollback_plan
Esta AR modifica modelos SQLAlchemy. Se algum campo adicionado requer migração Alembic:
```
git diff HEAD -- "Hb Track - Backend/app/models/" | head -200
```
Antes de fazer commit: verificar se novas `UniqueConstraint`/`Column` exigem `alembic revision --autogenerate`. Rollback via `git restore` proibido — usar `git revert <AR_229_commit>` se necessário.

**ARs predecessoras obrigatórias:** AR-TRAIN-044..047 VERIFICADO (suite tests/ zerada antes desta AR)

---

### AR-TRAIN-049 — Fix residuais test-layer pós-Batch 18/19 (6 FAILs + 10 ERRORs)

**Status:** VERIFICADO (2026-03-03)
> Promovido por evidência: AR_230 (hb seal 2026-03-03), paths: docs/hbtrack/evidence/AR_230/executor_main.log  
**Classe:** T  
**Prioridade:** CRÍTICA  
**Módulo:** TRAINING  
**Lote:** 14 (Batch 20)  
**Objetivo:** Eliminar 6 FAILs + 10 ERRORs remanescentes em `tests/training/invariants/` diagnosticados durante execução de AR_229 (Batch 19). Todos são bugs test-layer sem mudança de produto.

#### 8.0 Descrição
8 root causes distintos em 8 arquivos de teste:
1. **test_018_route** — `Person()` sem `birth_date` (NOT NULL) → adicionar `birth_date=date(1990,1,1)`
2. **test_035** (4 FAILs) — `SessionTemplate(organization_id=...)` mas modelo usa campo `org_id` → renomear kwarg
3. **test_058** — fixture `inv058_team` cria `Team()` sem `category_id` NOT NULL → adicionar fixture `category` + `category_id=category.id`
4. **test_059** — mesma causa que test_058 → mesmo fix
5. **test_063** (2 ERRORs) — `team_reg` usa `athlete.person_id` como FK mas `team_registrations.athlete_id` refs `athletes.id` (PK auto-gerada) → substituir `athlete.person_id` → `athlete.id`
6. **test_064** (1 ERROR) — mesmo bug que test_063 → mesmo fix
7. **test_076** (3 ERRORs) — INSERT usa `status='concluída'` invalido; `check_training_session_status` aceita apenas `draft|scheduled|in_progress|pending_review|readonly` → substituir por `'pending_review'`
8. **test_acl_006** (2 ERRORs) — `uuid4.__class__(exercise_id)` tenta instanciar `function` Python → substituir por `UUID(exercise_id)`

**ALERTA:** AR_229 (TRAIN-048) deve corrigir `training_session.py` `status` server_default (`'''draft'''` → `'draft'`) dentro do seu próprio write_scope, pois este bug revelou um FAIL em test_019. Esta AR_230 NÃO cobre esse fix (está fora do write_scope desta AR).

#### 8.5 WRITE (máximo 10 itens)
- `Hb Track - Backend/tests/training/invariants/test_inv_train_018_training_session_microcycle_status_route.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name_runtime.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_058_session_structure_mutable.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_059_exercise_order_contiguous.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_063_preconfirm.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_064_close_consolidation.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_076_wellness_policy.py`
- `Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py`

#### 8.6 FORBIDDEN
- `app/` — zero toque (bugs são exclusivamente test-layer)
- `Hb Track - Frontend/` — zero toque
- `tests/training/invariants/conftest.py` — zero toque (fixtures base são corretas)
- Qualquer arquivo de teste não listado explicitamente no §8.5

#### 8.7 AC binário

##### AC-001
**PASS:** `pytest tests/training/invariants/test_inv_train_018_*` = 0 FAIL, 0 ERROR.  
**FAIL:** Qualquer FAIL ou ERROR.

##### AC-002
**PASS:** `pytest tests/training/invariants/test_inv_train_035_*` = 0 FAIL, 0 ERROR (4 testes passando).  
**FAIL:** Qualquer `TypeError: 'organization_id' is an invalid keyword argument`.

##### AC-003
**PASS:** `pytest tests/training/invariants/test_inv_train_058_* tests/training/invariants/test_inv_train_059_*` = 0 ERROR.  
**FAIL:** Qualquer `NotNullViolationError` em `category_id`.

##### AC-004
**PASS:** `pytest tests/training/invariants/test_inv_train_063_* tests/training/invariants/test_inv_train_064_*` = 0 ERROR.  
**FAIL:** Qualquer `ForeignKeyViolationError` em `fk_team_registrations_athlete_id`.

##### AC-005
**PASS:** `pytest tests/training/invariants/test_inv_train_076_* tests/training/invariants/test_inv_train_exb_acl_006_*` = 0 ERROR.  
**FAIL:** `CheckViolationError` em `check_training_session_status` ou `TypeError: function() missing required argument 'globals'`.

##### AC-006
**PASS:** `pytest tests/training/ -q --tb=no` = `0 failed, 0 errors` (após AR_229 amendment).  
**FAIL:** Qualquer FAIL ou ERROR restante em `tests/training/`.

#### 8.8 validation_command
```
cd "Hb Track - Backend" && python -m pytest tests/training/ -q --tb=no 2>&1
```

#### 8.9 rollback_plan
Todos os fixes são localizados em arquivos de teste — nenhuma mudança de schema ou migração. Rollback via `git diff HEAD -- "Hb Track - Backend/tests/training/invariants/"`.

**ARs predecessoras obrigatórias:** AR-TRAIN-048 executado (AR_229 com amendment de status server_default)

---

### AR-TRAIN-050 — Sync §5 TEST_MATRIX_TRAINING.md pós-Batches 17-20

**Status:** PENDENTE
**Classe:** G
**Prioridade:** ALTA
**Módulo:** TRAINING
**Lote:** 15 (Batch 21)
**Objetivo:** Sync TEST_MATRIX_TRAINING.md §5: atualizar 11 itens com resultados validados por AR-TRAIN-046 (AR_227) e AR-TRAIN-049 (AR_230). INV-079/080/081: NOT_RUN→PASS; INV-018/035/058/059/063/064/076/EXB-ACL-006: FAIL/ERROR→PASS. Bump versão v2.1.0→v2.2.0.

#### 8.1 Alvos SSOT
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — §5 (11 linhas de resultados) + bump versão v2.1.0→v2.2.0 + §9 entry AR-TRAIN-050

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-046 VERIFICADO (AR_227) + AR-TRAIN-049 VERIFICADO (AR_230)

#### 8.5 WRITE (máximo 3 itens)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — §5 (11 itens) + versão + §9

#### 8.6 FORBIDDEN
- `Hb Track - Backend/` — zero toque
- `Hb Track - Frontend/` — zero toque
- Todos os demais §§ da TEST_MATRIX_TRAINING.md (não alterar §1..§4, §6..§8, §10)

#### 8.7 AC binário

##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` §5 contém `INV-TRAIN-079` com `Últ.Execução = PASS` e AR = AR-TRAIN-046.
**FAIL:** Linha ausente ou status diferente de PASS.

##### AC-002
**PASS:** `TEST_MATRIX_TRAINING.md` §5 contém `INV-TRAIN-080` e `INV-TRAIN-081` com `Últ.Execução = PASS`.
**FAIL:** Qualquer NOT_RUN ou status desatualizado.

##### AC-003
**PASS:** §5 contém `INV-TRAIN-018` com `Últ.Execução = PASS` e AR = AR-TRAIN-049.
**FAIL:** Status divergente.

##### AC-004
**PASS:** §5 contém INV-TRAIN-035/058/059/063/064/076 e EXB-ACL-006 todos com `Últ.Execução = PASS`.
**FAIL:** Qualquer FAIL ou ERROR restante nesses itens.

##### AC-005
**PASS:** `TEST_MATRIX_TRAINING.md` versão = `v2.2.0` no cabeçalho.
**FAIL:** Versão não atualizada.

##### AC-006
**PASS:** §9 contém entry `AR-TRAIN-050` com status VERIFICADO.
**FAIL:** Entry ausente.

#### 8.8 validation_command
```
python -c "
import re, sys
content = open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md', encoding='utf-8').read()
checks = [
    ('Versão: v2.2.0', 'AC-005 versão'),
    ('INV-TRAIN-079', 'AC-001 INV-079'),
    ('INV-TRAIN-080', 'AC-002 INV-080'),
    ('INV-TRAIN-081', 'AC-002 INV-081'),
    ('INV-TRAIN-018', 'AC-003 INV-018'),
    ('INV-TRAIN-035', 'AC-004 INV-035'),
    ('AR-TRAIN-050', 'AC-006 §9 entry'),
]
failed = [label for text, label in checks if text not in content]
if failed:
    print('FAIL:', failed); sys.exit(1)
print('PASS: todos os checks AC-001..AC-006 presentes')
"
```

#### 8.9 rollback_plan
Apenas mudança documental em `docs/`. `git diff HEAD -- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`.

---

### AR-TRAIN-051 — Done Gate §10 formal pós-Batch 21

**Status:** VERIFICADO
**Classe:** G
**Prioridade:** ALTA
**Módulo:** TRAINING
**Lote:** 16 (Batch 22)
**Objetivo:** Done Gate §10 formal pós-Batch 21: preencher §10 e §0 da TEST_MATRIX_TRAINING.md, bump versão v2.2.0→v3.0.0, e registrar evidência derivada em `_reports/training/DONE_GATE_TRAINING.md`. Substitui AR-TRAIN-043 (OBSOLETA).

#### 8.1 Alvos SSOT
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — §0 (contadores finais) + §10 (checkboxes) + bump versão v2.2.0→v3.0.0 + §9 entry AR-TRAIN-051

#### 8.3 Dependências
**ARs predecessoras obrigatórias:** AR-TRAIN-050 VERIFICADO

#### 8.5 WRITE (máximo 3 itens)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` — §0 + §10 + versão + §9

#### 8.6 FORBIDDEN
- `Hb Track - Backend/` — zero toque
- `Hb Track - Frontend/` — zero toque
- Não alterar §5 nem §1..§4 da TEST_MATRIX_TRAINING.md (cobertos por AR-TRAIN-050)

#### 8.7 AC binário

##### AC-001
**PASS:** `TEST_MATRIX_TRAINING.md` versão = `v3.0.0` no cabeçalho.
**FAIL:** Versão não atualizada.

##### AC-002
**PASS:** §10 da TEST_MATRIX tem todos os checkboxes marcados com ✅.
**FAIL:** Qualquer checkbox não marcado.

##### AC-003
**PASS:** §9 contém entry `AR-TRAIN-051` VERIFICADO.
**FAIL:** Entry ausente.

##### AC-004
**PASS:** `_reports/training/DONE_GATE_TRAINING.md` existe como evidência derivada (relatório de execução).
**FAIL:** Evidência ausente.

##### AC-005
**PASS:** §0 contém contadores de INV/CONTRACT/FLOW/SCREEN atualizados (0 GAPs).
**FAIL:** Contadores desatualizados ou GAPs existentes.

#### 8.8 validation_command
```
python -c "
import sys, os
content = open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md', encoding='utf-8').read()
gate = os.path.exists('_reports/training/DONE_GATE_TRAINING.md')
checks = [
    ('Versão: v3.0.0', 'AC-001 versão'),
    ('AR-TRAIN-051', 'AC-003 §9 entry'),
]
failed = [label for text, label in checks if text not in content]
if not gate:
    failed.append('AC-004 _reports/training/DONE_GATE_TRAINING.md ausente')
if failed:
    print('FAIL:', failed); sys.exit(1)
print('PASS: todos os checks AC-001..AC-005 presentes')
"
```

#### 8.9 rollback_plan
Apenas mudança documental. `git diff HEAD -- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`.

**ARs predecessoras obrigatórias:** AR-TRAIN-050 VERIFICADO (AR_231)

---

### AR-TRAIN-060 — Governance Sync Kanban (AR_244, Batch 27)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 244
- **Batch:** 27
- **Status:** VERIFICADO

#### 8.2 Objetivo
Sincronizar retroativamente o Kanban (adicionar Batches 23-26 com ARs 236-243 seladas) e adicionar seção Batch 27 (AR_244/245 PENDENTE).

#### 8.3 Contexto / Motivação
Kanban divergente: ausentes seções Batches 23-26 (ARs 236-243 já verificadas). Divergência detectada no BLOCKED_INPUT (Batch 26).

#### 8.4 Escopo / Write Scope
- `docs/hbtrack/Hb Track Kanban.md` — adicionar seções ## (Batches 23-26 retroativos + Batch 27)

#### 8.5 Acceptance Criteria
- AC-001: Kanban contém seção Batch 23 com AR_236 SEALED
- AC-002: Kanban contém seções Batch 24/25/26 com ARs respectivas SEALED
- AC-003: Kanban contém seção Batch 27 com AR_244/AR_245 PENDENTE

#### 8.6 Instrução de Implementação (Executor)
Adicionar no Kanban as seções numeradas conforme padrão existente. Antes: ler o último número de seção do Kanban e continuar sequencialmente.

#### 8.7 Validation Command
```python
python -c "
import sys
kanban = open('docs/hbtrack/Hb Track Kanban.md', encoding='utf-8').read()
checks = [
    ('Batch 23', kanban, 'AC-001 Kanban Batch23'),
    ('Batch 24', kanban, 'AC-002 Kanban Batch24'),
    ('Batch 25', kanban, 'AC-002 Kanban Batch25'),
    ('Batch 26', kanban, 'AC-002 Kanban Batch26'),
    ('Batch 27', kanban, 'AC-003 Kanban Batch27'),
]
failed = [label for text, content, label in checks if text not in content]
if failed:
    print('FAIL:', failed); sys.exit(1)
print('PASS: governance sync OK')
"
```

#### 8.8 rollback_plan
Documental: `git diff HEAD -- "docs/hbtrack/Hb Track Kanban.md"`

**ARs predecessoras obrigatórias:** AR-TRAIN-059 VERIFICADO (AR_243)

---

### AR-TRAIN-061 — Contract tests CONTRACT-074/075 wellness-rankings (AR_245, Batch 27)

#### 8.1 Metadados
- **Class:** T
- **Prioridade:** MEDIA
- **AR_ID:** 245
- **Batch:** 27
- **Status:** PENDENTE

#### 8.2 Objetivo
Criar testes de contrato para CONTRACT-TRAIN-074 (POST /analytics/wellness-rankings/calculate) e CONTRACT-TRAIN-075 (GET /analytics/wellness-rankings/{team_id}/athletes-90plus?month=). Marcar ambos COBERTO na TEST_MATRIX §8. Bump v3.2.0 → v3.3.0.

#### 8.3 Contexto / Motivação
CONTRACT-074/075 status PENDENTE/NOT_RUN na TEST_MATRIX v3.2.0. São P1. Endpoints implementados por AR-TRAIN-006 (VERIFICADO). Lacuna de cobertura residual pós-Batch 26.

#### 8.4 Escopo / Write Scope
- `Hb Track - Backend/tests/training/contracts/test_contract_train_074_075_wellness_rankings.py` (novo)
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` §8 CONTRACT-074/075 → COBERTO; §9 entry AR-TRAIN-061; bump v3.3.0

**FORBIDDEN:** `Hb Track - Backend/app/` (zero toque código produto), `Hb Track - Frontend/`.

#### 8.5 Acceptance Criteria
- AC-001: pytest `tests/training/contracts/test_contract_train_074_075_wellness_rankings.py` = 0 FAILs, 0 ERRORs
- AC-002: TEST_MATRIX §8 CONTRACT-TRAIN-074 status = COBERTO
- AC-003: TEST_MATRIX §8 CONTRACT-TRAIN-075 status = COBERTO
- AC-004: TEST_MATRIX versão = v3.3.0

#### 8.6 Instrução de Implementação (Executor)
1. Ler `app/api/v1/routers/training_analytics.py` (ou equivalente) para confirmar assinatura dos endpoints.
2. Criar arquivo de testes usando padrão de contract tests do projeto (ver tests/training/contracts/ existing files como referência).
3. Atualizar TEST_MATRIX_TRAINING.md §8 nas linhas CONTRACT-TRAIN-074 e CONTRACT-TRAIN-075: alterar status de PENDENTE para COBERTO.
4. Adicionar §9 entry para AR-TRAIN-061 com link ao arquivo criado.
5. Bump versão v3.2.0 → v3.3.0 no header do TEST_MATRIX.

#### 8.7 Validation Command
```bash
cd "Hb Track - Backend" && pytest -q tests/training/contracts/test_contract_train_074_075_wellness_rankings.py
```

#### 8.8 rollback_plan
`git diff HEAD -- "Hb Track - Backend/tests/training/contracts/test_contract_train_074_075_wellness_rankings.py" docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

**ARs predecessoras obrigatórias:** AR-TRAIN-060 VERIFICADO (AR_244), AR-TRAIN-006 VERIFICADO

> **Critérios PASS/FAIL** → ver `TEST_MATRIX_TRAINING.md` (§10 e `DONE_TRAINING_ATINGIDO`)

---

### AR-TRAIN-062 — Sync pós-Batch 27 (AR_246, Batch 28)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 246
- **Batch:** 28
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pós-Batch 27. Sincronizar: AR_BACKLOG_TRAINING.md (AR-TRAIN-060/061 PENDENTE→VERIFICADO + add AR-TRAIN-062) e TEST_MATRIX_TRAINING.md §9 (AR-TRAIN-061 EM_EXECUCAO→VERIFICADO + bump v3.4.0).

#### 8.3 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_246/executor_main.log`
- **Status Final**: ✅ VERIFICADO (hb seal 246, 2026-03-04)

---

### AR-TRAIN-063 — Fase 0+1: TRUTH SUITE dupla + triage 4 buckets (AR_247, Batch 29)

#### 8.1 Metadados
- **Class:** T/G
- **Prioridade:** ALTA
- **AR_ID:** 247
- **Batch:** 29
- **Status:** VERIFICADO

#### 8.2 Objetivo
Executar TRUTH SUITE dupla (2 rodadas idempotentes) no VPS `hb_track`. Confirmar baseline 610p/4s/1xf/0f. Classificar os 4s+1xf em 3 buckets (A: produto, B: produto, C: test-layer) para planejar ARs 064/065/066.

#### 8.3 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_247/executor_main.log`
- **Status Final**: ✅ VERIFICADO (hb seal 247, 2026-03-05)

---

### AR-TRAIN-064 — Fix user.organization_id not a column (AR_248, Batch 29)

#### 8.1 Metadados
- **Class:** B
- **Prioridade:** ALTA
- **AR_ID:** 248
- **Batch:** 29
- **Status:** VERIFICADO

#### 8.2 Objetivo
Corrigir `exercise_acl_service.py` método `_validate_same_org` que acessa `user.organization_id` — coluna inexistente no modelo `User`. Fix = acessar via `athlete.organization_id`. Converte `test_inv_train_148` de xfail para PASS.

#### 8.3 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_248/executor_main.log`
- **Status Final**: ✅ VERIFICADO (hb seal 248, 2026-03-05)

---

### AR-TRAIN-065 — Fix 4 SKIP em test_058 e test_059 (AR_249, Batch 29)

#### 8.1 Metadados
- **Class:** B/E
- **Prioridade:** ALTA
- **AR_ID:** 249
- **Batch:** 29
- **Status:** VERIFICADO

#### 8.2 Objetivo
Converter os 4 testes skipped (`test_inv_train_058_*` e `test_inv_train_059_*`) de skip para PASS. Guards INV-058 (session structure mutable) e INV-059 (exercise order contiguous) implementados em `session_exercise_service.py`.

#### 8.3 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_249/executor_main.log`
- **Status Final**: ✅ VERIFICADO (hb seal 249, 2026-03-05)

---

### AR-TRAIN-066 — Converter 9 LEGACY_INVALID para TRUTH (AR_250, Batch 29)

#### 8.1 Metadados
- **Class:** T
- **Prioridade:** ALTA
- **AR_ID:** 250
- **Batch:** 29
- **Status:** VERIFICADO

#### 8.2 Objetivo
Converter 9 arquivos de testes `LEGACY_INVALID` (que usam `unittest.mock`/`MagicMock`) para TRUTH (banco real, sem mocks). Meta: `NO_MOCKS_GLOBAL` RH-09 atingido (rg retorna 0 matches). Estratégias: puro/None, TRUTH/async_db, contextlib/no-mock.

#### 8.3 Arquivos convertidos
`test_003`, `test_004`, `test_005`, `test_018`, `test_022`, `test_023`, `test_027`, `test_071`, `test_078` em `Hb Track - Backend/tests/training/invariants/`.

#### 8.4 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_250/executor_main.log`
- **Resultado**: 31/31 PASSED, Workspace Clean: True, rg=0 matches
- **Status Final**: ✅ VERIFICADO (hb seal 250, 2026-03-05)

---

### AR-TRAIN-067 — Sync documental pós-Batch 29 (AR_251, Batch 29)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 251
- **Batch:** 29
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pós-Batch 29. Sincronizar SSOTs: AR_BACKLOG_TRAINING.md (bump v3.2.0→v3.3.0 + add AR-TRAIN-063..067), TEST_MATRIX_TRAINING.md (bump v3.6.0→v3.7.0 + §9 entries), `_reports/training/DONE_GATE_TRAINING.md` (RH-08 baseline 610p/4s/1xf/0f→615p/0s/0xf/0f) e Kanban (add §46 Batch 29 SEALED).

#### 8.3 Evidência
- **Evidence**: `docs/hbtrack/evidence/AR_251/executor_main.log`
- **Status Final**: ✅ VERIFICADO (hb seal 251, 2026-03-05)

### AR-TRAIN-068 — Refactor FE Wellness Pre/Pos: migrar para cliente gerado (AR_252, Batch 30)

#### 8.1 Metadados
- **Class:** M
- **Prioridade:** MEDIA
- **AR_ID:** 252
- **Batch:** 30
- **Status:** VERIFICADO

#### 8.2 Objetivo
Refactor funcional (Categoria B): migrar WellnessPreForm.tsx e WellnessPostForm.tsx de src/lib/api/wellness (camada manual) para src/api/generated (WellnessPreApi, WellnessPostApi). Adiciona export wellnessPostApi em api-instance.ts. Sem mudanca de contrato BE, sem regeneracao de openapi.json. CONTRACT_SYNC_FE nao acionado (cliente gerado ja existe de AR_236).

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_252/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 252, 2026-03-06)

### AR-TRAIN-069 — BE: implementar GET/PATCH wellness-pre e wellness-post por ID (AR_253, Batch 31)

#### 8.1 Metadados
- **Class:** B
- **Prioridade:** ALTA
- **AR_ID:** 253
- **Batch:** 31
- **Status:** VERIFICADO

#### 8.2 Objetivo
Implementar os 4 endpoints BE que retornavam 501 Not Implemented. Sem mudancas de schema DB. Apenas service layer + router. AC1..AC8 (presença de async def + metodos de servico). INV-TRAIN-022 (cache_invalidation) mantida via chamadas a _invalidate_training_analytics_cache e _trigger_overload_alert_on_wellness_post.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_253/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 253, 2026-03-06)

---

### AR-TRAIN-070 — Testes impl GET/PATCH wellness por ID (AR_254, Batch 32)

#### 8.1 Metadados
- **Class:** T
- **Prioridade:** ALTA
- **AR_ID:** 254
- **Batch:** 32
- **Status:** VERIFICADO

#### 8.2 Objetivo
Adicionar 4 classes de teste de implementação (static analysis aprimorada, NO_MOCKS_GLOBAL compliant) ao arquivo test_contract_train_029_039_wellness.py para CONTRACT-031/032/037/038. Verificam: async def, get_current_user, service delegation, db.commit(). Sem mudança de schema DB ou openapi.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_254/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 254, 2026-03-06)

---

### AR-TRAIN-071 — Sync documental pós-Batch 31+32 (AR_255, Batch 32)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 255
- **Batch:** 32
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pura — sincronizar BACKLOG v3.6.0, TEST_MATRIX v4.2.0, Kanban (Batch 32), e _INDEX v1.5.0 após Batch 31 (AR_253) e Batch 32 (AR_254). Sem mudança de código produto, testes ou contrato BE.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_255/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 255, 2026-03-06)

---

### AR-TRAIN-072 — api-instance.ts: 9 singletons + fix interceptor (AR_256, Batch 33)

#### 8.1 Metadados
- **Class:** D
- **Prioridade:** ALTA
- **AR_ID:** 256
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Adicionar 9 singletons ao api-instance.ts do cliente gerado: cyclesApi, microcyclesApi, sessionTemplatesApi, exercisesApi, exerciseTagsApi, exerciseFavoritesApi, athleteTrainingApi, aiCoachApi, attendanceApi. Fix: import `from '.'` (não `from './generated'`), remoção de interceptor duplicado, remoção de `withCredentials` inválido em ConfigurationParameters.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_256/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 256, 2026-03-07)

---

### AR-TRAIN-073 — Migrar useSessions + useSessionTemplates para cliente gerado (AR_257, Batch 33)

#### 8.1 Metadados
- **Class:** D
- **Prioridade:** ALTA
- **AR_ID:** 257
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Migrar useSessions.ts (11 chamadas) e useSessionTemplates.ts (2 chamadas) de TrainingSessionsAPI manual para trainingApi e sessionTemplatesApi do cliente gerado.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_257/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 257, 2026-03-07)

---

### AR-TRAIN-074 — Migrar componentes session para generated client (AR_258, Batch 33)

#### 8.1 Metadados
- **Class:** D
- **Prioridade:** ALTA
- **AR_ID:** 258
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Migrar 9 componentes session para generated client: ConfiguracoesClient.tsx, CreateTemplateModal.tsx, EditTemplateModal.tsx, EditSessionModal.tsx, CreateSessionModal.tsx, CreateTrainingModal.tsx, OverviewTab.tsx, StatsTab.tsx, TrainingsTab.tsx.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_258/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 258, 2026-03-07)

---

### AR-TRAIN-075 — Migrar useCycles + useMicrocycles + useExercises (AR_259, Batch 33)

#### 8.1 Metadados
- **Class:** D
- **Prioridade:** ALTA
- **AR_ID:** 259
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Migrar useCycles.ts (cyclesApi, 8 chamadas), useMicrocycles.ts (microcyclesApi, 9 chamadas) e useExercises.ts (exercisesApi/exerciseTagsApi/exerciseFavoritesApi, 9 chamadas) para o cliente gerado.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_259/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 259, 2026-03-07)

---

### AR-TRAIN-076 — Migrar exercise components + training-phase3.ts (AR_260, Batch 33)

#### 8.1 Metadados
- **Class:** D
- **Prioridade:** ALTA
- **AR_ID:** 260
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Migrar ExerciseACLModal.tsx (exercisesApi, 3 chamadas), ExerciseVisibilityToggle.tsx (exercisesApi, 1 chamada) e training-phase3.ts (athleteTrainingApi + aiCoachApi + attendanceApi, 7 funções) para o cliente gerado.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_260/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 260, 2026-03-07)

---

### AR-TRAIN-077 — Fix DEC-TRAIN-004 export-pdf 503 → 202 (AR_261, Batch 33)

#### 8.1 Metadados
- **Class:** B
- **Prioridade:** ALTA
- **AR_ID:** 261
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Corrigir exports.py: substituir 2x `raise HTTPException(status_code=503)` por `return JSONResponse(status_code=202, content={degraded:True, ...})` implementando degraded mode conforme DEC-TRAIN-004.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_261/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 261, 2026-03-07)

---

### AR-TRAIN-078 — Sync documental pós-Batch 33 (AR_262, Batch 33)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 262
- **Batch:** 33
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pura — sincronizar BACKLOG v3.7.0, TEST_MATRIX v4.3.0, Kanban (Batch 33), e _INDEX v1.6.0 após Batch 33 (AR_256..AR_261). FE_MIGRATION_COMPLETE = TRUE (exceto useSuggestions.ts — DIVERGENTE_DO_SSOT pendente).

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_262/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 262, 2026-03-07)

### AR-TRAIN-079 — trainingAlertsSuggestionsApi singleton + CONTRACT §5.10 fix (AR_263, Batch 34)

#### 8.1 Metadados
- **Class:** D/E
- **Prioridade:** ALTA
- **AR_ID:** 263
- **Batch:** 34
- **Status:** VERIFICADO

#### 8.2 Objetivo
Adicionar `trainingAlertsSuggestionsApi` singleton em `api-instance.ts` (exposição de CONTRACT-TRAIN-077..085 via cliente gerado). Sincronizar TRAINING_FRONT_BACK_CONTRACT.md §5.10 de DIVERGENTE_DO_SSOT para IMPLEMENTADO pós AR-TRAIN-001. Formalizar useSuggestions.ts como deferred a CAP-001 (roteador inativo).

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_263/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 263, 2026-03-07)

### AR-TRAIN-080 — Sync documental pós-Batch 34 (AR_264, Batch 34)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 264
- **Batch:** 34
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pura — sincronizar BACKLOG v3.8.0, TEST_MATRIX v4.4.0, Kanban (Batch 34), e _INDEX v1.7.0 após Batch 34 (AR_263..AR_264). FE_MIGRATION_COMPLETE = TRUE (100% endpoints canônicos; useSuggestions.ts deferred a CAP-001).

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_264/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 264, 2026-03-07)

### AR-TRAIN-081 — Registrar DONE_CONTRACT_TRAINING.md na cadeia canônica (AR_265, Batch 35)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 265
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Registrar DONE_CONTRACT_TRAINING.md na cadeia canônica do módulo TRAINING: _INDEX.md v1.8.0 + entry 6b. Done Contract define os gates DONE_TECNICO, DONE_SEMANTICO e DONE_PRODUTO.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_265/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 265, 2026-03-08)

### AR-TRAIN-082 — Criar TRAINING_SCOPE_REGISTRY.yaml (AR_266, Batch 35)

#### 8.1 Metadados
- **Class:** A
- **Prioridade:** ALTA
- **AR_ID:** 266
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Criar TRAINING_SCOPE_REGISTRY.yaml com 13 itens CORE, 7 EXTENDED, 2 EXPERIMENTAL conforme DONE_CONTRACT §4 + §5.1.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_266/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 266, 2026-03-08)

### AR-TRAIN-083 — Criar TRAINING_STATE_MACHINE.yaml (AR_267, Batch 35)

#### 8.1 Metadados
- **Class:** A
- **Prioridade:** ALTA
- **AR_ID:** 267
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Criar TRAINING_STATE_MACHINE.yaml com 5 entidades stateful CORE: TrainingSession, WellnessPre, WellnessPost, AttendanceRecord, CoachSuggestionDraft.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_267/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 267, 2026-03-08)

### AR-TRAIN-084 — Criar TRAINING_PERF_LIMITS.json (AR_268, Batch 35)

#### 8.1 Metadados
- **Class:** A
- **Prioridade:** ALTA
- **AR_ID:** 268
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Criar TRAINING_PERF_LIMITS.json com 16 itens CORE + global_limits (SLOs baseline conforme DONE_CONTRACT §5.3 + §9).

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_268/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 268, 2026-03-08)

### AR-TRAIN-085 — Criar traceability_training_core.csv skeleton (AR_269, Batch 35)

#### 8.1 Metadados
- **Class:** A
- **Prioridade:** ALTA
- **AR_ID:** 269
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Criar _evidence/traceability_training_core.csv como skeleton com 9 headers (test_id, flow_id, screen_id, contract_id, invariant_id, selector_id, visual_baseline_id, side_effect_check_id, state_transition_id) e zero linhas de dados.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_269/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 269, 2026-03-08)

### AR-TRAIN-086 — Sync documental pós-Batch 35 (AR_270, Batch 35)

#### 8.1 Metadados
- **Class:** G
- **Prioridade:** ALTA
- **AR_ID:** 270
- **Batch:** 35
- **Status:** VERIFICADO

#### 8.2 Objetivo
Governança pura — sincronizar BACKLOG v3.9.0, TEST_MATRIX v4.5.0, Kanban (Batch 35), e _INDEX v1.8.0 após Batch 35 (AR_265..AR_270). DONE_CONTRACT_TRAINING.md implementado.

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_270/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 270, 2026-03-08)

---

### AR-TRAIN-REC-01 — Reconciliação Documental: lifecycle canônico nos 3 artefatos de base TRAINING (AR_271, Batch REC)

#### 8.1 Metadados
- **Class:** G+A
- **Prioridade:** ALTA
- **AR_ID:** 271
- **Batch:** REC-01
- **Status:** READY

#### 8.2 Objetivo
Reconciliação semântica dos 3 artefatos de base do módulo TRAINING. Eliminar vocabulário legado publish/close/PUBLISHED/CLOSED. Promover lifecycle canônico `draft -> scheduled -> in_progress -> pending_review -> readonly`. Renomear chave raiz `limits` → `operations` em TRAINING_PERF_LIMITS.json. NENHUM arquivo de backend ou frontend é tocado.

**Gates da OS:**
- Gate 1 (Negative lexical): sem PUBLISHED/CLOSED/training_session_publish/training_session_close nos 3 artefatos
- Gate 2 (Positive lifecycle): lifecycle canônico explícito em TRAINING_SCOPE_REGISTRY.yaml
- Gate 3 (Positive ledger): ai_coach_core descreve ledger imutável (Planned_State/Adjustment_Log/append-only)
- Gate 4 (Positive perf): TRAINING_PERF_LIMITS.json tem `operations` com training_session_schedule + training_session_finalize + task_update_session_statuses
- Gate 5 (Positive index): _INDEX.md v1.9.0 promove artefatos reconciliados com lifecycle canônico

#### 8.3 Evidencia
- **Evidence**: docs/hbtrack/evidence/AR_271/executor_main.log
- **Status Final**: ✅ VERIFICADO (hb seal 271, 2026-03-09)
