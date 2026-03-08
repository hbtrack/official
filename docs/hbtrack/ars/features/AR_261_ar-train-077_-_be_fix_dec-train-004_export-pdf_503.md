# AR_261 — AR-TRAIN-077 — BE fix DEC-TRAIN-004: export-pdf 503 -> 202 Accepted degradado

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
DEC-TRAIN-004: o endpoint `POST /api/v1/analytics/export-pdf` retorna `HTTP 503 Service Unavailable` quando o worker de PDF esta indisponivel. O normativo (CONTRACT-TRAIN-086) exige retorno `202 Accepted` com body `{degraded: true, task_id: null, message: '...'}` nesse caso — comportamento degradado aceito, nao erro fatal.

O decorator do router ja declara `status_code=status.HTTP_202_ACCEPTED` (linha 35 de exports.py). O problema esta nos dois branches de controle de fluxo que levantam `HTTPException(status_code=503)`.

## Fix em `Hb Track - Backend/app/api/v1/routers/exports.py`

Localizar as duas ocorrencias de `raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, ...)` no endpoint `export_training_pdf`.

Substituir cada uma por retorno 202 com degraded=True:

```python
# Antes:
raise HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail='...'  
)

# Depois — retornar JSONResponse 202 com flag degraded:
from fastapi.responses import JSONResponse
return JSONResponse(
    status_code=status.HTTP_202_ACCEPTED,
    content={
        'degraded': True,
        'task_id': None,
        'message': '<mensagem do erro original>',
        'estimated_ready_at': None
    }
)
```

O comportamento deve ser: independente da disponibilidade do worker, o endpoint retorna 202. O campo `degraded: true` sinaliza ao FE que o PDF nao sera gerado de imediato.

## Nota sobre openapi.json

O SSOT openapi.json em `Hb Track - Backend/docs/ssot/openapi.json` documenta o endpoint com resposta 202 (condicao normal). Nao ha mudanca de contrato — apenas a implementacao converge para o contrato. CONTRACT_DIFF_GATE: N/A.

## Critérios de Aceite
AC1: exports.py nao tem HTTPException(status_code=503) no endpoint export_training_pdf.
AC2: exports.py retorna JSONResponse status 202 com campo degraded=True nos branches de worker indisponivel.
AC3: pytest tests/training/ exit=0 (sem regressao).

## Write Scope
- Hb Track - Backend/app/api/v1/routers/exports.py

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/app/api/v1/routers/exports.py').read_text(encoding='utf-8')
checks = [
  ('HTTP_503_SERVICE_UNAVAILABLE' not in c, 'AC1: 503 removido de exports.py'),
  ('degraded' in c, 'AC2: campo degraded presente'),
  ('HTTP_202_ACCEPTED' in c, 'AC2b: retorno 202 presente'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC2 PASS')
" && cd "Hb Track - Backend" && python -m pytest tests/training/ -q 2>&1 | tail -4
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_261/executor_main.log`

## Análise de Impacto
- **exports.py**: Adicionado `from fastapi.responses import JSONResponse` nos imports. Os dois branches que faziam `raise HTTPException(status_code=503)` foram substituídos por `return JSONResponse(status_code=202, content={degraded: True, task_id: None, message: ..., estimated_ready_at: None})`. O decorator do router já declara `status_code=202`, então o contrato OpenAPI não muda.
- **Comportamento**: O endpoint agora retorna 202 mesmo quando o worker Celery não está disponível, sinalizado pelo campo `degraded: True`. O FE pode tratar esse caso sem crash.
- **Sem mudança de contrato**: openapi.json não alterado. CONTRACT_DIFF_GATE N/A.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
c = Path('Hb Track - Backend/app/api/v1/routers/exports.py').read_text(encoding='utf-8')
checks = [
  ('HTTP_503_SERVICE_UNAVAILABLE' not in c, 'AC1: 503 removido de exports.py'),
  ('degraded' in c, 'AC2: campo degraded presente'),
  ('HTTP_202_ACCEPTED' in c, 'AC2b: retorno 202 presente'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC2 PASS')
" && cd "Hb Track - Backend" && python -m pytest tests/training/ -q 2>&1 | tail -4`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T05:47:53.257358+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_261/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_261_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-07T18:01:17.651081+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_261_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_261/executor_main.log`
