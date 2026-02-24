# AR_060 — Verificar integridade do contrato OpenAPI SSOT (214 paths)

**Status**: 🔴 REJEITADO
**Versão do Protocolo**: 1.3.0

## Descrição
Verificar que o openapi.json SSOT é válido e completo: (1) arquivo existe e é JSON parseável; (2) tem pelo menos 200 paths documentados (baseline = 214 na última geração); (3) contém paths críticos: /api/v1/athletes, /api/v1/match-events, /api/v1/training/sessions (ou equivalente), /api/v1/attendance/{attendance_id}; (4) versão da API declarada no openapi.json (campo info.version); (5) manifest.json referencia openapi.json com checksum não-vazio. Esta validação garante que o contrato de API não foi corrompido silenciosamente.

## Critérios de Aceite
- Hb Track - Backend/docs/ssot/openapi.json existe
- JSON válido (parseável sem erro)
- paths count >= 200
- /api/v1/athletes presente
- /api/v1/attendance/{attendance_id} presente
- info.version declarado no openapi.json
- manifest.json tem entrada openapi.json com checksum não-vazio
- hb report gera evidence exit 0

## Validation Command (Contrato)
```
python -c "import json,pathlib,hashlib; oapi_path=pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json'); mf_path=pathlib.Path('Hb Track - Backend/docs/ssot/manifest.json'); assert oapi_path.exists(),'FAIL: openapi.json nao encontrado em Hb Track - Backend/docs/ssot/'; d=json.loads(oapi_path.read_bytes().decode('utf-8')); paths=list(d.get('paths',{}).keys()); assert len(paths)>=200,f'FAIL: openapi.json tem {len(paths)} paths, esperado >= 200'; assert '/api/v1/athletes' in paths,'FAIL: /api/v1/athletes ausente no openapi.json'; assert '/api/v1/attendance/{attendance_id}' in paths,'FAIL: /api/v1/attendance/{{attendance_id}} ausente'; assert d.get('info',{}).get('version'),'FAIL: info.version nao declarado no openapi.json'; mf=json.loads(mf_path.read_text(encoding='utf-8')); oapi_entry=[f for f in mf['files'] if f['filename']=='openapi.json']; assert oapi_entry and oapi_entry[0].get('checksum'),'FAIL: manifest.json nao tem checksum para openapi.json'; print(f'PASS AR_060: openapi.json valido — {len(paths)} paths, info.version={d[\"info\"][\"version\"]}, manifest checksum presente')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_060/executor_main.log`

## Notas do Arquiteto
Verificação estática do contrato existente. Para regenerar o openapi.json (necessário após novas rotas): rodar scripts/ssot/gen_docs_ssot.py --openapi com servidor FastAPI ativo e DB disponível — criar AR separada para esse ciclo.

## Análise de Impacto
- Verificação estática do contrato OpenAPI SSOT existente
- Sem modificações de código; risco operacional zero
- Confirma integridade do openapi.json: parseável, >= 200 paths, paths críticos presentes (/api/v1/athletes, /api/v1/attendance/{attendance_id})
- Valida info.version declarado e manifest.json com checksum não-vazio
- Rollback: N/A (apenas verificação, sem alterações)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib,hashlib; oapi_path=pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json'); mf_path=pathlib.Path('Hb Track - Backend/docs/ssot/manifest.json'); assert oapi_path.exists(),'FAIL: openapi.json nao encontrado em Hb Track - Backend/docs/ssot/'; d=json.loads(oapi_path.read_bytes().decode('utf-8')); paths=list(d.get('paths',{}).keys()); assert len(paths)>=200,f'FAIL: openapi.json tem {len(paths)} paths, esperado >= 200'; assert '/api/v1/athletes' in paths,'FAIL: /api/v1/athletes ausente no openapi.json'; assert '/api/v1/attendance/{attendance_id}' in paths,'FAIL: /api/v1/attendance/{{attendance_id}} ausente'; assert d.get('info',{}).get('version'),'FAIL: info.version nao declarado no openapi.json'; mf=json.loads(mf_path.read_text(encoding='utf-8')); oapi_entry=[f for f in mf['files'] if f['filename']=='openapi.json']; assert oapi_entry and oapi_entry[0].get('checksum'),'FAIL: manifest.json nao tem checksum para openapi.json'; print(f'PASS AR_060: openapi.json valido — {len(paths)} paths, info.version={d[\"info\"][\"version\"]}, manifest checksum presente')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:27:17.985293+00:00
**Behavior Hash**: 489aac0b350c72f79bb40782b1dc3254f0e6c08af242f0efb41309f6ec3e1ad7
**Evidence File**: `docs/hbtrack/evidence/AR_060/executor_main.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Executor reported exit 0 but Testador got exit 1

### Verificacao Testador em c5f1ba8
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_060_c5f1ba8/result.json`
