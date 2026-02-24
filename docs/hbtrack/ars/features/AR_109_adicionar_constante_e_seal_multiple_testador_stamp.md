# AR_109 — Adicionar constante E_SEAL_MULTIPLE_TESTADOR_STAMPS no top do hb_cli.py

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em scripts/run/hb_cli.py, adicionar nova constante de erro na seção de Exit Codes (após E_SEAL_REPORT_NOT_STAGED, antes de HBLock): 'E_SEAL_MULTIPLE_TESTADOR_STAMPS = "E_SEAL_MULTIPLE_TESTADOR_STAMPS"' (aspas duplas). Comentário inline: '# Seal abort: AR tem múltiplos carimbos do Testador (re-runs não limpos)'. NÃO modificar outras constantes. NÃO adicionar exit_code mapping (será exit 2 via fail()).

## Critérios de Aceite
- Constante E_SEAL_MULTIPLE_TESTADOR_STAMPS definida na seção de Exit Codes
- Comentário inline explica o erro
- String value é exatamente 'E_SEAL_MULTIPLE_TESTADOR_STAMPS' (self-descriptive)
- NÃO quebra imports ou outras constantes
- Posicionada após E_SEAL_REPORT_NOT_STAGED (manter ordem alfabética do bloco E_SEAL_*)

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar109.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_109/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Task pré-requisito para task 110 (cmd_seal fix). Exit code pattern: E_SEAL_* sempre usa exit(2) via fail().

## Análise de Impacto

**Escopo**: Adicionar constante de erro no hb_cli.py (top-level, seção Exit Codes)

**Impacto**:
- Nova constante `E_SEAL_MULTIPLE_TESTADOR_STAMPS` na linha ~131 (após E_SEAL_REPORT_NOT_STAGED)
- Comentário inline explica o erro: múltiplos carimbos do Testador (re-runs não limpos)
- NÃO requer exit_code mapping (usa exit 2 via fail() como outros E_SEAL_*)
- Pré-requisito para AR_110 (guarda em cmd_seal())

**Risco**: Baixo (apenas declaração de constante, não afeta lógica existente)

**Implementação**: Constante inserida entre E_SEAL_REPORT_NOT_STAGED e E_SEAL_EVIDENCE_NOT_STAGED (manter ordem alfabética do bloco E_SEAL_*).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 8608b0a
**Status Executor**: ❌ FALHA
**Comando**: `python temp/validate_ar109.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T17:52:40.434927+00:00
**Behavior Hash**: b32a3881f2c56d4e8f50bb66422a6dedddecea810bff62e922075ff864053f68
**Evidence File**: `docs/hbtrack/evidence/AR_109/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 8608b0a
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar109.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:53:01.008197+00:00
**Behavior Hash**: 9f7df3e31d4ae692b29bb8ac29f67ee3f0bebbd1aea75927fd592b52fa5fcbd1
**Evidence File**: `docs/hbtrack/evidence/AR_109/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em ab81cc3
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_109_ab81cc3/result.json`

### Selo Humano em ab81cc3
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T18:12:03.703396+00:00
**Motivo**: 110
**TESTADOR_REPORT**: `_reports/testador/AR_109_ab81cc3/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_109/executor_main.log`
