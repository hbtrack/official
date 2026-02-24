# AR_061 — Aplicar migrations 0056-0061 e regenerar alembic_state.txt SSOT

**Status**: 🔲 PENDENTE
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
python -c "import pathlib; p=pathlib.Path('Hb Track - Backend/docs/ssot/alembic_state.txt'); assert p.exists(),'FAIL: alembic_state.txt nao encontrado'; c=p.read_text(encoding='utf-8'); assert '0061' in c,f'FAIL: alembic_state.txt nao menciona 0061 (head atual esperado). Conteudo atual:
{c}'; assert '0059 (head)' not in c,'FAIL: alembic_state.txt ainda mostra 0059 como head (stale)'; print(f'PASS AR_061: alembic_state.txt atualizado, 0061 presente. Conteudo: {c.strip()[:200]}')"
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

