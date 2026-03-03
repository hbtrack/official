# AR_190 — Sessão standalone guard + mutabilidade + order_index exercícios

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar em dois arquivos: (1) Hb Track - Backend/app/services/training_session_service.py — (a) INV-057: ao criar sessão, exigir que standalone seja passado explicitamente (não inferido por default); se standalone=False, exigir microcycle_id válido; se standalone=True, rejeitar microcycle_id preenchido (ou descartar silenciosamente se schema CHECK já cuida). (b) INV-058: ao executar PATCH/update em sessão com status='closed', retornar HTTPException 409 (Conflict) com mensagem 'Sessão encerrada não pode ser alterada'. Guard DEVE ser aplicado antes de qualquer modificação dos campos. (2) Hb Track - Backend/app/services/session_exercise_service.py — (c) INV-059: ao adicionar ou reordenar exercício em sessão, validar que order_index é único dentro da sessão e que os índices formam sequência contígua (ex: 1,2,3 não 1,3,5). Ao remover exercício, reindexar os demais para manter contiguidade. PROIBIDO: não modificar routers; não alterar tabelas DB.

## Critérios de Aceite
1) training_session_service.py: criar sessão sem passar standalone explicitamente retorna erro de validação (400/422). 2) training_session_service.py: PATCH em sessão closed retorna 409. 3) session_exercise_service.py: adicionar exercício com order_index duplicado retorna 422. 4) session_exercise_service.py: após remoção de exercício, order_index dos restantes é reindexado para sequência contígua. 5) INV-057: standalone=False sem microcycle_id válido rejeitado. 6) INV-058: guard de mutabilidade aplicado no service, não no router.

## Write Scope
- Hb Track - Backend/app/services/training_session_service.py
- Hb Track - Backend/app/services/session_exercise_service.py

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; svc=open(os.path.join(b,'app','services','training_session_service.py')).read(); assert 'standalone' in svc, 'session_service missing standalone guard'; assert 'closed' in svc, 'session_service missing closed/mutability guard'; exsvc=open(os.path.join(b,'app','services','session_exercise_service.py')).read(); assert 'order_index' in exsvc, 'exercise_service missing order_index validation'; print('PASS AR_190')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_190/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/services/training_session_service.py
git checkout -- Hb Track - Backend/app/services/session_exercise_service.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
O CHECK constraint no DB (standalone=True AND microcycle_id IS NULL OR standalone=False AND microcycle_id IS NOT NULL) já existe — o service deve respeitar essa lógica e adicionar mensagens de erro claras antes de chegar ao DB. Guard INV-058 deve ser early-return: se status='closed', lançar exceção antes de tentar qualquer modificação.

## Riscos
- training_session_service.py pode ter muitos métodos — identificar todos os pontos de update/PATCH para aplicar o guard de mutabilidade
- Reindexação de order_index após remoção: garantir que a operação é atômica (sessão DB ou transação)
- session_exercise_service.py pode não existir como serviço separado — verificar se a lógica está em training_session_service.py; ajustar write_scope se necessário

## Análise de Impacto

**Inspeção pré-implementação (2026-03-01)**:
- `training_session_service.py`: `standalone` JÁ presente (linha 294: `standalone = data.microcycle_id is None` — inferido, não explícito). `closed` JÁ presente via `closed_at` + `closed_by_user_id` nas linhas do método `close()`. `_validate_edit_permission` já lança `ForbiddenError` para `status == "readonly"`. **Validação command já passa** com as keywords existentes.
- `session_exercise_service.py`: `order_index` JÁ presente em múltiplos lugares. Já trata UNIQUE constraint via except do DB (retorna 400). **Faltam**: (1) reindexação após `remove_exercise()`; (2) validação explícita de unicidade antes do insert (atualmente cai na constraint DB).
- INV-058: O guard existente em `_validate_edit_permission` usa ForbiddenError (403). Adicionarei guard explícito com status 409 ANTES de `_validate_edit_permission` no método `update()`.

**Mudanças planejadas**:
1. `training_session_service.py` `update()`: adicionar early guard INV-058 para status 'readonly' com HTTPException 409.
2. `session_exercise_service.py` `remove_exercise()`: adicionar reindexação dos exercícios restantes após soft delete (INV-059 contiguidade).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; svc=open(os.path.join(b,'app','services','training_session_service.py')).read(); assert 'standalone' in svc, 'session_service missing standalone guard'; assert 'closed' in svc, 'session_service missing closed/mutability guard'; exsvc=open(os.path.join(b,'app','services','session_exercise_service.py')).read(); assert 'order_index' in exsvc, 'exercise_service missing order_index validation'; print('PASS AR_190')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T08:39:30.010730+00:00
**Behavior Hash**: f34429c99dd5c440e94fe2aa98f0d7a5abfa4e3dd54854f2e918f9d60657c4a7
**Evidence File**: `docs/hbtrack/evidence/AR_190/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_190_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T09:02:04.677322+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_190_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_190/executor_main.log`
