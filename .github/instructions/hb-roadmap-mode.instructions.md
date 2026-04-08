---
applyTo: "infra/**,config/**,Dockerfile*,.github/workflows/**"
---

# Modo ROADMAP — Não rotear por CDD

Arquivos neste escopo pertencem ao **Modo ROADMAP** (`execute_roadmap_phase`), não ao Modo CDD.

## Regras

- **NÃO** rotear por `pre_contract_orchestrator`
- **NÃO** executar `hb check` nem `hb artifact` sobre artefatos de infraestrutura
- **NÃO** exigir `validated_contract` nem `ADVERSARIAL_ANALYSIS_GATE` para estes paths
- Ponto de entrada: `ROADMAP.md` + `SESSION_HANDOFF.md`
- Verificar Critério de Done da fase N-1 antes de iniciar fase N

## Paths incluídos

- `infra/` — Docker Compose, Nginx, scripts de deploy
- `config/` — Celery, ASGI, settings Django
- `Dockerfile`, `Dockerfile.frontend` — imagens de container
- `.github/workflows/` — CI/CD pipelines

## Referências

- `ROADMAP.md` — fases 0-13, critérios de done, stack canônica
- `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md` — worker do modo ROADMAP
- `.github/skills/hb-roadmap-executor/SKILL.md` — skill Copilot para ROADMAP
