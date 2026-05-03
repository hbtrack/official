# AGENTS.md — Inventário de Agentes HB Track

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Inventário operacional de agentes. Não possui autoridade normativa.
> Em caso de conflito, prevalecem: enforcement executável > schemas > `docs/_canon/` > este arquivo.

## Agentes ativos

| Agente | Plataforma | Instrução principal | Auto-load? | Hooks | Skills | Scope |
|---|---|---|---|---|---|---|
| **GitHub Copilot** | VS Code Chat / Agent | `.github/copilot-instructions.md` | ✅ | N/A | `hb-pipeline-orchestrator`, `hb-roadmap-executor`, `hb-merge-orchestrator` | Full workspace |
| **Claude Code** | VS Code Extension | `CLAUDE.md` | ✅ | `.claude/settings.local.json` → `PreToolUse` + `Stop` | N/A | Full workspace |
| **Codex** | OpenAI Codex CLI | `.codex` | ✅ | N/A | N/A | Full workspace |
| **Gemini (AI Review)** | GitHub Actions | `.github/ai-review/styleguide.md` | N/A (workflow) | N/A | N/A | PR reviews only |

## Fontes de governança por agente

### GitHub Copilot
- **Bridge doc:** `.github/copilot-instructions.md` (auto-load)
- **Agent definitions:** `.github/agents/hb-contract.agent.md`, `.github/agents/hb-implementer.agent.md`, `.github/agents/hb-adversarial-tester.agent.md`, `.github/agents/hb-mesclado.agent.md`
- **Skills:** `.github/skills/hb-pipeline-orchestrator/SKILL.md`, `.github/skills/hb-roadmap-executor/SKILL.md`, `.github/skills/hb-merge-orchestrator/SKILL.md`
- **Instructions:** `.github/instructions/hb-contract-guards.instructions.md` (scope: `src/**`), `.github/instructions/hb-roadmap-mode.instructions.md` (scope: infra/CI), `.github/instructions/hb-no-manual-schema-edit.instructions.md` (scope: `frontend/src/api/**`), `.github/instructions/hb-derived-not-sovereign.instructions.md` (scope: root `*.md`), `.github/instructions/hb-mesclado.instructions.md` (scope: global router)
- **Enforcement:** `scripts/hb`, `validate_contracts.py`, `pre-commit hook`, CI workflows
- **Camada adicional desta trilha:** revisão externa recomendada via `Claude` + gates executáveis

### Claude Code
- **Bridge doc:** `CLAUDE.md` (auto-load)
- **Hooks:** `.claude/settings.local.json` → `PreToolUse` (`check_backend_gate.py`), `Stop` (`check_session_commit.py`)
- **Enforcement:** `scripts/hb`, `validate_contracts.py`, `pre-commit hook`, CI workflows
- **UI dedicada:** não há mecanismo equivalente a `.github/agents/*.agent.md`
- **Uso recomendado nesta trilha:** testador adversarial externo com pacote estruturado de evidências

### Codex
- **Bridge doc:** `.codex` (auto-load)
- **Enforcement:** CI workflows (único enforcement ativo para Codex)
- **UI dedicada:** não há mecanismo equivalente a `.github/agents/*.agent.md`
- **Uso nesta trilha:** paridade operacional documentada, sem agente separado

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

## Exposição por plataforma

### GitHub Copilot
- Suporta agentes selecionáveis via `.github/agents/*.agent.md`
- Exposição real agora:
  - `HB Contract`
  - `Hb Implementer`
  - `Hb Adversarial Tester`
  - `Hb Merger`
- Os papéis usam o mesmo enforcement central do repo; o dropdown não cria soberania nova.
- A revisão adversarial final forte não depende só do mesmo chat: o handoff
  recomendado é para Claude usando pacote estruturado de evidências + gates.

### Claude Code
- Não há, neste repositório, mecanismo equivalente a `.github/agents/` para criar opções novas no dropdown do VS Code.
- Exposição possível no mesmo padrão operacional:
  - `CLAUDE.md` como bridge doc auto-load
  - `.contract_driven/TASK_CATALOG.yaml` para task routing
  - `.contract_driven/BOOT_PROFILES.yaml` para pré-condições
  - `.contract_driven/agent_prompts/*.prompt.md` para workers especializados
  - hooks locais em `.claude/settings.local.json`
- Resultado: Claude pode executar os mesmos papéis operacionais, mas não aparece como agentes separados por dropdown a partir deste mecanismo.
- Nesta trilha, Claude é a camada recomendada de revisão adversarial externa,
  recebendo apenas pacote de evidências sem narrativa do executor.

### Codex
- Não há, neste repositório, mecanismo equivalente a `.github/agents/` para criar opções novas no dropdown do VS Code.
- Exposição possível no mesmo padrão operacional:
  - `.codex` como bridge doc auto-load
  - `.contract_driven/TASK_CATALOG.yaml` para task routing
  - `.contract_driven/BOOT_PROFILES.yaml` para boot
  - `.contract_driven/agent_prompts/*.prompt.md` para workers especializados
  - enforcement por `scripts/hb`, `validate_contracts.py` e CI
- Resultado: Codex pode operar como `Hb Implementer` ou `Hb Adversarial Tester`, mas não como opções de UI nativas do Copilot.
- Codex mantém paridade operacional documentada, mas não é a camada preferida
  de revisão externa final nesta trilha.
