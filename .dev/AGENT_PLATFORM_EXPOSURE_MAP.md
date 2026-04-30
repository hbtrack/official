# AGENT PLATFORM EXPOSURE MAP

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: plano operacional desta trilha.
> Em caso de conflito, prevalecem: enforcement executável > schemas >
> `docs/_canon/` > este arquivo.

## Objetivo

Mapear e governar a exposição de papéis operacionais por plataforma no HB Track,
separando:

- papel interno do pipeline;
- agente selecionável na UI;
- mecanismo real de enforcement;
- como materializar e governar a revisão adversarial externa.

## Relação com outros artefatos

- `.dev/CODEXPLAN.md` cobre o trilho antifraude interno já implementado — escopo distinto deste arquivo.
- `AGENTS.md` e os bridge docs (`CLAUDE.md`, `.codex`, `copilot-instructions.md`) devem contar a mesma história deste arquivo.

## Decisão arquitetural

| Plataforma | Exposição dedicada | Onde vive | Observação |
|---|---|---|---|
| Copilot | Sim | `.github/agents/*.agent.md` | Dropdown/UI real |
| Claude | Sim | `.claude/agents/*.md` | Subagents com contexto isolado |
| Codex | Sim | `.dev/codex-agents/*.toml` | Gate auditor / sandbox runner |

Esta versão **revoga** a regra anterior que proibia agentes Claude e Codex separados.
Motivo: subagents Claude com contexto isolado e Codex em sandbox são a camada de
revisão independente que o fluxo anterior não cobria.

| Decisão | Razão |
|---|---|
| Criar `.claude/agents/*.md` | Contexto isolado reduz contaminação do revisor |
| Criar `.dev/codex-agents/*.toml` | Sandbox/worktree reduz risco ambiental |
| Não criar novo runtime | Copilot + Claude + Codex + CI já são suficientes |
| Não criar novos task types | TASK_CATALOG existente cobre os papéis |
| Não criar nova soberania normativa | Bridge docs, não canon |

Regra principal:

```text
Troca de papel não é separação de confiança.
Contexto isolado reduz contaminação.
Sandbox reduz risco ambiental.
Gate executável valida.
```

## Evolução arquitetural

Esta trilha consolida a exposição por plataforma e o plano operacional em um único bridge doc: `.dev/AGENT_PLATFORM_EXPOSURE_MAP.md`.

A regra anterior que proibia agentes Claude e Codex separados foi revogada.
Motivo: subagents Claude com contexto isolado e Codex em sandbox/worktree reduzem riscos que handoff same-chat do Copilot não cobre.

Codex mantém paridade operacional documentada.

## GitHub Copilot

### Suporte de UI

Suporta agentes selecionáveis no dropdown do VS Code via:

```text
.github/agents/*.agent.md
```

### Papéis expostos

- `HB Contract`
- `Hb Implementer`
- `Hb Adversarial Tester`
- `HandTracker`

### Fontes reais

- `.github/agents/*.agent.md`
- `.github/copilot-instructions.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/agent_prompts/*.prompt.md`
- `scripts/hb`
- `scripts/contracts/validate/validate_contracts.py`

### Limite importante

O dropdown do Copilot só expõe um papel operacional.
Ele não cria soberania nova e não substitui task types, schemas, gates ou CI.

## Claude Code

### Suporte de UI

Neste repositório, não há mecanismo equivalente a `.github/agents/*.agent.md`
para criar papéis separados no dropdown do VS Code.

### Exposição possível

Claude pode operar nos mesmos papéis internos usando:

- `CLAUDE.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/agent_prompts/*.prompt.md`
- hooks locais em `.claude/settings.local.json`
- enforcement por `scripts/hb` e `validate_contracts.py`

### Conclusão

Claude consegue exercer `HB Contract`, `Hb Implementer`, `Hb Adversarial Tester`
e `HandTracker`, mas não como papéis de dropdown configurados por arquivo no mesmo
padrão do Copilot.

### Uso recomendado nesta trilha

Claude é a camada recomendada de revisão adversarial externa.
Ele deve receber apenas pacote estruturado de evidências do trilho
`implementation_execution` / `adversarial_test_execution`, nunca a narrativa
completa do executor.

## Codex

### Suporte de UI

Neste repositório, não há mecanismo equivalente a `.github/agents/*.agent.md`
para criar papéis separados no dropdown do VS Code.

### Exposição possível

Codex pode operar nos mesmos papéis internos usando:

- `.codex`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `.contract_driven/agent_prompts/*.prompt.md`
- enforcement por `scripts/hb`, `validate_contracts.py` e CI

### Conclusão

Codex consegue exercer `HB Contract`, `Hb Implementer`, `Hb Adversarial Tester`
e `HandTracker`, mas não como opções nativas de UI do Copilot. Não recebe papel
especial de revisão externa final.

## Fluxo-alvo de execução

```text
Copilot / Hb Implementer
-> Copilot / Hb Adversarial Tester
-> Claude (tester externo com pacote estruturado)
-> scripts/hb + validate_contracts.py + pytest + CI
```

Claude melhora a independência da revisão, mas não substitui os gates executáveis.

## Pacote mínimo para Claude (revisão adversarial)

- objetivo original
- critérios de aceite
- `approved_plan_path`
- arquivos modificados
- diff completo
- comandos executados
- saídas brutas dos comandos
- testes positivos e negativos
- limitações declaradas
- `PR_URL`
- `current_state.json`
- `implementation_evidence_pack.json`
- `plan_to_diff_trace.json`
- `negative_test_manifest.json`
- `adversarial_report.json`, se existir
- `SESSION_HANDOFF.md` apenas como estado operacional

## Proibições

- Não enviar narrativa longa do executor ao Claude.
- Não enviar opinião persuasiva do implementador ao Claude.
- Não vender a revisão do Claude como autoridade final.

## Regra final

No HB Track, o papel verdadeiro do agente não vem da UI.
Ele vem de:

```text
TASK_CATALOG
→ BOOT_PROFILES
→ worker prompt
→ schema
→ gate
→ enforcement executável
```

O dropdown é só exposição operacional de conveniência.

## Critérios de aceite desta configuração

- Copilot continua sendo a única plataforma com agentes dedicados reais via dropdown.
- `CLAUDE.md` e `.codex` deixam explícita a ausência de mecanismo equivalente.
- `CLAUDE.md` registra o papel de testador adversarial externo.
- `AGENTS.md` e os bridge docs contam a mesma história deste arquivo.
- Os testes de exposição por plataforma falham quando essa coerência é quebrada.

## Matriz de exposição por plataforma

| Plataforma | Exposição | Onde vive | Papéis | Limite |
|---|---|---|---|---|
| Copilot | UI/workflow/custom agents | `.github/agents/*.agent.md` | HB Contract, Hb Implementer, Hb Adversarial Tester, HandTracker | Same-chat handoff não é validação independente |
| Claude | Subagents com contexto isolado | `.claude/agents/*.md` | hb-adversarial-tester, hb-governance-auditor, hb-evidence-verifier | Revisa, não valida final |
| Codex | Gate audit / sandbox / PR review | `.dev/codex-agents/*.toml` | hb-gate-auditor, hb-pr-reviewer | Não implementa durante gate |
| CI/scripts | Validação executável | `scripts/hb`, `validate_contracts.py`, CI | final_validation_gate | Única autoridade para VALIDATED |

