# AR_052 — AR_008 re-validação: Evidence Pack 3-camadas para migration 0055 no DB local

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
CONTEXTO: AR_008 tem status ✅ CONCLUIDO no arquivo mas o Evidence Pack registra falhas:
  - Exit Code 1: test_rdb1_postgresql_version falha (local usa PG12, teste exige PG15+)
  - Exit Code 3: alembic upgrade head falha com TCP timeout para VPS 191.252.185.34

AMBOS os erros são de INFRA, não de código. A migration 0055 está correta.

PROBLEMA REAL: O validation_command de AR_008 usa pytest full suite que inclui
teste de conformidade de versão do PostgreSQL (irrelevante para validar migration DDL).

AÇÃO DO EXECUTOR:

1) PROVA ESTRUTURAL — verificar arquivo de migration:
   python -c "import pathlib; p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py')); assert p, 'FAIL: 0055 file not found'; content=p[0].read_text(); assert \"revision = '0055'\" in content, 'FAIL: revision mismatch'; print(f'PASS: {p[0].name} with revision=0055')"

2) PROVA COMPORTAMENTAL — verificar colunas no DB LOCAL (porta 5433):
   Conectar ao DB local e verificar que as colunas deleted_at/deleted_reason existem nas 5 tabelas.
   Usar scripts/checks/db/check_migration.py ou psycopg2 direto.

3) PROVA OPERACIONAL — verificar triggers:
   SELECT trigger_name FROM information_schema.triggers WHERE trigger_name LIKE '%block_delete%'
   Deve retornar 5 linhas.

4) Executar hb report 052 com o validation_command desta task para gravar novo Evidence Pack.

NAO reexecutar pytest full suite (que falha no PG version test). O novo Evidence Pack
deve documentar EXPLICITAMENTE que a falha do Evidence Pack original foi de INFRA,
e que a migration 0055 está aplicada e operacional no DB local.

Atenção: DB local usa porta 5433 (não 5432). URL canônica:
postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev

## Critérios de Aceite
1) Migration 0055 arquivo existe com revision='0055' e down_revision='0054'. 2) Tabela match_events no DB local tem colunas deleted_at e deleted_reason. 3) Tabela competition_matches no DB local tem colunas deleted_at e deleted_reason. 4) information_schema.triggers contém pelo menos 5 triggers com nome '%block_delete%'. 5) Evidence Pack documenta claramente que falha anterior foi de INFRA (PG version test + VPS unreachable).

## Validation Command (Contrato)
```
python -c "import pathlib, psycopg2; p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py')); assert p, 'FAIL: 0055 not found'; c=p[0].read_text(encoding='utf-8'); assert 'revision' in c and '\"0055\"' in c, 'FAIL: revision 0055 not found'; assert 'down_revision' in c and '\"0054\"' in c, 'FAIL: down_revision 0054 not found'; conn=psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev'); cur=conn.cursor(); cur.execute(\"SELECT count(*) FROM information_schema.columns WHERE table_name IN ('match_events','competition_matches','competition_opponent_teams','competition_phases','match_roster') AND column_name='deleted_at'\"); cols=cur.fetchone()[0]; assert cols==5, f'FAIL: expected 5 cols, got {cols}'; cur.execute(\"SELECT count(*) FROM information_schema.triggers WHERE trigger_name LIKE '%%block_delete%%'\"); trigs=cur.fetchone()[0]; assert trigs>=24, f'FAIL: expected >=24 triggers, got {trigs}'; cur.execute(\"SELECT version_num FROM alembic_version\"); head=cur.fetchone()[0]; conn.close(); print(f'PASS: 0055 verified on head {head} — {cols} cols, {trigs} triggers')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_052_ar008_revalidation_3layer.log`

## Rollback Plan (Contrato)
```
git revert <commit_hash>  # re-validação doc-only — nenhuma DDL foi executada nesta task. Se alembic upgrade head foi executado como prerequisito e precisa ser revertido: alembic downgrade -1 (reverte migration 0055).
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Este Evidence Pack SUBSTITUI a evidência anterior de AR_008 (que registrava falhas de INFRA). O objetivo é ter um registro limpo mostrando que migration 0055 está funcional no ambiente local canônico.

## Riscos
- DB local pode não estar rodando — verificar com 'docker ps' antes de executar. Container: hbtrack-postgres-dev, porta 5433.
- Se triggers não existem (migration não aplicada), executar 'cd Hb Track - Backend && alembic upgrade head' PRIMEIRO — isso pode falhar no test_rdb1 mas o upgrade head em si deve funcionar no DB local PG12.
- psycopg2 e psycopg3 coexistem — usar psycopg2 para compatibilidade (import psycopg2).

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: Re-validação 3 camadas de migration 0055 no DB local (Docker hbtrack-postgres-dev, porta 5433, postgres:12). Nenhuma DDL executada — apenas evidência coletada.

**Resultado**:
- PROOF 1 (Structural): arquivo 0055_*.py confirmado com revision chain correto.
- PROOF 2 (Behavioral): 5/5 tabelas têm `deleted_at` + `deleted_reason` no schema local.
- PROOF 3 (Operational): 24 block_delete triggers ativos (inclui os 5 de competition/scout).
- Falhas do Evidence Pack original (AR_008) eram de INFRA (PG version test + VPS unreachable), não de código.

**Impacto**: Evidence Pack limpo documenta que migration 0055 está operacional no ambiente local canônico.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib, psycopg2; p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py')); assert p, 'FAIL: 0055 not found'; c=p[0].read_text(encoding='utf-8'); assert 'revision' in c and '\"0055\"' in c, 'FAIL: revision 0055 not found'; assert 'down_revision' in c and '\"0054\"' in c, 'FAIL: down_revision 0054 not found'; conn=psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev'); cur=conn.cursor(); cur.execute(\"SELECT count(*) FROM information_schema.columns WHERE table_name IN ('match_events','competition_matches','competition_opponent_teams','competition_phases','match_roster') AND column_name='deleted_at'\"); cols=cur.fetchone()[0]; assert cols==5, f'FAIL: expected 5 cols, got {cols}'; cur.execute(\"SELECT count(*) FROM information_schema.triggers WHERE trigger_name LIKE '%%block_delete%%'\"); trigs=cur.fetchone()[0]; assert trigs>=24, f'FAIL: expected >=24 triggers, got {trigs}'; cur.execute(\"SELECT version_num FROM alembic_version\"); head=cur.fetchone()[0]; conn.close(); print(f'PASS: 0055 verified on head {head} — {cols} cols, {trigs} triggers')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_052_ar008_revalidation_3layer.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_052_b2e7523/result.json`

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib, psycopg2; p=list(pathlib.Path('Hb Track - Backend/db/alembic/versions').glob('0055_*.py')); assert p, 'FAIL: 0055 not found'; c=p[0].read_text(encoding='utf-8'); assert 'revision' in c and '\"0055\"' in c, 'FAIL: revision 0055 not found'; assert 'down_revision' in c and '\"0054\"' in c, 'FAIL: down_revision 0054 not found'; conn=psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev'); cur=conn.cursor(); cur.execute(\"SELECT count(*) FROM information_schema.columns WHERE table_name IN ('match_events','competition_matches','competition_opponent_teams','competition_phases','match_roster') AND column_name='deleted_at'\"); cols=cur.fetchone()[0]; assert cols==5, f'FAIL: expected 5 cols, got {cols}'; cur.execute(\"SELECT count(*) FROM information_schema.triggers WHERE trigger_name LIKE '%%block_delete%%'\"); trigs=cur.fetchone()[0]; assert trigs>=24, f'FAIL: expected >=24 triggers, got {trigs}'; cur.execute(\"SELECT version_num FROM alembic_version\"); head=cur.fetchone()[0]; conn.close(); print(f'PASS: 0055 verified on head {head} — {cols} cols, {trigs} triggers')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_052_ar008_revalidation_3layer.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_052_b2e7523/result.json`
