# AR_147 — Service: catalog visibility + session exercise guard

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar guards de visibilidade ao catálogo e à adição de exercícios em sessões:

1. INV-051 (catalog visibility): Em exercise_service.py, método list_exercises(organization_id, user_id) deve retornar:
   - Exercises SYSTEM (scope='SYSTEM') sem deleted_at: sempre visíveis
   - Exercises ORG próprias (organization_id match) sem deleted_at: visíveis
   - Exercises ORG de OUTRAS orgs: NUNCA visíveis
   - Exercises deleted (deleted_at IS NOT NULL): excluídas do catálogo

2. INV-062 (session exercise visibility guard): Em session_exercise_service.py, método add_exercise_to_session(session_id, exercise_id, user_id) deve verificar:
   - Se exercise.scope == 'SYSTEM': permitir (sempre acessível)
   - Se exercise.scope == 'ORG' e exercise.visibility_mode == 'org_wide' e exercise.organization_id == session.organization_id: permitir
   - Se exercise.scope == 'ORG' e exercise.visibility_mode == 'restricted': verificar exercise_acl_service.has_access(exercise_id, user_id)
   - Qualquer outro caso: levantar ExerciseNotVisibleError

## Critérios de Aceite
1. list_exercises() não retorna exercises de outras orgs. 2. list_exercises() não retorna exercises deleted. 3. list_exercises() retorna exercises SYSTEM. 4. add_exercise_to_session() falha com ExerciseNotVisibleError se exercise não está no scope do usuário. 5. add_exercise_to_session() permite SYSTEM exercises para todas as orgs.

## Write Scope
- Hb Track - Backend/app/services/exercise_service.py
- Hb Track - Backend/app/services/session_exercise_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices::test_051_catalog_visibility tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices::test_062_session_exercise_guard -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_147/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 144 (scope/visibility_mode colunas) e Task 146 (exercise_acl_service.has_access()). O Executor DEVE verificar a assinatura atual de session_exercise_service.py antes de adicionar guard. NÃO alterar lógica de order_index/reorder já existente.

## Riscos
- Se session_exercise_service.py já tem add_exercise_to_session(), verificar se guard pode ser injetado sem quebrar testes existentes (058, 059)
- LIST query com múltiplos filtros pode ser lenta sem índice em exercises(organization_id, scope, deleted_at)

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

