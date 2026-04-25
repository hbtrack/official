# Merge Policy — main

> **ARTEFATO GERADO — DERIVADO NÃO-SOBERANO. Não editar manualmente.**
> Gerador: `python3 scripts/audit/generate_merge_policy.py --write`
> Fontes: `merge-readiness.json` + `.github/rulesets/contract-gates.snapshot.json`
> Paridade live: `python3 scripts/audit/check_live_ruleset_parity.py --json`

## Required checks (bloqueiam merge via ruleset `contract-gates`)

Estes 6 checks devem passar para que qualquer PR possa ser merged em `main`.
Configurados no ruleset GitHub ID 13901517 com `strict_required_status_checks_policy: true`.

| # | Contexto requerido (exato) | Workflow |
|---|---|---|
| 1 | `Architecture Drift Check` | `contract-gates.yml` |
| 2 | `Governance Tests` | `contract-gates.yml` |
| 3 | `Validate Contract Gates` | `contract-gates.yml` |
| 4 | `ci / Frontend Build + Tests` | `_reusable-ci.yml` |
| 5 | `ci / Tests` | `_reusable-ci.yml` |
| 6 | `ci / Validate Contracts` | `_reusable-ci.yml` |

## Informational checks (não bloqueiam merge)

| Contexto | Workflow | Motivo |
|---|---|---|
| `Pact Provider Gate — training` | `contract-gates.yml` | test_pact_provider_gate.py ausente — gate deletado durante refactor training (Fases 0-6). Waiver formal: contracts/_waivers/PACT_PROVIDER_GATE_TRAINING_20260422.json (expira 2026-07-22). Recriar em N+1 após consumer contract ser emitido. Ver .dev/decisões/rafatora_training.md §7.3 P6. |
| `ci / Docker Build Check` | `_reusable-ci.yml` | Valida Dockerfile mas não bloqueia merge — falha de build de imagem não impede integração de código |

## Conditional checks (só executam quando a condição declarada for satisfeita)

| Contexto | Workflow | Condição |
|---|---|---|
| `Governance Enforcement (survival-suite)` | `contract-gates.yml` | `governance_changed == true` |
| `Paridade Registry × Executor` | `contract-gates.yml` | `governance_changed == true` |
| `Paridade Schema × Template × Skills` | `contract-gates.yml` | `governance_changed == true` |
| `Validação Cruzada SESSION_HANDOFF ↔ session_start` | `contract-gates.yml` | `governance_changed == true` |

## Regras de enforcement verificáveis

- **Atualização obrigatória com a branch base**: sim
- **Aprovações requeridas**: 0
- **Code owner review**: não
- **Resolver todas as threads**: obrigatório
- **Force push**: proibido
- **Deletion da branch default**: proibido
- **Bypass actors declarados no manifesto**: []

## Bypass actors expostos pelo ruleset normalizado

Nenhum. O ruleset normalizado expõe `bypass_actors: []`.
