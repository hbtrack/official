# Merge Policy — main

> **SSOT operacional.** Fonte de verdade para checks obrigatórios vs informativos.
> Gerado em: 2026-04-03 | PR: parity/enforcement-unification
> Ruleset canônico ID: 13901517 (contract-gates — enforcement: active)

## Required checks (bloqueiam merge via ruleset `contract-gates`)

Estes 6 checks devem passar para que qualquer PR possa ser merged em `main`.
Configurados no ruleset GitHub ID 13901517 com `strict_required_status_checks_policy: true`.

| # | Job name (conforme GitHub Actions) | Workflow |
|---|---|---|
| 1 | `Validate Contract Gates` | `contract-gates.yml` |
| 2 | `Governance Tests` | `contract-gates.yml` |
| 3 | `Architecture Drift Check` | `contract-gates.yml` |
| 4 | `CI / Validate Contracts` | `ci.yml` |
| 5 | `CI / Tests` | `ci.yml` |
| 6 | `CI / Frontend Build + Tests` | `ci.yml` |

> **Nota:** `Adversarial Suite` foi removido do ruleset em 2026-04-03 porque o job correspondente não existe em nenhum workflow — adicioná-lo causaria bloqueio permanente de PRs. Será re-adicionado no PR-4 após criação do job em `contract-gates.yml`.

## Informational checks (não bloqueiam merge)

| Job name | Workflow | Motivo |
|---|---|---|
| `Docker Build Check` | `ci.yml` | Diagnóstico — falha não reverte produção |

## Conditional checks (só executam quando arquivos de governança mudam)

Disparados por mudanças em: `contracts/`, `scripts/`, `.github/`, `docs/_canon/`.

| Job name | Workflow | Condição |
|---|---|---|
| `Governance Enforcement` | `contract-gates.yml` | `governance_changed == 'true'` |
| `Paridade Registry × Executor` | `contract-gates.yml` | `governance_changed == 'true'` |
| `Paridade Schema × Template × Skills` | `contract-gates.yml` | `governance_changed == 'true'` |

## Regras de merge

- **Método:** merge, squash ou rebase (todos permitidos)
- **Aprovações requeridas:** 0 (CI gates substituem review humano)
- **Dismiss stale reviews:** sim
- **Resolve todas as threads:** obrigatório antes de merge
- **Force push:** proibido (regra `non_fast_forward` no ruleset)
- **Deletion da branch default:** proibido (regra `deletion` no ruleset)

## Bypass actors

Nenhum. O ruleset não tem bypass configurado — `bypass_actors: []`.

## Histórico de mudanças

| Data | Mudança | PR |
|---|---|---|
| 2026-04-03 | Criação inicial — migração branch protection → ruleset | parity/enforcement-unification |
| 2026-04-03 | Adição de `CI / Frontend Build + Tests` (5 → 6 checks via PUT) | parity/enforcement-unification |
| 2026-04-03 | Remoção de branch protection legada (branch protection + ruleset em paralelo era duplicidade) | parity/enforcement-unification |
| 2026-04-03 | Remoção de `Adversarial Suite` do ruleset — job não existe nos workflows (seria bloqueio permanente) | parity/enforcement-unification |
