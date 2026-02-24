# Índice de Architectural Records (ARs)
> ⚠️ Auto-gerado por `hb plan`/`hb report`. NÃO editar manualmente.
> Última atualização: 2026-02-24

| ID | Título | Status | Evidence |
|---|---|---|---|
| AR_001 | Migration: ADD COLUMN competition_standings.team_id (uuid... | ✅ SUCESSO | docs/hbtrack/evidence/AR_001_competition_standings_add_team_id_migration.log |
| AR_002 | Model: CompetitionStanding.team_id — mapped_column + rela... | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_002_competition_standings_model_team_id.log |
| AR_002.5 | Schema: match_goalkeeper_stints para Eficiência de Goleira | ✅ VERIFICADO | docs/hbtrack/evidence/AR_002.5_A/executor_main.log |
| AR_002.5 | Schema: attendance.presence_status + status 'justified' | ✅ VERIFICADO | docs/hbtrack/evidence/AR_002.5_B/executor_main.log |
| AR_002.5 | Documentar divergência de escalas wellness_pre vs. PRD | 🏗️ EM_EXECUCAO | docs/hbtrack/evidence/AR_002_5_C_evidence.log |
| AR_002.5 | Schema: match_analytics_cache para Relatórios V1.1 | ✅ VERIFICADO | docs/hbtrack/evidence/AR_002.5_D/executor_main.log |
| AR_003 | Schemas Pydantic Canônicos de Scout | 🔴 REJEITADO | docs/hbtrack/evidence/AR_003/executor_main.log |
| AR_004 | MatchEventService.create() — ORM correto, roster, is_shot... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_004/executor_main.log |
| AR_005 | Router match_events — schemas canônicos ScoutEventCreate/... | 🔍 NEEDS REVIEW | docs/hbtrack/evidence/AR_005_endpoint_match_events.log |
| AR_006 | Migração path planos para docs/_canon/_agent/planos + v1.0.5 | COMPLETED ✅ | docs/hbtrack/evidence/AR_006_gov_plans_path_migration.log |
| AR_007 | Exit Code Zero Test | 🔴 REJEITADO | docs/hbtrack/evidence/AR_007_exit_zero.log |
| AR_008 | Migration 0055: soft delete (COMP-DB-001) em 5 tabelas do... | ✅ CONCLUIDO | docs/hbtrack/evidence/AR_008_comp_db_001_soft_delete_migration.log |
| AR_009 | Models: soft delete (deleted_at, deleted_reason) nos 5 mo... | ✅ CONCLUIDO | docs/hbtrack/evidence/AR_009_comp_db_001_soft_delete_models.log |
| AR_010 | hb report: atualizar campo **Status** no cabeçalho da AR ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_010_gov_ar_status_header_sync.log |
| AR_011 | hb_cli.py: rebuild_ar_index() — auto-rebuild _INDEX.md em... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_011_gov_ar_index_rebuild.log |
| AR_012 | hb check: enforce _INDEX.md staged sync + imutabilidade d... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_012_gov_ar_check_immutability.log |
| AR_013 | Dev Flow v1.0.7: §9 Regras de Governança de ARs + bump pr... | ⛔ SUPERSEDED — ver AR_020 | docs/hbtrack/evidence/AR_013_gov_devflow_ar_rules.log |
| AR_014 | git mv: renomear Hb Track - Fronted → Hb Track - Frontend | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_014_infra_rename_frontend_dir.log |
| AR_015 | Update referências 'Fronted' → 'Frontend' em scripts e do... | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_015_infra_rename_frontend_refs.log |
| AR_016 | PRD v2.2: sync §1–§19 — header, RFs, RACI, modelo dados, ... | 🔴 REJEITADO | docs/hbtrack/evidence/AR_016_prd_v22_content_sync.log |
| AR_017 | PRD v2.2: §20 nova seção — Governança de Desenvolvimento ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_017_prd_v22_governance_section.log |
| AR_018 | Novo contrato: docs/_canon/contratos/Testador Contract.md... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_018_gov_testador_contract.log |
| AR_019 | Hb cli Spec v1.0.8: §10 hb verify, §11 novos status, §12 ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_019_gov_hb_cli_spec_v108.log |
| AR_020 | Dev Flow v1.0.8 + hb_cli.py: cmd_verify, hb check C3 upgr... | 🔴 REJEITADO | docs/hbtrack/evidence/AR_020_gov_testador_v108_implementation.log |
| AR_021 | Dual Executor Contract: protocolo de 2 agentes Executores... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_021_gov_dual_executor_contract.log |
| AR_022 | BATCH_001: assignment das ARs pendentes para Executor A e... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_022_gov_dual_executor_batch_001.log |
| AR_023 | Triple-Run Determinism + Anti-Trivial Gate + Protocol v1.... | 🔴 REJEITADO | docs/hbtrack/evidence/AR_023_triple_run_determinism.log |
| AR_024 | Docs v1.1.0: Dev Flow + Hb cli Spec + Testador Contract | 🏗️ EM_EXECUCAO | docs/hbtrack/evidence/AR_024/executor_main.log |
| AR_025 | Agente-Arquiteto Contract v2.0: Regras, Gates, Prompt Ent... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_025_arquiteto_contract_enterprise.log |
| AR_026 | Agente-Executor Contract v2.0: Regras, Guardrails, Eviden... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_026_executor_contract_enterprise.log |
| AR_027 | Agente-Testador Contract v2.0: Triple-Run Enterprise + An... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_027_testador_contract_enterprise.log |
| AR_028 | HBLock: Concurrency Lock Atômico para hb_cli.py (3 Agentes) | ✅ VERIFICADO | docs/hbtrack/evidence/AR_028_hblock_concurrency_enterprise.log |
| AR_029 | Evidence Integrity: SHA-256 Checksum + Git-Status Pre-Che... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_029_evidence_integrity_antiforja.log |
| AR_030 | Dev Flow v1.1.0: AR-as-Semaphore + Notes como Canal + Tri... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_030_devflow_v110_enterprise.log |
| AR_031 | Ambiente SSOT: docs/_canon/contratos/Ambiente.md + gemini... | 🔴 REJEITADO | docs/hbtrack/evidence/AR_031_ambiente_ssot.log |
| AR_032 | Hb cli Spec.md: sync v1.0.8 → v1.1.0 (GATE P3.5, HBLock, ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_032_hb_cli_spec_v110_sync.log |
| AR_033 | AR Index Checkpoint: _INDEX.md completo e sincronizado co... | ❌ FALHA | docs/hbtrack/evidence/AR_033_ar_index_validation_checkpoint.log |
| AR_034 | Governança Plans — Gate JSON-to-AR obrigatório | ✅ SUCESSO | docs/hbtrack/evidence/AR_034_gov_plans_json_ar_sync_validation.log |
| AR_035 | Criar scripts/run/hb_watch.py — sentinela de estado do fluxo | ✅ SUCESSO | docs/hbtrack/evidence/AR_035_hb_watch_sentinela_fluxo.log |
| AR_036 | Migration 0056: ADD COLUMN competitions.points_per_draw +... | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_036_comp_db_003_scoring_rules_migration.log |
| AR_037 | Model: Competition.points_per_draw + Competition.points_p... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_037/executor_main.log |
| AR_038 | Migration 0057: DROP uk_competition_standings_team_phase ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_038_comp_db_004_unique_index_migration.log |
| AR_039 | Model: CompetitionStanding — UniqueConstraint legado → NU... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_039/executor_main.log |
| AR_040 | Migration 0058 COMP-DB-006: ADD 3 CHECK constraints statu... | ✅ SUCESSO | docs/hbtrack/evidence/AR_040_comp_db_006_check_constraints_migration.log |
| AR_041 | Model Competition: ADD ck_competitions_status + ck_compet... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_041/executor_main.log |
| AR_042 | Model CompetitionMatch: ADD CheckConstraint ck_competitio... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_042/executor_main.log |
| AR_043 | hb_cli.py: scan recursivo (rglob) + subdir routing + hb r... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_043/executor_main.log |
| AR_044 | git mv: docs/_canon/planos/ → governance/, competitions/,... | ✅ SUCESSO | docs/hbtrack/evidence/AR_044_gov_ar_folder_reorg_planos.log |
| AR_045 | git mv: docs/hbtrack/ars/ → governance/, competitions/, f... | ✅ SUCESSO | docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log |
| AR_046 | Limpeza Segura: Arquivos Temporários e Scripts Ad-hoc | ✅ VERIFICADO | docs/hbtrack/evidence/AR_046_removed_files.log |
| AR_047 | Sync AR_003 status DESCONHECIDO → SUCESSO no _INDEX.md | ✅ VERIFICADO | docs/hbtrack/evidence/AR_047_gov_sync_ar003_status.log |
| AR_048 | Criar INVARIANTS_COMPETITIONS.md (INV-COMP-001 a INV-COMP... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_048_invariants_competitions.log |
| AR_049 | Criar INVARIANTS_SCOUT.md (INV-SCOUT-001 a INV-SCOUT-004) | ✅ VERIFICADO | docs/hbtrack/evidence/AR_049_invariants_scout.log |
| AR_050 | Wellness: documentar decisão de escala 0-10 e corrigir Fi... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_050_wellness_scale_decision.log |
| AR_051 | hb_cli.py v1.2.0: GATES_REGISTRY suporte + retry_count sc... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_051_hb_cli_v120.log |
| AR_052 | AR_008 re-validação: Evidence Pack 3-camadas para migrati... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_052_ar008_revalidation_3layer.log |
| AR_053 | hb_watch.py — Windows UTF-8 stdout fix + contract sync | ✅ VERIFICADO | docs/hbtrack/evidence/AR_053_hb_watch_unicode_fix.log |
| AR_054 | Fix Arquiteto Contract §1: INDEX path errado + DEV FLOW c... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_054_contract_index_path_fix.log |
| AR_055 | hb_cli.py: Kanban write + check_retry_limit call site (do... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_055_hb_cli_kanban_write.log |
| AR_056 | [STUB] Business Invariant: Data Consistency Check | 🔲 PENDENTE | — |
| AR_057 | [STUB] Business Invariant: Audit Trail Integrity | 🔲 PENDENTE | — |
| AR_058 | [STUB] Business Invariant: Concurrency Control | 🔲 PENDENTE | — |
| AR_059 | [STUB] Kanban Context Map | 🔲 PENDENTE | — |
| AR_060 | [STUB] OpenAPI Contract Sync | 🔲 PENDENTE | — |
| AR_061 | [STUB] Alembic Migration Gate | 🔲 PENDENTE | — |
| AR_062 | [STUB] RBAC Architecture Hardening | 🔲 PENDENTE | — |
| AR_063 | [STUB] Logging and Trace Implementation | 🔲 PENDENTE | — |
| AR_064 | Cleanup rogue: _agent/, agentes/, .github/cont + resolve ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_064_cleanup_rogue_dirs.log |
| AR_065 | Resgate de ARs de Governança (v1.2.0 Core) | ✅ VERIFICADO | docs/hbtrack/evidence/AR_065/executor_main.log |
| AR_066 | Resgate de ARs de Competitions e Features | ✅ VERIFICADO | docs/hbtrack/evidence/AR_066/executor_main.log |
| AR_067 | Resgate de Drafts e Invariantes Wellness | ✅ VERIFICADO | docs/hbtrack/evidence/AR_067/executor_main.log |
| AR_068 | Migration: persons.birth_date NOT NULL + Trigger de Parid... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_068/executor_main.log |
| AR_069 | Fix write_scope Pipeline: Schema + build_ar_content + GAT... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_069/executor_main.log |
| AR_070 | Criar hb_plan_watcher.py com claim atomico + dry-run + di... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_070/executor_main.log |
| AR_071 | Add auto-commit opt-in to hb_autotest (strict allowlist +... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_071/executor_main.log |
| AR_072 | Governance: Document daemons + bump PROTOCOL_VERSION v1.3.0 | ✅ VERIFICADO | docs/hbtrack/evidence/AR_072/executor_main.log |
| AR_100 | Estabilização do Protocolo v1.2.0 e Unificação de Registros | ✅ VERIFICADO | docs/hbtrack/evidence/AR_100/executor_main.log |
| AR_101 | Resgate de ARs de Governança (v1.2.0 Core) | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_101/executor_main.log |
| AR_102 | Resgate de ARs de Competitions e Features | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_102/executor_main.log |
| AR_103 | Resgate de Drafts e Invariantes Wellness | ⚠️ PENDENTE | docs/hbtrack/evidence/AR_103/executor_main.log |
| AR_104 | Modificar migration 0060 para detectar versão PostgreSQL ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_104/executor_main.log |
| AR_105 | Validar comportamento semântico da constraint/index em Po... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_105/executor_main.log |
| AR_109 | Adicionar constante E_SEAL_MULTIPLE_TESTADOR_STAMPS no to... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_109/executor_main.log |
| AR_110 | Adicionar guarda anti-múltiplos-carimbos em cmd_seal (ant... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_110/executor_main.log |
| AR_111 | Adicionar limpeza automática de carimbos antigos em cmd_v... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_111/executor_main.log |
| AR_112 | Limpar manualmente carimbos duplicados de AR_071 e AR_004 | ✅ VERIFICADO | — |
| AR_113 | Corrigir contrato AR_032 — versao protocolo v1.1.0 obsoleta | ✅ VERIFICADO | docs/hbtrack/evidence/AR_113/executor_main.log |
| AR_114 | Corrigir contrato AR_034 — path de evidencia pre-canonical | ✅ VERIFICADO | docs/hbtrack/evidence/AR_114/executor_main.log |
| AR_115 | Corrigir contrato AR_035 — INDEX path e status PENDENTE v... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_115/executor_main.log |
| AR_116 | Corrigir contrato AR_038 — banco renumerado de 0057 para ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_116/executor_main.log |
| AR_117 | Corrigir contrato AR_040 — banco renumerado de 0058 para ... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_117/executor_main.log |
| AR_118 | Corrigir contrato AR_044 — contagens de planos e orphan c... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_118/executor_main.log |
| AR_119 | Corrigir contrato AR_045 — contagens de ARs com valores e... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_119/executor_main.log |
| AR_120 | Fix cmd_seal — verificacao de REJEITADO por campo Status | ✅ VERIFICADO | docs/hbtrack/evidence/AR_120/executor_main.log |
| AR_121 | Corrigir contrato AR_003 — validation nao-deterministica | ✅ VERIFICADO | docs/hbtrack/evidence/AR_121/executor_main.log |
| AR_122 | Fix cmd_seal — idempotencia VERIFICADO por campo Status | ✅ VERIFICADO | docs/hbtrack/evidence/AR_122/executor_main.log |
| AR_123 | Fix AR_003 validation_command — cmd-safe via arquivo de v... | 🏗️ EM_EXECUCAO | docs/hbtrack/evidence/AR_123/executor_main.log |
| AR_998 | Test Write Scope Section Generation | ✅ VERIFICADO | docs/hbtrack/evidence/AR_998/executor_main.log |
| AR_999 | Exemplo: Adicionar campo birthdate em Person | ✅ VERIFICADO | docs/hbtrack/evidence/AR_999/executor_main.log |
