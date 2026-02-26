# AR_154 — Service: attendance_service.py — preconfirm + close flow

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar ao attendance_service.py existente os fluxos avançados:

1. ✅ **INV-063 (preconfirm)**: Adicionar método set_preconfirm(session_id, athlete_id, user_id) que cria/atualiza attendance com presence_status='preconfirm'. Regra: só pode ser chamado ANTES da sessão começar (session.status em ['scheduled','draft']. Atleta e treinador podem chamar (RBAC verificado no router).

2. ✅ **INV-064 (consolidação oficial no fechamento)**: Adicionar lógica em close_session_attendance(session_id, closed_by_user_id):
   - attendance com presence_status='preconfirm' → converter para 'absent' se não confirmado pelo treinador (regra padrão, reversível por correction)
   - Ou: manter 'preconfirm' e requerer resolução manual (verificar INV-064 no INVARIANTS_TRAINING.md para decisão correta)

3. ❌ **CANCELADO — INV-065 (guard fecha com pending)**: ~~Adicionar guard em close_session() ou session_service: ANTES de fechar sessão, verificar COUNT de training_pending_items com status='open' para a sessão. Se > 0, levantar SessionHasPendingItemsError.~~
   
   **RAZÃO DO CANCELAMENTO**: Contradição com INV-TRAIN-065 canônica. A invariante diz: "Se no encerramento houver atleta não elegível ou dado não resolvido, o sistema DEVE PERMITIR encerrar. Itens inconsistentes viram pendências (INV-066), NÃO bloqueiam." Implementar guard de bloqueio violaria a invariante. **Decisão do Arquiteto (2026-02-26)**: Manter comportamento canônico — pendências não bloqueiam encerramento.

4. ⚠️ **PENDENTE (fora de scope)** — Integração: close_session_attendance() deve ser chamado automaticamente quando session.status transita para 'readonly'. **Requer AR separada** para training_session_service.py (fora do write scope desta AR).

## Critérios de Aceite
1. ✅ set_preconfirm() cria attendance com presence_status='preconfirm' para sessão scheduled. 
2. ✅ set_preconfirm() falha se sessão já está in_progress ou readonly. 
3. ❌ ~~close_session() falha com SessionHasPendingItemsError se há pending items open.~~ **CANCELADO** (contradição canônica)
4. ✅ close_session_attendance() converte preconfirm→absent (regra padrão implementada).

## Write Scope
- Hb Track - Backend/app/services/attendance_service.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/attendance_service.py'); assert f.exists(), 'FAIL: attendance_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'preconfirm' in c.lower(), 'FAIL: logica preconfirm ausente'; assert 'close' in c.lower(), 'FAIL: logica close ausente'; print('PASS AR_154: attendance_service.py com preconfirm+close OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_154/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 153 (preconfirm status + training_pending_items). Para INV-064: a regra de consolidação ('preconfirm→absent' vs 'preconfirm→manter') pode ser ambígua no PRD. Executor DEVE ler INVARIANTS_TRAINING.md INV-064 verbatim antes de implementar. Se ambíguo, marcar como PENDING e reportar ao Arquiteto.

## Riscos
- INV-064 regra de consolidação pode ser ambígua — verificar PRD_TREINOS ou INVARIANTS_TRAINING.md antes de implementar
- close_session() pode estar em training_session_service.py, não attendance_service.py — verificar e adaptar o guard sem duplicar lógica

## Análise de Impacto
- **Arquivos lidos**: attendance_service.py (4 métodos existentes: get_session_attendance, record_batch, update_participation, get_session_statistics, correct_attendance), training_session_service.py (close_session L751: pending_review→readonly), INVARIANTS_TRAINING.md (INV-063/064/065 verbatim), exceptions.py (SessionHasPendingItemsError ausente)
- **Contradição crítica (Item 3)**: AR_154 item 3 descreve INV-065 como "guard que bloqueia close" (raise SessionHasPendingItemsError). INV-TRAIN-065 canonical diz OPOSTO: "o sistema DEVE permitir encerrar — itens inconsistentes viram pendências (INV-066), não bloqueiam". Item 3 NÃO implementado — violaria canonical invariant.
- **Item 4 (integração)**: close_session() está em training_session_service.py (fora do WRITE_SCOPE). close_session_attendance() será adicionado ao attendance_service.py; integração automática requer AR separada para training_session_service.py.
- **Mudanças implementadas**:
  1. attendance_service.py: add set_preconfirm(session_id, athlete_id, user_id) — upsert attendance com presence_status='preconfirm', guard session.status in ['scheduled','draft']
  2. attendance_service.py: add close_session_attendance(session_id, closed_by_user_id) → int — converte presence_status='preconfirm' para 'absent' (regra padrão), retorna count de convertidos
- **Dependência confirmada**: migration 0067 (AR_153) adicionou 'preconfirm' a ck_attendance_status — DB aceita o valor. ✓
- **Risco residual**: Item 3 não implementado; se Arquiteto quiser o guard, requer decisão explícita contrapondo INV-065 + AR dedicada para training_session_service.py

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em eb88236
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/attendance_service.py'); assert f.exists(), 'FAIL: attendance_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'preconfirm' in c.lower(), 'FAIL: logica preconfirm ausente'; assert 'close' in c.lower(), 'FAIL: logica close ausente'; print('PASS AR_154: attendance_service.py com preconfirm+close OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T17:28:44.389004+00:00
**Behavior Hash**: bf79b90579c655b32603c8a04b6ee77e99038831ea412ba7e2f2f68eff0216ee
**Evidence File**: `docs/hbtrack/evidence/AR_154/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em eb88236
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_154_eb88236/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:53:06.193444+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_154_eb88236/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_154/executor_main.log`
