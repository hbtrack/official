# AR_155 — Service: training_pending_service.py + RBAC atleta

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar novo arquivo Hb Track - Backend/app/services/training_pending_service.py:

1. INV-066 (pending_items service): Implementar CRUD para training_pending_items:
   - create_pending_item(session_id, athlete_id, item_type, description, user_id)
   - resolve_pending_item(item_id, resolved_by_user_id)
   - cancel_pending_item(item_id, cancelled_by_user_id)
   - list_pending_items(session_id) → retorna todos os pending items da sessão

2. INV-067 (atleta pode editar até fechar): Guard em update/cancel_pending_item:
   - Verificar que session.status NOT IN ('readonly') — se readonly, levantar SessionClosedError
   - Verificar que user_id é o dono do item (athlete_id) ou tem role de treinador

3. Adicionar endpoint/router em training_pending_router.py (ou similar) para expor operações via API (RBAC: atleta vê/edita próprio, treinador vê todos).

## Critérios de Aceite
1. create_pending_item() cria item com status='open'. 2. resolve_pending_item() muda status para 'resolved' e seta resolved_at. 3. update/cancel falha com SessionClosedError se session.status='readonly'. 4. Atleta só pode editar/cancelar próprios items.

## Write Scope
- Hb Track - Backend/app/services/training_pending_service.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/training_pending_service.py'); assert f.exists(), 'FAIL: training_pending_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'athlete' in c.lower() or 'rbac' in c.lower() or 'permission' in c.lower(), 'FAIL: logica RBAC/atleta ausente'; print('PASS AR_155: training_pending_service.py com RBAC OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_155/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 153 (training_pending_items table). RBAC verificado no service (não apenas no router) para garantir invariante de negócio. Executor DEVE verificar padrão de RBAC do projeto antes de implementar (pode ser via dependency injection de current_user ou direto no service).

## Riscos
- Se o projeto usa RBAC via FastAPI dependencies no router, o guard de service pode ser redundante — verificar e documentar onde o RBAC vive no projeto

## Análise de Impacto
**Arquivos modificados:**
- `Hb Track - Backend/app/services/training_pending_service.py` — CRIADO (CRUD INV-066 + guards INV-067)
- `Hb Track - Backend/app/core/exceptions.py` — `SessionClosedError(BusinessError)` adicionada (necessária para contrato INV-067)

**Dependência confirmada:**
- AR_153 ✅ — migration `0067_attendance_preconfirm_pending_items.py` criou `training_pending_items` com status enum ('open','resolved','cancelled') e item_type ('equipment','material','admin','other')

**Sem modelo ORM:** `TrainingPendingItem` model não existe — service usa queries SQLAlchemy text/core diretamente sobre a tabela.

**RBAC:** verificado no service via `context.role_code` e `context.user_id`. Roles de treinador: 'treinador', 'dirigente', 'superadmin'. Atleta só edita/cancela próprios items.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em eb88236
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/training_pending_service.py'); assert f.exists(), 'FAIL: training_pending_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'athlete' in c.lower() or 'rbac' in c.lower() or 'permission' in c.lower(), 'FAIL: logica RBAC/atleta ausente'; print('PASS AR_155: training_pending_service.py com RBAC OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T17:51:25.504982+00:00
**Behavior Hash**: 0ae7fb89c2f8b431135e763060f96b045af0d569984c7ccde141067e807f6b79
**Evidence File**: `docs/hbtrack/evidence/AR_155/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em eb88236
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_155_eb88236/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:47:28.512712+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_155_eb88236/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_155/executor_main.log`
