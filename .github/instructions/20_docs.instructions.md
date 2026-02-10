---
description: Carregar quando a tarefa envolver criação/edição de documentação (docs/_canon, guides, ADRs, changelog/executionlog).
applyTo: "docs/**, Hb Track - Backend/docs/**"
---
Regras de documentação:
- SSOT de comportamento é o código + docs/_generated quando aplicável. Não inventar.
- Evitar duplicar prompts em instruções; manter prompts em `docs/_canon/06_AGENT_PROMPTS_MODELS.md` e referenciar por link/path.
- Atualizar CHANGELOG/EXECUTIONLOG somente no final de um lote (commit separado), nunca durante varredura/correção automática.
