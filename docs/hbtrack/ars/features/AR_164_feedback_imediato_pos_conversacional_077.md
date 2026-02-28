# AR_164 — Feedback imediato pos conversacional (077)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar enforcement para INV-TRAIN-077: ao concluir o pos-treino conversacional, gerar feedback curto (1 reconhecimento + 1 orientacao). Sem pos-treino concluido, nao gerar. Criar teste dedicado e atualizar SSOT para IMPLEMENTADO.

## Critérios de Aceite
1) Implementar regra e gatilho em services (ai_coach_service + service do pos-treino). 2) Criar teste test_inv_train_077_immediate_virtual_coach_feedback.py. 3) Atualizar SSOT: INV-TRAIN-077 status=IMPLEMENTADO. 4) pytest invariants exitcode=0.

## Write Scope
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/app/services/*wellness*post*service*.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md

## Validation Command (Contrato)
```
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-077.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 077'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 077 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py','-q','--tb=short','-p','no:randomly','--no-header'],capture_output=True,text=True); assert r.returncode==0,'FAIL pytest\n'+r.stdout[-400:]+r.stderr[-200:]; print('PASS AR_164')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_164/executor_main.log`

## Riscos
- O service real do pos-treino pode ter outro nome; ajustar write_scope e chamada mantendo a semantica.
- Garantir que o teste simula 'concluido' sem depender de estado externo.

## Análise de Impacto

**Arquivos afetados (write_scope):**

1. `Hb Track - Backend/app/services/ai_coach_service.py`
   - Adicionar dataclasses `PostTrainingFeedback` e `FeedbackNotGenerated` após bloco INV-075 (~linha 222)
   - Adicionar método `AICoachService.generate_post_training_feedback(conversation_completed, session_rpe)` após `request_extra_training` (~linha 392)
   - Lógica: retorna `PostTrainingFeedback` somente se `conversation_completed=True`; caso contrário `FeedbackNotGenerated`
   - Classe C1: sem IO, sem DB

2. `Hb Track - Backend/app/services/wellness_post_service.py`
   - Adicionar chamada ao `generate_post_training_feedback` no final de `submit_wellness_post`, antes dos dois `return` (update path ~linha 278 e create path ~linha 295)
   - Feedback é transiente: armazenado em atributo dinâmico `wellness.virtual_coach_feedback` (não persiste no DB)
   - Import local para evitar circular imports

3. `Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py`
   - Arquivo novo — 7 casos Classe C1 (unit, sem IO): concluído (RPE alto/médio/None), não-concluído, anti-falso-positivo, source invariante, campos não-vazios

4. `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
   - INV-TRAIN-077: `status: GAP → IMPLEMENTADO`, adicionar evidência referenciando test_inv_train_077 e AR_164

**Risco:** Baixo — service é Classe C1 (stateless, sem IO). O campo `virtual_coach_feedback` é transiente; nenhuma migração necessária. O trigger em `wellness_post_service.py` é additive (não altera paths existentes de erro).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em ad0e159
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-077.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 077'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 077 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py','-q']); print('PASS AR_164')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T09:23:15.021962+00:00
**Behavior Hash**: 0c8e48d5a54b882b5eb1bc8430140fc89257f5b99ab9776e156b2f6d3a7e36ad
**Evidence File**: `docs/hbtrack/evidence/AR_164/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em dce9117
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-077.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 077'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 077 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py','-q','--tb=short','-p','no:randomly','--no-header'],capture_output=True,text=True); assert r.returncode==0,'FAIL pytest\n'+r.stdout[-400:]+r.stderr[-200:]; print('PASS AR_164')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T10:57:15.848141+00:00
**Behavior Hash**: 4bf76f4a7f8c176921ce83d3b983834c6cdb0e62021c6cb64ce29d99bcf5a28b
**Evidence File**: `docs/hbtrack/evidence/AR_164/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em dce9117
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_164_dce9117/result.json`

### Selo Humano em c6f3dd1
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T16:19:25.347256+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_164_dce9117/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_164/executor_main.log`
