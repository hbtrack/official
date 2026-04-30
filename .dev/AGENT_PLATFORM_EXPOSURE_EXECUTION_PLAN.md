# HB Track — Plano de Execução da Exposição de Papéis por Plataforma

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: plano operacional desta trilha.
> Em caso de conflito, prevalecem: enforcement executável > schemas >
> `docs/_canon/` > este arquivo.

## Objetivo

Materializar e governar a exposição de papéis por plataforma sem criar falsa
simetria entre interfaces que o repositório não possui.

## Relação com artefatos existentes

- `.dev/CODEXPLAN.md` continua cobrindo o trilho antifraude interno já implementado.
- `.dev/AGENT_PLATFORM_EXPOSURE_MAP.md` continua sendo o mapa curto de capacidade por plataforma.
- Este arquivo é o plano operacional específico desta trilha:
  exposição por plataforma + revisão adversarial externa com Claude.

## Decisão arquitetural

| Plataforma | Exposição dedicada | Onde vive | Observação |
|---|---|---|---|
| Copilot | Sim | `.github/agents/*.agent.md` | Dropdown/UI real |
| Claude | Sim | `.claude/agents/*.md` | Subagents com contexto isolado |
| Codex | Sim | `.dev/codex-agents/*.toml` | Gate auditor / sandbox runner |

## Evolução arquitetural

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

## Fluxo-alvo

```text
Copilot / Hb Implementer
-> Copilot / Hb Adversarial Tester
-> Claude (tester externo com pacote estruturado)
-> scripts/hb + validate_contracts.py + pytest + CI
```

## Pacote mínimo para Claude

- objetivo original
- critérios de aceite
- `approved_plan_path`
- arquivos modificados
- diff completo
- comandos executados
- saídas brutas dos comandos
- testes positivos
- testes negativos
- limitações declaradas
- `PR_URL`
- `current_state.json`
- `implementation_evidence_pack.json`
- `plan_to_diff_trace.json`
- `negative_test_manifest.json`
- `adversarial_report.json`, se existir
- `SESSION_HANDOFF.md` apenas como estado operacional

## Proibições

- Não enviar narrativa longa do executor.
- Não enviar opinião persuasiva do implementador.
- Não vender a revisão do Claude como autoridade final.

## Critérios de aceite

- Copilot continua sendo a única plataforma com agentes dedicados reais.
- `CLAUDE.md` e `.codex` deixam explícita a ausência de mecanismo equivalente.
- `CLAUDE.md` registra o papel de testador adversarial externo.
- `AGENTS.md`, o mapa de exposição e os bridge docs contam a mesma história.
- Os testes de exposição por plataforma falham quando essa coerência é quebrada.
