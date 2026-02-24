# AR_122 — Fix cmd_seal — idempotencia VERIFICADO por campo Status

**Status**: 🔲 PENDENTE
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
python -c "import pathlib, subprocess, sys; content = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert 'if \"✅ VERIFICADO\" in ar_content' not in content, 'FAIL: ainda usa busca em ar_content inteiro para idempotencia'; assert '_status_idem_match = re.search' in content, 'FAIL: regex por campo Status (idem) nao encontrada'; assert '_status_idem_value' in content, 'FAIL: _status_idem_value nao encontrado'; r = subprocess.run([sys.executable, 'scripts/run/hb_cli.py', 'seal', '071'], capture_output=True, text=True, encoding='utf-8'); assert r.returncode == 0, f'FAIL: hb seal 071 retornou {r.returncode}: {r.stderr.strip()}'; assert 'VERIFICADO' in r.stdout, f'FAIL: output={r.stdout}'; print('PASS AR_122: cmd_seal idempotencia fix aplicado, AR_071 selada com sucesso')"
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

