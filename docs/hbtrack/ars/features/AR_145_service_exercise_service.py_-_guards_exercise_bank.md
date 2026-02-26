# AR_145 — Service: exercise_service.py — guards Exercise Bank

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar guards ao exercise_service.py existente para implementar as invariantes de serviço do Exercise Bank:

1. INV-048 (SYSTEM imutável): Guard em update/delete — se exercise.scope == 'SYSTEM', levantar ExerciseImmutableError (business exception, não DB error). SYSTEM exercises só podem ser alterados por superadmin com permissão especial.

2. INV-060 (default restricted): Ao criar exercise com scope='ORG', visibility_mode deve defaultar para 'restricted' se não informado explicitamente.

3. INV-061 (copy-to-org): Adicionar método copy_system_exercise_to_org(exercise_id, organization_id, user_id) que cria um clone ORG da exercise SYSTEM em vez de editar o original. O clone herda campos mas fica com scope='ORG' e organization_id da org destino.

4. INV-053 (soft-delete): Implementar soft_delete_exercise(exercise_id, reason, user_id) que seta deleted_at + deleted_reason. Guard: se exercise está referenciada em session_exercises históricas (session.status='readonly'), NÃO remover — apenas marcar como deleted. Exercícios deletados NÃO aparecem em catálogos mas continuam acessíveis via session_exercise para histórico.

## Critérios de Aceite
1. update() para exercise SYSTEM levanta ExerciseImmutableError. 2. create() com scope='ORG' e visibility_mode omitido resulta em visibility_mode='restricted'. 3. copy_system_exercise_to_org() cria clone ORG retornando novo exercise com scope='ORG'. 4. soft_delete_exercise() marca deleted_at/deleted_reason sem apagar registros históricos em session_exercises.

## Write Scope
- Hb Track - Backend/app/services/exercise_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices::test_048_system_immutable tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices::test_060_default_restricted tests/training/invariants/test_inv_train_148_exercise_bank_services.py::TestInvTrain148ExerciseBankServices::test_053_soft_delete_preserves_history -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_145/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 144 (schema scope/visibility_mode/deleted_at existirem). O Executor DEVE primeiro verificar a assinatura atual de exercise_service.py antes de adicionar guards. NÃO remover funcionalidade existente. ExerciseImmutableError deve ser definida em app/exceptions.py ou equivalente.

## Riscos
- Se exercise_service.py não tem um método update() claro, o guard pode precisar ser adicionado em múltiplos pontos
- INV-053: se session_exercises não tem FK para sessions.status, a queryhistórica pode ser custosa — usar indexed query

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

