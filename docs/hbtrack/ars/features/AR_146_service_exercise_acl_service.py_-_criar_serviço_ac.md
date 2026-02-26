# AR_146 — Service: exercise_acl_service.py — criar serviço ACL

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar novo arquivo Hb Track - Backend/app/services/exercise_acl_service.py implementando todas as invariantes de ACL:

1. INV-EXB-ACL-002 (ACL só para restricted): grant_access() deve rejeitar se exercise.visibility_mode != 'restricted' — levantar AclNotApplicableError.

2. INV-EXB-ACL-003 (anti-cross-org): grant_access() deve verificar que user.organization_id == exercise.organization_id — levantar AclCrossOrgError.

3. INV-EXB-ACL-004 (creator authority only): Apenas exercise.created_by_user_id pode chamar grant_access() e revoke_access() — levantar AclUnauthorizedError para outros.

4. INV-EXB-ACL-005 (creator bypass): has_access(exercise_id, user_id) deve retornar True se user_id == exercise.created_by_user_id INDEPENDENTE do ACL. Creator sempre acessa.

5. INV-EXB-ACL-006 (constraint uq): Tentativa de insert duplicado (mesmo exercise_id + user_id) deve ser detectada — preferir verificação prévia via SELECT antes do INSERT para retornar AclDuplicateError (não mensagem de DB).

6. INV-EXB-ACL-007 (sem retrobreak): revoke_access() e change_visibility_to_org_wide() NÃO devem afetar session_exercises históricas — apenas impedir novos acessos. Log da mudança em audit_logs se tabela existir.

## Critérios de Aceite
1. grant_access() para exercise org_wide levanta AclNotApplicableError. 2. grant_access() para user de outra org levanta AclCrossOrgError. 3. grant_access() por não-criador levanta AclUnauthorizedError. 4. has_access() retorna True para criador mesmo sem ACL entry. 5. grant_access() duplicado levanta AclDuplicateError. 6. revoke_access() não afeta sessions históricas existentes.

## Write Scope
- Hb Track - Backend/app/services/exercise_acl_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices -k 'acl' -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_146/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 144 (exercise_acl table existir com uq_exercise_acl_exercise_user). Exceções devem ser definidas em app/exceptions.py. O Executor DEVE verificar se app/exceptions.py existe e qual padrão de exceção usa o projeto antes de criar as novas exceptions.

## Riscos
- Se app/exceptions.py usa padrão diferente (ex: HTTPException direto no service), adaptar ao padrão existente
- INV-EXB-ACL-007: verificar session_exercises históricas pode ser N+1 — usar EXISTS query

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

