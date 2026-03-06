# AR_241 — BE: endpoint GET wellness-content-gate no athlete_training router (AR-TRAIN-057)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar endpoint GET /api/v1/athlete/wellness-content-gate/{session_id} ao router athlete_training.py.

Contexto: athlete_content_gate_service.py ja tem check_content_access() e has_completed_daily_wellness() implementados. O router athlete_training.py so tem /athlete/training-sessions/{session_id}/preview.

Contrato alvo: CONTRACT-TRAIN-105
- Metodo: GET
- Path: /api/v1/athlete/wellness-content-gate/{session_id}
- Params: session_id (UUID)
- Response: {has_wellness: bool, can_see_full_content: bool, blocked_reason?: string}
- Auth: apenas o proprio atleta (INV-TRAIN-076: wellness self-only)
- INV-TRAIN-071: sem wellness = conteudo completo bloqueado

PASSOS:
1. Ler Hb Track - Backend/app/api/v1/routers/athlete_training.py
2. Ler Hb Track - Backend/app/services/athlete_content_gate_service.py (check_content_access)
3. Adicionar endpoint chamando athlete_content_gate_service.check_content_access(session_id, athlete_id)
4. Response schema: {has_wellness: bool, can_see_full_content: bool, blocked_reason: Optional[str]}
5. Executar gen_docs_ssot.py
6. Rodar hb report 241

## Critérios de Aceite
AC-001: openapi.json tem path /api/v1/athlete/wellness-content-gate/{session_id} com metodo GET.
AC-002: response schema tem campos has_wellness e can_see_full_content.
AC-003: suite 594+ passed, 0 failed.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/athlete_training.py
- Hb Track - Backend/docs/ssot/openapi.json
- Hb Track - Backend/docs/ssot/manifest.json

## Validation Command (Contrato)
```
python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; wg=[p for p in paths if 'wellness-content-gate' in p]; print('PASS wellness-content-gate found:', wg) if wg else (print('FAIL: wellness-content-gate endpoint missing'), __import__('sys').exit(1))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_241/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/api/v1/routers/athlete_training.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- INV-TRAIN-076: atleta so pode ver seu proprio gate — athlete_id deve ser inferido do token JWT, NAO do query param.
- athlete_content_gate_service.check_content_access() pode ter assinatura assíncrona — verificar antes de usar.
- Dependencia: nao tem pre-requisito (independente de AR_239 e AR_240).
- Se o service retornar ContentGateResult (dataclass), mapear para dict canonico {has_wellness, can_see_full_content, blocked_reason}.

## Análise de Impacto

**Arquivos modificados:**
- `Hb Track - Backend/app/api/v1/routers/athlete_training.py` — adicionar GET /athlete/wellness-content-gate/{session_id}
- `Hb Track - Backend/docs/ssot/openapi.json` — regenerado via gen_docs_ssot.py

**Método do serviço:** `AthleteContentGateService.check_content_access(athlete_id, resource_type='default')` — linha 167, retorna `AccessGranted` ou `AccessGated` (dataclass).

**Mapeamento de resposta:** `AccessGranted` → `{has_wellness: true, can_see_full_content: true, blocked_reason: null}`; `AccessGated` → `{has_wellness: false, can_see_full_content: false, blocked_reason: reason}`.

**INV-TRAIN-076:** athlete_id inferido do token JWT (via `current_user.person_id` → lookup em athletes), NÃO de query param.

**Reutilização:** Padrão idêntico ao existente no endpoint de preview (linhas 60-75 de athlete_training.py).

**Impacto suite:** Zero — adição aditiva ao router existente.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; wg=[p for p in paths if 'wellness-content-gate' in p]; print('PASS wellness-content-gate found:', wg) if wg else (print('FAIL: wellness-content-gate endpoint missing'), __import__('sys').exit(1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:11:45.483970+00:00
**Behavior Hash**: 07133bd3ea54d5c853f2c7cce40bae97e1f6df268e9153e86faf1fcbc49878e8
**Evidence File**: `docs/hbtrack/evidence/AR_241/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; wg=[p for p in paths if 'wellness-content-gate' in p]; print('PASS wellness-content-gate found:', wg) if wg else (print('FAIL: wellness-content-gate endpoint missing'), __import__('sys').exit(1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:12:40.304313+00:00
**Behavior Hash**: 07133bd3ea54d5c853f2c7cce40bae97e1f6df268e9153e86faf1fcbc49878e8
**Evidence File**: `docs/hbtrack/evidence/AR_241/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; wg=[p for p in paths if 'wellness-content-gate' in p]; print('PASS wellness-content-gate found:', wg) if wg else (print('FAIL: wellness-content-gate endpoint missing'), __import__('sys').exit(1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:13:43.375375+00:00
**Behavior Hash**: 07133bd3ea54d5c853f2c7cce40bae97e1f6df268e9153e86faf1fcbc49878e8
**Evidence File**: `docs/hbtrack/evidence/AR_241/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_241_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T18:38:58.073593+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_241_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_241/executor_main.log`
