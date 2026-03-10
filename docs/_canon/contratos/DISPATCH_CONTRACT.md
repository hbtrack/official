# DISPATCH CONTRACT — HB Track (dispatch.v1)

Status: SSOT  
Owner: HB Track Governance  
Scope: roteamento determinístico entre papéis via arquivos em `_reports/dispatch/`  
Anti-goal: usar histórico de chat como “fila” ou “fonte de verdade”.

## 1) Objetivo

Este contrato define um mecanismo determinístico de handoff entre papéis (ARQUITETO, EXECUTOR, TESTADOR, HUMANO) usando “dispatch tokens” no disco.

Um dispatch token é um arquivo JSON que representa 1 evento de roteamento (“há trabalho para o papel X”).

O token é imutável após criado. O processamento do token é idempotente e auditável via transições de estado do arquivo: `.todo.json` → `.inprogress.json` → `.done.json`|`.fail.json`|`.blocked.json`.

## 2) Pastas e Estados

Raiz: `_reports/dispatch/`

Filas (obrigatórias):
- `_reports/dispatch/ARQUITETO/`
- `_reports/dispatch/EXECUTOR/`
- `_reports/dispatch/TESTADOR/`
- `_reports/dispatch/HUMANO/`

Estados do token (extensão do arquivo):
- `.todo.json`        (pendente; pronto para claim)
- `.inprogress.json`  (claimed; lock atômico)
- `.done.json`        (processado com sucesso)
- `.fail.json`        (processado; falhou por motivo técnico)
- `.blocked.json`     (não processado; precondições não atendidas / stale handoff)

## 3) Atomicidade (Regra Crítica)

3.1) O produtor MUST escrever tokens em arquivo temporário e fazer `rename` atômico:
- escreve: `<token>.tmp`
- finaliza: `os.replace(tmp, final.todo.json)`

3.2) O consumidor MUST obter lock por rename atômico:
- `os.replace(token.todo.json, token.inprogress.json)`

3.3) Se claim falhar por “file not found”, outro consumidor venceu. O consumidor MUST seguir sem erro.

## 4) Anti-race (Handoff Hash)

Cada token carrega:
- `handoff_path`
- `handoff_sha256`

O consumidor MUST:
- ler o arquivo indicado por `handoff_path`
- calcular sha256
- comparar com `handoff_sha256`

Se diferente:
- MUST finalizar como `.blocked.json` com motivo `BLOCKED_STALE_HANDOFF`
- MUST NOT executar nenhuma ação de pipeline.

## 5) Autoridade de Emissão (Quem pode dropar tokens)

- ARQUITETO pode dropar tokens para EXECUTOR (`READY_FOR_EXECUTION`)
- EXECUTOR pode dropar tokens para TESTADOR (`READY_FOR_VERIFY`)
- TESTADOR pode dropar tokens para:
  - EXECUTOR (`REJECTED_IMPL`)
  - ARQUITETO (`AH_DIVERGENCE`)
  - HUMANO (`PASS_FOR_SEAL`)
- EXECUTOR pode dropar tokens para ARQUITETO apenas em motivos de bloqueio de input/ambiguidade:
  - `BLOCKED_INPUT` / `PLAN_AMBIGUOUS` / `WRITE_SCOPE_INVALID`

Qualquer outro roteamento é inválido.

## 6) Enum fechado: reason

`reason` MUST ser um destes valores:

- `READY_FOR_EXECUTION`
- `READY_FOR_VERIFY`
- `REJECTED_IMPL`
- `AH_DIVERGENCE`
- `BLOCKED_INPUT`
- `PLAN_AMBIGUOUS`
- `WRITE_SCOPE_INVALID`
- `BLOCKED_INFRA`
- `PASS_FOR_SEAL`

## 7) Naming determinístico do token

O nome do arquivo MUST ser:
`{run_id}__AR_{ar_id}__A{attempt}__{from_role}_TO_{to_role}.todo.json`

Exemplo:
`RUN-2026-02-26T20-11-33Z__AR_045__A0__ARQUITETO_TO_EXECUTOR.todo.json`

Regras:
- `run_id` MUST ser estável e único por ciclo.
- `attempt` MUST iniciar em 0 e incrementar a cada re-dispatch do mesmo `run_id`.

## 8) Idempotência e Duplicatas

Consumidor MUST:
- tratar tokens com mesmo `{run_id, ar_id, to_role, attempt}` como duplicata se já existir `.done.json` correspondente.
- em duplicata, pode mover para `.blocked.json` com motivo `BLOCKED_DUPLICATE_TOKEN`.

## 9) Evidência mínima

Ao finalizar, o consumidor MUST gravar um “receipt” no JSON de saída (done/fail/blocked) sob:
- `receipt.finished_utc`
- `receipt.result` = `DONE|FAIL|BLOCKED`
- `receipt.note` (curto)
- `receipt.worker_id` (ex: hostname/user)

Sem isso, o token é considerado não auditável.

## 10) Integração com os handoffs `_reports/*.md`

Os arquivos `_reports/ARQUITETO.yaml`, `_reports/EXECUTOR.yaml`, `_reports/TESTADOR.yaml` continuam sendo o handoff humano/LLM.
O dispatch token é o semáforo determinístico para “quem deve agir agora”.

O chat NÃO é fonte de verdade do pipeline.

