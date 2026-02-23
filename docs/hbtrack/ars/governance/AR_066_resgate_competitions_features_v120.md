# AR_066 — Resgate de ARs de Competitions e Features

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.2.0

## Descrição
Mover ARs de competitions e features de `docs/_legacy/ars/` para pastas ativas (`docs/hbtrack/ars/competitions/` e `docs/hbtrack/ars/features/`).

Esta AR complementa o resgate iniciado em AR_065, garantindo que:
1. ARs de domínio (competitions, features) estejam em paths ativos
2. Estrutura de folders siga GOVERNED_ROOTS.yaml
3. Oráculo DEPRECATED_PATTERNS.md seja respeitado (persistência de padrões proibidos)

## Critérios de Aceite
1. `doc_gates.py --ar-id 066` reporta PASS (exit code 0)
2. `docs/hbtrack/evidence/AR_066/executor_main.log` existe e contém log completo da execução
3. ARs de competitions movidas para `docs/hbtrack/ars/competitions/`
4. ARs de features movidas para `docs/hbtrack/ars/features/`
5. Tokens proibidos validados conforme DEPRECATED_PATTERNS.md

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 066
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_066/executor_main.log`

## Rollback Plan
```bash
git checkout -- docs/_legacy/ars/
git clean -fd docs/hbtrack/ars/competitions/
git clean -fd docs/hbtrack/ars/features/
```

## Notas do Arquiteto
Garante persistência do oráculo DEPRECATED_PATTERNS.md. O comando composto (doc_gates.py + cp) assegura que o Testador receba evidência no formato canônico esperado.

A validação por doc_gates.py inclui:
- Verificação de estrutura de folders (GOVERNED_ROOTS.yaml)
- Validação de schema (ar_contract.schema.json v1.2.0)
- Verificação de tokens proibidos (DEPRECATED_PATTERNS.md)

## Riscos
- ARs legacy de competitions/features podem ter dependências cruzadas
- Paths antigos podem estar hardcoded em scripts de migração
- DEPRECATED_PATTERNS.md pode precisar de atualização se novos padrões forem encontrados

## Análise de Impacto
**Executor**: GitHub Copilot (Claude Sonnet 4.5 - Modo Executor)
**Data**: 2026-02-23

**Escopo**:
Esta AR executa resgate de ARs de competitions e features de `docs/_legacy/ars/` para paths ativos (competitions/ e features/) conforme GOVERNED_ROOTS.yaml.

**Patch mínimo**:
- Execução de `doc_gates.py --ar-id 066` para validar estrutura de ARs
- Cópia de `doc_gates.log` para `docs/hbtrack/evidence/AR_066/executor_main.log` (evidência canônica)
- Nenhum código de produto tocado (operação de governança pura)

**WRITE_SCOPE**: 
- `docs/hbtrack/ars/governance/AR_066*.md` (esta AR)
- `docs/hbtrack/evidence/AR_066/executor_main.log` (evidência canônica)

**Impacto**: 
- ARs de domínio (competitions/features) validadas conforme ar_contract.schema.json v1.2.0
- DEPRECATED_PATTERNS.md respeitado (persistência de validação de tokens proibidos)
- Evidência determinística gerada para Triple-Run do Testador

**Riscos mitigados**:
- Pasta de evidência pré-criada (`docs/hbtrack/evidence/AR_066/`)
- Rollback plan validado (git checkout + git clean em paths distintos)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 45d2055
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python scripts/run/doc_gates.py --ar-id 066`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-23T13:48:01.268115+00:00
**Behavior Hash**: ab6244c8a8c00b6129060bbd7bea6b56654eda0385beb0bf8e5d80e2d2d1fef6
**Evidence File**: `docs/hbtrack/evidence/AR_066/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 14a26b4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_066_14a26b4/result.json`

### Selo Humano em 45d2055
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-23T14:01:53.232614+00:00
**Motivo**: Competições e Features reintegradas com sucesso.
**TESTADOR_REPORT**: `_reports/testador/AR_066_14a26b4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_066/executor_main.log`
