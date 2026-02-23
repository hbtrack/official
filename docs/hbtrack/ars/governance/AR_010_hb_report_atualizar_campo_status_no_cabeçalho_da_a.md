# AR_010 — hb report: atualizar campo **Status** no cabeçalho da AR após execução

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: cmd_report em scripts/run/hb_cli.py (linha ~556) usa open(ar_file, 'a') para gravar o carimbo de execução ao final da AR, mas não atualiza o campo **Status** no cabeçalho (linha ~3 da AR). O resultado é que ARs executadas permanecem com Status=DRAFT ou Status=EM_EXECUCAO mesmo após conclusão, causando divergência de governança.

FIX NECESSÁRIO em scripts/run/hb_cli.py, função cmd_report:
Após a seção '# Anexar carimbo na AR' (após o bloco with open(ar_file, 'a'))::

(1) Ler o arquivo AR completo novamente (ou usar o ar_content já em memória).
(2) Aplicar re.sub para substituir a linha **Status** no cabeçalho:
    novo_status = '✅ SUCESSO' if exit_code == 0 else '❌ FALHA'
    ar_content_updated = re.sub(r'\*\*Status\*\*:.*', f'**Status**: {novo_status}', ar_content_updated, count=1)
(3) Gravar o arquivo completo atualizado (modo 'w', não 'a').

ORDEM DE OPERAÇÕES (para evitar inconsistência):
1. Executar o comando (já feito).
2. Gravar evidence pack (já feito).
3. Ler ar_content atualizado (após append do carimbo).
4. Re.sub no **Status** header.
5. Reescrever o arquivo completo.

Arquivo a modificar (ÚNICO): scripts/run/hb_cli.py
Função: cmd_report (linhas ~503-569)
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) Após hb report <id> <cmd> com exit code 0, o campo **Status** na linha 3 da AR deve ser '**Status**: ✅ SUCESSO'. 2) Após hb report <id> <cmd> com exit code != 0, o campo **Status** deve ser '**Status**: ❌ FALHA'. 3) O carimbo '### Execução em <hash>' continua sendo appendado ao final (comportamento anterior mantido). 4) hb check continua funcionando (não regride). 5) A função cmd_report em hb_cli.py contém re.sub para atualizar **Status** no cabeçalho.

## Validation Command (Contrato)
```
python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); fn=re.search(r'def cmd_report.*?(?=\ndef [a-z])', src, re.DOTALL); assert fn, 'cmd_report not found'; body=fn.group(0); assert re.search(r'\*\*Status\*\*', body), 'FAIL: no Status update in cmd_report'; print('PASS: cmd_report contains **Status** header update logic')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_010_gov_ar_status_header_sync.log`

## Riscos
- re.sub com count=1 garante que apenas a primeira ocorrência de **Status** (no cabeçalho) seja substituída — não afeta possíveis menções de **Status** no corpo da AR.
- Se a AR não tiver linha **Status** (formato incorreto), o re.sub não substitui nada — comportamento seguro (não gera erro, apenas não atualiza).
- A leitura do arquivo após o append deve usar encoding='utf-8' para evitar erro no Windows com emojis.

## Análise de Impacto
- Arquivos afetados: [scripts/run/hb_cli.py]
- Mudança no Schema? [Não]
- Risco de Regressão? [Baixo]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); fn=re.search(r'def cmd_report.*?(?=\ndef [a-z])', src, re.DOTALL); assert fn, 'cmd_report not found'; body=fn.group(0); assert re.search(r'\*\*Status\*\*', body), 'FAIL: no Status update in cmd_report'; print('PASS: cmd_report contains **Status** header update logic')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_010_gov_ar_status_header_sync.log`
**Python Version**: 3.11.9


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); fn=re.search(r'def cmd_report.*?(?=\ndef [a-z])', src, re.DOTALL); assert fn, 'cmd_report not found'; body=fn.group(0); assert re.search(r'\*\*Status\*\*', body), 'FAIL: no Status update in cmd_report'; print('PASS: cmd_report contains **Status** header update logic')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_010_gov_ar_status_header_sync.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_010_b2e7523/result.json`
