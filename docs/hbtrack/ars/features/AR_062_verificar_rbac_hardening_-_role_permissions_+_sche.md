# AR_062 — Verificar RBAC hardening — ROLE_PERMISSIONS + schema constraints

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Verificar estrutura de RBAC: (1) permissions_map.py tem ROLE_PERMISSIONS com roles obrigatórias: superadmin, treinador, atleta; (2) permissions.py tem função _forbidden ou HTTPException 403; (3) schema.sql tem UNIQUE constraints ux_roles_code e ux_permissions_code; (4) model role.py existe em app/models/; (5) schemas/rbac.py existe. O mapa canônico de permissões (ROLE_PERMISSIONS) é fonte única da verdade para autorização — sua integridade estrutural é crítica para segurança.

## Critérios de Aceite
- permissions_map.py existe e tem ROLE_PERMISSIONS dict
- 'superadmin' presente em ROLE_PERMISSIONS
- 'treinador' presente em ROLE_PERMISSIONS
- 'atleta' presente em ROLE_PERMISSIONS
- permissions.py tem HTTP_403_FORBIDDEN ou 'FORBIDDEN'
- schema.sql tem ux_roles_code UNIQUE
- schema.sql tem ux_permissions_code UNIQUE
- app/models/role.py existe
- app/schemas/rbac.py existe
- hb report gera evidence exit 0

## Write Scope
- Hb Track - Backend/app/core/permissions_map.py
- Hb Track - Backend/app/core/permissions.py
- Hb Track - Backend/docs/ssot/schema.sql

## Validation Command (Contrato)
```
python -c "import pathlib,re; pm=pathlib.Path('Hb Track - Backend/app/core/permissions_map.py').read_text(encoding='utf-8'); assert 'ROLE_PERMISSIONS' in pm,'FAIL: ROLE_PERMISSIONS ausente em permissions_map.py'; roles_needed=['superadmin','treinador','atleta']; missing_roles=[r for r in roles_needed if r not in pm]; assert not missing_roles,f'FAIL: roles ausentes em ROLE_PERMISSIONS: {missing_roles}'; perm=pathlib.Path('Hb Track - Backend/app/core/permissions.py').read_text(encoding='utf-8'); assert 'FORBIDDEN' in perm or '403' in perm,'FAIL: guard FORBIDDEN ausente em permissions.py'; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); assert 'ux_roles_code' in s,'FAIL: UNIQUE ux_roles_code ausente no schema'; assert 'ux_permissions_code' in s,'FAIL: UNIQUE ux_permissions_code ausente no schema'; assert pathlib.Path('Hb Track - Backend/app/models/role.py').exists(),'FAIL: app/models/role.py ausente'; assert pathlib.Path('Hb Track - Backend/app/schemas/rbac.py').exists(),'FAIL: app/schemas/rbac.py ausente'; print('PASS AR_062: RBAC hardening verificado — ROLE_PERMISSIONS OK, guards OK, schema constraints OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_062/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Verificação estática completa. Se 'treinador' ou 'atleta' estiverem nomeados diferente no ROLE_PERMISSIONS (ex: 'coach', 'player'), Executor deve identificar o nome real e reportar para Arquiteto ajustar o plano antes de reaplicar.

## Análise de Impacto
- Verificação estática da estrutura de RBAC
- Sem modificações de código; risco operacional zero
- Confirma ROLE_PERMISSIONS com roles obrigatórias (superadmin, treinador, atleta)
- Valida guards de permissão (HTTP_403_FORBIDDEN) em permissions.py
- Confirma UNIQUE constraints em schema.sql (ux_roles_code, ux_permissions_code)
- Valida modelos e schemas RBAC existentes (role.py, rbac.py)
- Rollback: N/A (apenas verificação, sem alterações)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re; pm=pathlib.Path('Hb Track - Backend/app/core/permissions_map.py').read_text(encoding='utf-8'); assert 'ROLE_PERMISSIONS' in pm,'FAIL: ROLE_PERMISSIONS ausente em permissions_map.py'; roles_needed=['superadmin','treinador','atleta']; missing_roles=[r for r in roles_needed if r not in pm]; assert not missing_roles,f'FAIL: roles ausentes em ROLE_PERMISSIONS: {missing_roles}'; perm=pathlib.Path('Hb Track - Backend/app/core/permissions.py').read_text(encoding='utf-8'); assert 'FORBIDDEN' in perm or '403' in perm,'FAIL: guard FORBIDDEN ausente em permissions.py'; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); assert 'ux_roles_code' in s,'FAIL: UNIQUE ux_roles_code ausente no schema'; assert 'ux_permissions_code' in s,'FAIL: UNIQUE ux_permissions_code ausente no schema'; assert pathlib.Path('Hb Track - Backend/app/models/role.py').exists(),'FAIL: app/models/role.py ausente'; assert pathlib.Path('Hb Track - Backend/app/schemas/rbac.py').exists(),'FAIL: app/schemas/rbac.py ausente'; print('PASS AR_062: RBAC hardening verificado — ROLE_PERMISSIONS OK, guards OK, schema constraints OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:28:10.240149+00:00
**Behavior Hash**: d3e8f239933e6a0f164ba34ace5f9a50a98c97121728b0e533adf9bbd3df9ccf
**Evidence File**: `docs/hbtrack/evidence/AR_062/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c5f1ba8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_062_c5f1ba8/result.json`

### Selo Humano em c5f1ba8
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T22:54:54.819313+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_062_c5f1ba8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_062/executor_main.log`
