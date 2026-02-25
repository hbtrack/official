# AR_129 — Regenerar OpenAPI SSOT e validar UUID em paths Step18

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Apos convergencia dos tipos nas tasks 001-003, regenerar OpenAPI SSOT e validar que TODOS os path params de Step18 estao como string/uuid no spec.

Passos obrigatorios:
1. Executar: python scripts/ssot/gen_docs_ssot.py
2. Verificar docs/ssot/openapi.json: todos os paths contendo 'alerts-suggestions'
3. Para cada path param (team_id, alert_id, suggestion_id) em 'in: path':
   - schema.type DEVE ser 'string'
   - schema.format DEVE ser 'uuid'
4. Confirmar que ha pelo menos 9 paths Step18 no OpenAPI
5. Confirmar que NENHUM param Step18 path e type: integer

REFERENCIAS:
- CONTRACT-TRAIN-077..085 (TRAINING_FRONT_BACK_CONTRACT.md secao 5.8)
- INV-TRAIN-014 (INVARIANTS_TRAINING.md)

## Critérios de Aceite
1) OpenAPI SSOT regenerado sem erros.
2) Pelo menos 9 paths Step18 (alerts-suggestions ou training-alerts) presentes.
3) TODOS os params team_id/alert_id/suggestion_id em path sao format: uuid.
4) NENHUM param Step18 path e type: integer.

## Write Scope
- Hb Track - Backend/docs/ssot/openapi.json

## SSOT Touches
- [ ] docs/ssot/openapi.json

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python ../scripts/ssot/gen_docs_ssot.py && python -c "import json; spec=json.load(open('docs/ssot/openapi.json')); paths=[p for p in spec.get('paths',{}) if 'alert' in p.lower() and ('step18' in p.lower() or 'suggestion' in p.lower() or 'training' in p.lower())]; ids=('team_id','alert_id','suggestion_id'); bad=[p+':'+pr.get('name') for p in paths for _,d in spec['paths'][p].items() if isinstance(d,dict) for pr in d.get('parameters',[]) if pr.get('name') in ids and pr.get('in')=='path' and pr.get('schema',{}).get('format')!='uuid']; assert not bad,'FAIL:'+str(bad); print('PASS:'+str(len(paths))+' paths, all UUID')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_129/executor_main.log`

## Notas do Arquiteto
OpenAPI e derivado automaticamente do FastAPI via gen_docs_ssot.py. Apos tasks 001-003, os path params aparecerao como string/uuid no spec. NAO editar openapi.json manualmente.

## Análise de Impacto
**Executor:** 2026-02-25

**Arquivos modificados:** 1
- `Hb Track - Backend/docs/ssot/openapi.json`

**Ação:** execução de `python scripts/ssot/gen_docs_ssot.py` após AR_126+127+128 concluídas.
O OpenAPI é derivado automaticamente do FastAPI — após a convergência int→UUID nos routers e schemas, os path params Step18 aparecerão como `type: string, format: uuid` no spec gerado.
**NÃO editar openapi.json manualmente** — derivado pelos decorators FastAPI + Pydantic.
**Dependência:** BLOQUEADA até AR_126, AR_127, AR_128 possuírem evidência canônica.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 529b87c
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python ../scripts/ssot/gen_docs_ssot.py && python -c "import json; spec=json.load(open('docs/ssot/openapi.json')); paths=[p for p in spec.get('paths',{}) if 'alert' in p.lower() and ('step18' in p.lower() or 'suggestion' in p.lower() or 'training' in p.lower())]; ids=('team_id','alert_id','suggestion_id'); bad=[p+':'+pr.get('name') for p in paths for _,d in spec['paths'][p].items() if isinstance(d,dict) for pr in d.get('parameters',[]) if pr.get('name') in ids and pr.get('in')=='path' and pr.get('schema',{}).get('format')!='uuid']; assert not bad,'FAIL:'+str(bad); print('PASS:'+str(len(paths))+' paths, all UUID')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-25T17:16:18.711473+00:00
**Behavior Hash**: 89e87fc90adba66ef2456982c79e44d8f7d4f8ff2baf9937655ba77deb518d3b
**Evidence File**: `docs/hbtrack/evidence/AR_129/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python ../scripts/ssot/gen_docs_ssot.py && python -c "import json; spec=json.load(open('docs/ssot/openapi.json')); paths=[p for p in spec.get('paths',{}) if 'alert' in p.lower() and ('step18' in p.lower() or 'suggestion' in p.lower() or 'training' in p.lower())]; ids=('team_id','alert_id','suggestion_id'); bad=[p+':'+pr.get('name') for p in paths for _,d in spec['paths'][p].items() if isinstance(d,dict) for pr in d.get('parameters',[]) if pr.get('name') in ids and pr.get('in')=='path' and pr.get('schema',{}).get('format')!='uuid']; assert not bad,'FAIL:'+str(bad); print('PASS:'+str(len(paths))+' paths, all UUID')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:17:50.941396+00:00
**Behavior Hash**: 3f01e4fcc12a8e90c9bfd553b550d5a93cfe5d6ab9b4930dfe6e79b733c9ebb7
**Evidence File**: `docs/hbtrack/evidence/AR_129/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_129_529b87c/result.json`
