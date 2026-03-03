# AR_185 — Expor endpoints preconfirm + close_session no router attendance.py

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar em Hb Track - Backend/app/api/v1/routers/attendance.py dois endpoints novos: (1) POST /attendance/sessions/{session_id}/preconfirm — endpoint para atleta registrar pre-confirmacao de presenca; chama attendance_service.set_preconfirm(session_id, user_id). Payload: {} vazio (autenticado via JWT). Response: 200 {presence_status: 'preconfirm', session_id}. Permissao: apenas atleta autenticado. (2) POST /attendance/sessions/{session_id}/close — endpoint para treinador encerrar sessao e gerar registros oficiais + pending items para divergencias; chama attendance_service.close_session_attendance(session_id). Response: 200 {closed: true, pending_count: int}. Permissao: apenas treinador/admin. Regras normativas: preconfirm NAO gera presenca oficial (INV-TRAIN-063); fechamento gera oficial e divergencias viram pending (INV-TRAIN-065/066); encerramento DEVE ser sempre permitido mesmo com pending items (DEC-INV-065). Tambem expor GET /attendance/sessions/{session_id}/pending-items — delegando para training_pending_service.list_pending_items. PROIBIDO: nao alterar attendance_service.py nem training_pending_service.py (ja corretos); nao criar nova migration.

## Critérios de Aceite
1) attendance.py router tem endpoint POST .../preconfirm que retorna 200 com presence_status. 2) attendance.py router tem endpoint POST .../close que retorna 200. 3) attendence.py router tem endpoint GET .../pending-items. 4) Validacao comportamental: chamar estrutura do service via import sem erro de modulo. 5) INV-TRAIN-063: preconfirm endpoint nao define is_official=True. 6) INV-TRAIN-065/066/DEC-INV-065: close endpoint nao bloqueia por pending items.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/attendance.py

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','api','v1','routers','attendance.py')).read(); assert 'preconfirm' in c, 'router missing preconfirm endpoint'; assert 'close' in c, 'router missing close endpoint'; assert 'pending' in c.lower(), 'router missing pending-items endpoint'; s=open(os.path.join(b,'app','services','attendance_service.py')).read(); assert 'set_preconfirm' in s, 'service missing set_preconfirm'; assert 'close_session' in s, 'service missing close_session'; print('PASS AR_185')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_185/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/api/v1/routers/attendance.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
attendance_service.py e training_pending_service.py JA EXISTEM e sao corretos — proibido modificar salvo bug critico. O router attendance.py deve apenas CHAMAR os servicos existentes. Verificar permissao RBAC: preconfirm = atleta, close = treinador/admin.

## Riscos
- attendance_service.close_session_attendance pode ter assinatura diferente do esperado — Executor deve ler a funcao antes de expor no router
- INV-TRAIN-063: garantir que preconfirm NAO cria registro com is_official=True
- DEC-INV-065: close endpoint NUNCA deve retornar erro por causa de pending items — verifcar que service nao levanta SessionHasPendingItemsError

## Análise de Impacto
**Executor**: 2026-03-01

- **Arquivo alterado**: `Hb Track - Backend/app/api/v1/routers/attendance.py` (+3 endpoints, sem quebra de endpoints existentes)
- **set_preconfirm**: assinatura real é `(session_id, athlete_id, user_id)` — `athlete_id` é UUID da tabela `athletes` ligada por `person_id`. Necessário query inline `SELECT id FROM athletes WHERE person_id = :pid` para resolver `athlete_id` do current_user.
- **close_session_attendance**: assinatura real é `(session_id, closed_by_user_id) → int` (qtd convertidos preconfirm→absent). Mapeado como `pending_count` na response.
- **list_pending_items**: `TrainingPendingService(db, context: ExecutionContext)` — construtor requer contexto; passar `current_user` diretamente.
- INV-TRAIN-063: `set_preconfirm` não define `is_official=True` (confirmado na implementação do service).
- DEC-INV-065: `close_session_attendance` não levanta exceção por pending items (confirmado no service).
- Zero migrations, zero alterações em services.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','api','v1','routers','attendance.py')).read(); assert 'preconfirm' in c, 'router missing preconfirm endpoint'; assert 'close' in c, 'router missing close endpoint'; assert 'pending' in c.lower(), 'router missing pending-items endpoint'; s=open(os.path.join(b,'app','services','attendance_service.py')).read(); assert 'set_preconfirm' in s, 'service missing set_preconfirm'; assert 'close_session' in s, 'service missing close_session'; print('PASS AR_185')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T05:08:07.290650+00:00
**Behavior Hash**: d6ea739320342fd772402dcc1f2fad4fe6e4c71841cbe9b0553fe0bbdc5dc0b6
**Evidence File**: `docs/hbtrack/evidence/AR_185/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_185_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T05:38:52.307794+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_185_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_185/executor_main.log`
