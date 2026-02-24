# AR_116 — Corrigir contrato AR_038 — banco renumerado de 0057 para 0060

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_038 (competitions). O arquivo de atualizacao de banco comp_db_004 foi renumerado de 0057 para 0060. Tres valores devem mudar no validation_command: (A) nome do arquivo: 0057_comp_db_004_standings_unique_nulls_not_distinct para 0060_comp_db_004_standings_unique_nulls_not_distinct; (B) valor de revisao interno: de '0057' para '0060'; (C) valor de revisao base: de '0056' para '0059'. Todas as verificacoes de nomes de constraint (uq_competition_standings_comp_phase_opponent, uk_competition_standings_team_phase) e o check de NULLS NOT DISTINCT PERMANECEM identicos. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_038 referencia '0060_comp_db_004_standings_unique_nulls_not_distinct' (nao 0057)
- Secao Validation Command de AR_038 verifica revision 0060 e down_revision 0059
- Checks de constraint names permanecem intactos (uq_competition_standings_comp_phase_opponent etc)
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_038 permanece SUCESSO

## Validation Command (Contrato)
```
python -c "import pathlib; ar=list(pathlib.Path('docs/hbtrack/ars/competitions').glob('AR_038*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert '0057_comp_db_004' not in content,'FAIL: old 0057 path ainda no AR_038'; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0060_comp_db_004_standings_unique_nulls_not_distinct.py'); assert f.exists(),'FAIL: arquivo de banco 0060 nao existe'; c=f.read_text(encoding='utf-8'); assert 'uq_competition_standings_comp_phase_opponent' in c; assert \"revision = '0060'\" in c; print('PASS AR_116: AR_038 validation_command corrigido para banco 0060')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_116/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/competitions/AR_038_migration_0057_drop_uk_competition_standings_team_.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: arquivo comp_db_004 foi renumerado de 0057 para 0060 para evitar conflito com outro arquivo adicionado posteriormente. Fato entregue correto (constraint existe). Apenas o contrato de verificacao apontava para numero obsoleto. AR file path usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

