# AR_011 — hb_cli.py: rebuild_ar_index() — auto-rebuild _INDEX.md em hb plan e hb report

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: docs/hbtrack/ars/_INDEX.md está desatualizado (lista apenas AR_001–AR_005 com títulos errados, com entradas duplicadas) e é editado manualmente — qualquer um pode alterar sem rastro.

FIX: Adicionar função rebuild_ar_index(repo_root) em scripts/run/hb_cli.py que:
(1) Scanneia todos os arquivos AR_*.md em docs/hbtrack/ars/
(2) Para cada AR, extrai via regex: ID (AR_NNN), título (linha # AR_NNN — ...), status (campo **Status**: ...)
(3) Extrai o evidence file path (campo Evidence File (Contrato))
(4) Gera docs/hbtrack/ars/_INDEX.md com tabela markdown:

```
# Índice de Architectural Records (ARs)
> ⚠️ Auto-gerado por `hb plan`/`hb report`. NÃO editar manualmente.
> Última atualização: <DATA_ISO>

| ID | Título | Status | Evidence |
|---|---|---|---|
| AR_001 | <título> | <status> | <evidence ou —> |
...
```

(5) Ordenar por ID numérico (001, 002, ..., 011, ...).
(6) Chamar rebuild_ar_index(repo_root) no FINAL de cmd_plan (após materializar ARs) e no FINAL de cmd_report (após atualizar Status e gravar carimbo).

ARQUIVO A MODIFICAR (ÚNICO): scripts/run/hb_cli.py
- Adicionar função rebuild_ar_index() antes de cmd_plan.
- Adicionar chamada rebuild_ar_index(repo_root) no final de cmd_plan (antes de sys.exit(0)).
- Adicionar chamada rebuild_ar_index(repo_root) no final de cmd_report (antes de sys.exit).

NAO modificar nenhum outro arquivo além de scripts/run/hb_cli.py.

## Critérios de Aceite
1) docs/hbtrack/ars/_INDEX.md existe após execução de hb plan ou hb report. 2) _INDEX.md contém uma linha para cada AR_*.md presente em docs/hbtrack/ars/ (excluindo o próprio _INDEX.md). 3) _INDEX.md contém o aviso 'NÃO editar manualmente'. 4) _INDEX.md está ordenado por ID numérico. 5) O campo Status de cada AR é refletido corretamente no index. 6) a função rebuild_ar_index existe em hb_cli.py e é chamada em cmd_plan e cmd_report.

## Validation Command (Contrato)
```
python -c "import re, pathlib; idx=pathlib.Path('docs/hbtrack/ars/_INDEX.md').read_text(encoding='utf-8'); assert 'NAO editar manualmente' in idx or 'NÃO editar manualmente' in idx, 'FAIL: aviso ausente'; ars=sorted([f for f in pathlib.Path('docs/hbtrack/ars').iterdir() if re.match(r'AR_[0-9]+', f.name) and f.suffix=='.md']); ids=[re.search(r'AR_([0-9]+)', a.name).group(1) for a in ars]; missing=[i for i in ids if f'AR_{i}' not in idx]; assert not missing, f'FAIL: ARs ausentes do index: {missing}'; print(f'PASS: _INDEX.md contém todas as {len(ids)} ARs e aviso de proteção')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_011_gov_ar_index_rebuild.log`

## Riscos
- O _INDEX.md atual tem conteúdo manual histórico — será sobrescrito completamente. Isso é intencional.
- Se uma AR_*.md tiver formato inválido (sem linha **Status**), rebuild_ar_index deve usar 'DESCONHECIDO' como status e não falhar.
- A chamada em cmd_report deve ocorrer APÓS a atualização do **Status** header (AR_010), para que o index reflita o status correto.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import re, pathlib; idx=pathlib.Path('docs/hbtrack/ars/_INDEX.md').read_text(encoding='utf-8'); assert 'NAO editar manualmente' in idx or 'NÃO editar manualmente' in idx, 'FAIL: aviso ausente'; ars=sorted([f for f in pathlib.Path('docs/hbtrack/ars').iterdir() if re.match(r'AR_[0-9]+', f.name) and f.suffix=='.md']); ids=[re.search(r'AR_([0-9]+)', a.name).group(1) for a in ars]; missing=[i for i in ids if f'AR_{i}' not in idx]; assert not missing, f'FAIL: ARs ausentes do index: {missing}'; print(f'PASS: _INDEX.md contém todas as {len(ids)} ARs e aviso de proteção')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_011_gov_ar_index_rebuild.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_011_b2e7523/result.json`
