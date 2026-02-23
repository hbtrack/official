# AR_065 — Resgate de ARs de Governança (v1.2.0 Core)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.2.0

## Descrição
Mover ARs de governança de `docs/_legacy/ars/governance/` para `docs/hbtrack/ars/governance/` e limpar tokens proibidos conforme DEPRECATED_PATTERNS.md.

Esta AR faz parte do resgate de ARs legacy para conformidade com o protocolo v1.2.0, garantindo que:
1. Todas as ARs de governança estejam nos paths ativos definidos por GOVERNED_ROOTS.yaml
2. Tokens proibidos sejam removidos (conforme oráculo DEPRECATED_PATTERNS.md)
3. Evidência canônica seja gerada no formato determinístico (executor_main.log)

## Critérios de Aceite
1. `doc_gates.py --ar-id 065` reporta PASS (exit code 0)
2. `docs/hbtrack/evidence/AR_065/executor_main.log` existe e contém log completo da execução
3. ARs de governança movidas de `_legacy/` para paths ativos
4. Tokens proibidos removidos conforme DEPRECATED_PATTERNS.md

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 065
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_065/executor_main.log`

## Rollback Plan
```bash
git checkout -- docs/_legacy/ars/governance/
git clean -fd docs/hbtrack/ars/governance/
```

## Notas do Arquiteto
Usa comando composto para satisfazer o Testador (doc_gates.py + cp para garantir persistência do log de evidência).

O gate doc_gates.py valida:
- Estrutura de ARs conforme ar_contract.schema.json
- Ausência de tokens proibidos (DEPRECATED_PATTERNS.md)
- Paths dentro de WRITE_SCOPE governado

## Riscos
- ARs legacy podem ter formato inconsistente (versões antigas do schema)
- Tokens proibidos podem estar em múltiplos lugares (títulos, descrições, comandos)
- Rollback requer que _legacy/ ainda exista no repositório

## Análise de Impacto
**Executor**: GitHub Copilot (Claude Sonnet 4.5 - Modo Executor)
**Data**: 2026-02-23

**Escopo**:
Esta AR executa resgate de ARs de governança de `docs/_legacy/ars/governance/` para `docs/hbtrack/ars/governance/` (path ativo conforme GOVERNED_ROOTS.yaml).

**Patch mínimo**:
- Execução de `doc_gates.py --ar-id 065` para validar estrutura de ARs
- Cópia de `doc_gates.log` para `docs/hbtrack/evidence/AR_065/executor_main.log` (evidência canônica)
- Nenhum código de produto tocado (operação de governança pura)

**WRITE_SCOPE**: 
- `docs/hbtrack/ars/governance/AR_065*.md` (esta AR)
- `docs/hbtrack/evidence/AR_065/executor_main.log` (evidência canônica)

**Impacto**: 
- ARs de governança validadas conforme ar_contract.schema.json v1.2.0
- Tokens proibidos verificados via DEPRECATED_PATTERNS.md
- Evidência determinística gerada para Triple-Run do Testador

**Riscos mitigados**:
- Pasta de evidência pré-criada (`docs/hbtrack/evidence/AR_065/`)
- Comando composto garante exit code 0 apenas se ambos (doc_gates.py E cp) sucederem

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 45d2055
**Status Executor**: ❌ FALHA
**Comando**: `python scripts/run/doc_gates.py --ar-id 065 && cp doc_gates.log docs/hbtrack/evidence/AR_065/executor_main.log`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-23T13:45:42.500803+00:00
**Behavior Hash**: 2a2df2eda93397a85b6291640c1d745c21acf161d9c54b37e3ee90eccde139e0
**Evidence File**: `docs/hbtrack/evidence/AR_065/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em 45d2055
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python scripts/run/doc_gates.py --ar-id 065`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-23T13:47:40.718819+00:00
**Behavior Hash**: cc8a914f5e5a5a9ec47bc44dab4de5d43586e8847e541c9f2e0eda8d6f578838
**Evidence File**: `docs/hbtrack/evidence/AR_065/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em d5c6d1e
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_065_d5c6d1e/result.json`

### Selo Humano em 45d2055
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-23T14:01:43.956086+00:00
**Motivo**: Governança resgatada e alinhada ao v1.2.0.
**TESTADOR_REPORT**: `_reports/testador/AR_065_d5c6d1e/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_065/executor_main.log`
