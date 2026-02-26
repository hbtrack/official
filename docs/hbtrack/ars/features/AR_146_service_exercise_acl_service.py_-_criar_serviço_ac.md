# AR_146 — Service: exercise_acl_service.py — criar serviço ACL

**Status**: ✅ SUCESSO
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
python temp/ar146_validate.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_146/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 144 (exercise_acl table existir com uq_exercise_acl_exercise_user). Exceções devem ser definidas em app/exceptions.py. O Executor DEVE verificar se app/exceptions.py existe e qual padrão de exceção usa o projeto antes de criar as novas exceptions.

## Riscos
- Se app/exceptions.py usa padrão diferente (ex: HTTPException direto no service), adaptar ao padrão existente
- INV-EXB-ACL-007: verificar session_exercises históricas pode ser N+1 — usar EXISTS query

## Análise de Impacto

**Tipo**: Service — Novo serviço ACL de exercícios
**Risco**: Baixo — novo arquivo sem impacto em existentes
**Arquivos afetados**:
- CREATE: `Hb Track - Backend/app/services/exercise_acl_service.py`
- CREATE: `Hb Track - Backend/app/models/exercise_acl.py`
- MODIFY: `Hb Track - Backend/app/core/exceptions.py`

**Novas exceptions**:
- AclNotApplicableError (INV-EXB-ACL-002)
- AclCrossOrgError (INV-EXB-ACL-003)
- AclUnauthorizedError (INV-EXB-ACL-004)
- AclDuplicateError (INV-EXB-ACL-006)

**Métodos implementados**:
- has_access(): INV-EXB-ACL-005 creator bypass
- grant_access(): INV-EXB-ACL-002/003/004/006
- revoke_access(): INV-EXB-ACL-004/007
- list_access(): lista ACL entries
- change_visibility_to_org_wide(): INV-EXB-ACL-007

**Dependências**: AR_144 (tabela exercise_acl)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar146_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:09:44.665633+00:00
**Behavior Hash**: 4e07a15047a6db53b4b1ec29676eb8f01acdab365448ffa50d3c3369aafa2f78
**Evidence File**: `docs/hbtrack/evidence/AR_146/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar146_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:09:53.605305+00:00
**Behavior Hash**: 4e07a15047a6db53b4b1ec29676eb8f01acdab365448ffa50d3c3369aafa2f78
**Evidence File**: `docs/hbtrack/evidence/AR_146/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 018412f
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_146_018412f/result.json`
