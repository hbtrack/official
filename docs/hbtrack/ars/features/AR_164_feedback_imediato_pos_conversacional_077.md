# AR_164 — Feedback imediato pos conversacional (077)

**Status**: 🔲 PENDENTE
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
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); t=ss.read_text(encoding='utf-8'); m=re.search(r'(?s)id:\s*INV-TRAIN-077.*?\n\s*status:\s*([A-Z_]+)', t); assert m, 'FAIL SSOT missing 077'; assert m.group(1)=='IMPLEMENTADO', 'FAIL 077 status='+m.group(1); req=['Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; miss=[p for p in req if not Path(p).exists()]; assert not miss,'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py','-q']); print('PASS AR_164')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_164/executor_main.log`

## Riscos
- O service real do pos-treino pode ter outro nome; ajustar write_scope e chamada mantendo a semantica.
- Garantir que o teste simula 'concluido' sem depender de estado externo.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

