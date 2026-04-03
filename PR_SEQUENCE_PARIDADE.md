# Sequência de Execução por PR — Paridade Local × CI

> **NON-SOVEREIGN** — Documento operacional de acompanhamento. Não é artefato canônico soberano. Não substitui `ROADMAP.md`, `SESSION_HANDOFF.md` nem os contratos em `contracts/`.

Baseline: `PLAN_EXEC_PARIDADE.md` (congelado 2026-04-03)
Regra: 1 PR por entregável. Nunca misturar. Caso encerrado apenas após PR-6 merged e verde.

---

## Status da sequência

| PR | Branch | Entregável | Status |
|---|---|---|---|
| #30 | `parity/enforcement-unification` | E1 — Ruleset unificado | ✅ MERGED |
| #32 | `parity/toolchain-manifest` | E2 — toolchain.json SSOT | ✅ MERGED |
| #33 | `parity/merge-readiness-manifest` | E3 — merge-readiness.json | ✅ MERGED |
| #35 | `parity/actionlint-invariants` | E4 — actionlint + invariantes | ✅ MERGED |
| #36 | `parity/canonical-executor` | E5 — reusable CI + Testcontainers | ✅ MERGED |
| #37 | `fix/hb-ci-parity-p1p2` | Fix E5 P1/P2 (code review) | ✅ MERGED |
| #38 | `parity/proof-of-parity` | E6 — Evidência final | ✅ MERGED |

---

## PR-1 — `parity/enforcement-unification` ✅ MERGED

**Entregável:** 1 — Unificação de enforcement server-side
**Branch:** `parity/enforcement-unification` (a partir de `main`)
**Tipo:** Infraestrutura GitHub (API) + documentação versionada

### Ações manuais (fora do PR — via API ou UI)

Executar na ordem exata. **Não** pular passos.

**Passo 1 — Exportar snapshots:**
```bash
mkdir -p _reports/enforcement

# Branch protection atual:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/branches/main/protection" \
  | tee _reports/enforcement/branch_protection_snapshot_20260403.json

# Ruleset atual:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | tee _reports/enforcement/ruleset_snapshot_20260403.json
```

**Passo 2 — Atualizar ruleset com 7 checks:**
```bash
curl -X PUT \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  -d '{
    "name": "contract-gates",
    "enforcement": "active",
    "conditions": {
      "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
    },
    "rules": [
      { "type": "deletion" },
      { "type": "non_fast_forward" },
      {
        "type": "pull_request",
        "parameters": {
          "required_approving_review_count": 0,
          "dismiss_stale_reviews_on_push": true,
          "require_code_owner_review": false,
          "require_last_push_approval": false,
          "required_review_thread_resolution": true,
          "allowed_merge_methods": ["merge", "squash", "rebase"]
        }
      },
      {
        "type": "required_status_checks",
        "parameters": {
          "strict_required_status_checks_policy": true,
          "do_not_enforce_on_create": false,
          "required_status_checks": [
            { "context": "Validate Contract Gates", "integration_id": 15368 },
            { "context": "Governance Tests", "integration_id": 15368 },
            { "context": "Architecture Drift Check", "integration_id": 15368 },
            { "context": "Adversarial Suite", "integration_id": 15368 },
            { "context": "CI / Validate Contracts", "integration_id": 15368 },
            { "context": "CI / Tests", "integration_id": 15368 },
            { "context": "CI / Frontend Build + Tests", "integration_id": 15368 }
          ]
        }
      }
    ],
    "bypass_actors": []
  }'
```

**Passo 3 — Validar ruleset (BLOQUEIO se falhar):**
```bash
# Deve retornar 7:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | jq '.rules[] | select(.type == "required_status_checks") | .parameters.required_status_checks | length'

# Deve retornar []:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | jq '.bypass_actors'
```

**Passo 4 — Remover branch protection legada (só após passo 3 OK):**
```bash
curl -X DELETE \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/branches/main/protection"
```

**Passo 5 — Confirmar remoção:**
```bash
# Deve retornar 404:
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/branches/main/protection"
```

### Arquivos no PR

| Arquivo | Ação | Descrição |
|---|---|---|
| `_reports/enforcement/branch_protection_snapshot_20260403.json` | criar | Snapshot pré-migração |
| `_reports/enforcement/ruleset_snapshot_20260403.json` | criar | Snapshot pré-migração |
| `.github/merge-policy.md` | criar | Lista oficial de required vs informativos (bootstrap para entregável 3) |

### Critério de merge ✅ CUMPRIDO

- [x] `GET /branches/main/protection` → 404
- [x] `GET /rulesets/13901517` → checks ativos, `bypass_actors: []`, `enforcement: "active"`
- [x] PR de teste trivial mostra checks como required na UI

---

## PR-2 — `parity/toolchain-manifest` ✅ MERGED

**Entregável:** 2 — Manifesto canônico de toolchain
**Branch:** `parity/toolchain-manifest` (a partir de `main`, após PR-1 merged)

### Arquivos no PR

| Arquivo | Ação | Mudança exata |
|---|---|---|
| `toolchain.json` | **criar** | Manifesto SSOT |
| `contracts/schemas/shared/toolchain.schema.json` | **criar** | JSON Schema de validação |
| `.nvmrc` | alterar | `v24.14.0` → `24` |
| `.github/workflows/ci.yml` | alterar | `node-version: "22"` → `"24"` (2 ocorrências) |
| `.github/workflows/context-efficiency-audit.yml` | alterar | python `3.11`→`3.12`, setup-python `@v4`→`@v5` |
| `.github/workflows/domain-completeness-audit.yml` | alterar | python `3.11`→`3.12`, setup-python/upload/download-artifact modernizados |
| `infra/docker-compose.yml` | alterar | `postgres:12`→`postgres:16`, porta `5433`→`5432` |

### Critério de merge ✅ CUMPRIDO

- [x] `toolchain.json` existe e passa contra o schema
- [x] Todos workflows usam `node-version: "24"` e `python-version: "3.12"`
- [x] `infra/docker-compose.yml` usa `postgres:16` na porta `5432:5432`
- [x] `.nvmrc` contém `24`
- [x] CI verde

---

## PR-3 — `parity/merge-readiness-manifest` ✅ MERGED

**Entregável:** 3 — Manifesto canônico de merge-readiness
**Branch:** `parity/merge-readiness-manifest` (a partir de `main`, após PR-2 merged)

### Arquivos no PR

| Arquivo | Ação | Descrição |
|---|---|---|
| `merge-readiness.json` | **criar** | Manifesto com taxonomia `required`/`informational`/`conditional` |
| `contracts/schemas/shared/merge-readiness.schema.json` | **criar** | Schema com enum `category` + validação condicional `allOf`/`if`/`then` |

### Critério de merge ✅ CUMPRIDO

- [x] `merge-readiness.json` valida contra o schema
- [x] 6 required + 4 conditional + 1 informational
- [x] Todo check `required` tem `local_equivalent`
- [x] CI verde

---

## PR-4 — `parity/actionlint-invariants` ✅ MERGED

**Entregável:** 4 — actionlint + políticas mínimas de integridade estrutural
**Branch:** `parity/actionlint-invariants` (a partir de `main`, após PR-3 merged)

### Arquivos no PR

| Arquivo | Ação | Mudança exata |
|---|---|---|
| `tests/invariants/__init__.py` | **criar** | Vazio (package marker) |
| `tests/invariants/test_toolchain_parity.py` | **criar** | Testes de drift de versão |
| `tests/invariants/test_merge_readiness_parity.py` | **criar** | Testes de estrutura + schema |
| `.github/workflows/contract-gates.yml` | alterar | Fix path validate_contracts.py + job `lint-workflows` |
| `scripts/hb` | alterar | `tests/invariants` na lista de suítes em `_preflight_step_test_suites` |

### Critério de merge ✅ CUMPRIDO

- [x] `actionlint` verde em CI
- [x] `contract-gates.yml` chama o path correto
- [x] `pytest tests/invariants/ -v` passa localmente
- [x] `hb preflight` inclui suíte de invariantes
- [x] CI verde

---

## PR-5 — `parity/canonical-executor` ✅ MERGED (#36)

**Entregável:** 5 — Executor canônico + reusable workflow + Testcontainers
**Branch:** `parity/canonical-executor` (a partir de `main`, após PR-4 merged)

### Arquivos no PR

| Arquivo | Ação | Mudança |
|---|---|---|
| `.github/workflows/_reusable-ci.yml` | **criar** | Reusable workflow que lê `toolchain.json` via `jq` |
| `.github/workflows/ci.yml` | alterar | Caller fino (19 linhas) |
| `.github/workflows/contract-gates.yml` | alterar | actionlint expandido para `_reusable-ci.yml` |
| `conftest.py` | alterar | Testcontainers híbrido Phase 1 (socket → containers → skip) + fix DB_PORT |
| `requirements-dev.txt` | alterar | `testcontainers[postgres,redis]==4.10.0` |
| `scripts/hb` | alterar | `_ci_test_env`, `cmd_ci()`, subcomando `ci --profile` |
| `tests/invariants/test_toolchain_parity.py` | alterar | Testes verificam delegação para reusable |
| `merge-readiness.json` | alterar | Contexts atualizados para `ci / *` (pós-reusable) |

### Impacto observado: nomes de check-runs

Após merge, os check-runs do CI mudaram de `CI / Validate Contracts` para `ci / Validate Contracts`
(prefixo = nome do job caller, não nome do workflow). Ruleset 13901517 **atualizado via API** antes do merge.

Contexts atuais no ruleset:
- `Validate Contract Gates`
- `Governance Tests`
- `Architecture Drift Check`
- `ci / Validate Contracts`
- `ci / Tests`
- `ci / Frontend Build + Tests`

### Critério de merge ✅ CUMPRIDO

- [x] `ci.yml` tem 19 linhas
- [x] `_reusable-ci.yml` lê versões de `toolchain.json` via `jq`
- [x] `scripts/hb ci --profile pr` funciona
- [x] Testes invariantes passam
- [x] Survival suite: 107/107 PASS
- [x] CI verde — 13/13 checks
- [x] Ruleset atualizado com novos context names
- [x] Code review P1/P2 — entregues via PR #37

---

## Fix E5 — `fix/hb-ci-parity-p1p2` ✅ MERGED (#37)

**Tipo:** Hotfix do code review do PR-5
**Branch:** `fix/hb-ci-parity-p1p2` (cherry-pick de `parity/canonical-executor@9a7cd731`)

### Mudanças

| Fix | Descrição |
|---|---|
| **P1** | `HB_RUN_SCHEMATHESIS` controlado por perfil: `pr`→`"0"`, `full`→`"1"` (paridade real com CI) |
| **P2** | `cmd_ci()` configura `core.hooksPath` antes de rodar pytest (alinha com o que CI faz) |

### Critério de merge ✅ CUMPRIDO

- [x] CI verde
- [x] Conversations resolvidas

---

## PR-6 — `parity/proof-of-parity` ✅ MERGED (#38)

**Entregável:** 6 — Prova operacional definitiva
**Branch:** `parity/proof-of-parity` (criada a partir de `main` @ 563ccdb6, após Fix E5 merged)

### Pré-requisitos

PR #37 (Fix E5) merged. Toda a infraestrutura de paridade na `main`.

### Protocolo

Este PR contém apenas a evidência gerada. Não contém mudanças de código.

**Passo 1 — Preflight local:**
```bash
python3 scripts/hb preflight
# Resultado esperado: verdict PASS
```

**Passo 2 — Registrar SHA:**
```bash
SHA=$(git rev-parse HEAD)
echo "SHA: $SHA"
cat _reports/preflight/latest.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('head_sha'), d.get('verdict'), d.get('timestamp'))"
```

**Passo 3 — Criar evidência de paridade:**
```bash
mkdir -p _reports/parity

SHA=$(git rev-parse HEAD)
python3 -c "
import json, datetime
evidence = {
    'sha': '$SHA',
    'date': datetime.date.today().isoformat(),
    'preflight_local': 'PASS',
    'preflight_evidence': '_reports/preflight/latest.json',
    'ci_checks': 'pending — will be filled after push',
    'parity_confirmed': False
}
print(json.dumps(evidence, indent=2))
" > _reports/parity/proof_$(date +%Y%m%d).json
```

**Passo 4 — Commit + push:**
```bash
git add _reports/parity/ _reports/preflight/latest.json
git commit -m "evidence: parity proof — preflight PASS at $SHA"
git push
```

**Passo 5 — Aguardar CI e registrar checks reais:**
```bash
SHA=$(git rev-parse HEAD)
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/commits/$SHA/check-runs" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin).get('check_runs', [])
print(json.dumps([{'name': r['name'], 'conclusion': r.get('conclusion')} for r in runs], indent=2))
" > _reports/parity/ci_checks_$(date +%Y%m%d).json
```

**Passo 6 — Atualizar evidence final e merge:**

Editar `_reports/parity/proof_*.json`:
- `parity_confirmed: true`
- `verdict: "PARIDADE_CONFIRMADA"`
- Incluir resultados dos checks

### Arquivos no PR

| Arquivo | Ação |
|---|---|
| `_reports/parity/proof_20260403.json` | criar |
| `_reports/parity/ci_checks_20260403.json` | criar |
| `_reports/preflight/latest.json` | atualizar (gerado pelo preflight) |

### Critério de merge ✅ CUMPRIDO

- [x] `hb preflight` → PASS com evidence
- [x] `git push` aceito pelo pre-push hook
- [x] 6/6 required checks verdes no GitHub para o mesmo SHA
- [x] Evidence registrada em `_reports/parity/`
- [x] Nenhum check informational/conditional vermelho

---

## Resumo visual

```
PR-1  parity/enforcement-unification    → E1 (API + docs)              ✅ #30
  ↓
PR-2  parity/toolchain-manifest         → E2 (manifesto + versões)     ✅ #32
  ↓
PR-3  parity/merge-readiness-manifest   → E3 (manifesto de merge)      ✅ #33
  ↓
PR-4  parity/actionlint-invariants      → E4 (lint + testes de drift)  ✅ #35
  ↓
PR-5  parity/canonical-executor         → E5 (reusable + testcontainers)✅ #36
  ↓
Fix   fix/hb-ci-parity-p1p2            → Fix P1/P2 do code review E5  ✅ #37
  ↓
PR-6  parity/proof-of-parity           → E6 (evidência final)          ✅ #38
```

### Regras de execução

1. **1 PR por entregável. Nunca misturar.**
2. Cada PR é mergeado para `main` antes de iniciar o próximo.
3. Se um PR quebrar CI, corrigir no mesmo PR antes de avançar.
4. O caso **NÃO** está encerrado até PR-6 merged com evidência verde.
5. Critério final: mesmo SHA → PASS local → 6 required checks verdes GitHub.
