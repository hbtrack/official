# AR_033 — AR Index Checkpoint: _INDEX.md completo e sincronizado com todos AR_*.md

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: nenhum (governance checkpoint — sem alteração de código)

### Problema
O _INDEX.md é auto-gerado por hb plan e hb report, mas não existe gate que valide se ele está COMPLETO em relação a todos os AR_*.md em disco. O hb check (C5) valida apenas que o _INDEX.md está staged junto com ARs — não valida o conteúdo.

Risco: se alguém criar uma AR fora do fluxo (ou se hb plan falhar no meio), o index pode ter menos entradas que o número real de ARs, gerando confusão para o Arquiteto e os agentes.

### Implementação

O Executor NÃO precisa alterar nenhum arquivo. A ação é:

1. Executar: python scripts/run/hb_cli.py report 033 "<validation_command_exato>"
   - hb report internamente chama rebuild_ar_index() ANTES de gravar o carimbo
   - O index será reconstruído automaticamente como efeito colateral
   - Depois o validation_command roda e valida o resultado

### Por que isto funciona como gate permanente

Cada vez que o Arquiteto suspeitar que o index está defasado, basta:
- Executor re-executar: hb report 033 "<validation_command>" --force
- Isso reconstrói o index E valida que está completo
- A AR vira prova auditável de que o index estava sincronizado naquele commit

## Critérios de Aceite
1) docs/hbtrack/_INDEX.md existe. 2) Todos os AR_XXX IDs presentes em AR_*.md no disco têm entrada correspondente em _INDEX.md. 3) Contagem de ARs em disco == linhas de dados no _INDEX.md (excluindo header). 4) _INDEX.md contém header '⚠️ Auto-gerado'. 5) Nenhum AR_*.md ficou de fora do index.

## Validation Command (Contrato)
```
python -c "import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); idx_path=pathlib.Path('docs/hbtrack/_INDEX.md'); files=[f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]; ar_ids=set(); [ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3}(?:\.[0-9]+)?[A-Za-z]?)',f.name)] if m]; idx=idx_path.read_text(encoding='utf-8'); assert 'Auto-gerado' in idx,'FAIL: _INDEX.md nao e auto-gerado ou foi editado manualmente'; missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; assert not missing,f'FAIL: ARs ausentes no index: {missing}'; idx_ids=set(m.group(1) for l in idx.splitlines() for m in [re.match(r'\| AR_([0-9]+(?:\.[0-9]+)?[A-Za-z]?) ',l)] if m); assert len(idx_ids)==len(ar_ids),f'FAIL: index tem {len(idx_ids)} ARs mas disco tem {len(ar_ids)} ARs'; print(f'PASS: _INDEX.md completo - {len(ar_ids)} ARs sincronizados')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_033/executor_main.log`

## Notas do Arquiteto
TESTES DETERMINÍSTICOS (formato Manual Deterministico):

GATE-INDEX-001: Completude
  cmd: python -c "import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); idx=pathlib.Path('docs/hbtrack/_INDEX.md').read_text(encoding='utf-8'); files=[f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]; ar_ids=set(); [ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3})',f.name)] if m]; missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; assert not missing,f'FAIL: {missing}'; print(f'PASS: {len(ar_ids)} ARs no index')"
  PASS: 'PASS: N ARs no index' (N determinístico a cada run)
  FAIL: 'FAIL: ARs ausentes no index: [...]'

GATE-INDEX-002: Header de auto-geração intacto
  cmd: python -c "import pathlib; idx=pathlib.Path('docs/hbtrack/_INDEX.md').read_text(encoding='utf-8'); assert 'Auto-gerado' in idx,'FAIL'; print('PASS: header ok')"
  PASS: 'PASS: header ok'
  FAIL: 'AssertionError: FAIL'

GATE-INDEX-003: Contagem exata (sem linhas fantasma)
  cmd: python -c "import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); n_files=len([f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]); idx=pathlib.Path('docs/hbtrack/_INDEX.md').read_text(encoding='utf-8'); n_rows=len([l for l in idx.splitlines() if l.startswith('| AR_')]); assert n_rows==n_files,f'FAIL: {n_rows} rows vs {n_files} files'; print(f'PASS: {n_rows}=={n_files}')"
  PASS: 'PASS: N==N'
  FAIL: 'FAIL: M rows vs N files'

## Riscos
- O validation_command conta linhas que começam com '| AR_' — se o formato do _INDEX.md mudar, o gate pode falhar erroneamente
- Se duas ARs tiverem o mesmo prefixo ID (ex: AR_031 e AR_031b), o gate pode dar falso positivo — IDs MUST ser únicos (enforcement via hb plan GATE 2)
- hb report reconstrói o index ANTES de chamar o validation_command — ordem garantida pelo hb_cli.py linha 797 então linha de execução do cmd
- Se rodar --force no hb report 033, o carimbo antigo é sobrescrito — isso é correto para um checkpoint reutilizável
- Triple-run do Testador: o filesystem não muda entre runs → stdout_hash será idêntico → triple_consistency=OK garantido

## Análise de Impacto
**Executor**: Roo (Executor HB Track)
**Data**: 2026-02-22

**Estado Atual**:
- O `_INDEX.md` é mantido automaticamente, mas requer uma validação formal de completude.
- Esta AR atua como um checkpoint de governança.

**Ações Necessárias**:
1. Executar `hb report 033` com o comando de validação fornecido.
2. O comando validará se todos os arquivos `AR_*.md` estão listados no `_INDEX.md`.

**Impacto**:
- Garante a integridade da documentação de rastreabilidade.
- Sem alterações de código.

**Conclusão**: Operação de governança segura e necessária para manter o determinismo do fluxo.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em b2e7523
**Status Final**: ❌ FALHA
**Comando**: `python -c "import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); files=[f for f in ar_dir.glob('AR_*.md') if '_INDEX' not in f.name]; ar_ids=set(); [ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3})',f.name)] if m]; idx=( ar_dir/'_INDEX.md').read_text(encoding='utf-8'); assert 'Auto-gerado' in idx,'FAIL: _INDEX.md nao e auto-gerado ou foi editado manualmente'; missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; assert not missing,f'FAIL: ARs ausentes no index: {missing}'; rows=[l for l in idx.splitlines() if l.startswith('| AR_')]; assert len(rows)==len(ar_ids),f'FAIL: index tem {len(rows)} linhas mas disco tem {len(ar_ids)} ARs'; print(f'PASS: _INDEX.md completo — {len(ar_ids)} ARs sincronizados')"`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_033_ar_index_validation_checkpoint.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Execução Executor em 8d39a14
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re; ar_dir=pathlib.Path('docs/hbtrack/ars'); idx_path=pathlib.Path('docs/hbtrack/_INDEX.md'); files=[f for f in ar_dir.rglob('AR_*.md') if '_INDEX' not in f.name]; ar_ids=set(); [ar_ids.add(m.group(1)) for f in files for m in [re.match(r'AR_([0-9]{3}(?:\.[0-9]+)?[A-Za-z]?)',f.name)] if m]; idx=idx_path.read_text(encoding='utf-8'); assert 'Auto-gerado' in idx,'FAIL: _INDEX.md nao e auto-gerado ou foi editado manualmente'; missing=[i for i in sorted(ar_ids) if f'AR_{i}' not in idx]; assert not missing,f'FAIL: ARs ausentes no index: {missing}'; idx_ids=set(m.group(1) for l in idx.splitlines() for m in [re.match(r'\| AR_([0-9]+(?:\.[0-9]+)?[A-Za-z]?) ',l)] if m); assert len(idx_ids)==len(ar_ids),f'FAIL: index tem {len(idx_ids)} ARs mas disco tem {len(ar_ids)} ARs'; print(f'PASS: _INDEX.md completo - {len(ar_ids)} ARs sincronizados')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T20:47:35.496907+00:00
**Behavior Hash**: b87f7c7fd0901ee3902d5ac62d4200d6306644136f99e52b005d77ebaec792cd
**Evidence File**: `docs/hbtrack/evidence/AR_033/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 8d39a14
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_033_8d39a14/result.json`

### Selo Humano em 8d39a14
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T20:48:05.129434+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_033_8d39a14/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_033/executor_main.log`
