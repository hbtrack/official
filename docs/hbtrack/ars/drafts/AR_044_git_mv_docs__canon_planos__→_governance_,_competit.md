# AR_044 — git mv: docs/_canon/planos/ → governance/, competitions/, infra/, features/

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
DEPENDÊNCIA: Task 043 deve estar concluída antes desta.

Criar subdirs e mover 28 JSON files:

# 1. Criar subdirs
mkdir -p docs/_canon/planos/governance docs/_canon/planos/competitions docs/_canon/planos/infra docs/_canon/planos/features

# 2. governance/ (11 files)
git mv 'docs/_canon/planos/AR_GOV_001_plans_path_migration.json' docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_002_ar_status_header_sync.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_003_ar_governance_index_immutability.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_004_testador_protocol_v108.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_005_dual_executor_protocol.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_006_determinismo_triple_run_v110.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_007_enterprise_3agent_flow_v110.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_008_hardening_enterprise_batch004_v110.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_009_hb_cli_spec_v110_sync.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_010_ar_index_validation_checkpoint.json docs/_canon/planos/governance/
git mv docs/_canon/planos/gov_034_plans_ar_sync_gate.json docs/_canon/planos/governance/

# 3. competitions/ (8 files)
git mv docs/_canon/planos/comp_db_001_soft_delete.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_001_soft_delete_competition_tables.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_003_scoring_rules.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_004_unique_index.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_006a_migration.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_006b_competition_model.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/comp_db_006c_match_model.json docs/_canon/planos/competitions/
git mv docs/_canon/planos/competition_standings_add_team_id.json docs/_canon/planos/competitions/

# 4. infra/ (3 files)
git mv docs/_canon/planos/infra_001_rename_frontend_dir.json docs/_canon/planos/infra/
git mv docs/_canon/planos/infra_002_env_ssot.json docs/_canon/planos/infra/
git mv docs/_canon/planos/infra_003_hb_watch.json docs/_canon/planos/infra/

# 5. features/ (6 files)
git mv docs/_canon/planos/ar_002_5_schema_conformidade_prd.json docs/_canon/planos/features/
git mv 'docs/_canon/planos/AR_003.5_persons_birth_date_not_null.json' docs/_canon/planos/features/
git mv docs/_canon/planos/ar_contract.json docs/_canon/planos/features/
git mv docs/_canon/planos/matchservice.json docs/_canon/planos/features/
git mv docs/_canon/planos/prd_001_prd_v22_sync_estado_real.json docs/_canon/planos/features/
git mv docs/_canon/planos/scout_plan.json docs/_canon/planos/features/

# 6. Mover gov_011_ar_folder_reorg.json (este plano) para governance/
git mv docs/_canon/planos/gov_011_ar_folder_reorg.json docs/_canon/planos/governance/

Nota: top-level docs/_canon/planos/ fica sem nenhum .json após as moves.

## Critérios de Aceite
1) 4 subdirs criados: governance/, competitions/, infra/, features/. 2) Nenhum .json no top-level de docs/_canon/planos/ (exceto se houver novo plano ainda não classificado). 3) governance=11 files, competitions=8 files, infra=3 files, features=6 files (+ gov_011 = 12 em governance). 4) python scripts/run/hb_cli.py plan docs/_canon/planos/governance/gov_011_ar_folder_reorg.json --dry-run retorna exit_code=0.

## Validation Command (Contrato)
```
python -c "import pathlib; base=pathlib.Path('docs/_canon/planos'); subdirs=['governance','competitions','infra','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; counts={d:len(list((base/d).glob('*.json'))) for d in subdirs}; assert counts['governance']>=11,'FAIL: governance<11'; assert counts['competitions']>=8,'FAIL: competitions<8'; assert counts['infra']>=3,'FAIL: infra<3'; assert counts['features']>=4,'FAIL: features<4'; print(f'PASS: planos organized {counts}')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_044/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit com os git mv dos planos
# OU, antes de commit:
git mv docs/_canon/planos/governance/*.json docs/_canon/planos/ && git mv docs/_canon/planos/competitions/*.json docs/_canon/planos/ && git mv docs/_canon/planos/infra/*.json docs/_canon/planos/ && git mv docs/_canon/planos/features/*.json docs/_canon/planos/
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Arquivos com caracteres especiais (AR_003.5, AR_GOV) requerem aspas no git mv. Usar aspas simples ou escaping correto.
- Se Task 043 não foi aplicada primeiro, hb plan falhará ao tentar usar novos planos de subdirs (path OK, mas _get_ar_subdir não existe). Executar Tasks em ordem.
- gov_011_ar_folder_reorg.json (este arquivo) também deve ser movido para governance/ como último passo, pois é um plano gov_.
- Após move, o path canonical do plano muda para docs/_canon/planos/governance/gov_011_ar_folder_reorg.json. Atualizar referências em notas/documentação.

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-02-22
**Status**: 🏗️ EM_EXECUÇÃO

### Estado Atual
- docs/_canon/planos/ contém 28 arquivos JSON em top-level
- Subdirs já existem (governance/, competitions/, infra/, features/)
- AR_043 já foi completada (hb_cli.py preparado)

### Ações Necessárias
1. Verificar se subdirs existem; criar se não
2. Executar 28 comandos git mv para reorganizar arquivos
3. Validar contagem com validation_command
4. Confirmar pelo hb report

### Impacto
- **Escopo**: docs/_canon/planos/ (28 movimentos de arquivo via git)
- **SSOT**: Nenhum toque em SSOT (schema.sql, openapi.json, alembic_state.txt)
- **Rollback**: git mv ... em reversa (fácil, todos os arquivos já existem)
- **Risco**: Bajo (movimentos estruturais, sem código alterado)

### Conclusão
Reorganização pura de estrutura. Sem SSOT touches, sem lógica complexa.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/_canon/planos'); subdirs=['governance','competitions','infra','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.json')]; assert not orphans,f'FAIL: JSONs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.json'))) for d in subdirs}; assert counts['governance']>=11,'FAIL: governance<11'; assert counts['competitions']==8,'FAIL: competitions!=8'; assert counts['infra']==3,'FAIL: infra!=3'; assert counts['features']==6,'FAIL: features!=6'; print(f'PASS: planos organized {counts}')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_044_gov_ar_folder_reorg_planos.log`
**Python Version**: 3.11.9

### Execução Executor em acf34a8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/_canon/planos'); subdirs=['governance','competitions','infra','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; counts={d:len(list((base/d).glob('*.json'))) for d in subdirs}; assert counts['governance']>=11,'FAIL: governance<11'; assert counts['competitions']>=8,'FAIL: competitions<8'; assert counts['infra']>=3,'FAIL: infra<3'; assert counts['features']>=4,'FAIL: features<4'; print(f'PASS: planos organized {counts}')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T20:02:18.591296+00:00
**Behavior Hash**: 4bcc44dbc6f56a8fe8937ef22b9744973ecacd2cd09f1e8e8f728c6bd4e5cd1d
**Evidence File**: `docs/hbtrack/evidence/AR_044/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em acf34a8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_044_acf34a8/result.json`
