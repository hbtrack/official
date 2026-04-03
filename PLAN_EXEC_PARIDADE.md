# Plano Executivo de Paridade Local × GitHub

Data: 2026-04-02 | Última atualização: 2026-04-03
Base: diagnóstico validado ao vivo em `PLAN_PARIEDADE.md`
Escopo: 6 entregáveis obrigatórios, sequenciais, com critério de aceite binário.
Revisão: ajustes incorporados após revisão humana de 2026-04-03.
Baseline: congelado em 2026-04-03 — SHA256 `424ba943be2f...` (1340 linhas pré-freeze).
Execução: 1 PR por entregável; caso encerrado somente após Entregável 6 verde.

> **Estado em 2026-04-03:** Entregável 1 **merged** — PR #31 merged em `main` às 04:18 UTC (merge commit `eb15c1f6`). Entregável 2 **merged** — PR #32 merged em `main` (squash commit `a83fd57b`). Entregáveis 3–6 pendentes.

---

## Entregável 1 — Unificação de enforcement server-side ✅ CONCLUÍDO (PR #31)

### Problema que resolve

Hoje existem **dois mecanismos ativos em paralelo** na `main`:
- Branch protection legada: 7 required checks, `enforce_admins: false` (admin pode bypassar).
- Ruleset `contract-gates`: 5 required checks, `bypass_actors: []` (ninguém pode bypassar).

A dualidade cria ambiguidade operacional: qual é a fonte de verdade? Admin pode ou não pode bypassar? A resposta depende de qual camada intercepta primeiro.

### Dependências

Nenhuma. Este é o primeiro entregável.

### Arquivos a alterar

Nenhum arquivo versionado. Ação exclusivamente via GitHub Settings API ou UI.

### Mudanças exatas

> **Ordem de execução segura**: exportar estado → atualizar ruleset → validar ruleset → remover branch protection. Nunca remover antes de validar. Objetivo: janela de configuração incorreta = zero.

**1. Exportar e registrar o estado atual (snapshot de segurança):**

```bash
# Salvar branch protection legada:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/branches/main/protection" \
  | tee _reports/enforcement/branch_protection_snapshot_$(date +%Y%m%d).json

# Salvar ruleset atual:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | tee _reports/enforcement/ruleset_snapshot_$(date +%Y%m%d).json
```

> Esses snapshots permitem rollback manual se algo der errado nos passos seguintes.

**2. Atualizar o ruleset `contract-gates` (ID 13901517) para cobrir todos os checks reais:**

Adicionar os checks ausentes. O ruleset atual tinha 5; o alvo final são 7 quando o job `Adversarial Suite` existir (PR-4). Estado pós PR #31:

| Check | Workflow | Status pós PR #31 |
|---|---|---|
| `Validate Contract Gates` | contract-gates.yml | ✅ Presente |
| `Governance Tests` | contract-gates.yml | ✅ Presente |
| `Architecture Drift Check` | contract-gates.yml | ✅ Presente |
| `CI / Validate Contracts` | ci.yml | ✅ Presente |
| `CI / Tests` | ci.yml | ✅ Presente |
| `CI / Frontend Build + Tests` | ci.yml | ✅ Adicionado em PR #31 |
| `Adversarial Suite` | contract-gates.yml | ⏳ Aguarda criação do job (PR-4) — removido do ruleset para não bloquear PRs |

> **Decisão de design (2026-04-03):** `Adversarial Suite` foi inicialmente adicionado ao ruleset mas removido em seguida após review do Codex bot (P1): o job não existe em nenhum workflow — required check sem job correspondente bloqueia PRs permanentemente. Será re-adicionado no PR-4 após criação do job em `contract-gates.yml`. Ruleset fechou em **6 required checks** (não 7).

```bash
# Via API — PUT para atualizar o ruleset com os 7 checks:
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

**3. Validar que o ruleset novo está correto (antes de remover a proteção legada):**

```bash
# Confirmar que o ruleset agora tem 7 checks:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | jq '.rules[] | select(.type == "required_status_checks") | .parameters.required_status_checks | length'
# Deve retornar: 7

# Confirmar bypass_actors vazio:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/rulesets/13901517" \
  | jq '.bypass_actors'
# Deve retornar: []
```

> **BLOQUEIO**: Se a validação acima falhar, NÃO prosseguir para o passo 4. Corrigir o ruleset primeiro.

**4. Remover branch protection legada da `main` (só após validação do passo 3):**

```bash
curl -X DELETE \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/branches/main/protection"
```

**5. Documentar quais checks são required vs informativos:**

Criar `.github/merge-policy.md` com a lista oficial (entregável 3 formaliza isso como manifesto versionado; aqui é o bootstrap mínimo).

### Critério de aceite

- [x] `GET /repos/hbtrack/official/branches/main/protection` retorna `404` (branch protection removida). ✅ confirmado 2026-04-03
- [x] `GET /repos/hbtrack/official/rulesets/13901517` retorna 6 required checks (7 após PR-4), `bypass_actors: []`, `enforcement: "active"`. ✅ confirmado 2026-04-03
- [x] PR de teste: PR #31 mergeado em `main` às 04:18 UTC — required checks satisfeitos via CI. ✅ 2026-04-03

### Evidências geradas

| Arquivo | Conteúdo |
|---|---|
| `_reports/enforcement/branch_protection_snapshot_20260403.json` | Estado da branch protection antes da remoção |
| `_reports/enforcement/ruleset_snapshot_20260403.json` | Estado do ruleset antes do update |
| `_reports/enforcement/ruleset_snapshot_after.json` | Estado do ruleset após update (6 checks) |
| `_reports/enforcement/ruleset_update_response.json` | Resposta da API no PUT |
| `_reports/enforcement/ruleset_fix_adversarial.json` | Evidência da remoção do `Adversarial Suite` |
| `_reports/enforcement/branch_protection_delete_response.json` | Evidência do DELETE (body vazio = 204) |
| `.github/merge-policy.md` | SSOT canônico de checks obrigatórios × informativos × condicionais |

### Risco eliminado

- Admin bypass via `enforce_admins: false`. ✅
- Ambiguidade operacional entre dois mecanismos de enforcement. ✅
- `CI / Frontend Build + Tests` passando sem ser required. ✅
- `Adversarial Suite` como required check fantasma (bloqueio permanente de PRs). ✅ removido — PR-4 cria o job.

### Validação de paridade

Não impacta paridade local diretamente — enforcement é server-side. Mas elimina a possibilidade de merge sem checks verdes, o que é o pré-requisito para que qualquer paridade local tenha consequência real.

---

## Entregável 2 — Manifesto canônico de toolchain

### Problema que resolve

Versões estão espalhadas em 6+ arquivos sem SSOT:

| Dimensão | Fontes conflitantes |
|---|---|
| Node | `.nvmrc` → `v24.14.0`, `ci.yml` → `"22"`, `contract-gates.yml` → `"24"` |
| Python | `ci.yml` → `"3.12"`, audits → `"3.11"`, sem `.python-version` |
| Postgres | `docker-compose` → `12`, CI → `16` |
| Postgres porta | `docker-compose` → `5433`, CI/conftest/hb → `5432` |

### Dependências

Entregável 1 (enforcement unificado).

### Arquivos a criar

**`toolchain.json`** (raiz do repositório):

```json
{
  "$schema": "./contracts/schemas/shared/toolchain.schema.json",
  "version": "1.0.0",
  "updated": "2026-04-02",
  "runtimes": {
    "node": "24",
    "python": "3.12"
  },
  "services": {
    "postgres": {
      "image": "postgres:16",
      "port": 5432,
      "test_db": "hbtrack_test",
      "test_user": "hbtrack",
      "test_password": "testpassword"
    },
    "redis": {
      "image": "redis:7-alpine",
      "port": 6379
    }
  },
  "tools": {
    "oasdiff": "1.12.3"
  }
}
```

**`contracts/schemas/shared/toolchain.schema.json`** (validação formal):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HB Track Toolchain Manifest",
  "type": "object",
  "required": ["version", "runtimes", "services", "tools"],
  "properties": {
    "version": { "type": "string" },
    "updated": { "type": "string", "format": "date" },
    "runtimes": {
      "type": "object",
      "required": ["node", "python"],
      "properties": {
        "node": { "type": "string" },
        "python": { "type": "string" }
      }
    },
    "services": {
      "type": "object",
      "required": ["postgres", "redis"],
      "properties": {
        "postgres": {
          "type": "object",
          "required": ["image", "port", "test_db", "test_user", "test_password"]
        },
        "redis": {
          "type": "object",
          "required": ["image", "port"]
        }
      }
    },
    "tools": {
      "type": "object",
      "required": ["oasdiff"]
    }
  }
}
```

### Arquivos a alterar

**1. `.nvmrc`** — alinhar com manifesto:

```
# Antes:
v24.14.0

# Depois — ler de toolchain.json não é possível em .nvmrc,
# mas o valor deve ser consistente:
24
```

> Nota: `.nvmrc` não suporta leitura dinâmica. O teste de invariante (criado no entregável 4) garante alinhamento.

**2. `.github/workflows/ci.yml`** — 2 mudanças de Node version:

```yaml
# Linha 39 — Antes:
          node-version: "22"
# Depois:
          node-version: "24"

# Linha 158 — Antes:
          node-version: "22"
# Depois:
          node-version: "24"
```

**3. `.github/workflows/context-efficiency-audit.yml`** — Python version:

```yaml
# Antes:
          python-version: "3.11"
# Depois:
          python-version: "3.12"
```

**4. `.github/workflows/domain-completeness-audit.yml`** — Python version:

```yaml
# Antes:
          python-version: "3.11"
# Depois:
          python-version: "3.12"
```

**5. `infra/docker-compose.yml`** — Postgres version e porta:

```yaml
# Antes:
  postgres:
    image: postgres:12
    # ...
    ports:
      - "5433:5432"

# Depois:
  postgres:
    image: postgres:16
    # ...
    ports:
      - "5432:5432"
```

> Nota: a mudança de porta para `5432:5432` alinha com `conftest.py`, `hb preflight` e CI. Se houver outro serviço Postgres na máquina do dev, o teste de invariante avisa.

**6. `infra/docker-compose.yml`** — credenciais de teste para Postgres:

```yaml
# Antes:
    environment:
      POSTGRES_DB: hb_track_dev
      POSTGRES_USER: hbtrack_dev
      POSTGRES_PASSWORD: hbtrack_dev_pwd

# Depois — banco de dev continua, mas adicionar profile de teste:
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-hb_track_dev}
      POSTGRES_USER: ${POSTGRES_USER:-hbtrack_dev}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-hbtrack_dev_pwd}
```

> A separação dev/test será completa quando Testcontainers entrar (entregável 5). Aqui o mínimo é alinhar versão e porta.

### Critério de aceite

- [ ] `toolchain.json` existe na raiz, passa validação contra `toolchain.schema.json`.
- [ ] `grep -rn 'node-version' .github/workflows/` retorna apenas `"24"` em todos os workflows.
- [ ] `grep -rn 'python-version' .github/workflows/` retorna apenas `"3.12"` em todos os workflows.
- [ ] `infra/docker-compose.yml` usa `postgres:16` na porta `5432:5432`.
- [ ] `.nvmrc` contém `24`.

### Risco eliminado

- Node 22 vs 24 vs v24.14.0 — **3 valores → 1**.
- Python 3.11 vs 3.12 — **2 valores → 1**.
- Postgres 12 vs 16 — **2 valores → 1**.
- Porta 5433 vs 5432 — **2 valores → 1**.

### Regra de autoridade do manifesto

`toolchain.json` é SSOT. **Nenhum** arquivo pode declarar versão de runtime, serviço ou ferramenta fora dele.

**Consumidores obrigatórios** (devem ler ou alinhar com o manifesto):

| Consumidor | Como consome |
|---|---|
| `.github/workflows/*.yml` | Hardcoda o mesmo valor (validado por `test_toolchain_parity.py`) |
| `.nvmrc` | Hardcoda o mesmo valor de `runtimes.node` |
| `infra/docker-compose.yml` | Usa mesma image e porta de `services.postgres` e `services.redis` |
| `scripts/hb` (`_ci_test_env`) | Lê `toolchain.json` em runtime (entregável 5) |
| `scripts/bootstrap/dev_contract_env.sh` | Lê `toolchain.json` para oasdiff version |
| `conftest.py` | Lê `toolchain.json` para Testcontainers config (entregável 5) |
| `.github/workflows/_reusable-ci.yml` | Lê `toolchain.json` via `jq` (entregável 5) |

**Proibição explícita**: qualquer script, workflow ou arquivo de configuração que instale ou configure Node, Python, Postgres, Redis, ou oasdiff **não pode** declarar versão inline. Deve consumir `toolchain.json` diretamente (via `jq`, `json.loads`, ou equivalente) **ou** ter o valor validado pelo teste de invariante `test_toolchain_parity.py`.

> Enforcement: o teste de invariante (entregável 4) garante que essa regra é verificada automaticamente em cada `hb preflight` e em CI.

### Validação de paridade

```bash
# Local:
node --version   # deve começar com v24
python3 --version  # deve ser 3.12.x
docker compose -f infra/docker-compose.yml up -d postgres
pg_isready -h localhost -p 5432  # deve responder OK
```

Comparar com CI: `grep` nos workflows confirma que os valores são idênticos ao manifesto.

---

## Entregável 3 — Manifesto canônico de merge-readiness

### Problema que resolve

Não existe declaração formal de quais checks bloqueiam merge, quais são informativos, e qual executor local reproduz cada um. O ruleset (entregável 1) configura isso no GitHub, mas sem rastreabilidade versionada. Se alguém alterar o ruleset pela UI, não há como detectar drift.

### Dependências

Entregável 1 (ruleset unificado) e entregável 2 (toolchain resolvido).

### Arquivos a criar

**`merge-readiness.json`** (raiz do repositório):

```json
{
  "$schema": "./contracts/schemas/shared/merge-readiness.schema.json",
  "version": "1.0.0",
  "updated": "2026-04-02",
  "target_branch": "main",
  "ruleset_name": "contract-gates",
  "ruleset_id": 13901517,
  "checks": [
    {
      "context": "Validate Contract Gates",
      "workflow": "contract-gates.yml",
      "job": "validate-contracts",
      "category": "required",
      "local_equivalent": "python3 scripts/hb preflight (STEP 3)"
    },
    {
      "context": "Governance Tests",
      "workflow": "contract-gates.yml",
      "job": "governance-tests",
      "category": "required",
      "local_equivalent": "pytest tests/test_pipeline_governance.py"
    },
    {
      "context": "Architecture Drift Check",
      "workflow": "contract-gates.yml",
      "job": "architecture-drift-check",
      "category": "required",
      "local_equivalent": "python3 scripts/audit/check_architecture_docs.py --json && pytest tests/pipeline_gates/test_architecture_drift.py"
    },
    {
      "context": "Adversarial Suite",
      "workflow": "contract-gates.yml",
      "job": "adversarial-suite",
      "category": "required",
      "local_equivalent": "pytest tests/adversarial -q"
    },
    {
      "context": "CI / Validate Contracts",
      "workflow": "ci.yml",
      "job": "validate",
      "category": "required",
      "local_equivalent": "python3 scripts/hb preflight (STEP 3)"
    },
    {
      "context": "CI / Tests",
      "workflow": "ci.yml",
      "job": "test",
      "category": "required",
      "local_equivalent": "python3 scripts/hb preflight (STEP 4)"
    },
    {
      "context": "CI / Frontend Build + Tests",
      "workflow": "ci.yml",
      "job": "build-frontend",
      "category": "required",
      "local_equivalent": "python3 scripts/hb preflight (STEP 6)"
    },
    {
      "context": "Docker Build Check",
      "workflow": "ci.yml",
      "job": "build",
      "category": "informational",
      "reason": "Valida Dockerfile mas não bloqueia merge"
    },
    {
      "context": "Governance Enforcement (survival-suite)",
      "workflow": "contract-gates.yml",
      "job": "governance-enforcement",
      "category": "conditional",
      "condition": "governance_changed == true",
      "reason": "Condicional — só roda em mudanças de governança"
    },
    {
      "context": "Paridade Registry × Executor",
      "workflow": "contract-gates.yml",
      "job": "registry-executor-parity",
      "category": "conditional",
      "condition": "governance_changed == true",
      "reason": "Condicional"
    },
    {
      "context": "Paridade Schema × Template × Skills",
      "workflow": "contract-gates.yml",
      "job": "schema-template-skills-parity",
      "category": "conditional",
      "condition": "governance_changed == true",
      "reason": "Condicional"
    },
    {
      "context": "Validação Cruzada SESSION_HANDOFF ↔ session_start",
      "workflow": "contract-gates.yml",
      "job": "session-handoff-crossval",
      "category": "conditional",
      "condition": "governance_changed == true",
      "reason": "Condicional"
    }
  ],
  "enforcement": {
    "require_pr": true,
    "require_conversation_resolution": true,
    "require_up_to_date": true,
    "block_force_push": true,
    "block_deletion": true,
    "bypass_actors": []
  },
  "local_executor": {
    "command": "python3 scripts/hb preflight",
    "evidence_path": "_reports/preflight/latest.json",
    "pre_push_hook": "scripts/git-hooks/pre-push"
  }
}
```

**`contracts/schemas/shared/merge-readiness.schema.json`**:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HB Track Merge-Readiness Manifest",
  "type": "object",
  "required": ["version", "target_branch", "ruleset_name", "checks", "enforcement", "local_executor"],
  "properties": {
    "version": { "type": "string" },
    "target_branch": { "type": "string" },
    "ruleset_name": { "type": "string" },
    "ruleset_id": { "type": "integer" },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["context", "workflow", "job", "category"],
        "properties": {
          "context": { "type": "string" },
          "workflow": { "type": "string" },
          "job": { "type": "string" },
          "category": {
            "type": "string",
            "enum": ["required", "informational", "conditional"],
            "description": "required = bloqueia merge no ruleset. informational = roda mas não bloqueia. conditional = roda apenas quando condição de path-filter é true."
          },
          "local_equivalent": {
            "type": "string",
            "description": "Obrigatório para category=required. Comando local que reproduz este check."
          },
          "condition": {
            "type": "string",
            "description": "Obrigatório para category=conditional. Expressão que ativa o check."
          },
          "reason": {
            "type": "string",
            "description": "Obrigatório para category=informational e conditional. Justificativa de não ser required."
          }
        },
        "allOf": [
          {
            "if": { "properties": { "category": { "const": "required" } } },
            "then": { "required": ["local_equivalent"] }
          },
          {
            "if": { "properties": { "category": { "const": "conditional" } } },
            "then": { "required": ["condition", "reason"] }
          },
          {
            "if": { "properties": { "category": { "const": "informational" } } },
            "then": { "required": ["reason"] }
          }
        ]
      }
    },
    "enforcement": {
      "type": "object",
      "required": ["require_pr", "require_conversation_resolution", "block_force_push", "bypass_actors"]
    },
    "local_executor": {
      "type": "object",
      "required": ["command", "evidence_path"]
    }
  }
}
```

> **Taxonomia formal**: o campo `category` é um enum restrito. Cada categoria exige campos diferentes (`local_equivalent` para required, `condition`+`reason` para conditional, `reason` para informational). O schema valida isso via `allOf`/`if`/`then`.

### Critério de aceite

- [ ] `merge-readiness.json` existe na raiz, passa validação contra o schema (incluindo `allOf`/`if`/`then`).
- [ ] Todo check com `"category": "required"` tem `local_equivalent` preenchido.
- [ ] Todo check com `"category": "conditional"` tem `condition` e `reason` preenchidos.
- [ ] A lista de checks com `"category": "required"` tem exatamente os mesmos contexts que o ruleset retornado pela API.
- [ ] `jq '[.checks[] | select(.category == "required")] | length' merge-readiness.json` retorna `7`.

### Risco eliminado

- Drift silencioso entre ruleset no GitHub e expectativa do time.
- Impossibilidade de auditar a política de merge sem acesso admin ao GitHub.
- Falta de mapeamento entre check CI e comando local equivalente.

### Validação de paridade

```bash
# Script de verificação (criado no entregável 4):
# Compara merge-readiness.json com o ruleset real via API.
# Se divergir, falha.
```

---

## Entregável 4 — actionlint + políticas mínimas de integridade estrutural

### Problema que resolve

Hoje não existe nenhuma proteção contra:
- Erro de sintaxe/semântica em workflows (ex: `scripts/validate_contracts.py` em `contract-gates.yml` — path errado, deveria ser `scripts/contracts/validate/validate_contracts.py`).
- Drift de versão entre `toolchain.json` e os workflows/docker-compose/bootstrap.
- Drift entre `merge-readiness.json` e o ruleset real no GitHub.

### Dependências

Entregáveis 2 e 3 (manifestos existem).

### Arquivos a criar

**`tests/invariants/test_toolchain_parity.py`**:

```python
"""
Testa que todas as fontes de versão consomem o manifesto toolchain.json.
Falha se qualquer arquivo usar versão diferente da canônica.
"""
import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = json.loads((ROOT / "toolchain.json").read_text())


def _grep_yaml_value(filepath: Path, key: str) -> list[str]:
    """Extrai valores associados a uma chave em YAML."""
    content = filepath.read_text()
    return re.findall(rf'{key}:\s*["\']?(\S+?)["\']?\s*$', content, re.MULTILINE)


class TestNodeVersion:
    expected = TOOLCHAIN["runtimes"]["node"]

    def test_nvmrc(self):
        nvmrc = (ROOT / ".nvmrc").read_text().strip()
        assert nvmrc == self.expected, f".nvmrc={nvmrc}, expected={self.expected}"

    @pytest.mark.parametrize("wf", list((ROOT / ".github/workflows").glob("*.yml")))
    def test_workflow_node_version(self, wf):
        versions = _grep_yaml_value(wf, "node-version")
        for v in versions:
            assert v == self.expected, f"{wf.name} has node-version={v}, expected={self.expected}"


class TestPythonVersion:
    expected = TOOLCHAIN["runtimes"]["python"]

    @pytest.mark.parametrize("wf", list((ROOT / ".github/workflows").glob("*.yml")))
    def test_workflow_python_version(self, wf):
        versions = _grep_yaml_value(wf, "python-version")
        for v in versions:
            assert v == self.expected, f"{wf.name} has python-version={v}, expected={self.expected}"


class TestPostgresVersion:
    pg = TOOLCHAIN["services"]["postgres"]

    def test_docker_compose(self):
        dc = (ROOT / "infra/docker-compose.yml").read_text()
        assert self.pg["image"] in dc, f"docker-compose missing {self.pg['image']}"

    def test_ci_services(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        assert self.pg["image"] in ci, f"ci.yml missing {self.pg['image']}"

    def test_port_in_docker_compose(self):
        dc = (ROOT / "infra/docker-compose.yml").read_text()
        expected_port = str(self.pg["port"])
        assert f'"{expected_port}:{expected_port}"' in dc or f"'{expected_port}:{expected_port}'" in dc


class TestOasdiffVersion:
    expected = TOOLCHAIN["tools"]["oasdiff"]

    @pytest.mark.parametrize("wf", list((ROOT / ".github/workflows").glob("*.yml")))
    def test_workflow_oasdiff_version(self, wf):
        content = wf.read_text()
        if "oasdiff" not in content:
            pytest.skip(f"{wf.name} does not use oasdiff")
        versions = re.findall(r'oasdiff[/_](\d+\.\d+\.\d+)', content)
        for v in versions:
            assert v == self.expected, f"{wf.name} has oasdiff={v}, expected={self.expected}"
```

**`tests/invariants/test_merge_readiness_parity.py`**:

```python
"""
Testa que merge-readiness.json está em sincronia com as definições locais.
A verificação contra o ruleset real no GitHub é feita por um script separado
(requer token — não roda em todo pytest local).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_merge_readiness_schema():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    schema = json.loads(
        (ROOT / "contracts/schemas/shared/merge-readiness.schema.json").read_text()
    )
    import jsonschema
    jsonschema.validate(manifest, schema)


def test_toolchain_schema():
    manifest = json.loads((ROOT / "toolchain.json").read_text())
    schema = json.loads(
        (ROOT / "contracts/schemas/shared/toolchain.schema.json").read_text()
    )
    import jsonschema
    jsonschema.validate(manifest, schema)


def test_required_checks_have_local_equivalent():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    for check in manifest["checks"]:
        if check["category"] == "required":
            assert check.get("local_equivalent"), (
                f"Check '{check['context']}' é required mas não tem local_equivalent"
            )


def test_conditional_checks_have_condition():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    for check in manifest["checks"]:
        if check["category"] == "conditional":
            assert check.get("condition"), (
                f"Check '{check['context']}' é conditional mas não tem condition"
            )
            assert check.get("reason"), (
                f"Check '{check['context']}' é conditional mas não tem reason"
            )


def test_all_required_check_workflows_exist():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    wf_dir = ROOT / ".github/workflows"
    for check in manifest["checks"]:
        wf = wf_dir / check["workflow"]
        assert wf.exists(), f"Workflow '{check['workflow']}' referenciado mas não existe"


def test_category_values_are_valid():
    manifest = json.loads((ROOT / "merge-readiness.json").read_text())
    valid = {"required", "informational", "conditional"}
    for check in manifest["checks"]:
        assert check["category"] in valid, (
            f"Check '{check['context']}' tem category='{check['category']}', válidos: {valid}"
        )
```

### Arquivos a alterar

**1. Corrigir `contract-gates.yml` — path errado do validate_contracts:**

```yaml
# Linha ~110 — Antes:
          python3 scripts/validate_contracts.py
# Depois:
          python3 scripts/contracts/validate/validate_contracts.py
```

**2. Adicionar actionlint ao CI — novo job em `contract-gates.yml`:**

```yaml
  # Adicionar como primeiro job (sem dependências):
  lint-workflows:
    name: Lint Workflows (actionlint)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run actionlint
        uses: rhysd/actionlint@v1
```

**3. Adicionar testes de invariante ao `hb preflight` — alterar `scripts/hb`:**

Na seção `_preflight_step_test_suites`, adicionar `tests/invariants` como uma das suítes:

```python
# Adicionar à lista de suítes em _preflight_step_test_suites:
("invariants", [str(self.root / "tests/invariants"), "-v"]),
```

**4. Adicionar actionlint ao pre-commit ou pre-push local:**

Instalar `actionlint` no bootstrap e executar em `hb preflight` STEP 1 (toolchain):

```python
# No _preflight_step_toolchain, adicionar verificação:
# actionlint (se disponível)
if shutil.which("actionlint"):
    result = subprocess.run(
        ["actionlint"],
        capture_output=True, text=True, cwd=self.root,
    )
    if result.returncode != 0:
        print(f"❌ actionlint found issues:\n{result.stdout}{result.stderr}")
        return False
```

### Critério de aceite

- [ ] `actionlint` roda em CI (job `lint-workflows` verde).
- [ ] `contract-gates.yml` chama path correto (`scripts/contracts/validate/validate_contracts.py`).
- [ ] `pytest tests/invariants/ -v` passa localmente.
- [ ] Se alguém mudar `node-version: "22"` em qualquer workflow, `test_toolchain_parity.py` falha.
- [ ] `hb preflight` inclui suíte de invariantes.

### Risco eliminado

- Workflow com sintaxe/semântica inválida passa para `main` (path errado já existe hoje).
- Drift de versão entre manifesto e consumidores passa despercebido.
- Manifesto de merge-readiness diverge dos workflows reais.

### Validação de paridade

```bash
# Rodar localmente:
pytest tests/invariants/ -v

# Rodar no GitHub:
# Job lint-workflows + testes de invariante incluídos nas suítes.
# Se ambos passam, as fontes de versão estão alinhadas.
```

---

## Entregável 5 — Executor canônico + reusable workflow + Testcontainers

### Problema que resolve

Hoje os workflows repetem inline toda a lógica de bootstrap (pip install, npm ci, oasdiff download, etc.) e os testes dependem de `services:` no GitHub e `docker-compose` local — dois mecanismos diferentes para subir Postgres/Redis.

### Dependências

Entregáveis 2, 3 e 4 (manifesto de toolchain, merge-readiness e testes de invariante existem).

### Arquivos a criar

**1. `.github/workflows/_reusable-ci.yml`** — reusable workflow:

```yaml
name: Reusable CI

on:
  workflow_call:
    inputs:
      profile:
        description: "Executor profile: pr | contract-gates | full"
        required: true
        type: string

jobs:
  setup-and-run:
    name: "CI [${{ inputs.profile }}]"
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Read toolchain manifest
        id: toolchain
        run: |
          echo "node=$(jq -r .runtimes.node toolchain.json)" >> "$GITHUB_OUTPUT"
          echo "python=$(jq -r .runtimes.python toolchain.json)" >> "$GITHUB_OUTPUT"

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "${{ steps.toolchain.outputs.node }}"
          cache: npm

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "${{ steps.toolchain.outputs.python }}"
          cache: pip

      - name: Install dependencies
        run: |
          pip install -r requirements.txt -r requirements-dev.txt -r scripts/_policy/requirements.txt
          npm ci

      - name: Install oasdiff
        run: |
          VERSION=$(jq -r .tools.oasdiff toolchain.json)
          curl -fsSL "https://github.com/oasdiff/oasdiff/releases/download/v${VERSION}/oasdiff_${VERSION}_linux_amd64.tar.gz" \
            -o "$RUNNER_TEMP/oasdiff.tar.gz"
          tar -xzf "$RUNNER_TEMP/oasdiff.tar.gz" -C "$RUNNER_TEMP"
          install -m 0755 "$RUNNER_TEMP/oasdiff" "$RUNNER_TEMP/oasdiff-bin"
          echo "$RUNNER_TEMP" >> "$GITHUB_PATH"

      - name: Configure git hooks path
        run: git config core.hooksPath scripts/git-hooks

      - name: Run executor
        run: python3 scripts/hb ci --profile "${{ inputs.profile }}"
        env:
          CI: "true"
```

> Nota: o reusable workflow lê versões do `toolchain.json`. Nunca hardcoda.

**2. `conftest.py`** — adicionar Testcontainers fixtures:

Adicionar ao `requirements-dev.txt`:
```
testcontainers[postgres,redis]==4.10.0
```

Alterar `conftest.py` para usar Testcontainers quando disponível:

```python
# Substituir _postgres_available() e django_db_setup() por:

def _postgres_available() -> bool:
    """Check if Postgres is reachable at configured host:port."""
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def _testcontainers_postgres():
    """Start Postgres via Testcontainers if no external Postgres available."""
    if _postgres_available():
        yield  # Use external Postgres (CI services: or local docker-compose)
        return

    try:
        import json as _json
        from testcontainers.postgres import PostgresContainer

        toolchain = _json.loads((_ROOT / "toolchain.json").read_text())
        pg = toolchain["services"]["postgres"]

        with PostgresContainer(
            image=pg["image"],
            username=pg["test_user"],
            password=pg["test_password"],
            dbname=pg["test_db"],
            port=pg["port"],
        ) as postgres:
            host = postgres.get_container_host_ip()
            port = postgres.get_exposed_port(pg["port"])
            os.environ["DB_HOST"] = host
            os.environ["DB_PORT"] = str(port)
            os.environ["DB_NAME"] = pg["test_db"]
            os.environ["DB_USER"] = pg["test_user"]
            os.environ["DB_PASSWORD"] = pg["test_password"]
            os.environ["DATABASE_URL"] = (
                f"postgres://{pg['test_user']}:{pg['test_password']}"
                f"@{host}:{port}/{pg['test_db']}"
            )
            yield
    except ImportError:
        pytest.skip("testcontainers not installed and no external Postgres")


@pytest.fixture(scope="session")
def _testcontainers_redis():
    """Start Redis via Testcontainers if no external Redis available."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(("localhost", 6379))
        s.close()
        yield
        return
    except OSError:
        pass

    try:
        import json as _json
        from testcontainers.redis import RedisContainer

        toolchain = _json.loads((_ROOT / "toolchain.json").read_text())
        redis_cfg = toolchain["services"]["redis"]

        with RedisContainer(image=redis_cfg["image"]) as redis:
            host = redis.get_container_host_ip()
            port = redis.get_exposed_port(redis_cfg["port"])
            os.environ["REDIS_URL"] = f"redis://{host}:{port}/0"
            os.environ["CELERY_BROKER_URL"] = f"redis://{host}:{port}/1"
            os.environ["CELERY_RESULT_BACKEND"] = f"redis://{host}:{port}/2"
            yield
    except ImportError:
        pytest.skip("testcontainers not installed and no external Redis")


@pytest.fixture(scope="session")
def django_db_setup(_testcontainers_postgres):
    """Override pytest-django database setup.
    Uses Testcontainers if no external Postgres available.
    """
    if not _postgres_available():
        pytest.skip("PostgreSQL não disponível e Testcontainers não instalado.")
```

### Roadmap de convergência para caminho único de teste

O `conftest.py` acima é **Phase 1 (híbrida)**: aceita Postgres externo ou Testcontainers. Isso é pragmático para a transição, mas mantém dois caminhos possíveis.

**Phase 2 (caminho único — Testcontainers only):**

| Quando | O que | Resultado |
|---|---|---|
| Entregável 5 (este) | Implementar `conftest.py` híbrido | Dev pode rodar testes sem `docker-compose up` |
| Pós-entregável 6 (prova verde) | Remover `services:` dos workflows CI (substituir por Testcontainers no runner) | CI e local usam o mesmo mecanismo |
| Após estabilização | Remover fallback para Postgres externo do `conftest.py` | Um único caminho oficial: Testcontainers |
| Após estabilização | Mover `infra/docker-compose.yml` para uso exclusivo de dev (app local, não testes) | `docker-compose` deixa de ser relevante para testes |

**Critério para entrar em Phase 2**: entregável 6 (prova operacional) verde. Ou seja, a transição para caminho único **não bloqueia** este plano — é evolução natural pós-paridade.

> Enquanto houver "às vezes usa externo, às vezes usa container", ainda existe superfície de divergência residual. A Phase 2 elimina isso por completo.

**3. `scripts/hb`** — adicionar subcomando `ci --profile`:

```python
def cmd_ci(self, profile: str = "full") -> int:
    """Executor canônico de CI — chamado por reusable workflow e hb preflight."""
    profiles = {
        "pr": ["validate", "test", "frontend", "invariants"],
        "contract-gates": ["validate", "compilers", "governance", "adversarial", "architecture", "invariants"],
        "full": ["validate", "test", "frontend", "compilers", "governance", "adversarial", "architecture", "docker", "invariants"],
    }
    steps = profiles.get(profile)
    if not steps:
        print(f"❌ Profile desconhecido: {profile}. Válidos: {', '.join(profiles)}")
        return 1
    # ... executar cada step
```

### Arquivos a alterar

**1. `.github/workflows/ci.yml`** — transformar em caller fino:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    name: CI
    uses: ./.github/workflows/_reusable-ci.yml
    with:
      profile: pr
```

> Nota: os job names reportados ao GitHub mudam. O entregável 1 (ruleset) precisa ser atualizado para refletir os novos nomes de check. Fazer isso atomicamente neste entregável.

**2. `.github/workflows/contract-gates.yml`** — jobs incondicionais viram callers:

Os jobs `validate-contracts`, `governance-tests`, `adversarial-suite`, `architecture-drift-check` podem ser consolidados no reusable workflow com `profile: contract-gates`. Os jobs condicionais (`governance-enforcement`, etc.) permanecem inline porque dependem de path filtering.

**3. `requirements-dev.txt`** — adicionar testcontainers:

```
testcontainers[postgres,redis]==4.10.0
```

**4. `scripts/hb` `_CI_TEST_ENV`** — ler do manifesto em vez de hardcodar:

```python
@property
def _ci_test_env(self) -> dict[str, str]:
    """Build CI test env from toolchain.json."""
    tc = json.loads((self.root / "toolchain.json").read_text())
    pg = tc["services"]["postgres"]
    redis_port = tc["services"]["redis"]["port"]
    return {
        "CI": "true",
        "SECRET_KEY": "ci-secret-key-for-testing-only-not-real",
        "DEBUG": "false",
        "ALLOWED_HOSTS": "localhost,127.0.0.1",
        "HB_RUN_SCHEMATHESIS": "1",
        "HB_SCHEMATHESIS_MAX_EXAMPLES": "10",
        "DATABASE_URL": f"postgres://{pg['test_user']}:{pg['test_password']}@localhost:{pg['port']}/{pg['test_db']}",
        "DB_NAME": pg["test_db"],
        "DB_USER": pg["test_user"],
        "DB_PASSWORD": pg["test_password"],
        "DB_HOST": "localhost",
        "DB_PORT": str(pg["port"]),
        "REDIS_URL": f"redis://localhost:{redis_port}/0",
        "CELERY_BROKER_URL": f"redis://localhost:{redis_port}/1",
        "CELERY_RESULT_BACKEND": f"redis://localhost:{redis_port}/2",
        "CORS_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:5173",
        "LOG_LEVEL": "WARNING",
        "JWT_ALGORITHM": "HS256",
        "JWT_SECRET": "ci-jwt-secret-for-testing-only",
    }
```

### Critério de aceite

- [ ] `ci.yml` tem menos de 30 linhas e chama `_reusable-ci.yml`.
- [ ] `_reusable-ci.yml` lê versões de `toolchain.json` (nunca hardcoda).
- [ ] `pytest` local sem `docker-compose up` sobe Postgres/Redis via Testcontainers automaticamente.
- [ ] `hb preflight` usa `_ci_test_env` derivado de `toolchain.json`.
- [ ] `scripts/hb ci --profile pr` reproduz o mesmo caminho que o reusable workflow.

### Risco eliminado

- Duplicação de lógica de bootstrap entre 5 workflows.
- Dependência de `docker-compose` ou `services:` para rodar testes.
- Hardcode de versões/portas/credenciais em `_CI_TEST_ENV`.
- Divergência entre o que roda local e o que roda no GitHub.

### Validação de paridade (prova operacional definitiva)

```bash
# 1. Rodar local:
python3 scripts/hb preflight
# Resultado: PASS, evidence gerada em _reports/preflight/latest.json

# 2. Push:
git push

# 3. Esperar CI:
# Todos os required checks (7) devem ficar verdes.

# 4. Comparar:
# Se PASS local + PASS CI no mesmo SHA → paridade confirmada.
```

---

## Entregável 6 — Prova operacional definitiva

### Problema que resolve

Os entregáveis 1–5 implementam a solução. Mas **implementar ≠ resolver**. O plano não está encerrado até que haja comprovação empírica de paridade end-to-end. Sem este entregável, os 5 anteriores são infraestrutura sem validação de resultado.

### Dependências

Entregáveis 1–5 implementados e commitados.

### Protocolo de execução

**Passo 1 — Executar preflight local:**

```bash
python3 scripts/hb preflight
```

Resultado esperado: `verdict: PASS` em `_reports/preflight/latest.json`.

**Passo 2 — Registrar SHA e evidência:**

```bash
SHA=$(git rev-parse HEAD)
echo "SHA testado: $SHA"
cat _reports/preflight/latest.json | jq '{sha, verdict, timestamp, steps}'
```

**Passo 3 — Push:**

```bash
git push
```

O pre-push hook valida que o SHA local tem evidence PASS recente (< 60 min).

**Passo 4 — Aguardar CI no GitHub:**

Todos os 7 required checks devem ficar verdes para o mesmo SHA.

**Passo 5 — Comparar e registrar:**

```bash
# Buscar status de checks para o SHA:
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/hbtrack/official/commits/$SHA/check-runs" \
  | jq '[.check_runs[] | {name, conclusion}]'
```

**Passo 6 — Registrar evidência final:**

Criar `_reports/parity/proof_$(date +%Y%m%d).json`:

```json
{
  "sha": "<SHA>",
  "date": "2026-04-XX",
  "preflight_local": "PASS",
  "preflight_evidence": "_reports/preflight/latest.json",
  "ci_checks": {
    "Validate Contract Gates": "success",
    "Governance Tests": "success",
    "Architecture Drift Check": "success",
    "Adversarial Suite": "success",
    "CI / Validate Contracts": "success",
    "CI / Tests": "success",
    "CI / Frontend Build + Tests": "success"
  },
  "parity_confirmed": true,
  "verdict": "PARIDADE_CONFIRMADA"
}
```

### Critério de aceite

- [ ] `hb preflight` retorna PASS com evidence.
- [ ] `git push` aceito pelo pre-push hook.
- [ ] 7/7 required checks verdes no GitHub para o mesmo SHA.
- [ ] Evidência registrada em `_reports/parity/`.
- [ ] Nenhum check informational ou conditional está vermelho (podem estar skipped, mas não failed).

### Risco eliminado

- Falsa sensação de conclusão sem validação empírica.
- Resultado "funciona na minha máquina mas não no CI" ou vice-versa.

### O que acontece se falhar

Se algum check falhar neste ponto:

1. O problema residual está **documentado** — os testes de invariante e manifestos indicam exatamente o que diverge.
2. Voltar ao entregável correspondente e corrigir.
3. Repetir entregável 6 até verde.

> **Este entregável é o critério de encerramento do problema.** O plano não está concluído até que este entregável passe.

---

## Resumo de arquivos

### Arquivos a criar (8)

| Arquivo | Entregável |
|---|---|
| `toolchain.json` | 2 |
| `contracts/schemas/shared/toolchain.schema.json` | 2 |
| `merge-readiness.json` | 3 |
| `contracts/schemas/shared/merge-readiness.schema.json` | 3 |
| `tests/invariants/test_toolchain_parity.py` | 4 |
| `tests/invariants/test_merge_readiness_parity.py` | 4 |
| `.github/workflows/_reusable-ci.yml` | 5 |
| `tests/invariants/__init__.py` | 4 |

### Evidências geradas (não versionadas, mas registradas)

| Arquivo | Entregável | Status |
|---|---|---|
| `_reports/enforcement/branch_protection_snapshot_20260403.json` | 1 | ✅ gerado |
| `_reports/enforcement/ruleset_snapshot_20260403.json` | 1 | ✅ gerado |
| `_reports/enforcement/ruleset_snapshot_after.json` | 1 | ✅ gerado |
| `_reports/enforcement/ruleset_update_response.json` | 1 | ✅ gerado |
| `_reports/enforcement/ruleset_fix_adversarial.json` | 1 | ✅ gerado |
| `_reports/enforcement/branch_protection_delete_response.json` | 1 | ✅ gerado |
| `_reports/parity/proof_*.json` | 6 | ⏳ pendente |

### Arquivos a alterar (11)

| Arquivo | Entregáveis | Mudança |
|---|---|---|
| `.nvmrc` | 2 | `v24.14.0` → `24` |
| `.github/workflows/ci.yml` | 2, 5 | Node 22→24, depois caller fino |
| `.github/workflows/contract-gates.yml` | 4, 5 | Fix path, add actionlint job, consolidar jobs |
| `.github/workflows/context-efficiency-audit.yml` | 2 | Python 3.11→3.12 |
| `.github/workflows/domain-completeness-audit.yml` | 2 | Python 3.11→3.12 |
| `infra/docker-compose.yml` | 2 | Postgres 12→16, porta 5433→5432 |
| `conftest.py` | 5 | Testcontainers fixtures |
| `scripts/hb` | 4, 5 | Invariants suite, `ci` subcommand, `_ci_test_env` from manifest |
| `requirements-dev.txt` | 5 | Adicionar testcontainers |
| `scripts/bootstrap/dev_contract_env.sh` | 4 | Instalar actionlint |
| `package.json` | — | Sem mudança (engines não adicionado; manifesto + teste de invariante é suficiente) |

### Ações no GitHub (não versionadas)

| Ação | Entregável | Status |
|---|---|---|
| Exportar snapshots de branch protection e ruleset | 1 | ✅ 2026-04-03 |
| Atualizar ruleset `contract-gates` com 6 checks (5→6; +`CI/Frontend Build + Tests`) | 1 | ✅ 2026-04-03 |
| Remover `Adversarial Suite` do ruleset (job inexistente) | 1 | ✅ 2026-04-03 |
| Validar ruleset via API | 1 | ✅ 2026-04-03 |
| Remover branch protection da `main` (após validação) | 1 | ✅ 2026-04-03 (404 confirmado) |
| Re-adicionar `Adversarial Suite` ao ruleset | 4 | ⏳ após criação do job |
| Atualizar ruleset após renomear checks (caller fino) | 5 | ⏳ pendente |
| Coletar check-runs do SHA e registrar prova | 6 | ⏳ pendente |

---

## Grafo de dependências

```
Entregável 1 (enforcement)
    └── Entregável 2 (toolchain)
            └── Entregável 3 (merge-readiness)
                    └── Entregável 4 (actionlint + invariantes)
                            └── Entregável 5 (executor + reusable + testcontainers)
                                    └── Entregável 6 (prova operacional)
```

Cada entregável 1–5 é independentemente commitável e mergeável. A sequência garante que nenhum entregável posterior depende de estrutura que ainda não existe. O entregável 6 é a validação final — roda após todos os anteriores estarem na `main`.

## Critério de encerramento do problema

O problema de paridade local × CI está **encerrado** quando, e somente quando:

1. Os 6 entregáveis estiverem implementados; — ⏳ E1 ✅ | E2–E6 pendentes
2. Os testes de invariante estiverem verdes;
3. O ruleset estiver correto e único; — ⏳ parcial (6 checks ✅; `Adversarial Suite` pendente PR-4)
4. `hb preflight` passar de ponta a ponta;
5. O mesmo SHA for enviado ao GitHub;
6. Os 7 required checks ficarem verdes;
7. A evidência final estiver registrada em `_reports/parity/`.

Qualquer condição faltando = problema aberto.
