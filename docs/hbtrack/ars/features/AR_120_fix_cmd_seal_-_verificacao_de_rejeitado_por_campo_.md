# AR_120 — Fix cmd_seal — verificacao de REJEITADO por campo Status

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir falso-positivo em cmd_seal no arquivo hb_cli.py. O guard atual verifica presenca de '🔴 REJEITADO' ou '🔍 NEEDS REVIEW' em todo o conteudo do AR (ar_content), gerando falso-positivo quando o AR menciona essas strings em sua descricao. SUBSTITUICAO CIRURGICA na funcao cmd_seal: ANTES (linha ~1524):
  if '🔴 REJEITADO' in ar_content or '🔍 NEEDS REVIEW' in ar_content:
    fail(E_SEAL_NOT_READY, f"AR_{ar_id} tem status REJEITADO ou NEEDS REVIEW. Corrija e re-execute hb verify {ar_id}", exit_code=2)
DEPOIS:
  # V11: Verificar apenas o campo **Status**: (nao o conteudo inteiro) para evitar falso-positivo
  _status_match = re.search(r'^\*\*Status\*\*:\s*(.+)$', ar_content, re.MULTILINE)
  _status_value = _status_match.group(1).strip() if _status_match else ''
  if '🔴 REJEITADO' in _status_value or '🔍 NEEDS REVIEW' in _status_value:
    fail(E_SEAL_NOT_READY, f"AR_{ar_id} tem status REJEITADO ou NEEDS REVIEW. Corrija e re-execute hb verify {ar_id}", exit_code=2)
NAO modificar nenhuma outra linha da funcao. Verificar que 're' ja esta importado no topo do arquivo (esta).

## Critérios de Aceite
- hb_cli.py NAO contem mais 'if .🔴 REJEITADO. in ar_content' na funcao cmd_seal
- hb_cli.py contem '_status_match = re.search' no contexto de cmd_seal
- hb_cli.py contem '_status_value' e a verificacao por campo especifico
- Executar hb seal 110 retorna exit 0 (AR_110 selada como VERIFICADO)
- Executar hb seal em AR realmente REJEITADA ainda retorna E_SEAL_NOT_READY
- Nenhuma outra funcao de hb_cli.py modificada

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar120.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_120/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Fix de 4 linhas. Nao alterar estrutura da funcao cmd_seal, apenas substituir o guard de status. AR_110 tem Testador SUCESSO (result.json) e evidence com Exit 0. Unico bloqueio era o false-positive na linha 1524. Apos fix, AR_110 deve selar automaticamente na validation_command.

## Análise de Impacto
**Escopo**: Patch cirúrgico em `cmd_seal` de `scripts/run/hb_cli.py` (~linha 1524).

**Impacto**:
- Substituída a verificação `if '🔴 REJEITADO' in ar_content` por regex que inspeciona apenas o campo `**Status**:` do AR.
- Elimina o falso-positivo que bloqueava AR_110, AR_111 e AR_112 (que mencionam 'REJEITADO' em suas Descrições).
- Nenhuma outra função ou lógica modificada.

**Risco**: Baixo. Fix de 4 linhas. Aplicado junto com AR_122 (mesmo bloco).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a06d856
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar120.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:04:32.401493+00:00
**Behavior Hash**: c3d95cfa48b7c420aec6969e8c672374a23bc6e53c886d063c0dbb5f740e4711
**Evidence File**: `docs/hbtrack/evidence/AR_120/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 2ef7e91
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_120_2ef7e91/result.json`

### Selo Humano em 2ef7e91
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T19:19:54.536848+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_120_2ef7e91/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_120/executor_main.log`
