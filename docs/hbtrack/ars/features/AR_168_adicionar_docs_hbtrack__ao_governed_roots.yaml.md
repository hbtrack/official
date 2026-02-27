# AR_168 — Adicionar docs/hbtrack/ ao GOVERNED_ROOTS.yaml

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar docs/_canon/specs/GOVERNED_ROOTS.yaml para incluir 'docs/hbtrack/' na lista de roots governadas. Verificar que o hb_cli valida e carrega corretamente a nova configuração.

## Critérios de Aceite
1) GOVERNED_ROOTS.yaml contém entrada 'docs/hbtrack/' na lista roots. 2) load_governed_roots() retorna lista incluindo 'docs/hbtrack/'. 3) Validação comportamental confirma que arquivo sob docs/hbtrack/ seria considerado 'governed'.

## Write Scope
- docs/_canon/specs/GOVERNED_ROOTS.yaml

## Validation Command (Contrato)
```
python -c "import yaml; from pathlib import Path; import sys; sys.path.insert(0, 'scripts/run'); from hb_cli import load_governed_roots; spec_path = Path('docs/_canon/specs/GOVERNED_ROOTS.yaml'); data = yaml.safe_load(spec_path.read_text(encoding='utf-8')); roots = data.get('roots', []); assert 'docs/hbtrack/' in roots, 'FAIL: docs/hbtrack/ ausente em GOVERNED_ROOTS.yaml'; loaded = load_governed_roots(Path('.')); assert 'docs/hbtrack/' in loaded, 'FAIL: load_governed_roots() nao retornou docs/hbtrack/'; test_path = 'docs/hbtrack/ars/features/AR_161.md'; is_governed = any(test_path.startswith(r.rstrip('/')) for r in loaded); assert is_governed, 'FAIL: docs/hbtrack/ nao sendo reconhecida como governed'; print('PASS AR_168: docs/hbtrack/ adicionada com sucesso as governed roots')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_168/executor_main.log`

## Análise de Impacto

**Arquivos Modificados**:
- `docs/_canon/specs/GOVERNED_ROOTS.yaml` (adicionar entrada 'docs/hbtrack/')

**Impacto no Sistema**:
- Após implementação, qualquer commit tocando `docs/hbtrack/` exigirá AR staged e selo humano (✅ VERIFICADO)
- Fecha brecha de governança onde mudanças em ARs/evidências/Kanban não eram protegidas pelo hb_cli
- Modificação é aditiva (não remove roots existentes)
- Não afeta código de runtime do hb_cli (apenas configuração YAML)

**Riscos Identificados**:
- NENHUM: Mudança é puramente aditiva e não invasiva

**Dependências**:
- GOVERNED_ROOTS.yaml deve existir (confirmado)
- hb_cli.py load_governed_roots() já implementado (confirmado)

**Rollback Plan**:
- `git checkout -- docs/_canon/specs/GOVERNED_ROOTS.yaml`

**Estimativa de Esforço**: Trivial (adicionar 1 linha YAML)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 8e20114
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import yaml; from pathlib import Path; import sys; sys.path.insert(0, 'scripts/run'); from hb_cli import load_governed_roots; spec_path = Path('docs/_canon/specs/GOVERNED_ROOTS.yaml'); data = yaml.safe_load(spec_path.read_text(encoding='utf-8')); roots = data.get('roots', []); assert 'docs/hbtrack/' in roots, 'FAIL: docs/hbtrack/ ausente em GOVERNED_ROOTS.yaml'; loaded = load_governed_roots(Path('.')); assert 'docs/hbtrack/' in loaded, 'FAIL: load_governed_roots() nao retornou docs/hbtrack/'; test_path = 'docs/hbtrack/ars/features/AR_161.md'; is_governed = any(test_path.startswith(r.rstrip('/')) for r in loaded); assert is_governed, 'FAIL: docs/hbtrack/ nao sendo reconhecida como governed'; print('PASS AR_168: docs/hbtrack/ adicionada com sucesso as governed roots')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T05:46:32.084628+00:00
**Behavior Hash**: 38efd2256b01f44152162bd6b6991d8e18d38b8be37227fdfd2edb778a59556d
**Evidence File**: `docs/hbtrack/evidence/AR_168/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 8e20114
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_168_8e20114/result.json`

### Selo Humano em 8e20114
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T05:54:24.138933+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_168_8e20114/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_168/executor_main.log`
