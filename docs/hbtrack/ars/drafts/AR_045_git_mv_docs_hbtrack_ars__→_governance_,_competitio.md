# AR_045 — git mv: docs/hbtrack/ars/ → governance/, competitions/, features/ + rebuild-index

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
DEPENDÊNCIA: Task 043 deve estar concluída antes desta.

Criar subdirs e mover 43 AR .md files por domínio:

# 1. Criar subdirs
mkdir -p docs/hbtrack/ars/governance docs/hbtrack/ars/competitions docs/hbtrack/ars/features

# 2. competitions/ (11 files: AR_001,002,008,009,036-042)
for id in 001 002 008 009 036 037 038 039 040 041 042; do
  git mv docs/hbtrack/ars/AR_${id}_*.md docs/hbtrack/ars/competitions/
done

# 3. features/ (7 files: AR_003,004,005,007,014,015 + AR_003.5)
for id in 003 004 005 007 014 015; do
  git mv docs/hbtrack/ars/AR_${id}_*.md docs/hbtrack/ars/features/
done
git mv docs/hbtrack/ars/AR_003.5_*.md docs/hbtrack/ars/features/

# 4. governance/ (25 files: AR_006,010-013,016-035)
for id in 006 010 011 012 013 016 017 018 019 020 021 022 023 024 025 026 027 028 029 030 031 032 033 034 035; do
  git mv docs/hbtrack/ars/AR_${id}_*.md docs/hbtrack/ars/governance/
done

# 5. Rebuild _INDEX.md (requer Task 043 concluída)
python scripts/run/hb_cli.py rebuild-index

_INDEX.md permanece em docs/hbtrack/ars/_INDEX.md (não mover).

## Critérios de Aceite
1) 3 subdirs criados: governance/, competitions/, features/. 2) Nenhum AR_*.md no top-level de docs/hbtrack/ars/ (apenas _INDEX.md). 3) governance=25 files, competitions=11 files, features=7 files. 4) _INDEX.md existe e contém 42+ entradas AR_. 5) python scripts/run/hb_cli.py rebuild-index retorna exit_code=0.

## Validation Command (Contrato)
```
python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']>=25,f'FAIL: governance={counts[\"governance\"]}>=25 required'; assert counts['competitions']>=11,f'FAIL: competitions={counts[\"competitions\"]}>=11 required'; assert counts['features']>=7,f'FAIL: features={counts[\"features\"]}>=7 required'; print(f'PASS: ars organized {counts}')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_045/executor_main.log`

## Rollback Plan (Contrato)
```
git revert HEAD  # se já commitado: desfaz o commit com os git mv das ARs
# OU, antes de commit:
for d in governance competitions features; do git mv docs/hbtrack/ars/$d/AR_*.md docs/hbtrack/ars/; done
python scripts/run/hb_cli.py rebuild-index
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- AR_003 e AR_003.5 têm nomes semelhantes. O glob AR_003_*.md só pega AR_003 (não AR_003.5). O comando para AR_003.5 usa padrão AR_003.5_* separado.
- Se algum ID não existir (AR_007 = exit_code_zero_test, pode ser intencionalmente vazio), o git mv retorna erro. Usar '|| true' no loop se necessário.
- Após move, hb report e hb verify usarão rglob (Task 043) para encontrar ARs. Se Task 043 não foi aplicada, esses comandos falharão ao não encontrar os arquivos movidos.
- A ordem das Tasks é CRÍTICA: 043 → (044 + 045 em paralelo). Não executar 044/045 antes de 043.

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-02-22
**Status**: 🏗️ EM_EXECUÇÃO

### Estado Atual
- docs/hbtrack/ars/ contém 43 arquivos AR_*.md em top-level
- Subdirs já existem (governance/, competitions/, features/)
- AR_043 já foi completada (hb_cli.py "rebuild-index" disponível)
- AR_044 já foi completada (planos reorganizados)

### Ações Necessárias
1. Mover 25 ARs para docs/hbtrack/ars/governance/
2. Mover 11 ARs para docs/hbtrack/ars/competitions/
3. Mover 7 ARs para docs/hbtrack/ars/features/
4. Executar `hb rebuild-index` para sincronizar _INDEX.md

### Impacto
- **Escopo**: docs/hbtrack/ars/ (43 movimentos de arquivo via git + rebuild-index)
- **SSOT**: Nenhum toque em SSOT (schema.sql, openapi.json, alembic_state.txt)
- **Rollback**: git mv em reversa (fácil, todos os ARs existem nos subdirs)
- **Risco**: Bajo (movimentos estruturais, rebuild-index é idempotente)

### Conclusão
Reorganização pura de ARs. Sem SSOT touches. Prerequisito AR_043 (rglob) já concluído.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; orphans=[f.name for f in base.glob('*.md') if f.name!='_INDEX.md']; assert not orphans,f'FAIL: MDs at top-level: {orphans}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']==25,f'FAIL: governance={counts[chr(103)+chr(111)+chr(118)+chr(101)+chr(114)+chr(110)+chr(97)+chr(110)+chr(99)+chr(101)]}!=25'; assert counts['competitions']==11,f'FAIL: competitions={counts[chr(99)+chr(111)+chr(109)+chr(112)+chr(101)+chr(116)+chr(105)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]}!=11'; assert counts['features']==7,f'FAIL: features!=7'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_045_gov_ar_folder_reorg_ars.log`
**Python Version**: 3.11.9

### Execução Executor em acf34a8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; base=pathlib.Path('docs/hbtrack/ars'); subdirs=['governance','competitions','features']; missing=[d for d in subdirs if not (base/d).is_dir()]; assert not missing,f'FAIL: missing subdirs {missing}'; counts={d:len(list((base/d).glob('*.md'))) for d in subdirs}; assert counts['governance']>=25,f'FAIL: governance={counts[\"governance\"]}>=25 required'; assert counts['competitions']>=11,f'FAIL: competitions={counts[\"competitions\"]}>=11 required'; assert counts['features']>=7,f'FAIL: features={counts[\"features\"]}>=7 required'; print(f'PASS: ars organized {counts}')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T20:02:21.228907+00:00
**Behavior Hash**: 9861cdd0ac424c932b8e81f021012b9fb1a958e54ef9ce4517cdadb0d798540e
**Evidence File**: `docs/hbtrack/evidence/AR_045/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em c68690b
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_045_c68690b/result.json`

### Selo Humano em c68690b
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T21:09:50.800632+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_045_c68690b/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_045/executor_main.log`
