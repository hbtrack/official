# AR_183 — Endpoints ACL + copy-to-org + toggle visibility em exercises.py router

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar 5 endpoints em Hb Track - Backend/app/api/v1/routers/exercises.py usando exercise_acl_service.py e exercise_service.py ja implementados: (1) GET /exercises/{id}/acl — lista users na ACL, apenas criador pode ver (403 caso contrario). (2) POST /exercises/{id}/acl — adiciona user da mesma org, retorna 201; delega para exercise_acl_service.grant_access. (3) DELETE /exercises/{id}/acl/{user_id} — remove user da ACL, retorna 204; delega para exercise_acl_service.revoke_access. (4) PATCH /exercises/{id}/visibility — altera visibility_mode (org_wide|restricted), apenas criador, retorna 200; delega para exercise_acl_service.change_visibility_to_org_wide ou novo metodo change_to_restricted. (5) POST /exercises/{id}/copy-to-org — cria copia ORG de exercise SYSTEM com scope=ORG, organization_id e created_by_user_id do solicitante, retorna 201. Todos os endpoints com response_model explicito. Apos implementar: rodar python scripts/ssot/gen_docs_ssot.py para atualizar openapi.json. Proibido: modificar FE, services ja implementados.

## Critérios de Aceite
1) Router exercises.py contem rotas /acl (GET, POST), /acl/{user_id} (DELETE), /visibility (PATCH), /copy-to-org (POST). 2) copy-to-org cria exercise ORG a partir de SYSTEM. 3) Todos os endpoints tem response_model declarado. 4) gen_docs_ssot.py roda apos implementacao.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/exercises.py
- Hb Track - Backend/docs/ssot/openapi.json

## SSOT Touches
- [ ] docs/ssot/openapi.json

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','api','v1','routers','exercises.py')).read(); assert 'copy-to-org' in c or 'copy_to_org' in c,'router missing copy-to-org'; assert '/acl' in c or 'acl' in c.lower(),'router missing ACL endpoints'; assert 'visibility' in c,'router missing visibility endpoint'; assert 'response_model' in c,'router missing response_model'; print('PASS AR_183')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_183/executor_main.log`

## Notas do Arquiteto
Executor roda gen_docs_ssot.py ANTES de hb report para atualizar openapi.json. copy-to-org deve criar novo exercise com scope=ORG, organization_id=current_user.organization_id, created_by_user_id=current_user.id, copiando name/description/tag_ids/category. Verificar se schema Pydantic ExerciseACLResponse existe; se nao, criar minimo em app/schemas/exercises.py.

## Riscos
- gen_docs_ssot.py pode falhar se houver erros de importacao no router — Executor deve testar import antes de rodar ssot
- change_visibility_to_restricted pode nao existir em exercise_acl_service — Executor adiciona metodo se necessario (dentro do write_scope de AR_182 que ja inclui o service)

## Análise de Impacto
- **exercises.py router (lido)**: Contém CRUD + favorites. Faltam 5 endpoints novos. Importa ExerciseService mas não ExerciseAclService.
- **exercise_acl_service.py (lido)**: grant_access, revoke_access, list_access, has_access, change_visibility_to_org_wide — tudo implementado.
- **exercise_service.py (lido)**: copy_system_exercise_to_org() — existe L480. update_exercise() aceita visibility_mode via data dict.
- **schemas/exercises.py (lido)**: Sem ExerciseACLResponse, ExerciseACLGrantRequest, VisibilityUpdateRequest — criar conforme nota Arquiteto.
- **Mudanças**:
  1. schemas/exercises.py: ADD ExerciseACLResponse (id/exercise_id/user_id/granted_by_user_id/granted_at), ExerciseACLGrantRequest (target_user_id), VisibilityUpdateRequest (visibility_mode)
  2. exercises.py router: ADD import ExerciseAclService + novos schemas; ADD 5 endpoints:
     - GET /exercises/{exercise_id}/acl → list_access(); creator guard inline
     - POST /exercises/{exercise_id}/acl → grant_access(); 201
     - DELETE /exercises/{exercise_id}/acl/{user_id} → revoke_access(); 204
     - PATCH /exercises/{exercise_id}/visibility → org_wide: change_visibility_to_org_wide(); restricted: update_exercise()
     - POST /exercises/{exercise_id}/copy-to-org → copy_system_exercise_to_org(); 201
  3. gen_docs_ssot.py antes de hb report
- **Sem migration nova**.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','api','v1','routers','exercises.py')).read(); assert 'copy-to-org' in c or 'copy_to_org' in c,'router missing copy-to-org'; assert '/acl' in c or 'acl' in c.lower(),'router missing ACL endpoints'; assert 'visibility' in c,'router missing visibility endpoint'; assert 'response_model' in c,'router missing response_model'; print('PASS AR_183')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T03:21:27.896041+00:00
**Behavior Hash**: 958b1038ac24dde4edd5bdb6f1ecd7b5d6e979b1f8dac1e9ca8627e9333ed081
**Evidence File**: `docs/hbtrack/evidence/AR_183/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_183_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T03:49:20.449671+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_183_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_183/executor_main.log`
