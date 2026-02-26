# AR_131 — Adicionar gate de proteção: cmd_verify MUST NOT rebuild _INDEX.md se houver ARs staged

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
O hb verify está destruindo a integridade do _INDEX.md quando há batch de ARs em paralelo. Cada hb verify chama rebuild_ar_index() que regenera o índice baseado no disco, descartando ARs staged que ainda não foram commitadas.

Problema identificado:
- Executor trabalha em 10 ARs simultaneamente
- hb report de cada AR atualiza _INDEX.md
- _INDEX.md fica staged com TODAS as ARs
- Alguém faz git restore _INDEX.md (limpeza manual)
- hb verify chama rebuild_ar_index() e regenera índice COM APENAS 1 AR
- _INDEX.md perde as outras 9 ARs

Solução:
1. Adicionar função get_staged_ars() que detecta ARs staged via git diff --cached
2. Modificar cmd_verify para chamar essa função ANTES de rebuild_ar_index
3. Se houver múltiplas ARs staged (len > 1), cmd_verify MUST SKIP rebuild_ar_index
4. Se houver apenas 1 AR ou nenhuma AR staged, cmd_verify pode chamar rebuild_ar_index normalmente

Implementação:
A) Adicionar get_staged_ars() após check_workspace_clean() (linha ~1040)
B) Modificar cmd_verify linha ~1515 com gate condicional
C) Adicionar error code E_VERIFY_BATCH_INDEX_SKIP
D) Modificar rebuild_ar_index docstring

Evidência de sucesso:
- get_staged_ars() detecta corretamente ARs staged
- _INDEX.md NÃO é regerado quando há múltiplas ARs staged
- _INDEX.md É regerado quando há 1 AR ou batch vazio

## Critérios de Aceite
get_staged_ars() implementada e funcional. cmd_verify chama get_staged_ars() antes de rebuild_ar_index. Se len(staged_ars) > 1, SKIP rebuild_ar_index com mensagem de warning. Se len(staged_ars) <= 1, CALL rebuild_ar_index normalmente. Error code E_VERIFY_BATCH_INDEX_SKIP definido. rebuild_ar_index docstring atualizada. _INDEX.md preservado em batch de 10 ARs sem desatualização.

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python temp/validate_ar131.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_131/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- scripts/run/hb_cli.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
CRITICAL: Correção de governança que estava atrasando sistema em 12+ ocorrências. Anti-desatualização do _INDEX.md em batch mode.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em dd11c7d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar131.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T02:22:58.919207+00:00
**Behavior Hash**: 08da82abdcf47be4c9bda949c2dcf46d11900c8f12d3681ad09a90f635e21e33
**Evidence File**: `docs/hbtrack/evidence/AR_131/executor_main.log`
**Python Version**: 3.11.9

