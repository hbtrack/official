# AR_162 — IA Coach core (072-074): guards + privacidade + educativo

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar enforcement em services e testes para INV-TRAIN-072 (ai_suggestion_not_order), INV-TRAIN-073 (ai_privacy_no_intimate_content), INV-TRAIN-074 (ai_educational_content_independent). Atualizar SSOT para marcar 072/073/074 como IMPLEMENTADO e incluir evidencias (arquivo de teste e/or service).

## Critérios de Aceite
1) Criar/atualizar services: app/services/ai_coach_service.py e app/services/coach_alerts_service.py com guards. 2) Criar 3 testes: test_inv_train_072_*.py, test_inv_train_073_*.py, test_inv_train_074_*.py. 3) Atualizar SSOT: 072/073/074 status=IMPLEMENTADO. 4) pytest invariants exitcode=0.

## Write Scope
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/app/services/coach_alerts_service.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_073_ai_privacy_no_intimate_content.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_074_ai_educational_content_independent.py
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md

## Validation Command (Contrato)
```
python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); assert ss.exists(), 'FAIL SSOT missing'; t=ss.read_text(encoding='utf-8'); ids=['INV-TRAIN-072','INV-TRAIN-073','INV-TRAIN-074']; bad=[]
for i in ids:
 m=re.search(r'(?s)id:\s*'+re.escape(i)+r'.*?\n\s*status:\s*([A-Z_]+)', t)
 if not m: bad.append((i,'MISSING_BLOCK')); continue
 if m.group(1)!='IMPLEMENTADO': bad.append((i,m.group(1)))
assert not bad, 'FAIL SSOT statuses '+str(bad); req=[ 'Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/app/services/coach_alerts_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py','Hb Track - Backend/tests/training/invariants/test_inv_train_073_ai_privacy_no_intimate_content.py','Hb Track - Backend/tests/training/invariants/test_inv_train_074_ai_educational_content_independent.py' ]; miss=[p for p in req if not Path(p).exists()]; assert not miss, 'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants','-q']); print('PASS AR_162')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_162/executor_main.log`

## Riscos
- Regex de status depende do SSOT conter linhas 'id:' e 'status:' no mesmo bloco do item.
- Se o projeto usa outro runner/caminho de pytest, ajustar o comando mantendo a semantica.

## Análise de Impacto
- **ai_coach_service.py**: já contém `check_suggestion_tone()`, `check_auto_publish()` (INV-072), `filter_privacy()` (INV-073), `get_educational_content()` (INV-074). Nenhuma alteração necessária.
- **coach_alerts_service.py**: já contém `generate_risk_summary()`, `create_alert_for_coach()` com `intimate_content_exposed=False` (INV-073). Nenhuma alteração necessária.
- **tests/training/invariants/**: test_inv_train_072/073/074 já existem e cobrem casos válidos + inválidos alinhados ao write_scope.
- **INVARIANTS_TRAINING.md**: INV-TRAIN-072, 073, 074 já com `status: IMPLEMENTADO` e `decision_trace: [AR_162]`.
- **Impacto colateral**: nenhum — mudanças são somente nos arquivos do write_scope; testes são unit (sem IO/DB).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 3dbcf3c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import re, subprocess; ss=Path('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md'); assert ss.exists(), 'FAIL SSOT missing'; t=ss.read_text(encoding='utf-8'); ids=['INV-TRAIN-072','INV-TRAIN-073','INV-TRAIN-074']; bad=[]
for i in ids:
 m=re.search(r'(?s)id:\s*'+re.escape(i)+r'.*?\n\s*status:\s*([A-Z_]+)', t)
 if not m: bad.append((i,'MISSING_BLOCK')); continue
 if m.group(1)!='IMPLEMENTADO': bad.append((i,m.group(1)))
assert not bad, 'FAIL SSOT statuses '+str(bad); req=[ 'Hb Track - Backend/app/services/ai_coach_service.py','Hb Track - Backend/app/services/coach_alerts_service.py','Hb Track - Backend/tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py','Hb Track - Backend/tests/training/invariants/test_inv_train_073_ai_privacy_no_intimate_content.py','Hb Track - Backend/tests/training/invariants/test_inv_train_074_ai_educational_content_independent.py' ]; miss=[p for p in req if not Path(p).exists()]; assert not miss, 'FAIL missing '+str(miss); subprocess.check_call(['pytest','Hb Track - Backend/tests/training/invariants','-q']); print('PASS AR_162')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T06:32:41.009816+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_162/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 3dbcf3c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_162_3dbcf3c/result.json`

### Selo Humano em 3dbcf3c
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T06:38:47.397535+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_162_3dbcf3c/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_162/executor_main.log`
