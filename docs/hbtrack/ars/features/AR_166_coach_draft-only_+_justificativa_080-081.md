# AR_166 — Coach draft-only + justificativa (080-081)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar guards 080/081 no ai_coach_service e criar testes 080 e 081.

## Critérios de Aceite
1) ai_coach_service atualizado. 2) testes 080/081 existem. 3) pytest invariants exit 0.

## Write Scope
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md

## Validation Command (Contrato)
```
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m080=re.search(r'(?s)id:\s*INV-TRAIN-080.*?\n\s*status:\s*([A-Z_]+)', t); assert m080, 'FAIL SSOT missing 080'; assert m080.group(1)=='IMPLEMENTADO', 'FAIL 080 status='+m080.group(1); m081=re.search(r'(?s)id:\s*INV-TRAIN-081.*?\n\s*status:\s*([A-Z_]+)', t); assert m081, 'FAIL SSOT missing 081'; assert m081.group(1)=='IMPLEMENTADO', 'FAIL 081 status='+m081.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py','-q','--tb=short'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); assert r.returncode==0,'FAIL pytest exit '+str(r.returncode); print('PASS AR_166')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_166/executor_main.log`

## Análise de Impacto
- **Arquivo modificado**: `Hb Track - Backend/app/services/ai_coach_service.py`
  - Adicionados dataclasses para INV-080: `CoachSuggestionDraft`, `CoachSuggestionBlocked`, `CoachSuggestionResult`.
  - Adicionados dataclasses para INV-081: `JustifiedSuggestion`, `UnjustifiedSuggestion`, `JustificationResult`.
  - Adicionado método `AICoachService.suggest_session_to_coach()` (INV-080) — toda sugestão ao treinador criada como rascunho.
  - Adicionado método `AICoachService.validate_ai_justification()` (INV-081) — valida se sugestão inclui justificativa mínima.
- **Arquivo criado**: `Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py`
  - Classe C1 (unit, sem IO/DB).
  - 3 casos: sugestão válida vira draft, publicação sem aprovação bloqueada, anti-false-positive.
- **Arquivo criado**: `Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py`
  - Classe C1 (unit, sem IO/DB).
  - 3 casos: justificativa válida aprovada, justificativa vazia bloqueada, anti-false-positive.
- **SSOT atualizado**: `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` — INV-TRAIN-080 e INV-TRAIN-081 `status: IMPLEMENTADO`.
- **Impacto colateral**: zero — métodos novos, sem alterar assinaturas existentes.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c6f3dd1
**Status Executor**: ❌ FALHA
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); def ok(i): m=re.search(r'(?s)id:\s*'+i+r'.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing '+i; assert m.group(1)=='IMPLEMENTADO', 'FAIL '+i+' status='+m.group(1); ok('INV-TRAIN-080'); ok('INV-TRAIN-081'); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py','-q']); print('PASS AR_166')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-27T13:29:31.061579+00:00
**Behavior Hash**: 82bbc93679a353288f512d80914e324627a8731913e861809950ed6a5eb512b0
**Evidence File**: `docs/hbtrack/evidence/AR_166/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em c6f3dd1
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m080=re.search(r'(?s)id:\s*INV-TRAIN-080.*?\n\s*status:\s*([A-Z_]+)', t); assert m080, 'FAIL SSOT missing 080'; assert m080.group(1)=='IMPLEMENTADO', 'FAIL 080 status='+m080.group(1); m081=re.search(r'(?s)id:\s*INV-TRAIN-081.*?\n\s*status:\s*([A-Z_]+)', t); assert m081, 'FAIL SSOT missing 081'; assert m081.group(1)=='IMPLEMENTADO', 'FAIL 081 status='+m081.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py','-q']); print('PASS AR_166')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T13:43:20.433248+00:00
**Behavior Hash**: 6af921b451d839bd7313093d3a14eaee926f2f0a0292a58285a08379850899ac
**Evidence File**: `docs/hbtrack/evidence/AR_166/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em c6f3dd1
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m080=re.search(r'(?s)id:\s*INV-TRAIN-080.*?\n\s*status:\s*([A-Z_]+)', t); assert m080, 'FAIL SSOT missing 080'; assert m080.group(1)=='IMPLEMENTADO', 'FAIL 080 status='+m080.group(1); m081=re.search(r'(?s)id:\s*INV-TRAIN-081.*?\n\s*status:\s*([A-Z_]+)', t); assert m081, 'FAIL SSOT missing 081'; assert m081.group(1)=='IMPLEMENTADO', 'FAIL 081 status='+m081.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py','-q','--tb=short'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); assert r.returncode==0,'FAIL pytest exit '+str(r.returncode); print('PASS AR_166')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T14:26:09.817189+00:00
**Behavior Hash**: cbb76909310fe24908192da0aea8b278f3b5260cadc72f00e2a3ad14cf9ce4e0
**Evidence File**: `docs/hbtrack/evidence/AR_166/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c6f3dd1
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_166_c6f3dd1/result.json`

### Selo Humano em c6f3dd1
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T14:31:46.640199+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_166_c6f3dd1/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_166/executor_main.log`
