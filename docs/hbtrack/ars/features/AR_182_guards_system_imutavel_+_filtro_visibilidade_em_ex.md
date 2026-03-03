# AR_182 — Guards SYSTEM imutavel + filtro visibilidade em exercise_service.py + testes INV

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar em Hb Track - Backend/app/services/exercise_service.py: (1) Guard SYSTEM imutavel: PATCH/DELETE em exercise.scope=SYSTEM por usuario nao-plataforma retorna 403 (INV-TRAIN-048). (2) Filtro de catalogo: listagem retorna apenas SYSTEM + ORG da org do usuario, respeitando visibility_mode e ACL (INV-TRAIN-051). Para visibility=restricted: incluir exercise se usuario e criador OU tem entrada em exercise_acl. (3) Guard RBAC Treinador explicito: criacao/edicao de exercise ORG exige papel Treinador (usar constante, nao inferencia). Criar testes em Hb Track - Backend/tests/training/invariants/: test_inv_train_048_system_immutable.py (verifica 403 em PATCH/DELETE SYSTEM), test_inv_train_051_catalog_visibility.py (verifica filtro org+visibilidade), test_inv_train_exb_acl_002_acl_restricted.py (ACL so aplicavel a restricted), test_inv_train_exb_acl_003_anti_cross_org.py (user cross-org rejeitado), test_inv_train_exb_acl_004_creator_authority.py (somente criador gerencia ACL). Proibido: modificar routers, exercise_acl_service.py, FE.

## Critérios de Aceite
1) Guard SYSTEM: PATCH/DELETE em exercise SYSTEM por user nao-plataforma levanta 403. 2) Filtro catalogo: SYSTEM + ORG da org, org_wide visivel a todos, restricted visivel apenas criador ou ACL entry. 3) RBAC Treinador: criacao ORG exige role explicito. 4) 5 testes novos passam (test_inv_train_048, 051, exb_acl_002, 003, 004). 5) pytest nos 5 novos testes retorna exit 0.

## Write Scope
- Hb Track - Backend/app/services/exercise_service.py
- Hb Track - Backend/tests/training/invariants/

## Validation Command (Contrato)
```
python -c "import subprocess; t='Hb Track - Backend/tests/training/invariants/'; tests=[t+'test_inv_train_048_system_immutable.py',t+'test_inv_train_051_catalog_visibility.py',t+'test_inv_train_exb_acl_002_acl_restricted.py',t+'test_inv_train_exb_acl_003_anti_cross_org.py',t+'test_inv_train_exb_acl_004_creator_authority.py']; r=subprocess.run(['pytest']+tests+['-q'],capture_output=True); assert r.returncode==0,'FAIL AR_182 exit='+str(r.returncode); print('PASS AR_182')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_182/executor_main.log`

## Notas do Arquiteto
exercise_acl_service.py JA EXISTE e NAO e escopo deste AR — nao modificar. Testes devem usar fixtures de DB async (pytest-asyncio pattern dos outros testes do modulo). Consultar test_inv_train_exb_acl_001 como referencia de estrutura de fixture.

## Riscos
- exercise_service.py pode nao ter acesso ao model User/role — Executor deve verificar imports existentes e adicionar se necessario
- Testes de invariantes requerem fixtures async + DB — Executor deve seguir padrao dos testes existentes no diretorio

## Análise de Impacto
- **exercise_service.py (lido)**: Guards ja implementados: INV-048 (SYSTEM imutavel) em update_exercise() L393 + soft_delete_exercise() L566; INV-051 (filtro catalogo) em list_exercises() L247; copy_system_exercise_to_org() para INV-061. Usa hasattr() que sera substituido por acesso direto apos AR_181 adicionar columns ao model.
- **exercise_acl_service.py (lido)**: grant_access/revoke_access/list_access/has_access/change_visibility_to_org_wide implementados. Sem change_visibility_to_restricted (necessario para AR_183).
- **Mudancas em exercise_service.py**: Guards ja existem. Adicionar role_code explícito em create_exercise() para RBAC Treinador conforme AR.
- **Criar 5 test files**: seguem padrao async_db de test_inv_train_exb_acl_001 (raw SQL para setup, service calls para verificar invariantes).
- **Risco**: testes sao DB integration — requerem postgres rodando (porta 5433). Seguem mesmo padrao dos testes existentes que passam.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; t='Hb Track - Backend/tests/training/invariants/'; tests=[t+'test_inv_train_048_system_immutable.py',t+'test_inv_train_051_catalog_visibility.py',t+'test_inv_train_exb_acl_002_acl_restricted.py',t+'test_inv_train_exb_acl_003_anti_cross_org.py',t+'test_inv_train_exb_acl_004_creator_authority.py']; r=subprocess.run(['pytest']+tests+['-q'],capture_output=True); assert r.returncode==0,'FAIL AR_182 exit='+str(r.returncode); print('PASS AR_182')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T03:15:00.389356+00:00
**Behavior Hash**: d737e9ed7ebaed4aec8f535d063416dfcc44d815abd9e794d7a47561bad39415
**Evidence File**: `docs/hbtrack/evidence/AR_182/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_182_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T03:49:13.243152+00:00
**Motivo**: 183
**TESTADOR_REPORT**: `_reports/testador/AR_182_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_182/executor_main.log`
