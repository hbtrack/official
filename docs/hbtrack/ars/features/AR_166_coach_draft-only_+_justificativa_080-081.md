# AR_166 — Coach draft-only + justificativa (080-081)

**Status**: 🔲 PENDENTE
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
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); def ok(i): m=re.search(r'(?s)id:\s*'+i+r'.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing '+i; assert m.group(1)=='IMPLEMENTADO', 'FAIL '+i+' status='+m.group(1); ok('INV-TRAIN-080'); ok('INV-TRAIN-081'); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py','Hb Track - Backend/tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py','-q']); print('PASS AR_166')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_166/executor_main.log`

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

