# AR_130 — Fix dismiss_alert user_id int para UUID

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir a unica divergencia remanescente de tipo nos services Step18: o parametro user_id no metodo TrainingAlertsService.dismiss_alert() esta tipado como int mas DEVE ser UUID.

Arquivo: Hb Track - Backend/app/services/training_alerts_service.py

Linha ~261 (metodo dismiss_alert):
  ANTES: async def dismiss_alert(self, alert_id: UUID, user_id: int) -> Optional[AlertResponse]:
  DEPOIS: async def dismiss_alert(self, alert_id: UUID, user_id: UUID) -> Optional[AlertResponse]:

Justificativa:
- schema.sql: dismissed_by_user_id uuid (linha 2475)
- context.py: ExecutionContext.user_id: UUID (linha 62)
- Router Step18: ctx.user_id passa UUID ao service (training_alerts_step18.py linha ~178)
- Sem essa correcao, SQLAlchemy pode falhar silenciosamente ou gravar tipo incorreto em dismissed_by_user_id

Verificar tambem:
- O import 'from uuid import UUID' ja esta presente no arquivo (confirmado linha 10)
- NAO alterar logica interna do metodo — apenas tipagem do parametro
- Conferir se nao ha outro parametro int remanescente nas assinaturas de metodos do mesmo arquivo

ANCORAS SSOT:
- schema.sql linha 2475: dismissed_by_user_id uuid
- context.py linha 62: user_id: UUID
- INV-TRAIN-014 + INV-TRAIN-023

## Critérios de Aceite
1) dismiss_alert declara user_id: UUID (nao int).
2) from uuid import UUID presente no arquivo.
3) Logica interna inalterada — apenas tipagem do parametro.
4) Import do modulo nao falha.
5) test_inv_train_023 passa (sem regressao na cadeia de alertas).

## Write Scope
- Hb Track - Backend/app/services/training_alerts_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import ast,sys;t=ast.parse(open('app/services/training_alerts_service.py',encoding='utf-8').read());r=[(n.name,a.arg,getattr(a.annotation,'id','?') if hasattr(a,'annotation') else '?') for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='dismiss_alert' for a in n.args.args if a.arg=='user_id'];assert r,'FAIL: dismiss_alert user_id not found';assert r[0][2]=='UUID','FAIL: user_id type is '+r[0][2]+' not UUID';print('PASS: dismiss_alert user_id is UUID')" && python -c "import subprocess,sys;r=subprocess.run([sys.executable,'-m','pytest','-q','tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py'],capture_output=True,text=True,encoding='utf-8');ok='passed' in r.stdout and r.returncode==0;print('PASS: INV-023 alert trigger test ok' if ok else 'FAIL: '+r.stdout[-200:]+r.stderr[-200:]);sys.exit(0 if ok else 1)
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_130/executor_main.log`

## Notas do Arquiteto
ANCORA: schema.sql:2475 dismissed_by_user_id uuid. context.py:62 user_id: UUID. Divergencia e APENAS na tipagem Python do parametro. SQLAlchemy ORM ja trabalha com UUID internamente. Correcao de 1 linha, validacao dupla (AST + test).

## Riscos
- Callers internos (Celery tasks, outros services) que passam int literal para user_id — Executor deve grep por chamadores de dismiss_alert
- NotificationService._send_critical_notification passa coordinator user_ids do ORM — verificar que membership.user_id ja e UUID no model

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em dd11c7d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "import ast,sys;t=ast.parse(open('app/services/training_alerts_service.py',encoding='utf-8').read());r=[(n.name,a.arg,getattr(a.annotation,'id','?') if hasattr(a,'annotation') else '?') for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='dismiss_alert' for a in n.args.args if a.arg=='user_id'];assert r,'FAIL: dismiss_alert user_id not found';assert r[0][2]=='UUID','FAIL: user_id type is '+r[0][2]+' not UUID';print('PASS: dismiss_alert user_id is UUID')" && python -c "import subprocess,sys;r=subprocess.run([sys.executable,'-m','pytest','-q','tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py'],capture_output=True,text=True,encoding='utf-8');ok='passed' in r.stdout and r.returncode==0;print('PASS: INV-023 alert trigger test ok' if ok else 'FAIL: '+r.stdout[-200:]+r.stderr[-200:]);sys.exit(0 if ok else 1)`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T00:54:25.802369+00:00
**Behavior Hash**: 59b3d7486376ee897bfc56428123a80fa4c6461987704d973a39bb9be2459749
**Evidence File**: `docs/hbtrack/evidence/AR_130/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em dd11c7d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_130_dd11c7d/result.json`

### Selo Humano em 236bfb6
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T11:48:59.015271+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_130_dd11c7d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_130/executor_main.log`
