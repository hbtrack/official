# AGENT PLATFORM EXPOSURE MAP

## Objetivo

Mapear o que o HB Track consegue expor como papel operacional em cada plataforma
de agente, separando:

- papel interno do pipeline;
- agente selecionável na UI;
- mecanismo real de enforcement.

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

Claude consegue exercer:

- `HB Contract`
- `Hb Implementer`
- `Hb Adversarial Tester`
- `HandTracker`

mas não como papéis de dropdown configurados por arquivo no mesmo padrão do Copilot.

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

Codex consegue exercer:

- `HB Contract`
- `Hb Implementer`
- `Hb Adversarial Tester`
- `HandTracker`

mas não como opções nativas de UI do Copilot.

### Uso recomendado nesta trilha

Codex mantém paridade operacional documentada.
Ele não recebe agente separado, dropdown equivalente nem papel especial de
revisão externa final.

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

## Revisão externa recomendada

Fluxo recomendado desta trilha:

```text
Copilot / Hb Implementer
-> Copilot / Hb Adversarial Tester
-> Claude (tester externo com pacote estruturado)
-> scripts/hb + validate_contracts.py + pytest + CI
```

Claude melhora a independência da revisão, mas não substitui os gates
executáveis.

## Arquitetura multiagente auditável

| Plataforma | Exposição | Onde vive | Papéis | Limite |
|---|---|---|---|---|
| Copilot | UI/workflow/custom agents | `.github/agents/*.agent.md` | HB Contract, Hb Implementer, Hb Adversarial Tester, HandTracker | Same-chat handoff não é validação independente |
| Claude | Subagents com contexto isolado | `.claude/agents/*.md` | hb-adversarial-tester, hb-governance-auditor, hb-evidence-verifier | Revisa, não valida final |
| Codex | Gate audit / sandbox | `.dev/codex-agents/*.toml` | hb-gate-auditor, hb-pr-reviewer | Não implementa durante gate |
| CI/scripts | Validação executável | `scripts/hb`, `validate_contracts.py`, CI | final_validation_gate | Única autoridade para `VALIDATED` |

**Regra de autoridade:**

```text
TASK_CATALOG → BOOT_PROFILES → worker prompt → schema → gate → enforcement executável
```

`VALIDATED` só pode ser produzido por CI, `scripts/hb`, `validate_contracts.py`
ou gate executável determinístico equivalente com logs.
