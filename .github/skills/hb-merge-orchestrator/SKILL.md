---
name: hb-merge-orchestrator
description: >
  HB Track Merge & CI Orchestrator. USE FOR: abrir PRs, corrigir falhas de CI,
  analisar code reviews, criar/reparar GitHub Actions workflows, auditar paridade
  local↔staging↔produção e manter a branch main saudável.
  Implementa 5 fluxos: MERGE FLOW → CI FIX FLOW → CODE REVIEW FLOW →
  WORKFLOW REPAIR FLOW → SYNC/AUDIT FLOW.
  DO NOT USE FOR: criação/revisão de contratos CDD (usar hb-pipeline-orchestrator),
  execução de fases do ROADMAP (usar hb-roadmap-executor).
---

# HB Track — Merge & CI Orchestrator

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este skill é uma ponte operacional. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`, `merge-readiness.json`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este skill.

Este skill implementa os 5 fluxos operacionais do agente HandTracker.
**Todo fluxo começa com o PROTOCOLO DE BOOT abaixo — sem exceções.**

O humano é leigo em desenvolvimento — comunicar SEMPRE em português, linguagem de produto, nunca jargão técnico.

---

## PROTOCOLO DE BOOT (Obrigatório em todo fluxo)

Antes de qualquer ação:

- [ ] **B1** — Verificar autenticação GitHub:
  ```bash
  gh auth status
  ```
  Se `not logged in` → instruir o humano a rodar `gh auth login` ou exportar `GH_TOKEN`.

- [ ] **B2** — Verificar saúde dos gates:
  ```bash
  python3 -c "import json; h=json.load(open('_reports/pipeline_health.json')); print(f\"Health: {h['health_score']}/100 | Status: {h['overall_status']} | Blocking: {h['blocking_fails']}\")"
  ```
  Se `blocking_fails > 0` → informar o humano ANTES de abrir qualquer PR. Gates blocking
  já existentes vão bloquear o merge independentemente das mudanças do PR.

- [ ] **B3** — Verificar SESSION_HANDOFF.md:
  ```bash
  # Verificar se existe e ler as primeiras 10 linhas do front matter
  head -20 SESSION_HANDOFF.md 2>/dev/null || echo "Sem handoff ativo"
  ```
  Carregar contexto da sessão anterior se existir.

- [ ] **B4** — Verificar waivers ativos:
  ```bash
  python3 -c "import json; w=json.load(open('.contract_driven/waivers.json')); [print(f\"WAIVER: {x.get('gate_id','?')} — {x.get('reason','?')}\") for x in w.get('waivers',[])]" 2>/dev/null || echo "Sem waivers"
  ```
  Gates com waiver válido NÃO devem ser corrigidos — podem depender de artefatos ainda não criados.

---

## FLUXO 1 — MERGE FLOW (Abrir e mergear PR)

**Trigger:** humano pede para subir mudanças para main, criar PR, mergear branch.

### Checklist Merge Flow

- [ ] **M1** — Executar protocolo de boot (4 passos acima)

- [ ] **M2** — Verificar reviewability:
  ```bash
  git diff --name-only $(git merge-base origin/main HEAD)...HEAD | wc -l
  git log --oneline $(git merge-base origin/main HEAD)...HEAD | wc -l
  ```
  Se arquivos > 150 ou commits > 20 → **PARAR**. Informar humano: PR deve ser dividido
  antes de abrir (`split_required_when_exceeded: true` em `merge-readiness.json`).

- [ ] **M3** — Detectar governance_changed:
  ```bash
  git diff --name-only $(git merge-base origin/main HEAD)...HEAD \
    | grep -qE "^\.(contract_driven|contracts|docs/_canon)/" \
    && echo "GOVERNANCE_CHANGED=true" || echo "GOVERNANCE_CHANGED=false"
  ```
  Se `GOVERNANCE_CHANGED=true` → executar **M4-GOVERNANCE** antes de continuar.

- [ ] **M4-GOVERNANCE** (condicional — só se governance_changed=true):
  ```bash
  # Gate 1: survival suite
  CI=true python3 scripts/hb survival-suite

  # Gate 2: registry executor parity
  python -m pytest tests/pipeline_gates/test_gate_registry_parity.py -v

  # Gate 3: schema template skills parity
  python -m pytest tests/pipeline_gates/test_schema_template_parity_phase4.py -v

  # Gate 4: session handoff cross-validation
  python -m pytest tests/pipeline_gates/test_session_state_phase3.py -v
  ```
  Todos devem passar antes de abrir o PR. Se falhar → entrar em CI FIX FLOW para esse gate.

- [ ] **M5** — Executar preflight completo:
  ```bash
  python3 scripts/hb preflight
  ```
  Verificar `_reports/preflight/latest.json` → deve mostrar `overall_status: PASS`.
  Se FAIL → entrar em **CI FIX FLOW** para cada check falhando.

- [ ] **M6** — Rodar CI local completo:
  ```bash
  python3 scripts/hb ci --profile pr
  ```
  Deve retornar exitcode 0. Se não → **CI FIX FLOW**.

- [ ] **M7** — Verificar OpenAPI breaking changes (se contratos foram tocados):
  ```bash
  git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -q "openapi" && \
    oasdiff breaking contracts/openapi/openapi.yaml --fail-on ERR || echo "Sem mudanças OpenAPI"
  ```

- [ ] **M8** — Criar o PR:
  ```bash
  gh pr create \
    --title "<titulo conciso, máx 70 chars>" \
    --body "$(cat <<'EOF'
  ## O que muda
  - <bullet 1>
  - <bullet 2>

  ## Por que
  <contexto de produto>

  ## Como testar
  - [ ] <passo 1>
  - [ ] <passo 2>

  ## Gates locais
  - preflight: PASS
  - hb ci --profile pr: PASS
  EOF
  )" \
    --base main
  ```

- [ ] **M9** — Monitorar checks do PR:
  ```bash
  gh pr checks <NUMERO_PR> --watch
  ```
  Se algum check falhar → **CI FIX FLOW** imediato para o check específico.

- [ ] **M10** — Verificar que conversas do PR estão resolvidas:
  ```bash
  gh pr view <NUMERO_PR> --json reviewDecision,reviewRequests
  ```
  `require_conversation_resolution: true` — PR não faz merge com conversas pendentes.

- [ ] **M11** — Merge (após todos os checks PASS):
  ```bash
  gh pr merge <NUMERO_PR> --squash --delete-branch
  ```

- [ ] **M12** — Atualizar SESSION_HANDOFF.md com resultado do merge.

---

## PROTOCOLO DE ACESSO A LOGS (WSL — usar em todos os fluxos)

> ⚠️ O `gh` CLI falha intermitentemente no WSL com "error connecting to api.github.com"
> mesmo com token válido e internet funcionando. Isso é um bug de rede do WSL, não de auth.
> Sempre usar a sequência abaixo: tentar `gh` primeiro, cair no curl se falhar.

### Passo 1 — Tentar gh CLI
```bash
gh pr checks <NUMERO_PR> --watch
# Se retornar "error connecting to api.github.com" → ir para Passo 2
```

### Passo 2 — Fallback: curl direto com $GITHUB_TOKEN

```bash
# Obter estado dos checks e identificar o que falhou
SHA=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/pulls/<NUMERO_PR>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/commits/$SHA/check-runs?per_page=50" \
  | python3 -c "
import sys, json
for c in json.load(sys.stdin).get('check_runs', []):
    print(f\"{c.get('conclusion','?'):12} | {c['name']}\")
"
```

### Passo 3 — Obter run_id do job que falhou

```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/actions/runs?head_sha=$SHA&per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin).get('workflow_runs', []):
    print(f\"run_id={r['id']} | conclusion={r.get('conclusion','?')} | name={r['name']}\")
"
```

### Passo 4 — Baixar logs completos do run que falhou

```bash
RUN_ID=<id_do_run_que_falhou>
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/actions/runs/$RUN_ID/logs" \
  -L -o /tmp/ci_logs.zip \
  && unzip -o /tmp/ci_logs.zip -d /tmp/ci_logs/ \
  && grep -rn "ERROR\|FAIL\|Error\|assert\|Exception\|SECRET\|No such" /tmp/ci_logs/ \
  | grep -v "^Binary" | head -80
```

### Passo 5 — Ver log de um job específico (mais preciso)

```bash
JOB_ID=<id_do_check_run_que_falhou>  # vem do Passo 2
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/hbtrack/official/actions/jobs/$JOB_ID/logs" \
  -L | head -200
```

---

## FLUXO 2 — CI FIX FLOW (Corrigir falha de CI na causa raiz)

**Trigger:** check falhou no GitHub, preflight falhou localmente, CI bloqueando merge.

**REGRA ZERO**: Nunca inferir o comando de fix. Sempre fazer lookup em `merge-readiness.json`.

### Checklist CI Fix Flow

- [ ] **CF1** — Identificar o check exato e obter logs da falha:
  Usar o **PROTOCOLO DE ACESSO A LOGS** acima (tentativa `gh` → fallback curl).
  Extrair o nome exato do check falho (campo `context`, case-sensitive).
  Exemplos: `ci / Tests`, `Validate Contract Gates`, `Governance Enforcement (survival-suite)`.
  Baixar os logs completos (Passo 4 ou 5) antes de qualquer tentativa de fix.

- [ ] **CF2** — Lookup obrigatório no SSOT:
  ```bash
  python3 -c "
  import json
  m = json.load(open('merge-readiness.json'))
  ctx = '<CHECK_CONTEXT_AQUI>'
  c = next((x for x in m['checks'] if x['context'] == ctx), None)
  if c:
      print('local_equivalent:', c.get('local_equivalent', 'SEM_LOCAL_EQUIVALENT'))
      print('category:', c.get('category'))
  else:
      print('GAP_DE_PARIDADE: context nao encontrado em merge-readiness.json')
  "
  ```
  Se `GAP_DE_PARIDADE` → **PARAR**. Reportar ao humano. Não improvisar alternativa.

- [ ] **CF3** — Para checks `conditional`: verificar se governance_changed=true:
  ```bash
  git diff --name-only $(git merge-base origin/main HEAD)...HEAD \
    | grep -qE "^\.(contract_driven|contracts|docs/_canon)/" \
    && echo "governance_changed=true" || echo "governance_changed=false"
  ```
  Se `governance_changed=false` e o check é conditional → o check não deveria ter ativado.
  Investigar configuração do workflow antes de tentar corrigir.

- [ ] **CF4** — Carregar worker `pr_fix.prompt.md`:
  ```
  .contract_driven/agent_prompts/pr_fix.prompt.md
  ```
  Seguir o algoritmo de 5 passos do worker. NÃO reinventar o protocolo.

- [ ] **CF5** — Executar o `local_equivalent` EXATAMENTE como mapeado:
  ```bash
  # Exemplo para "ci / Tests":
  python3 scripts/hb ci --profile pr

  # Exemplo para "Validate Contract Gates":
  python3 scripts/hb validate --profile ci

  # Exemplo para "Governance Enforcement (survival-suite)":
  CI=true python3 scripts/hb survival-suite
  ```
  Usar o `local_equivalent` do lookup — sem modificações, sem flags extras.

- [ ] **CF6** — Diagnosticar falha na causa raiz:
  - Ler saída de erro completa
  - Identificar arquivo, linha, invariante violada
  - Aplicar correção mínima (não expandir escopo)
  - Re-executar `local_equivalent` até PASS

- [ ] **CF7** — Verificar que outros checks ainda passam:
  ```bash
  python3 scripts/hb ci --profile pr
  ```

- [ ] **CF8** — Push:
  ```bash
  git push
  ```
  O pre-push hook roda `python3 scripts/hb preflight` automaticamente.
  Se bloquear → diagnosticar output do hook (NUNCA usar `--no-verify`).

- [ ] **CF9** — Confirmar PASS no GitHub:
  ```bash
  gh pr checks <NUMERO_PR> --watch
  # Se gh falhar → usar Passo 1-2 do PROTOCOLO DE ACESSO A LOGS acima
  ```

### Tabela de CI Checks → Comandos Locais

| GitHub Check Context | Categoria | local_equivalent |
|---|---|---|
| `Validate Contract Gates` | required | `python3 scripts/hb validate --profile ci` |
| `Governance Tests` | required | `pytest tests/test_pipeline_governance.py` |
| `Architecture Drift Check` | required | `python3 scripts/audit/check_architecture_docs.py --json && pytest tests/pipeline_gates/test_architecture_drift.py` |
| `ci / Validate Contracts` | required | `python3 scripts/hb validate --profile precommit` |
| `ci / Tests` | required | `python3 scripts/hb ci --profile pr` |
| `ci / Frontend Build + Tests` | required | `cd frontend && npm ci --legacy-peer-deps && npx vitest run --reporter=verbose && npm run build` |
| `ci / Docker Build Check` | informational | não bloqueia merge |
| `Governance Enforcement (survival-suite)` | conditional | `CI=true python3 scripts/hb survival-suite` |
| `Paridade Registry × Executor` | conditional | `python -m pytest tests/pipeline_gates/test_gate_registry_parity.py -v` |
| `Paridade Schema × Template × Skills` | conditional | `python -m pytest tests/pipeline_gates/test_schema_template_parity_phase4.py -v` |
| `Validação Cruzada SESSION_HANDOFF ↔ session_start` | conditional | `python -m pytest tests/pipeline_gates/test_session_state_phase3.py -v` |

---

## FLUXO 3 — CODE REVIEW FLOW (Analisar e corrigir comentários de review)

**Trigger:** humano pede para responder/corrigir comentários de code review em PR.

### Checklist Code Review Flow

- [ ] **CR1** — Listar comentários do PR:
  ```bash
  gh pr view <NUMERO_PR> --json reviews,comments
  gh api repos/:owner/:repo/pulls/<NUMERO_PR>/comments
  ```
  Alternativamente, usar Playwright MCP para ver a UI do GitHub e ler comentários com contexto visual.

- [ ] **CR2** — Categorizar cada comentário segundo `pr_fix_resolution` do `merge-readiness.json`:

  | Categoria | Ação |
  |---|---|
  | `defect_real` — bug real no código | `fix_repository` — corrigir o código |
  | `governance_gap` — violação de governance | `fix_governance_artifact` — corrigir artefato canônico |
  | `evidence_missing` — evidência ausente | `reply_with_evidence` — gerar e anexar evidência |
  | `advisory_non_actionable` — sugestão não mandatória | `reply_without_scope_expansion` — responder sem mexer no código |

- [ ] **CR3** — Para cada comentário `defect_real`:
  - Identificar o arquivo e linha exatos
  - Verificar se é causa raiz (não sintoma)
  - Aplicar correção mínima
  - Rodar testes relacionados: `python3 scripts/hb ci --profile pr`

- [ ] **CR4** — Para cada comentário `governance_gap`:
  - Identificar qual gate ou regra foi violada
  - Corrigir o artefato canônico (em `contracts/`, `docs/_canon/`, `.contract_driven/`)
  - Se governance_changed=true → rodar os 4 gates condicionais (ver M4-GOVERNANCE)
  - Executar `python3 scripts/hb artifact <path>` para cada artefato modificado

- [ ] **CR5** — Para cada comentário `evidence_missing`:
  - Gerar a evidência solicitada (report, test output, gate log)
  - Responder ao comentário com evidência anexada

- [ ] **CR6** — Para cada comentário `advisory_non_actionable`:
  - Responder explicando por que não será implementado agora (ou agradecer)
  - Não expandir escopo do PR

- [ ] **CR7** — Após todas as correções, verificar que CI ainda passa:
  ```bash
  python3 scripts/hb ci --profile pr
  git push
  gh pr checks <NUMERO_PR> --watch
  ```

- [ ] **CR8** — Resolver conversas resolvidas:
  ```bash
  # Usar gh API ou Playwright para marcar conversas como resolvidas após correção
  gh api repos/:owner/:repo/pulls/<NUMERO_PR>/comments
  ```

---

## FLUXO 4 — WORKFLOW REPAIR FLOW (Criar/corrigir GitHub Actions)

**Trigger:** workflow do GitHub Actions falhando com erro de YAML/lógica, criar novo workflow.

### Checklist Workflow Repair Flow

- [ ] **WR1** — Para workflow existente com erro: obter logs completos:
  ```bash
  gh run list --limit 5
  gh run view <RUN_ID> --log-failed
  ```
  Alternativamente, usar Playwright MCP para ver a UI de Actions com logs interativos.

- [ ] **WR2** — Validar sintaxe dos workflows localmente:
  ```bash
  # actionlint valida todos os workflows de uma vez
  actionlint .github/workflows/*.yml
  ```
  Se actionlint não estiver instalado: `go install github.com/rhysd/actionlint/cmd/actionlint@latest`

- [ ] **WR3** — Para criação de novo workflow: verificar instrução de roteamento:
  ```
  .github/instructions/hb-roadmap-mode.instructions.md
  ```
  Workflows em `.github/workflows/` pertencem ao **Modo ROADMAP** — não ao CDD pipeline.
  Ler `ROADMAP.md` para contexto de fase e stack canônica.

- [ ] **WR4** — Corrigir o workflow identificando a causa raiz:
  - Erro de expressão: verificar sintaxe `${{ ... }}`
  - Permissão ausente: adicionar `permissions:` na seção correta
  - Secret não configurado: verificar GitHub repo secrets (Settings → Secrets)
  - Job dependency: verificar `needs:` e `if:` condicionais
  - Reusable workflow: verificar `workflow_call` e `secrets: inherit`

- [ ] **WR5** — Verificar reusable workflows:
  - `_reusable-ci.yml` é chamado por `ci.yml` — não editar o chamador sem testar o reusable
  - `contract-gates.yml` tem jobs condicionais por path — verificar `paths` no `on:` trigger

- [ ] **WR6** — Testar o workflow localmente (quando possível):
  ```bash
  # Rodar o equivalente local do job que falha (via merge-readiness.json)
  python3 scripts/hb ci --profile pr
  ```

- [ ] **WR7** — Commit e push:
  ```bash
  git add .github/workflows/<arquivo.yml>
  git status  # confirmar que só o workflow está staged
  git commit -m "fix(ci): <descrição da correção>"
  git push
  gh run watch  # monitorar a nova execução
  ```

---

## FLUXO 5 — SYNC/AUDIT FLOW (Paridade e saúde do ambiente)

**Trigger:** humano pede para verificar paridade local↔staging↔produção, auditar saúde do repositório.

### Checklist Sync/Audit Flow

- [ ] **SA1** — Verificar saúde completa dos gates:
  ```bash
  python3 scripts/hb preflight
  cat _reports/pipeline_health.json | python3 -m json.tool
  ```

- [ ] **SA2** — Verificar status de CI na branch atual:
  ```bash
  gh run list --branch $(git branch --show-current) --limit 5
  gh run view --log-failed  # do run mais recente se houver falha
  ```

- [ ] **SA3** — Verificar paridade de configurações:
  ```bash
  # Comparar variáveis de ambiente entre ambientes (sem expor secrets)
  cat infra/docker-compose.staging.yml | grep -E "^[[:space:]]+(image:|environment:)" | head -30
  cat infra/docker-compose.production.yml | grep -E "^[[:space:]]+(image:|environment:)" | head -30
  ```

- [ ] **SA4** — Verificar health dos endpoints (staging):
  ```bash
  # Usar Playwright MCP ou curl para verificar /health
  gh api repos/:owner/:repo/deployments --jq '.[:3][] | {env: .environment, ref: .ref, sha: .sha}'
  ```

- [ ] **SA5** — Verificar branch protection:
  ```bash
  gh api repos/:owner/:repo/rulesets/13901517
  ```
  Confirmar que `enforcement: active`, `bypass_actors: []`, checks required ainda ativos.

- [ ] **SA6** — Relatório de paridade para o humano:
  Apresentar um resumo conciso:
  - Health score dos gates (X/100)
  - Status de CI (últimas N runs)
  - Checks required: todos ativos
  - Diferenças detectadas staging vs produção (se houver)
  - Ações recomendadas (se houver)

---

## REGRAS DE OURO

1. **NUNCA usar `--no-verify` ou `--force-push`** — investigar sempre a causa raiz
2. **NUNCA inferir `local_equivalent`** — sempre lookup em `merge-readiness.json`
3. **NUNCA bypassar gates** — zero bypass_actors, zero exceções
4. **NUNCA expandir escopo** além do diff do PR para corrigir um check
5. **SEMPRE começar pelo Boot Protocol** (B1-B4) antes de qualquer fluxo
6. **SEMPRE verificar waivers** antes de tentar corrigir um gate
7. **SEMPRE atuar na causa raiz**, nunca em sintomas
8. **SEMPRE usar Playwright** para inspecionar logs de Actions quando o terminal não mostrar contexto suficiente
9. **SE detectar task CDD** (criação de contrato, schema, evento) → handoff para agente `HB Contract`
10. **Comunicação em português**, linguagem de produto, nunca jargão técnico
