# AR_018 — Novo contrato: docs/_canon/contratos/Testador Contract.md — 3º agente + anti-alucinação

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
CRIAR novo arquivo docs/_canon/contratos/Testador Contract.md com o conteúdo EXATO abaixo (preservar formatação e seção numbers):

---INÍCIO DO ARQUIVO---
# TESTADOR_CONTRACT — HB Track (Determinístico) — v1.0.0

Este documento é o CONTRATO canônico do Testador, o 3º agente do fluxo HB Track.
Qualquer divergência entre prática e este contrato é BUG de governança.

## 1. Identidade e Papel

O Testador é o 3º agente independente no fluxo:

```
Arquiteto → [Plan JSON] → Executor → [hb report + SUCESSO] → Testador → [hb verify + VERIFICADO] → Humano (DONE)
```

- **Função**: verificar independentemente que o Evidence Pack do Executor é real, correto e não alucinado.
- **Subordinação**: subordinado ao Arquiteto; independente do Executor.
- **Regra de ouro**: o Testador NUNCA confia no output do Executor sem re-executar.
- **Escopo de escrita**: APENAS `_reports/testador/` e o campo `**Status**` da AR verificada.

## 2. Regras Anti-Alucinação (AH-1 a AH-7)

**AH-1 — Source-Inspection-Only é PROIBIDO para tasks de código:**
Validation commands que apenas verificam se uma string existe em um arquivo fonte (ex: `assert 'X' in open('file.py').read()`) são PROIBIDOS como único gate para tasks que modificam comportamento de código. Uma gate comportamental (execução real do código modificado) é OBRIGATÓRIA.

**AH-2 — Validation Commands trivialmente passáveis são PROIBIDOS:**
O Executor MUST NOT escrever validation commands que passam independentemente da implementação (ex: `echo PASS`, `python -c "print('PASS')"`). O comando MUST exercitar o comportamento real da mudança.

**AH-3 — Re-execução Independente é OBRIGATÓRIA:**
O Testador MUST re-executar o validation_command da AR de forma independente, no mesmo ambiente. MUST NOT aceitar o stdout/stderr do Executor como prova.

**AH-4 — Divergência de Exit Code é REJEIÇÃO:**
Se o Executor gravou `Exit Code: 0` no Evidence Pack MAS o Testador obtém exit code != 0 ao re-executar: a AR é **REJEITADO** com classificação `AH_DIVERGENCE`. Isso indica que o Executor reportou falso positivo.

**AH-5 — ERROR_INFRA não é REJEIÇÃO — é BLOQUEIO:**
Se a re-execução falha por infra (DB inacessível, rede, timeout) e não por lógica: o resultado é `BLOCKED` (exit code 3), não `REJEITADO`. Waiver formal pode ser solicitado ao Arquiteto.

**AH-6 — Evidence Pack incompleto é REJEIÇÃO:**
Se o Evidence Pack do Executor não contém os campos obrigatórios definidos em Manual Deterministico §2.1 (context.json, result.json, stdout.log, stderr.log), a AR é REJEITADO com classificação `INCOMPLETE_EVIDENCE`.

**AH-7 — Waiver para Validation Command fraco exige aprovação humana:**
Se a única opção de gate disponível for source-inspection (ex: mudança é puramente documental), o Arquiteto MUST aprovar explicitamente com waiver formal antes do Testador aceitar. Sem waiver: BLOCKED.

## 3. Protocolo de Verificação (7 Passos do Testador)

```
Passo T1 — LOCALIZAR     hb verify <id> → localiza AR_<id>_*.md
Passo T2 — PRÉ-CHECK     Verificar que Status=✅ SUCESSO (Executor terminou)
Passo T3 — EXTRAIR       Ler validation_command e criteria da AR
Passo T4 — RE-EXECUTAR   Executar validation_command independentemente
Passo T5 — CONFRONTAR    Comparar exit code com Evidence Pack do Executor
Passo T6 — RELATAR       Gravar TESTADOR_REPORT em _reports/testador/
Passo T7 — SELAR         Atualizar **Status** da AR para ✅ VERIFICADO ou 🔴 REJEITADO
```

## 4. TESTADOR_REPORT (estrutura obrigatória)

Caminho: `_reports/testador/AR_<id>_<git_hash_7>/`

Arquivos obrigatórios:

```
_reports/testador/AR_<id>_<hash>/
  context.json    # run_id, timestamp, git, environment
  result.json     # status, exit_code, consistency, ar_id, validation_cmd, checks
  stdout.log      # stdout da re-execução
  stderr.log      # stderr da re-execução
```

### 4.1 result.json (campos obrigatórios)

```json
{
  "ar_id": "018",
  "validation_command": "<cmd>",
  "testador_exit_code": 0,
  "executor_exit_code": 0,
  "consistency": "OK",
  "status": "VERIFICADO",
  "ah_flags": [],
  "evidence_pack_complete": true,
  "rejection_reason": null
}
```

Campos de `consistency`:
- `OK`: Testador e Executor obtiveram o mesmo exit code
- `AH_DIVERGENCE`: Executor reportou 0 mas Testador obteve != 0 (falso positivo detectado)
- `EXECUTOR_FAIL`: Executor já reportou falha (✅ SUCESSO ausente — não deveria chegar aqui)

Campos de `status`:
- `VERIFICADO`: re-execução exit 0 + consistency OK
- `REJEITADO`: re-execução exit != 0 OU AH_DIVERGENCE OU INCOMPLETE_EVIDENCE
- `BLOCKED`: ERROR_INFRA na re-execução

## 5. Status de AR após Testador

| Status hb verify | Novo **Status** na AR | Significado |
|---|---|---|
| VERIFICADO | `✅ VERIFICADO` | Testador confirmou independentemente |
| REJEITADO | `🔴 REJEITADO` | Falso positivo ou critérios não atendidos |
| BLOCKED | `⏸️ BLOQUEADO_INFRA` | Infra inacessível — waiver necessário |

## 6. hb check — Enforcement para ARs v1.0.8+

Para ARs com `**Versão do Protocolo**: 1.0.8` ou superior:
- `hb check` exige `✅ VERIFICADO` no conteúdo da AR (não apenas `✅ SUCESSO`).

Para ARs com protocolo anterior:
- `hb check` continua aceitando `✅ SUCESSO` (migração gradual).

Rationale: nenhum código gerado por IA deve ir para commit sem verificação independente.

## 7. Integração com hb_cli.py

Comando: `python scripts/run/hb_cli.py verify <id>`

Ver especificação completa em `docs/_canon/specs/Hb cli Spec.md §10`.

## 8. O que o Testador MUST verificar além da re-execução

8.1 Evidence Pack completeness (Manual Deterministico §2.1):
- Se o Evidence Pack referenciado na AR não existe: REJEITADO (INCOMPLETE_EVIDENCE)
- Se o Evidence Pack não contém `Exit Code:`: REJEITADO (INCOMPLETE_EVIDENCE)

8.2 Validation Command quality (AH-1, AH-2):
- Se o validation_command é source-inspection-only E não há waiver: BLOCKED (AH-7)
- Source-inspection pattern detectado por: ausência de import/subprocess/pytest/playwright + presença de `assert '...' in src`

8.3 Criteria checklist:
- Para cada critério numerado na AR ("1) ..., 2) ..."), o Testador MUST indicar em result.json se foi verificado ou não como parte do re-run.
---FIM DO ARQUIVO---

ARQUIVO A CRIAR (ÚNICO): docs/_canon/contratos/Testador Contract.md
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) Arquivo docs/_canon/contratos/Testador Contract.md existe. 2) Contém 'AH-1' a 'AH-7'. 3) Contém 'VERIFICADO' e 'REJEITADO'. 4) Contém '_reports/testador/'. 5) Contém 'hb verify'. 6) Contém 'result.json' com campos obrigatórios. 7) Contém seção '## 8. O que o Testador MUST verificar'.

## Validation Command (Contrato)
```
python -c "import pathlib; c=pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8'); required={'AH-1':'AH-1' in c,'AH-7':'AH-7' in c,'VERIFICADO':'VERIFICADO' in c,'REJEITADO':'REJEITADO' in c,'_reports/testador':'_reports/testador' in c,'hb verify':'hb verify' in c,'result.json':'result.json' in c,'consistency':'consistency' in c}; failed=[k for k,v in required.items() if not v]; print(f'FAIL: {failed}') if failed else print(f'PASS: Testador Contract OK — {len(required)} checks')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_018_gov_testador_contract.log`

## Riscos
- Este arquivo é novo — não existe colisão com arquivos existentes.
- O Dev Flow exige que mudanças em docs/_canon/contratos/** sejam via AR + bump. Esta tarefa É a AR. O bump (v1.0.8) é feito na task 020.
- Manter formatação exata dos code blocks (``` e ```) — importante para o hb_cli.py identificar padrões source-inspection.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; c=pathlib.Path('docs/_canon/contratos/Testador Contract.md').read_text(encoding='utf-8'); required={'AH-1':'AH-1' in c,'AH-7':'AH-7' in c,'VERIFICADO':'VERIFICADO' in c,'REJEITADO':'REJEITADO' in c,'_reports/testador':'_reports/testador' in c,'hb verify':'hb verify' in c,'result.json':'result.json' in c,'consistency':'consistency' in c}; failed=[k for k,v in required.items() if not v]; print(f'FAIL: {failed}') if failed else print(f'PASS: Testador Contract OK — {len(required)} checks')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_018_gov_testador_contract.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_018_b2e7523/result.json`
