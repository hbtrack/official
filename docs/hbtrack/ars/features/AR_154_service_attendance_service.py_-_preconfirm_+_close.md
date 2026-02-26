# AR_154 — Service: attendance_service.py — preconfirm + close flow

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar ao attendance_service.py existente os fluxos avançados:

1. INV-063 (preconfirm): Adicionar método set_preconfirm(session_id, athlete_id, user_id) que cria/atualiza attendance com presence_status='preconfirm'. Regra: só pode ser chamado ANTES da sessão começar (session.status em ['scheduled','draft']. Atleta e treinador podem chamar (RBAC verificado no router).

2. INV-064 (consolidação oficial no fechamento): Adicionar lógica em close_session_attendance(session_id, closed_by_user_id):
   - attendance com presence_status='preconfirm' → converter para 'absent' se não confirmado pelo treinador (regra padrão, reversível por correction)
   - Ou: manter 'preconfirm' e requerer resolução manual (verificar INV-064 no INVARIANTS_TRAINING.md para decisão correta)

3. INV-065 (guard fecha com pending): Adicionar guard em close_session() ou session_service: ANTES de fechar sessão, verificar COUNT de training_pending_items com status='open' para a sessão. Se > 0, levantar SessionHasPendingItemsError.

4. Integração: close_session_attendance() deve ser chamado automaticamente quando session.status transita para 'readonly'.

## Critérios de Aceite
1. set_preconfirm() cria attendance com presence_status='preconfirm' para sessão scheduled. 2. set_preconfirm() falha se sessão já está in_progress ou readonly. 3. close_session() falha com SessionHasPendingItemsError se há pending items open. 4. close_session_attendance() converte preconfirm→absent (ou mantém conforme regra definida).

## Write Scope
- Hb Track - Backend/app/services/attendance_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_063_preconfirm.py tests/training/invariants/test_inv_train_064_close_consolidation.py tests/training/invariants/test_inv_train_065_close_pending_guard.py -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_154/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 153 (preconfirm status + training_pending_items). Para INV-064: a regra de consolidação ('preconfirm→absent' vs 'preconfirm→manter') pode ser ambígua no PRD. Executor DEVE ler INVARIANTS_TRAINING.md INV-064 verbatim antes de implementar. Se ambíguo, marcar como PENDING e reportar ao Arquiteto.

## Riscos
- INV-064 regra de consolidação pode ser ambígua — verificar PRD_TREINOS ou INVARIANTS_TRAINING.md antes de implementar
- close_session() pode estar em training_session_service.py, não attendance_service.py — verificar e adaptar o guard sem duplicar lógica

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

