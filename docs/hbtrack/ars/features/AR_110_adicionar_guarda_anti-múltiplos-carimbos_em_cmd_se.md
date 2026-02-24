# AR_110 — Adicionar guarda anti-múltiplos-carimbos em cmd_seal (antes de check SUCESSO)

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Em scripts/run/hb_cli.py, função cmd_seal (linha ~1496), adicionar lógica de detecção ANTES do check 'if "✅ SUCESSO" not in ar_content' (linha ~1513): (1) Extrair todos os carimbos do Testador via regex: 'testador_stamps = re.findall(r"### Verificacao Testador em [a-f0-9]{7}", ar_content)', (2) Se len(testador_stamps) > 1: fail(E_SEAL_MULTIPLE_TESTADOR_STAMPS, f"AR_{ar_id} tem {len(testador_stamps)} carimbos do Testador. Apenas 1 permitido. Carimbos encontrados: {testador_stamps}. AÇÃO: Limpe carimbos antigos ou re-execute hb verify.", exit_code=2), (3) Se len(testador_stamps) == 0: fail(E_SEAL_NOT_READY, f"AR_{ar_id} não tem carimbo do Testador. Rode: hb verify {ar_id}", exit_code=2), (4) Se '🔴 REJEITADO' in ar_content OR '🔍 NEEDS REVIEW' in ar_content: fail(E_SEAL_NOT_READY, f"AR_{ar_id} tem status REJEITADO ou NEEDS REVIEW. Corrija e re-execute hb verify {ar_id}", exit_code=2). Posicionar ANTES do check original 'if "✅ SUCESSO" not in ar_content'. Preservar toda a lógica existente após (incluindo TESTADOR_REPORT validation, staged files check, selo humano stamp).

## Critérios de Aceite
- Regex extrai carimbos do Testador corretamente (padrão '### Verificacao Testador em <7-char hash>')
- Se > 1 carimbo: fail com E_SEAL_MULTIPLE_TESTADOR_STAMPS (exit 2)
- Se 0 carimbos: fail com E_SEAL_NOT_READY (exit 2)
- Se REJEITADO ou NEEDS REVIEW presente: fail com E_SEAL_NOT_READY (exit 2)
- Checks executam ANTES do check original 'if "✅ SUCESSO" not in ar_content'
- Mensagens de erro são claras e sugerem ação corretiva ("re-execute hb verify")
- NÃO modifica lógica após os checks (seal stamp, staged files, etc)
- Código idiomático Python (sem SQL injection ou vulnerabilidades)

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar110.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_110/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Guarda defensiva: previne seal de ARs em estado inconsistente (múltiplos carimbos ou REJEITADO residual). Depende de task 109 (constante).

## Análise de Impacto
**Escopo**: Modificar a função `cmd_seal` em `scripts/run/hb_cli.py`.

**Impacto**:
- Adicionar uma verificação com regex para encontrar todos os carimbos de Testador no conteúdo da AR.
- Se mais de um carimbo for encontrado, o processo falhará com o erro `E_SEAL_MULTIPLE_TESTADOR_STAMPS`.
- Se nenhum carimbo for encontrado, o processo falhará com `E_SEAL_NOT_READY`.
- Se a AR contiver os status '🔴 REJEITADO' ou '🔍 NEEDS REVIEW', o processo falhará com `E_SEAL_NOT_READY`.
- Essa nova lógica será inserida antes da verificação existente por "✅ SUCESSO", garantindo que o `seal` seja abortado mais cedo em caso de inconsistências.

**Risco**: Médio. A modificação toca uma função crítica (`cmd_seal`). A lógica de regex e as condições devem ser precisas para evitar falsos positivos ou negativos.

**Implementação**: Inserir o bloco de código com as novas validações na função `cmd_seal`, logo após a leitura do conteúdo do arquivo da AR e antes do `if "✅ SUCESSO" not in ar_content:`.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 8608b0a
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar110.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:56:18.556787+00:00
**Behavior Hash**: 6088b141363f363172b4f50591f7bfb24c9a865a3e01f8e49dda275ab1669946
**Evidence File**: `docs/hbtrack/evidence/AR_110/executor_main.log`
**Python Version**: 3.11.9

