# AR_148 — Tests: Exercise Bank — todos os invariantes (047-053, EXB-ACL-001..007, 060-062)

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar testes de invariantes para todo o Exercise Bank. Seguir INVARIANTS_TESTING_CANON.md.

Arquivos a criar:
- tests/training/invariants/test_inv_train_047_exercise_scope.py (Classe A: ck_exercises_scope constraint)
- tests/training/invariants/test_inv_train_049_exercise_org_scope.py (Classe A: ck_exercises_org_scope constraint)
- tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py (Classe A: uq_exercise_favorites_user_exercise ou PK)
- tests/training/invariants/test_inv_train_052_exercise_media.py (Classe A: uq_exercise_media_exercise_order constraint)
- tests/training/invariants/test_inv_train_exb_acl_001_visibility_mode.py (Classe A: ck_exercises_visibility_mode constraint)
- tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py (Classe A: uq_exercise_acl_exercise_user constraint)
- tests/training/invariants/test_inv_train_148_exercise_bank_services.py (Classes C2+C1: todos os guards de service: 048, 051, 053, 060, 061, 062, EXB-ACL-002..007)

Cada teste SCHEMA (047,049,050,052,EXB-ACL-001,006):
- 1 caso válido + 2 casos inválidos
- Validar SQLSTATE/constraint_name quando exposto
- usar async_db fixture

Teste SERVICE (148 multi-invariant):
- Classe TestInvTrain148ExerciseBankServices
- Métodos por invariante: test_048_*, test_051_*, test_053_*, test_060_*, test_061_*, test_062_*, test_acl_002_*, test_acl_003_*, test_acl_004_*, test_acl_005_*, test_acl_007_*

## Critérios de Aceite
Todos os 7+ arquivos de teste criados em tests/training/invariants/. pytest tests/training/invariants/test_inv_train_047* tests/training/invariants/test_inv_train_049* tests/training/invariants/test_inv_train_050* tests/training/invariants/test_inv_train_052* tests/training/invariants/test_inv_train_exb_acl* tests/training/invariants/test_inv_train_148* TODOS PASSAM.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_047_exercise_scope.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_049_exercise_org_scope.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_052_exercise_media.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_001_visibility_mode.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_148_exercise_bank_services.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_047_exercise_scope.py tests/training/invariants/test_inv_train_049_exercise_org_scope.py tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py tests/training/invariants/test_inv_train_052_exercise_media.py tests/training/invariants/test_inv_train_exb_acl_001_visibility_mode.py tests/training/invariants/test_inv_train_exb_acl_006_acl_table.py tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v --tb=short 2>&1 | Select-String -Pattern 'passed|failed|error'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_148/executor_main.log`

## Notas do Arquiteto
Classe A (schema) + Classe C2 (service). TODOS os testes de schema devem usar async_db fixture. Testes de service devem usar async_db sem mock de DB. Anti-falso-positivo obrigatório: para Classe A, o teste DEVE falhar se a constraint for removida — usar try/except e assert que o erro contém o constraint_name.

## Riscos
- Se async_db fixture or conftest.py não tem org + user fixtures para exercise setup, testes precisarão criar do zero — verificar conftest.py em tests/training/
- INV-050: se PK já supre uniqueness, criar teste que prova que INSERT duplicado é rejeitado via PK (não precisa de named UNIQUE constraint separada)

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

