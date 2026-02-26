# AR_145 — Service: exercise_service.py — guards Exercise Bank

**Status**: ✅ VERIFICADO
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
python temp/ar145_validate.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_145/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de Task 144 (schema scope/visibility_mode/deleted_at existirem). O Executor DEVE primeiro verificar a assinatura atual de exercise_service.py antes de adicionar guards. NÃO remover funcionalidade existente. ExerciseImmutableError deve ser definida em app/exceptions.py ou equivalente.

## Riscos
- Se exercise_service.py não tem um método update() claro, o guard pode precisar ser adicionado em múltiplos pontos
- INV-053: se session_exercises não tem FK para sessions.status, a queryhistórica pode ser custosa — usar indexed query

## Análise de Impacto

**Tipo**: Service — Guards de domínio Exercise Bank
**Risco**: Baixo — adiciona guards sem quebrar funcionalidade existente
**Arquivos afetados**:
- MODIFY: `Hb Track - Backend/app/services/exercise_service.py`
- MODIFY: `Hb Track - Backend/app/core/exceptions.py`

**Mudanças em exceptions.py**:
- ADD: ExerciseImmutableError (BusinessError subclass)
- ADD: ExerciseReferencedError (BusinessError subclass)

**Mudanças em exercise_service.py**:
- ADD import: ExerciseImmutableError, ExerciseReferencedError
- MODIFY create_exercise(): INV-060 default 'restricted' para ORG
- MODIFY update_exercise(): INV-048 guard SYSTEM immutable
- ADD copy_system_exercise_to_org(): INV-061 clone SYSTEM→ORG
- ADD soft_delete_exercise(): INV-053 soft delete com deleted_at/deleted_reason

**Backward compat**: Sim — todos os métodos existentes mantêm assinatura original

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar145_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:07:07.064919+00:00
**Behavior Hash**: ce0159efbf867e089810f53366f16032eb743e83721d3b432e55ef645105b2b5
**Evidence File**: `docs/hbtrack/evidence/AR_145/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar145_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:07:11.019164+00:00
**Behavior Hash**: ce0159efbf867e089810f53366f16032eb743e83721d3b432e55ef645105b2b5
**Evidence File**: `docs/hbtrack/evidence/AR_145/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 018412f
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_145_018412f/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:55:29.433743+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_145_018412f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_145/executor_main.log`
