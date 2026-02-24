# AR_117 — Corrigir contrato AR_040 — banco renumerado de 0058 para 0061

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_040 (competitions). O arquivo de atualizacao de banco comp_db_006 foi renumerado de 0058 para 0061. Tres valores devem mudar no validation_command: (A) nome do arquivo: 0058_comp_db_006_status_check_constraints para 0061_comp_db_006_status_check_constraints; (B) valor de revisao interno: de '0058' para '0061'; (C) valor de revisao base: de '0057' para '0060'. Os checks de nomes de constraints (ck_competitions_status, ck_competitions_modality, ck_competition_matches_status) e o check de create_check_constraint PERMANECEM identicos. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_040 referencia '0061_comp_db_006_status_check_constraints' (nao 0058)
- Secao Validation Command de AR_040 verifica revision 0061 e down_revision 0060
- Checks de constraint names permanecem (ck_competitions_status, ck_competitions_modality, ck_competition_matches_status)
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_040 permanece SUCESSO

## Validation Command (Contrato)
```
python -c "import pathlib; ar=list(pathlib.Path('docs/hbtrack/ars/competitions').glob('AR_040*.md'))[0]; content=ar.read_text(encoding='utf-8'); assert '0058_comp_db_006' not in content,'FAIL: old 0058 path ainda no AR_040'; f=pathlib.Path('Hb Track - Backend/db/alembic/versions/0061_comp_db_006_status_check_constraints.py'); assert f.exists(),'FAIL: arquivo de banco 0061 nao existe'; c=f.read_text(encoding='utf-8'); assert 'ck_competitions_status' in c; assert \"revision = '0061'\" in c; print('PASS AR_117: AR_040 validation_command corrigido para banco 0061')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_117/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/competitions/AR_040_migration_0058_comp-db-006_add_3_check_constraints.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: arquivo comp_db_006 foi renumerado de 0058 para 0061 para evitar conflito com outro arquivo adicionado posteriormente. Fato entregue correto (3 CHECK constraints existem). AR file path usa write_scope [].

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

