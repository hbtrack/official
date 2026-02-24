# AR_061 — Aplicar migrations 0056-0061 e regenerar alembic_state.txt SSOT

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
O alembic_state.txt está defasado: SSOT diz head=0059 mas o disco tem até 0061. Migrations pendentes:
- 0056_comp_db_003_scoring_rules_competitions.py
- 0057_add_match_goalkeeper_stints.py
- 0058_attendance_add_justified_status.py
- 0059_add_match_analytics_cache.py
- 0060_comp_db_004_standings_unique_nulls_not_distinct.py
- 0061_comp_db_006_status_check_constraints.py

Passos do Executor:
1. Ativar venv: .venv\Scripts\Activate.ps1
2. cd 'Hb Track - Backend'
3. alembic upgrade head (aplica todas as pendentes até 0061)
4. cd ..
5. python scripts/ssot/gen_docs_ssot.py --alembic

Isto atualiza Hb Track - Backend/docs/ssot/alembic_state.txt com head=0061.

## Critérios de Aceite
- Hb Track - Backend/docs/ssot/alembic_state.txt contém '0061' como head
- Arquivo não mostra mais '0059 (head)'
- alembic_state.txt tem linha com '0061 (head)' ou '0061'
- hb report gera evidence exit 0

## Write Scope
- Hb Track - Backend/docs/ssot/alembic_state.txt
- Hb Track - Backend/docs/ssot/manifest.json

## SSOT Touches
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python -c "import pathlib; p=pathlib.Path('Hb Track - Backend/docs/ssot/alembic_state.txt'); assert p.exists(),'FAIL: alembic_state.txt nao encontrado'; c=p.read_text(encoding='utf-8'); assert '0061' in c,f'FAIL: alembic_state.txt nao menciona 0061 (head atual esperado). Conteudo atual: {c}'; assert '0059 (head)' not in c,'FAIL: alembic_state.txt ainda mostra 0059 como head (stale)'; print(f'PASS AR_061: alembic_state.txt atualizado, 0061 presente. Conteudo: {c.strip()[:200]}')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_061/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
git checkout -- "Hb Track - Backend/docs/ssot/manifest.json"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Executor deve rodar alembic upgrade head ANTES de regenerar o SSOT. Se upgrade falhar por constraint/data error, reportar bloqueio ao Arquiteto com saída do alembic. NÃO forçar migration — não usar --sql ou bypass.

## Riscos
- alembic upgrade pode falhar se DB não estiver disponível — verificar DATABASE_URL antes
- Migration 0060 altera standings UNIQUE NULLS NOT DISTINCT — requer PostgreSQL >= 15
- Migration 0058 adiciona status 'justified' em attendance — verificar enum existente

## Análise de Impacto
- **CRÍTICO**: Aplica 6 migrations pendentes no banco de dados (0056-0061)
- Migrations incluem: scoring rules, match_goalkeeper_stints, attendance justified status, analytics cache, standings UNIQUE NULLS NOT DISTINCT, status CHECK constraints
- Modifica schema do BD: novas tabelas, colunas, constraints, enums
- Requer PostgreSQL >= 15 (migration 0060 usa NULLS NOT DISTINCT)
- Regenera SSOT: alembic_state.txt (head 0059 → 0061) e manifest.json
- **Rollback**: `git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt" "Hb Track - Backend/docs/ssot/manifest.json"` + rollback BD com alembic downgrade se necessário
- **Pré-requisito**: DATABASE_URL configurado, DB disponível, PostgreSQL >= 15
- **Risco Alto**: Falha de migration pode deixar BD em estado inconsistente
- Se alembic upgrade falhar, **NÃO FORÇAR** — reportar erro ao Arquiteto

---
## Carimbo de Execução
_(Gerado por hb report)_
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T22:34:17.090195+00:00
**Behavior Hash**: f3e90d8198d26cc476bfad4b1387ec4f48b9f2f0525730af1564e74b0fada318
**Evidence File**: `docs/hbtrack/evidence/AR_061/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em c5f1ba8
**Status Executor**: ❌ FALHA
**Comando**: `python -c "import pathlib; p=pathlib.Path('Hb Track - Backend/docs/ssot/alembic_state.txt'); assert p.exists(),'FAIL: alembic_state.txt nao encontrado'; c=p.read_text(encoding='utf-8'); assert '0061' in c,f'FAIL: alembic_state.txt nao menciona 0061 (head atual esperado). Conteudo atual:
{c}'; assert '0059 (head)' not in c,'FAIL: alembic_state.txt ainda mostra 0059 como head (stale)'; print(f'PASS AR_061: alembic_state.txt atualizado, 0061 presente. Conteudo: {c.strip()[:200]}')"`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T22:34:32.250955+00:00
**Behavior Hash**: f3e90d8198d26cc476bfad4b1387ec4f48b9f2f0525730af1564e74b0fada318
**Evidence File**: `docs/hbtrack/evidence/AR_061/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; p=pathlib.Path('Hb Track - Backend/docs/ssot/alembic_state.txt'); assert p.exists(),'FAIL: alembic_state.txt nao encontrado'; c=p.read_text(encoding='utf-8'); assert '0061' in c,f'FAIL: alembic_state.txt nao menciona 0061 (head atual esperado). Conteudo atual: {c}'; assert '0059 (head)' not in c,'FAIL: alembic_state.txt ainda mostra 0059 como head (stale)'; print(f'PASS AR_061: alembic_state.txt atualizado, 0061 presente. Conteudo: {c.strip()[:200]}')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:41:34.281663+00:00
**Behavior Hash**: 319795879cc49c87f9e62b82f28b3dbbc2feb7742b9ce1621d9b0fbd96c105fb
**Evidence File**: `docs/hbtrack/evidence/AR_061/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c5f1ba8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_061_c5f1ba8/result.json`

### Selo Humano em c5f1ba8
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T22:54:44.085284+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_061_c5f1ba8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_061/executor_main.log`
