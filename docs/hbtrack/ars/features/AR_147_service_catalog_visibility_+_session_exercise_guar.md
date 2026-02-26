# AR_147 — Service: catalog visibility + session exercise guard

**Status**: ✅ VERIFICADO
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
python temp/ar147_validate.py
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

### Execução Executor em 017cc0c
**Status Executor**: ❌ FALHA
**Comando**: `python temp/ar147_validate.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-26T13:15:19.209898+00:00
**Behavior Hash**: f36ba26eb52247c02fe18b8fd355d06b1cf0ba20518cdd18af9076351398e2fa
**Evidence File**: `docs/hbtrack/evidence/AR_147/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 017cc0c
**Status Executor**: ❌ FALHA
**Comando**: `python temp/ar147_validate.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-26T13:15:30.231570+00:00
**Behavior Hash**: f36ba26eb52247c02fe18b8fd355d06b1cf0ba20518cdd18af9076351398e2fa
**Evidence File**: `docs/hbtrack/evidence/AR_147/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar147_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:16:33.285559+00:00
**Behavior Hash**: 5073b547e3ad981207147a66cab5dd691435276ad1e7d202e27235c07d466cbf
**Evidence File**: `docs/hbtrack/evidence/AR_147/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar147_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:16:48.957921+00:00
**Behavior Hash**: 5073b547e3ad981207147a66cab5dd691435276ad1e7d202e27235c07d466cbf
**Evidence File**: `docs/hbtrack/evidence/AR_147/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 018412f
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_147_018412f/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:55:34.676460+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_147_018412f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_147/executor_main.log`
