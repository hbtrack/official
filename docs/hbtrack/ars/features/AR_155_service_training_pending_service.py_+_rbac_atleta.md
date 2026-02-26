# AR_155 — Service: training_pending_service.py + RBAC atleta

**Status**: 🔲 PENDENTE
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
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_066_pending_items.py tests/training/invariants/test_inv_train_067_athlete_pending_rbac.py -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_155/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 153 (training_pending_items table). RBAC verificado no service (não apenas no router) para garantir invariante de negócio. Executor DEVE verificar padrão de RBAC do projeto antes de implementar (pode ser via dependency injection de current_user ou direto no service).

## Riscos
- Se o projeto usa RBAC via FastAPI dependencies no router, o guard de service pode ser redundante — verificar e documentar onde o RBAC vive no projeto

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

