# AR_043 — hb_cli.py: scan recursivo (rglob) + subdir routing + hb rebuild-index

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
Atualizar scripts/run/hb_cli.py com 6 mudanças mínimas:

1. rebuild_ar_index(): mudar de ar_dir.iterdir() (filtra AR_\d) para ar_dir.rglob('AR_*.md') (excluindo _INDEX.md)

2. check_ar_collision() (~linha 282): ar_dir.glob(f'AR_{task_id}_*.md') → ar_dir.rglob(f'AR_{task_id}_*.md')

3. cmd_report() (~linha 717): ar_dir.glob(f'AR_{ar_id}_*.md') → ar_dir.rglob(f'AR_{ar_id}_*.md')

4. cmd_verify() (~linha 813): ar_dir.glob(f'AR_{ar_id}_*.md') → ar_dir.rglob(f'AR_{ar_id}_*.md')

5. Adicionar função auxiliar _get_ar_subdir(plan_basename: str) -> str:
   if plan_basename.startswith(('comp_db_','competition')): return 'competitions'
   if plan_basename.startswith(('gov_','AR_GOV')): return 'governance'
   if plan_basename.startswith('infra_'): return 'infra'
   return 'features'

6. Em cmd_plan(), onde ar_path = ar_dir / ar_filename, substituir por:
   subdir = _get_ar_subdir(plan_file.name)
   target_dir = ar_dir / subdir
   target_dir.mkdir(parents=True, exist_ok=True)
   ar_path = target_dir / ar_filename
   (também ajustar rollback_created_ars para usar rglob)
   (também ajustar materialize_ar_atomic para usar ar_path.parent / '.tmp' em vez de ar_dir / '.tmp')

7. Adicionar ao main() dispatch: 'rebuild-index' → rebuild_ar_index(get_repo_root())
   Adicionar 'rebuild-index' ao help string.

NAO alterar lógica de validação, gates, contracts ou outros comandos.

## Critérios de Aceite
1) python scripts/run/hb_cli.py rebuild-index executa sem erro (exit_code=0). 2) hb_cli.py contém 'rglob' em pelo menos 4 locais. 3) hb_cli.py contém '_get_ar_subdir'. 4) hb_cli.py contém 'rebuild-index'. 5) python scripts/run/hb_cli.py plan docs/_canon/planos/gov_011_ar_folder_reorg.json --dry-run retorna exit_code=0 e mostra subdir 'governance' no output.

## Validation Command (Contrato)
```
python -c "import pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); checks=['rglob','_get_ar_subdir','rebuild-index','competitions','governance','infra']; missing=[c for c in checks if c not in src]; assert not missing,f'FAIL: missing in hb_cli.py: {missing}'; count_rglob=src.count('rglob'); assert count_rglob>=4,f'FAIL: rglob count={count_rglob}, expected >=4'; print(f'PASS: hb_cli.py suporta subdirectórios (rglob x{count_rglob})')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_043_gov_ar_folder_reorg_hb_cli.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit com as mudanças em hb_cli.py
# OU, antes de commit:
git restore scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Se materialize_ar_atomic() criar .tmp/ em ar_dir/ (ao invés de ar_path.parent/), os locks de concorrência podem falhar para ARs em subdirs. Garantir que tempdir usa ar_path.parent.
- rollback_created_ars() varrendo apenas ar_dir/ (não recursivo) pode não encontrar ARs criadas em subdirs. Deve usar rglob ou iterar o created_ars list diretamente.
- O sort_key de rebuild_ar_index() deve continuar funcionando com paths absolutos retornados por rglob (usar f.name em vez de f para o regex).
- Testar com --dry-run antes de executar Tasks 044/045: python scripts/run/hb_cli.py plan docs/_canon/planos/gov_011_ar_folder_reorg.json --dry-run

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-02-22
**Status**: 🏗️ EM_EXECUÇÃO

### Estado Atual
- scripts/run/hb_cli.py usa glob() e iterdir() para descobrir ARs
- ARs estão sendo materializadas em subdirs (governance/, competitions/, features/)
- Funções de busca precisam ser atualizadas para suportar subdirs com rglob()

### Ações Necessárias
1. Identificar e atualizar 5 funções que usam glob/iterdir
2. Adicionar função auxiliar _get_ar_subdir() para determinar subdir alvo
3. Atualizar cmd_plan() para usar subdir routing
4. Adicionar comando 'rebuild-index' ao CLI
5. Validar com validation_command exato

### Impacto
- **Escopo**: scripts/run/hb_cli.py (modificação em ~10 linhas)
- **SSOT**: Nenhum toque em SSOT (schema.sql, openapi.json, alembic_state.txt)
- **Rollback**: git restore scripts/run/hb_cli.py
- **Risco**: Bajo (mudança mecânica, sem lógica de negócio alterada)

### Conclusão
Mudança estrutural necessária para suportar subdirs em ARs. Sem SSOT touches, sem rollback complexo.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); checks=['rglob','_get_ar_subdir','rebuild-index','competitions','governance','infra']; missing=[c for c in checks if c not in src]; assert not missing,f'FAIL: missing in hb_cli.py: {missing}'; count_rglob=src.count('rglob'); assert count_rglob>=4,f'FAIL: rglob count={count_rglob}, expected >=4'; print(f'PASS: hb_cli.py suporta subdirectórios (rglob x{count_rglob})')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_043_gov_ar_folder_reorg_hb_cli.log`
**Python Version**: 3.11.9

