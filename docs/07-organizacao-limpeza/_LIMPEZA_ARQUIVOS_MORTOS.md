<!-- STATUS: NEEDS_REVIEW -->

# Arquivos Mortos - HB Track

Lista de arquivos obsoletos identificados para limpeza:

## ✅ REMOVIDOS

### Arquivos .bak (backups manuais)
- `c:\HB TRACK\Hb Track - Fronted\tests\e2e\setup\simple-auth.setup.ts.bak`
- `c:\HB TRACK\Hb Track - Backend\tests\api\test_openapi_OBSOLETE.py.bak`

### Arquivos E2E obsoletos (Docker)
- `c:\HB TRACK\Hb Track - Backend\_archived_e2e\reset-db-e2e.ps1`
- `c:\HB TRACK\Hb Track - Backend\_archived_e2e\start_e2e_backend.ps1`

### Seeds obsoletos (dados agora nas migrations)
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\001_seed_roles.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\002_seed_superadmin.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\005_seed_positions.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\006_seed_permissions.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\007_seed_role_permissions.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\008_seed_schooling_levels.py`
- `c:\HB TRACK\Hb Track - Backend\db\seeds\_archived\run_all_seeds.py`

## ⚠️ MANTIDOS (por enquanto)

### Backups de Schema
- `c:\HB TRACK\Hb Track - Backend\db\alembic\schema_backup.sql` - Backup do schema (manter por segurança)

### Dados críticos
- `c:\HB TRACK\backup-dados-criticos\*` - Dados de produção (NUNCA remover)

## 📝 Ações Executadas

1. ✅ Seeds obsoletos movidos para `_archived/`
2. ✅ Scripts E2E obsoletos já em pasta `_archived_e2e/` 
3. ✅ Novos seeds criados focados em dados de teste
4. ✅ Scripts de reset atualizados para nova arquitetura