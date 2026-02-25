# AR_128 — Convergir services Step18 de int para UUID nas assinaturas

**Status**: ⚠️ PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar 2 arquivos de services para usar UUID em vez de int nas assinaturas de metodos.

=== ARQUIVO 1: Hb Track - Backend/app/services/training_alerts_service.py ===
Ocorrencias confirmadas (5 total):
- Linha ~41: check_weekly_overload(team_id: int, ...) -> team_id: UUID
- Linha ~134: check_focus_monotony(team_id: int, ...) -> team_id: UUID (ou metodo similar)
- Linha ~244: dismiss_alert(alert_id: int, ...) -> alert_id: UUID
- Linha ~274: get_alert_history(team_id: int, ...) -> team_id: UUID
- Linha ~292: get_alert_stats(team_id: int, ...) -> team_id: UUID
- Adicionar 'from uuid import UUID' nos imports
- NAO alterar logica interna — SQLAlchemy ORM ja trabalha com UUID (model confirmado)

=== ARQUIVO 2: Hb Track - Backend/app/services/training_suggestion_service.py ===
Ocorrencias confirmadas (5 total — metodos Step18 regressaram para int):
- Linha ~426: get_active_suggestions(team_id: int, ...) -> team_id: UUID
- Linha ~498: apply_suggestion(suggestion_id: int, ...) -> suggestion_id: UUID
- Linha ~580: dismiss_suggestion(suggestion_id: int, ...) -> suggestion_id: UUID
- Linha ~611: get_suggestion_history(team_id: int, ...) -> team_id: UUID
- Linha ~629: get_suggestion_stats(team_id: int, ...) -> team_id: UUID
- NOTA: este arquivo JA importa UUID (linha 22) — mas metodos Step18 nao usam

ANCORAS SSOT:
- Model TrainingAlert: id Mapped[UUID], team_id Mapped[UUID]
- Model TrainingSuggestion: id Mapped[UUID], team_id Mapped[UUID]
- SQLAlchemy queries com == funciona com UUID sem alteracao

## Critérios de Aceite
1) NENHUMA assinatura de metodo em training_alerts_service.py usa int para team_id ou alert_id.
2) NENHUMA assinatura de metodo em training_suggestion_service.py usa int para team_id ou suggestion_id.
3) from uuid import UUID presente em training_alerts_service.py.
4) Logica interna dos metodos inalterada — apenas tipagem das assinaturas.
5) Import do modulo nao falha.

## Write Scope
- Hb Track - Backend/app/services/training_alerts_service.py
- Hb Track - Backend/app/services/training_suggestion_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import ast,sys; t1=ast.parse(open('app/services/training_alerts_service.py',encoding='utf-8').read()); t2=ast.parse(open('app/services/training_suggestion_service.py',encoding='utf-8').read()); ids=('team_id','alert_id','suggestion_id'); bad=[]; [bad.append('alerts:'+n.name+':'+a.arg) for n in ast.walk(t1) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; [bad.append('suggestions:'+n.name+':'+a.arg) for n in ast.walk(t2) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; assert not bad,'FAIL:'+str(bad); print('PASS: All service signatures UUID')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_128/executor_main.log`

## Notas do Arquiteto
training_suggestion_service.py ja importa UUID (linha 22) mas metodos Step18 (linha 426+) regressaram para int. Provavelmente copy-paste do alerts_service. Corrigir as 5 assinaturas.

## Riscos
- Callers internos (Celery tasks, outros services) podem passar int literal — Executor deve grep por chamadores
- Type hints em variaveis locais dentro dos metodos podem usar int — verificar mas nao e bloqueante

## Análise de Impacto
**Executor:** 2026-02-25

**Arquivos modificados:** 2
- `Hb Track - Backend/app/services/training_alerts_service.py`
- `Hb Track - Backend/app/services/training_suggestion_service.py`

**training_alerts_service.py:**
- Sem import UUID — adicionado `from uuid import UUID`
- 5 assinaturas convergidas: `check_weekly_overload` (l.41), `check_wellness_response_rate` (l.134), `dismiss_alert` (l.244), `get_alert_history` (l.274), `get_alert_stats` (l.292)
- Lógica interna inalterada (SQLAlchemy ORM já opera com UUID)

**training_suggestion_service.py:**
- UUID já importado (linha 22) — sem alteração de import
- 5 assinaturas convergidas: `get_active_suggestions` (l.426), `apply_suggestion` (l.498), `dismiss_suggestion` (l.580), `get_suggestion_history` (l.611), `get_suggestion_stats` (l.629)

**Grep callers:** `check_weekly_overload`, `dismiss_alert`, `apply_suggestion`, `dismiss_suggestion` — todos chamados somente via router (path params FastAPI). Sem callers Celery com int literal identificados.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 529b87c
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -c "import ast,sys; t1=ast.parse(open('app/services/training_alerts_service.py').read()); t2=ast.parse(open('app/services/training_suggestion_service.py').read()); ids=('team_id','alert_id','suggestion_id'); bad=[]; [bad.append('alerts:'+n.name+':'+a.arg) for n in ast.walk(t1) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; [bad.append('suggestions:'+n.name+':'+a.arg) for n in ast.walk(t2) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; assert not bad,'FAIL:'+str(bad); print('PASS: All service signatures UUID')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-25T17:15:09.833198+00:00
**Behavior Hash**: 5d3466087bde2ac68f2d874d2669a438dbca478747edb7f8dcc0a69a43f46081
**Evidence File**: `docs/hbtrack/evidence/AR_128/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "import ast,sys; t1=ast.parse(open('app/services/training_alerts_service.py').read()); t2=ast.parse(open('app/services/training_suggestion_service.py').read()); ids=('team_id','alert_id','suggestion_id'); bad=[]; [bad.append('alerts:'+n.name+':'+a.arg) for n in ast.walk(t1) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; [bad.append('suggestions:'+n.name+':'+a.arg) for n in ast.walk(t2) if isinstance(n,ast.FunctionDef) for a in n.args.args if a.arg in ids and hasattr(a,'annotation') and isinstance(a.annotation,ast.Name) and a.annotation.id=='int']; assert not bad,'FAIL:'+str(bad); print('PASS: All service signatures UUID')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:15:31.272341+00:00
**Behavior Hash**: 06419ad8744166100ea5aa7f080cbdc2676da4c526d7f9c3ab9b1475082e14f0
**Evidence File**: `docs/hbtrack/evidence/AR_128/executor_main.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Executor reported exit 0 but Testador got exit 1

### Verificacao Testador em 529b87c
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_128_529b87c/result.json`
