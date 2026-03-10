content = """

---

## ARQUITETO-BATCH1-TRAINING-HANDOFF-EXECUTOR

RUN_ID: BATCH1-TRAINING-AR175-AR176-20260228
PROTOCOLO: 1.3.0

=== BATCH 1 — O QUE FOI PLANEJADO ===

**AR-TRAIN-002** -> AR_175
- Arquivo: docs/hbtrack/ars/features/AR_175_fix_step18_services_training_alerts_service.py_+_t.md
- Status: PENDENTE
- Objetivo: Corrigir training_alerts_service.py + training_suggestion_service.py para UUID
- write_scope:
  - Hb Track - Backend/app/services/training_alerts_service.py
  - Hb Track - Backend/app/services/training_suggestion_service.py
- validation_command: cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py 2>&1
- evidence_file: docs/hbtrack/evidence/AR_175/executor_main.log
- anchors: INV-TRAIN-014, INV-TRAIN-023, schema.sql (training_alerts.id UUID PK)

**AR-TRAIN-004** -> AR_176
- Arquivo: docs/hbtrack/ars/features/AR_176_fix_wellness_be_self-only_athlete_id_do_jwt_+_payl.md
- Status: PENDENTE
- Objetivo: Fix wellness BE self-only (athlete_id do JWT) + payload minimo + LGPD log staff
- write_scope:
  - Hb Track - Backend/app/services/wellness_pre_service.py
  - Hb Track - Backend/app/services/wellness_post_service.py
- validation_command: cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_026_lgpd_access_logging.py tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py tests/training/invariants/test_inv_train_003_wellness_post_deadline.py 2>&1
- evidence_file: docs/hbtrack/evidence/AR_176/executor_main.log
- anchors: INV-TRAIN-002, INV-TRAIN-003, INV-TRAIN-026, DEC-TRAIN-001 (RESOLVIDA: self-only)

=== PLAN_HANDOFF ===
- plan_json AR_175: docs/_canon/planos/ar_train_002_step18_services.json
- plan_json AR_176: docs/_canon/planos/ar_train_004_wellness_backend.json
- dry_run_exit_code: 0 (ambos verificados)
- ordem_execucao: AR_175 primeiro (independente mas serve de base), AR_176 segundo
- modo: EXECUTE (nao PLAN)

=== STAGING STATUS ===
Staged (git add OK, git diff --name-only = VAZIO):
- A  docs/_canon/planos/ar_train_002_step18_services.json
- A  docs/_canon/planos/ar_train_004_wellness_backend.json
- M  docs/hbtrack/Hb Track Kanban.md (Section 12 adicionada)
- M  docs/hbtrack/_INDEX.md
- A  docs/hbtrack/ars/features/AR_175_fix_step18_services_training_alerts_service.py_+_t.md
- A  docs/hbtrack/ars/features/AR_176_fix_wellness_be_self-only_athlete_id_do_jwt_+_payl.md

=== INSTRUCOES PARA O EXECUTOR ===
1. Ler AR_175 completo ANTES de implementar (leitura previa obrigatoria listada no AR)
2. Preencher Analise de Impacto ANTES de escrever codigo (obrigatorio pelo contrato Executor)
3. Implementar apenas dentro do write_scope da AR
4. Rodar: python scripts/run/hb_cli.py report 175 "<validation_command>"
   OU usar: python temp/_hb_report_helper.py 175
5. Evidencia canonica obrigatoria: docs/hbtrack/evidence/AR_175/executor_main.log
6. Somente apos AR_175 completo: repetir para AR_176
7. NAO executar hb verify, hb seal (papel do Testador/Humano)
8. workspace limpo pre-verify e responsabilidade do Executor
"""

with open('_reports/ARQUITETO.yaml', 'a', encoding='utf-8') as f:
    f.write(content)

print('Handoff BATCH1 escrito com sucesso em _reports/ARQUITETO.yaml')
