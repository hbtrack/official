VOCÊ É O AGENTE CODEX DO REPOSITÓRIO HB TRACK.

TAREFA — “PROMOVER SSOT (TRAINING) A PARTIR DO KANBAN” (SEM RELATÓRIO)
IMPORTANTE: GOVERNANÇA DE DOCUMENTAÇÃO. NÃO implementar código. NÃO criar migrações. NÃO alterar Backend/Frontend. NÃO criar arquivos novos. APENAS editar SSOTs existentes do módulo TRAINING.

OBJETIVO
Atualizar os status nos SSOTs do módulo TRAINING (INVARIANTS/CONTRACT/FLOW/SCREEN e, se necessário, TEST_MATRIX) para refletir o que já está ✅ VERIFICADO/✅ DONE no Hb Track Kanban.md, usando evidência rastreável.

BINDINGS (ler linha a linha)
- docs/hbtrack/Hb Track Kanban.md
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md
- docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
- docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md
- docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md

REGRAS (FAIL-CLOSED / ANTI-ALUCINAÇÃO)
- NÃO inventar IDs. Só mexer em IDs existentes nos SSOTs.
- NÃO criar novos status. Use somente os status já usados em cada SSOT.
- Só promover um item (GAP/PARCIAL/BLOQUEADO/DIVERGENTE/DEPRECATED → “ok”) se existir evidência mínima:
  (1) Kanban cita AR_### como ✅ VERIFICADO/✅ DONE, E
  (2) existe pelo menos 1 arquivo de evidência em:
      - docs/hbtrack/evidence/AR_###/executor_main.log OU
      - _reports/testador/AR_###_*/ (stdout/stderr/result)
- Se a evidência não existir: NÃO promover. Deixar como está.
- Para cada item promovido, registrar rastreabilidade NO PRÓPRIO SSOT:
  - adicionar/atualizar “note:” ou linha curta no changelog do arquivo com:
    “Promovido por Kanban+evidência: AR_### (hb seal YYYY-MM-DD), paths: …”
  (sem criar seção nova grande; delta mínimo)

PROCEDIMENTO
1) No Kanban, coletar as ARs HB do módulo TRAINING marcadas ✅ VERIFICADO/✅ DONE (por batch).
2) Para cada AR, identificar quais IDs SSOT ela cobre (usar: TEST_MATRIX_TRAINING.md §9 e/ou trechos de batch/kanban que listam alvos).
3) Para cada ID alvo, localizar no SSOT correspondente e:
   - se status já está “ok”: não mexer
   - se status é problemático e evidência mínima existe: promover para status “ok”
   - se status é problemático e evidência mínima NÃO existe: não mexer

CASOS OBRIGATÓRIOS A VALIDAR (promover somente se evidência existir)
- INVARIANTS_TRAINING.md: INV-TRAIN-040 e INV-TRAIN-041 (PARCIAL) → promover para “ok” se as evidências do Kanban (batch 0 AR_173/174) e logs existirem.
- TRAINING_SCREENS_SPEC.md: SCREEN-TRAIN-013 (BLOQUEADO) → promover para “ok” se Kanban indicar ExportPDFModal entregue e houver evidência.
- TRAINING_FRONT_BACK_CONTRACT.md: CONTRACT-TRAIN-091..095 e CONTRACT-TRAIN-096..105 (GAP) → promover para “ok” se Kanban+evidência confirmarem que endpoints/integrações foram entregues.

SAÍDA FINAL
- Listar quais arquivos SSOT foram modificados (paths).
- Imprimir “EXIT: 0” se pelo menos 1 promoção foi feita com evidência.
- Imprimir “EXIT: 2” se não conseguir validar evidência mínima para qualquer promoção (ou se algum binding estiver ausente).

