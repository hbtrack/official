# AR_212 — Criar 6 testes ausentes: INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar os 6 únicos arquivos de teste de invariante que genuinamente não existem no filesystem. Cada arquivo deve seguir o padrão dos existentes (pytest, ao menos 1 test case testando o happy path e 1 testando a violação da invariante via assert de exceção ou status HTTP 4xx). Invariantes a cobrir: INV-TRAIN-053 (soft delete de exercício não deve quebrar sessões históricas que o referenciam); INV-TRAIN-060 (exercício ORG novo criado com visibility_mode=restricted por default, não org_wide); INV-TRAIN-061 (adaptar exercício SYSTEM cria cópia ORG, não edita o original); INV-TRAIN-062 (exercise_visibility_mode é required ao adicionar exercício a sessão — validação de schema); INV-TRAIN-EXB-ACL-005 (criador de exercício ORG tem acesso implícito mesmo sem estar explicitamente na ACL); INV-TRAIN-EXB-ACL-007 (mudança de ACL ou visibility_mode não invalida leitura de sessões históricas que referenciam o exercício). Após criar e validar os 6 arquivos, atualizar TEST_MATRIX_TRAINING.md §5 para as 6 INV: status COBERTO, Últ.Execução=data_atual, evidência apontando para o arquivo.

## Critérios de Aceite
Existência de test_inv_train_053_soft_delete_exercise_no_break_historic.py com >= 2 test cases (happy + violação); Existência de test_inv_train_060_org_exercise_default_restricted.py com >= 2 test cases; Existência de test_inv_train_061_system_exercise_copy_not_edit.py com >= 2 test cases; Existência de test_inv_train_062_exercise_visibility_required.py com >= 2 test cases; Existência de test_inv_train_exb_acl_005_creator_implicit_access.py com >= 2 test cases; Existência de test_inv_train_exb_acl_007_acl_change_no_retrobreak.py com >= 2 test cases; pytest dos 6 arquivos = 0 FAILs; TEST_MATRIX §5: INV-053/060/061/062/EXB-ACL-005/007 = COBERTO

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_062_exercise_visibility_required.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py tests/training/invariants/test_inv_train_062_exercise_visibility_required.py tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_212/executor_main.log`

## Riscos
- Os 6 testes dependem de models/services já implementados pelas ARs 144-167. Verificar imports antes de criar os testes.
- INV-053 (soft delete) e INV-EXB-ACL-007 (ACL retroativo) podem requerer fixtures de DB para criar exercícios referenciados em sessões históricas — usar approach estático (schema inspection) se DB não disponível.
- INV-060 contradiz a noção original do DEC-TRAIN-EXB-001B que diz 'default org_wide' — mas INV-TRAIN-060 e a emenda de v1.3.0 definem default=restricted. AR-TRAIN-032 deve confirmar qual é o SSOT autoritativo antes de criar o teste.

## Análise de Impacto

**Escopo**: 6 novos arquivos de teste + TEST_MATRIX_TRAINING.md §5 (6 linhas).

**Serviços/exceções utilizados** (confirmados no codebase):
- ExerciseService.create_exercise() — INV-060 (default restricted)
- ExerciseService.soft_delete_exercise() — INV-053 (soft delete sem break histórico)
- ExerciseService.copy_system_exercise_to_org() — INV-061 (copy, não edit)
- SessionExerciseService._verify_exercise_visibility() + ExerciseNotVisibleError — INV-062
- ExerciseAclService.has_access() — EXB-ACL-005 (creator bypass)
- ExerciceAclService.revoke_access() + DB session_exercise — EXB-ACL-007 (retrobreak)

**Abordagem por INV**:
- INV-053: INTEGRATION — soft_delete_exercise(); verificar via DB que session_exercise ainda lê o exercício (deleted_at não cascadeado).
- INV-060: SERVICE — ExerciseService.create_exercise() sem visibility_mode → deve defaultar para restricted.
- INV-061: SERVICE — copy_system_exercise_to_org() → novo ORG criado, original SYSTEM inalterado.
- INV-062: SERVICE — add_exercise() para exercício restricted com usuário sem ACL → ExerciseNotVisibleError.
- EXB-ACL-005: SERVICE — ExerciseAclService.has_access() para criador sem ACL entry → True.
- EXB-ACL-007: INTEGRATION — criar exercise+session_exercise, revogar ACL, verificar session_exercise intacto.

**§5 TEST_MATRIX — 6 linhas atualizadas** (após pytest OK):
- INV-053/060/061/062/EXB-ACL-005/EXB-ACL-007: PENDENTE → COBERTO, data 2026-03-04.

**Efeito colateral**: nenhum em código de produto (somente novos arquivos de teste e doc).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py tests/training/invariants/test_inv_train_062_exercise_visibility_required.py tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py 2>&1 | tail -5`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-03T12:45:35.379721+00:00
**Behavior Hash**: d7f0027db1b9f614c9423cc40145a57f68b1cffb191d13110e7ed140b25fbadd
**Evidence File**: `docs/hbtrack/evidence/AR_212/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py tests/training/invariants/test_inv_train_062_exercise_visibility_required.py tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py 2>&1 | Select-Object -Last 5`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-03T12:46:55.798351+00:00
**Behavior Hash**: 2d24c65d62abc6c47598c16bbfe974104367861253896cf74284de3a94258cc3
**Evidence File**: `docs/hbtrack/evidence/AR_212/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_053_soft_delete_exercise_no_break_historic.py tests/training/invariants/test_inv_train_060_org_exercise_default_restricted.py tests/training/invariants/test_inv_train_061_system_exercise_copy_not_edit.py tests/training/invariants/test_inv_train_062_exercise_visibility_required.py tests/training/invariants/test_inv_train_exb_acl_005_creator_implicit_access.py tests/training/invariants/test_inv_train_exb_acl_007_acl_change_no_retrobreak.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T12:47:43.641371+00:00
**Behavior Hash**: 6a86838d0052b8003f4d7cf1b6e69c2804546ba8516fe8ac4a1d2ef91cae3647
**Evidence File**: `docs/hbtrack/evidence/AR_212/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_212_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T13:03:09.868127+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_212_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_212/executor_main.log`
