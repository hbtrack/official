# AR_126 — Convergir router Step18 path params de int para UUID

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar o router training_alerts_step18.py para usar UUID em vez de int nos 9 endpoints.

Arquivo: Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py

Endpoints afetados (9 total):
1. get_active_alerts: team_id: int -> team_id: UUID
2. get_alert_history: team_id: int -> team_id: UUID
3. get_alert_stats: team_id: int -> team_id: UUID
4. dismiss_alert: alert_id: int -> alert_id: UUID
5. get_pending_suggestions: team_id: int -> team_id: UUID
6. get_suggestion_history: team_id: int -> team_id: UUID
7. get_suggestion_stats: team_id: int -> team_id: UUID
8. apply_suggestion: suggestion_id: int -> suggestion_id: UUID
9. dismiss_suggestion: suggestion_id: int -> suggestion_id: UUID

Acoes obrigatorias:
- Adicionar 'from uuid import UUID' nos imports (se nao existir)
- Alterar TODOS os path params acima de int para UUID
- NAO alterar logica de negocio, apenas tipagem

ANCORAS SSOT:
- schema.sql: training_alerts.id (uuid), training_alerts.team_id (uuid FK teams.id)
- schema.sql: training_suggestions.id (uuid), training_suggestions.team_id (uuid FK teams.id)
- Model TrainingAlert: id Mapped[UUID], team_id Mapped[UUID]
- Model TrainingSuggestion: id Mapped[UUID], team_id Mapped[UUID]

## Critérios de Aceite
1) NENHUM path param em training_alerts_step18.py usa int para team_id, alert_id ou suggestion_id.
2) from uuid import UUID esta presente nos imports.
3) Todos os 9 endpoints mantidos funcionais (import do modulo nao falha).
4) Logica de negocio inalterada — apenas tipagem dos path params.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import ast,sys; tree=ast.parse(open('app/api/v1/routers/training_alerts_step18.py').read()); [sys.exit('FAIL:'+n.name+':'+a.arg+'=int') for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in('team_id','alert_id','suggestion_id') and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; print('PASS: No int Step18 IDs in router')" && python -c "from app.api.v1.routers.training_alerts_step18 import router; print('PASS: router imported with '+str(len(router.routes))+' routes')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_126/executor_main.log`

## Notas do Arquiteto
ANCORA: schema.sql training_alerts.id uuid, .team_id uuid FK; training_suggestions.id uuid, .team_id uuid FK. Model confirmado: Mapped[UUID]. Divergencia e APENAS na camada de tipagem Python.

## Riscos
- Callers do router podem esperar int na URL (frontend/postman) — apos correcao UUIDs devem ser usados
- Middleware ou dependencias FastAPI podem fazer validacao customizada de path params — verificar

## Análise de Impacto
**Executor:** 2026-02-25

**Arquivos modificados:** 1
- `Hb Track - Backend/app/api/v1/routers/training_alerts_step18.py`

**Mudanças:**
- Adicionado `from uuid import UUID` nos imports (linha 10)
- 6× `team_id: int` → `team_id: UUID` (endpoints: get_active_alerts, get_alert_history, get_alert_stats, get_pending_suggestions, get_suggestion_history, get_suggestion_stats)
- 1× `alert_id: int` → `alert_id: UUID` (endpoint: dismiss_alert)
- 2× `suggestion_id: int` → `suggestion_id: UUID` (endpoints: apply_suggestion, dismiss_suggestion)

**Sem alteração de lógica de negócio.** Apenas tipagem de path params.
**Callers FastAPI:** nenhum caller interno injeta esses path params — vêm exclusivamente da URL HTTP. Sem risco de caller int.
**Nenhuma migration necessária** (schema.sql já usa UUID).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "import ast,sys; tree=ast.parse(open('app/api/v1/routers/training_alerts_step18.py').read()); [sys.exit('FAIL:'+n.name+':'+a.arg+'=int') for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in('team_id','alert_id','suggestion_id') and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; print('PASS: No int Step18 IDs in router')" && python -c "from app.api.v1.routers.training_alerts_step18 import router; print('PASS: router imported with '+str(len(router.routes))+' routes')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:14:55.729014+00:00
**Behavior Hash**: d35d8ef64df06742a862b1a6cd374be26a21bfc2f6641ea7daa1aacd9535c2e8
**Evidence File**: `docs/hbtrack/evidence/AR_126/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_126_529b87c/result.json`

### Selo Humano em 236bfb6
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T11:48:55.886457+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_126_529b87c/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_126/executor_main.log`
