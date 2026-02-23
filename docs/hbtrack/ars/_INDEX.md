# Índice de Architectural Records (ARs)
> ⚠️ Auto-gerado por `hb plan`/`hb report`. NÃO editar manualmente.
> Última atualização: 2026-02-21

| ID | Título | Status | Evidence |
|---|---|---|---|
| AR_001 | Migration: ADD COLUMN competition_standings.team_id (uuid... | ✅ SUCESSO | docs/hbtrack/evidence/AR_001_competition_standings_add_team_id_migration.log |
| AR_002.5 | Schema: match_goalkeeper_stints para Eficiência de Goleira | DRAFT | docs/hbtrack/evidence/AR_002_5_A_evidence.log |
| AR_002.5 | Schema: attendance.presence_status + status 'justified' | DRAFT | docs/hbtrack/evidence/AR_002_5_B_evidence.log |
| AR_002.5 | Documentar divergência de escalas wellness_pre vs. PRD | DRAFT | docs/hbtrack/evidence/AR_002_5_C_evidence.log |
| AR_002.5 | Schema: match_analytics_cache para Relatórios V1.1 | DRAFT | docs/hbtrack/evidence/AR_002_5_D_evidence.log |
| AR_002 | Model: CompetitionStanding.team_id — mapped_column + rela... | DRAFT | docs/hbtrack/evidence/AR_002_competition_standings_model_team_id.log |
| AR_003.5 | Migration: persons.birth_date NOT NULL + Trigger de Parid... | PROPOSTA | — |
| AR_003 | Schemas Pydantic Canônicos de Scout | ✅ SUCESSO | — |
| AR_004 | MatchEventService.create() — ORM correto, roster, is_shot... | 🏗️ EM_EXECUCAO | docs/hbtrack/evidence/AR_004_match_event_service_create.log |
| AR_005 | Router match_events — schemas canônicos ScoutEventCreate/... | 🏗️ EM_EXECUCAO | docs/hbtrack/evidence/AR_005_endpoint_match_events.log |
| AR_006 | Migração path planos para docs/_canon/_agent/planos + v1.0.5 | COMPLETED ✅ | docs/hbtrack/evidence/AR_006_gov_plans_path_migration.log |
| AR_007 | Exit Code Zero Test | DRAFT | docs/hbtrack/evidence/AR_007_exit_zero.log |
| AR_008 | Migration 0055: soft delete (COMP-DB-001) em 5 tabelas do... | ✅ CONCLUIDO | docs/hbtrack/evidence/AR_008_comp_db_001_soft_delete_migration.log |
| AR_009 | Models: soft delete (deleted_at, deleted_reason) nos 5 mo... | ✅ CONCLUIDO | docs/hbtrack/evidence/AR_009_comp_db_001_soft_delete_models.log |
| AR_010 | hb report: atualizar campo **Status** no cabeçalho da AR ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_010_gov_ar_status_header_sync.log |
| AR_011 | hb_cli.py: rebuild_ar_index() — auto-rebuild _INDEX.md em... | ✅ SUCESSO | docs/hbtrack/evidence/AR_011_gov_ar_index_rebuild.log |
| AR_012 | hb check: enforce _INDEX.md staged sync + imutabilidade d... | ✅ SUCESSO | docs/hbtrack/evidence/AR_012_gov_ar_check_immutability.log |
| AR_013 | Dev Flow v1.0.7: §9 Regras de Governança de ARs + bump pr... | ⛔ SUPERSEDED — ver AR_020 | docs/hbtrack/evidence/AR_013_gov_devflow_ar_rules.log |
| AR_014 | git mv: renomear Hb Track - Fronted → Hb Track - Frontend | DRAFT | docs/hbtrack/evidence/AR_014_infra_rename_frontend_dir.log |
| AR_015 | Update referências 'Fronted' → 'Frontend' em scripts e do... | DRAFT | docs/hbtrack/evidence/AR_015_infra_rename_frontend_refs.log |
| AR_016 | PRD v2.2: sync §1–§19 — header, RFs, RACI, modelo dados, ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_016_prd_v22_content_sync.log |
| AR_017 | PRD v2.2: §20 nova seção — Governança de Desenvolvimento ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_017_prd_v22_governance_section.log |
| AR_018 | Novo contrato: docs/_canon/contratos/Testador Contract.md... | ✅ SUCESSO | docs/hbtrack/evidence/AR_018_gov_testador_contract.log |
| AR_019 | Hb cli Spec v1.0.8: §10 hb verify, §11 novos status, §12 ... | ✅ SUCESSO | docs/hbtrack/evidence/AR_019_gov_hb_cli_spec_v108.log |
| AR_020 | Dev Flow v1.0.8 + hb_cli.py: cmd_verify, hb check C3 upgr... | ✅ SUCESSO | docs/hbtrack/evidence/AR_020_gov_testador_v108_implementation.log |
| AR_021 | Dual Executor Contract: protocolo de 2 agentes Executores... | ✅ SUCESSO | docs/hbtrack/evidence/AR_021_gov_dual_executor_contract.log |
| AR_022 | BATCH_001: assignment das ARs pendentes para Executor A e... | ✅ SUCESSO | docs/hbtrack/evidence/AR_022_gov_dual_executor_batch_001.log |
| AR_023 | Triple-Run Determinism + Anti-Trivial Gate + Protocol v1.... | DRAFT | docs/hbtrack/evidence/AR_023_triple_run_determinism.log |
| AR_024 | Docs v1.1.0: Dev Flow + Hb cli Spec + Testador Contract | DRAFT | docs/hbtrack/evidence/AR_024_docs_v110.log |
| AR_025 | Agente-Arquiteto Contract v2.0: Regras, Gates, Prompt Ent... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_025_arquiteto_contract_enterprise.log |
| AR_026 | Agente-Executor Contract v2.0: Regras, Guardrails, Eviden... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_026_executor_contract_enterprise.log |
| AR_027 | Agente-Testador Contract v2.0: Triple-Run Enterprise + An... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_027_testador_contract_enterprise.log |
| AR_028 | HBLock: Concurrency Lock Atômico para hb_cli.py (3 Agentes) | ✅ VERIFICADO | docs/hbtrack/evidence/AR_028_hblock_concurrency_enterprise.log |
| AR_029 | Evidence Integrity: SHA-256 Checksum + Git-Status Pre-Che... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_029_evidence_integrity_antiforja.log |
| AR_030 | Dev Flow v1.1.0: AR-as-Semaphore + Notes como Canal + Tri... | ✅ VERIFICADO | docs/hbtrack/evidence/AR_030_devflow_v110_enterprise.log |
| AR_031 | Ambiente SSOT: docs/_canon/contratos/Ambiente.md + gemini... | ✅ SUCESSO | docs/hbtrack/evidence/AR_031_ambiente_ssot.log |
| AR_032 | Hb cli Spec.md: sync v1.0.8 → v1.1.0 (GATE P3.5, HBLock, ... | DRAFT | docs/hbtrack/evidence/AR_032_hb_cli_spec_v110_sync.log |
| AR_033 | AR Index Checkpoint: _INDEX.md completo e sincronizado co... | DRAFT | docs/hbtrack/evidence/AR_033_ar_index_validation_checkpoint.log |
| AR_034 | Governança Plans — Gate JSON-to-AR obrigatório | DRAFT | docs/hbtrack/evidence/AR_034_gov_plans_json_ar_sync_validation.log |
| AR_035 | Criar scripts/run/hb_watch.py — sentinela de estado do fluxo | DRAFT | docs/hbtrack/evidence/AR_035_hb_watch_sentinela_fluxo.log |
| AR_036 | Migration 0056: ADD COLUMN competitions.points_per_draw +... | DRAFT | docs/hbtrack/evidence/AR_036_comp_db_003_scoring_rules_migration.log |
| AR_037 | Model: Competition.points_per_draw + Competition.points_p... | DRAFT | docs/hbtrack/evidence/AR_037_comp_db_003_scoring_rules_model.log |
| AR_038 | Migration 0057: DROP uk_competition_standings_team_phase ... | DRAFT | docs/hbtrack/evidence/AR_038_comp_db_004_unique_index_migration.log |
| AR_039 | Model: CompetitionStanding — UniqueConstraint legado → NU... | DRAFT | docs/hbtrack/evidence/AR_039_comp_db_004_unique_index_model.log |
| AR_040 | Migration 0058 COMP-DB-006: ADD 3 CHECK constraints statu... | DRAFT | docs/hbtrack/evidence/AR_040_comp_db_006_check_constraints_migration.log |
| AR_041 | Model Competition: ADD ck_competitions_status + ck_compet... | DRAFT | docs/hbtrack/evidence/AR_041_comp_db_006_competition_model_checks.log |
| AR_042 | Model CompetitionMatch: ADD CheckConstraint ck_competitio... | DRAFT | docs/hbtrack/evidence/AR_042_comp_db_006_competition_match_model_check.log |
| AR_043 | hb_cli.py: scan recursivo (rglob) + subdir routing + hb r... | DRAFT | docs/hbtrack/evidence/AR_043_gov_ar_folder_reorg_hb_cli.log |
| AR_044 | git mv: docs/_canon/planos/ → governance/, competitions/,... | DRAFT | docs/hbtrack/evidence/AR_044_gov_ar_folder_reorg_planos.log |
| AR_045 | git mv: docs/hbtrack/ars/ → governance/, competitions/, f... | DRAFT | docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log |
