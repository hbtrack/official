# AR_129 — Regenerar OpenAPI SSOT e validar UUID em paths Step18

**Status**: 🔲 PENDENTE
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

