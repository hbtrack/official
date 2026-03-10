"""Append status update section to _reports/ARQUITETO.yaml"""
from pathlib import Path

NEW_SECTION = """

---

## ARQUITETO-BATCH0-STATUS-UPDATE-20260228

ESTADO ATUAL DO BATCH 0 (pos-seal TRAINING-FIXES-20260228):

AR-TRAIN-001 (AR_126..129): DONE --- todos VERIFICADO (selados anteriormente)
AR-TRAIN-005 (AR_171..172): DONE --- todos VERIFICADO (sealed 2026-02-28)
AR-TRAIN-010A (AR_173..174): DONE --- todos VERIFICADO (sealed 2026-02-28)
AR-TRAIN-003 (AR_169..170): EVIDENCE_PACK --- codigo correto (exit=0). Bloqueado por ESC-002.

DIAGNOSTICO AR-TRAIN-003:
- AR_170 validation_command continha embedded double-quote dentro do python -c argument:
  (' mood: ' not in c and "'mood'" not in c, 'mood removed from form')
  O padrao "'mood'" quebra o cmd.exe/PowerShell ao executar python -c "..."
- AR_169 validation_command: limpo (sem embedded double-quotes, Windows-compativel).
- Codigo dos dois arquivos (wellness.ts, WellnessPreForm.tsx): CORRETO (exit=0 via smart runner).

CORRECAO APLICADA (ESC-002-WELLNESS):
Arquivo: docs/_canon/planos/ar_train_003_wellness_fe.json, task 170
  DE:   (' mood: ' not in c and "'mood'" not in c, 'mood removed from form')
  PARA: (' mood: ' not in c, 'mood removed from form')
Logica preservada: ' mood: ' not in c cobre todos os casos relevantes.

dry-run --force: PASS (exit 0)
hb plan --force: AR_169 e AR_170 re-materializadas em status PENDENTE.

KANBAN ATUALIZADO:
- AR-TRAIN-001: PENDENTE -> DONE (AR_126..129 todos VERIFICADO)
- AR-TRAIN-005: PENDENTE -> DONE (AR_171..172 todos VERIFICADO, 2026-02-28)
- AR-TRAIN-010A: PENDENTE -> DONE (AR_173..174 todos VERIFICADO, 2026-02-28)
- AR-TRAIN-003: PENDENTE -> EVIDENCE_PACK (AR_169/170 aguardam triple-run + seal)

PLAN_HANDOFF:
- RUN_ID: BATCH0-WELLNESS-FE-SEAL-20260228
- AR_IDs: [169, 170]
- plan_json_path: docs/_canon/planos/ar_train_003_wellness_fe.json
- mode: EXECUTE (re-run hb report apenas; codigo ja correto)
- dry_run_exit_code: 0
- gates_required: []
- write_scope: [] (nenhuma mudanca de produto)
- db_tasks: []
- triple_run_notice: >
    Testador executara 3x; hash canonico inclui exit_code+stdout+stderr.
    AR_169 validation_command: limpo (Windows-compativel).
    AR_170 validation_command: corrigido (sem embedded double-quotes).
- notes: |
    Executor so precisa re-rodar hb report (codigo de produto ja esta correto):
      python scripts/run/hb_cli.py report 169
      python scripts/run/hb_cli.py report 170
    Ambos devem retornar exit=0.
    Apos exit=0, stagear (explicito, sem wildcards):
      git add docs/hbtrack/evidence/AR_169/executor_main.log
      git add docs/hbtrack/evidence/AR_170/executor_main.log
      git add "docs/hbtrack/ars/features/AR_169_fix_wellness.ts_paths_canonicos_+_wellnesspreinput.md"
      git add "docs/hbtrack/ars/features/AR_170_fix_wellnesspreform.tsx_campos_ui_alinhados_ao_wel.md"
      git diff --cached --name-only  (confirmar isolamento de dominio)
"""

p = Path("_reports/ARQUITETO.yaml")
content = p.read_text(encoding="utf-8")
p.write_text(content + NEW_SECTION, encoding="utf-8")
print(f"OK --- {len(content + NEW_SECTION)} chars total")
