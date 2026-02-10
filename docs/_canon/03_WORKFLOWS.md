# Workflows Operacionais

Cada workflow = checklist. Clique nos links para instruções completas.

---

## WF-1: Adicionar Invariante de Training

**Objetivo:** Inserir nova restrição de negócio e validá-la com testes.

1. [ ] Descreva a invariante (não-técnico) + critério de aceitação
2. [ ] Consulte [INVARIANTS_AGENT_PROTOCOL.md](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/INVARIANTS_AGENT_PROTOCOL.md) (protocolo de agente)
3. [ ] Implemente a validação no `app/services/` ou `app/models/` (conforme precedência em [01_AUTHORITY_SSOT.md](C:/HB TRACK/docs/_canon/01_AUTHORITY_SSOT.md))
4. [ ] Crie testes em `tests/` seguindo [VALIDAR_INVARIANTS_TESTS.md](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/VALIDAR_INVARIANTS_TESTS.md)
5. [ ] Documente em [INVARIANTS_TRAINING.md](C:/HB TRACK/docs/02_modulos/training/INVARIANTS/INVARIANTS_TRAINING.md)
6. [ ] Execute `pytest`; confirme cobertura > 80%

**Saída:** PR com label `invariant:training`

---

## WF-2: Consertar Parity/Guard Violations

**Objetivo:** Resolver divergências DB vs Model ou violações de guard.

1. [ ] Execute parity scan; consulte [PARITY_SCAN._PROTOCOL.md](C:/HB TRACK/docs/02_modulos/training/PROTOCOLS/PARITY_SCAN._PROTOCOL.md)
2. [ ] Revise `parity_report.json` para identificar conflitos
3. [ ] Consulte `schema.sql` (SSOT); see [001-ADR-TRAIN-ssot-precedencia.md](C:/HB TRACK/docs/ADR/architecture/001-ADR-TRAIN-ssot-precedencia.md) para precedência
4. [ ] Corrija arquivo (model ou migration ou constraint) seguindo [013-ADR-MODELS.md](C:/HB TRACK/docs/ADR/architecture/013-ADR-MODELS.md)
5. [ ] Reexecute parity → confirme "divergências ↓" ou "0"
6. [ ] Envie PR com evidência antes/depois do parity report

**Saída:** `parity_report.json` com status "clean" ou melhorado

---

## WF-3: Validar Model Conformance

**Objetivo:** Certificar que `app/models/` segue constraints de `schema.sql`.

1. [ ] Consulte [model_requirements_guide.md](C:/HB TRACK/docs/references/model_requirements_guide.md)
2. [ ] Execute o validador (path em model_requirements_guide.md)
3. [ ] Se exit=0 → tudo ok; se exit=4 → revise lista de discrepâncias
4. [ ] Use [EXEC_TASK_ADR_MODELS_001.md](C:/HB TRACK/docs/ADR/workflows/EXEC_TASK_ADR_MODELS_001.md) como guia de correção
5. [ ] Revalidate; execute testes
6. [ ] Commit com msg: "[models] conformance: XYZ fixed"

**Saída:** exit=0 com todos testes verdes
