# AR_120 — Fix cmd_seal — verificacao de REJEITADO por campo Status

**Status**: 🔲 PENDENTE
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
python -c "import pathlib, subprocess, sys; content = pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert \"if '🔴 REJEITADO' in ar_content\" not in content, 'FAIL: ainda usa busca em ar_content inteiro'; assert '_status_match = re.search' in content, 'FAIL: regex por campo Status nao encontrada'; assert '_status_value' in content, 'FAIL: _status_value nao encontrado no cmd_seal'; r = subprocess.run([sys.executable, 'scripts/run/hb_cli.py', 'seal', '110'], capture_output=True, text=True, encoding='utf-8'); assert r.returncode == 0, f'FAIL: hb seal 110 retornou {r.returncode}: {r.stderr.strip()}'; assert 'VERIFICADO' in r.stdout, f'FAIL: VERIFICADO nao na saida: {r.stdout}'; print('PASS AR_120: cmd_seal fix aplicado, AR_110 selada com sucesso')"
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

