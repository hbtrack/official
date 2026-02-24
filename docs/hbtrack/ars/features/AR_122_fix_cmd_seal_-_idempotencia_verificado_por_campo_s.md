# AR_122 — Fix cmd_seal — idempotencia VERIFICADO por campo Status

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir falso-positivo de idempotencia em cmd_seal. O guard atual verifica presenca de '✅ VERIFICADO' em todo ar_content, gerando falso-positivo quando o AR menciona essa string em sua descricao. SUBSTITUICAO CIRURGICA na funcao cmd_seal em hb_cli.py, bloco de idempotencia: ANTES (linha ~1513):
  if "✅ VERIFICADO" in ar_content:
    print(f"✅ AR_{ar_id} ja esta VERIFICADO (idempotente).")
    sys.exit(0)
DEPOIS:
  # V11: Verificar apenas o campo **Status**: para evitar falso-positivo de idempotencia
  _status_idem_match = re.search(r'^\*\*Status\*\*:\s*(.+)$', ar_content, re.MULTILINE)
  _status_idem_value = _status_idem_match.group(1).strip() if _status_idem_match else ''
  if '✅ VERIFICADO' in _status_idem_value:
    print(f"✅ AR_{ar_id} ja esta VERIFICADO (idempotente).")
    sys.exit(0)
NAO modificar nenhuma outra linha da funcao. Nomes de variaveis distintos dos de AR_120 (_status_idem_match vs _status_match) para evitar colisao de escopo.

## Critérios de Aceite
- hb_cli.py NAO contem 'if "✅ VERIFICADO" in ar_content' no bloco de idempotencia
- hb_cli.py contem '_status_idem_match = re.search' no contexto de cmd_seal
- hb_cli.py contem '_status_idem_value' no contexto de cmd_seal
- Executar hb seal 071 retorna exit 0 (AR_071 selada como VERIFICADO)
- Executar hb seal para AR realmente VERIFICADA ainda retorna idempotente (exit 0)
- Nenhuma outra funcao de hb_cli.py modificada

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar122.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_122/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Fix de 4 linhas. Mesmo padrao do AR_120, mas para verificacao de idempotencia (linha 1513 vs 1524). Usar nomes de variaveis distintos (_status_idem_*) para evitar colisao com variaveis do fix de AR_120. AR_071 tem Testador SUCESSO — unico bloqueio era falso-positivo de idempotencia. Nota: se AR_120 ja tiver sido aplicada antes deste fix, o hb_cli.py tera mudado — o Executor deve aplicar este patch sobre a versao ja corrigida pelo AR_120.

## Análise de Impacto
**Escopo**: Patch cirúrgico em `cmd_seal` de `scripts/run/hb_cli.py` (~linha 1513).

**Impacto**:
- Substituída a verificação `if '✅ VERIFICADO' in ar_content` por regex que inspeciona apenas o campo `**Status**:` do AR.
- Elimina o falso-positivo que impedia AR_071 de ser selada (ela menciona 'VERIFICADO' em sua Descrição).
- Nomes de variáveis distintos (`_status_idem_*`) para não colidir com variáveis do fix AR_120.

**Risco**: Baixo. Fix de 4 linhas. Aplicado junto com AR_120 (mesmo bloco, mesmo arquivo).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a06d856
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar122.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:04:38.700203+00:00
**Behavior Hash**: f620aeb8f88c13f540cfa6230f5c5a02e977bbf974d36fd422be43d9fbc7580f
**Evidence File**: `docs/hbtrack/evidence/AR_122/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 09654e9
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_122_09654e9/result.json`

### Selo Humano em 162dc4e
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T19:18:46.497756+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_122_09654e9/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_122/executor_main.log`
