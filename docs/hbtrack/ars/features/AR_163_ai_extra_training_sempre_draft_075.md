# AR_163 — AI extra training sempre draft (075)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar enforcement para INV-TRAIN-075: requisicao de treino extra via IA cria apenas rascunho (draft) e nao altera treino/sessao publicada. Criar teste dedicado e atualizar SSOT para IMPLEMENTADO.

## Critérios de Aceite
1) Implementar regra em ai_coach_service.py. 2) Criar teste test_inv_train_075_ai_extra_training_draft_only.py. 3) Atualizar SSOT: INV-TRAIN-075 status=IMPLEMENTADO. 4) pytest invariants exitcode=0.

## Write Scope
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md

## Validation Command (Contrato)
```
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-075.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 075'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 075 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py','-q','--tb=short','-p','no:randomly','--no-header'],capture_output=True,text=True); assert r.returncode==0,'FAIL pytest\n'+r.stdout[-400:]+r.stderr[-200:]; print('PASS AR_163')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_163/executor_main.log`

## Riscos
- Se INV-TRAIN-075 exigir persistencia de status draft em tabela especifica, criar/ajustar modelo conforme o backend atual.

## Análise de Impacto

**Arquivos afetados (write_scope):**

1. `Hb Track - Backend/app/services/ai_coach_service.py`
   - Contém dataclasses `ExtraTrainingDraft`, `ExtraTrainingBlocked`, `ExtraTrainingResult` (linhas ~197-220)
   - Contém método `AICoachService.request_extra_training(title)` (linha ~370) — retorna sempre `status="draft"`, `source="ai_athlete_request"`, `requires_coach_approval=True`; bloqueia títulos vazios com `ExtraTrainingBlocked`
   - Nenhuma alteração necessária — implementação já presente desde ciclo anterior

2. `Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py`
   - 6 casos de teste Classe C1 (Unit, sem IO, sem DB): draft válido, status invariante, source invariante, requires_coach_approval invariante, anti-false-positive, entradas inválidas bloqueadas
   - Nenhuma alteração necessária — arquivo já presente

3. `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
   - INV-TRAIN-075 `status: IMPLEMENTADO`, `decision_trace: [DECISÃO_HUMANA_2026-02-27]`, evidência referenciando test_inv_train_075 e AR_163
   - Nenhuma alteração necessária — SSOT já atualizado

**Risco:** Zero — service é stateless (Classe C1), sem IO, sem DB. Sem impacto em outros módulos.

**Mudança desta execução:** Apenas re-execução de `hb report` com validation_command v2 (subprocess.run + capture_output=True para output determinístico).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em f5b91a8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-075.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 075'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 075 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_075_ai_extra_training_draft_only.py','-q','--tb=short','-p','no:randomly','--no-header'],capture_output=True,text=True); assert r.returncode==0,'FAIL pytest\n'+r.stdout[-400:]+r.stderr[-200:]; print('PASS AR_163')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T07:54:18.766612+00:00
**Behavior Hash**: d362868db385b63525521d5e901aa2a996445a4c68af9a4edcad173ea06363a0
**Evidence File**: `docs/hbtrack/evidence/AR_163/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em f5b91a8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_163_f5b91a8/result.json`
