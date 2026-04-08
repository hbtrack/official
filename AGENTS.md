# AGENTS.md — Inventário de Agentes HB Track

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Inventário operacional de agentes. Não possui autoridade normativa.
> Em caso de conflito, prevalecem: enforcement executável > schemas > `docs/_canon/` > este arquivo.

## Agentes ativos

| Agente | Plataforma | Instrução principal | Auto-load? | Hooks | Skills | Scope |
|---|---|---|---|---|---|---|
| **GitHub Copilot** | VS Code Chat / Agent | `.github/copilot-instructions.md` | ✅ | N/A | `hb-pipeline-orchestrator`, `hb-roadmap-executor` | Full workspace |
| **Claude Code** | VS Code Extension | `CLAUDE.md` | ✅ | `.claude/settings.local.json` → `PreToolUse` + `Stop` | N/A | Full workspace |
| **Codex** | OpenAI Codex CLI | `.codex` | ✅ | N/A | N/A | Full workspace |
| **Gemini (AI Review)** | GitHub Actions | `.github/ai-review/styleguide.md` | N/A (workflow) | N/A | N/A | PR reviews only |

## Fontes de governança por agente

### GitHub Copilot
- **Bridge doc:** `.github/copilot-instructions.md` (auto-load)
- **Agent definition:** `.github/agents/hb-contract.agent.md`
- **Skills:** `.github/skills/hb-pipeline-orchestrator/SKILL.md`, `.github/skills/hb-roadmap-executor/SKILL.md`
- **Instructions:** `.github/instructions/hb-contract-guards.instructions.md` (scope: `src/**`)
- **Enforcement:** `scripts/hb`, `validate_contracts.py`, `pre-commit hook`, CI workflows

### Claude Code
- **Bridge doc:** `CLAUDE.md` (auto-load)
- **Hooks:** `.claude/settings.local.json` → `PreToolUse` (`check_backend_gate.py`), `Stop` (`check_session_commit.py`)
- **Enforcement:** `scripts/hb`, `validate_contracts.py`, `pre-commit hook`, CI workflows

### Codex
- **Bridge doc:** `.codex` (auto-load)
- **Enforcement:** CI workflows (único enforcement ativo para Codex)

### Gemini (AI Review)
- **Style guide:** `.github/ai-review/styleguide.md`
- **Scope:** Apenas reviews automáticas de PRs via `ai-pr-review.yml`

## Boot obrigatório (todos os agentes)
1. Ler `docs/_canon/AGENT_INSTRUCTIONS.md`
2. Se existir `SESSION_HANDOFF.md` → ler antes de qualquer ação
3. Ler `ROADMAP.md` — fase atual

## Cadeia de precedência
```
enforcement executável > schemas ativos > SOURCE_AUTHORITY_GRAPH > concept_owner > bridge_docs > derived > legacy
```

## Worker prompts (20 — compartilhados por todos os agentes)
Diretório: `.contract_driven/agent_prompts/`
- Workers são prompts especializados carregados pelo mesmo agente
- Não assumir subagente autônomo, fila ou runtime distribuído
