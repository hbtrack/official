---
adr_id: ADR-030
title: "Frontend Strategy"
status: accepted
date: "2026-03-17"
deciders: [product-owner, tech-lead]
decision: D7
state_semantics: governance
supersedes: []
superseded_by: []
related_adrs: [ADR-031]
---

# ADR-030 — Frontend Strategy

**Status:** accepted
**Data:** 2026-03-17
**Decision ref:** D7
**Decidido por:** humano (recomendação aplicada: Opção D)
**Relação com ADR-031:** este ADR define frontend. ADR-031 não o supersede; apenas o referencia na stack consolidada.

---

## Contexto

O HB Track precisa de uma interface para os usuários (treinadores, atletas, gestores de clube).
A decisão D7 define qual plataforma será usada e em qual ordem será desenvolvida.

As opções avaliadas foram:
- **A** — Só app mobile (iOS + Android)
- **B** — Só web (navegador)
- **C** — App mobile + web simultâneos
- **D** — Começar pela web, adicionar mobile depois ← **escolhida**

## Decisão

**Opção D — Web primeiro (React + Vite), mobile depois (React Native + Expo).**

## Justificativa

1. **Ciclo de desenvolvimento mais rápido:** web não requer distribuição via App Store/Play Store,
   permitindo validar funcionalidades com usuários reais mais cedo.
2. **Reaproveitamento de código:** ao usar React no web e React Native no mobile, a lógica de
   negócio (hooks, utils, API client) pode ser compartilhada via monorepo.
3. **Validação de produto:** melhor esperar o produto estabilizar no web antes de investir na
   complexidade adicional do desenvolvimento mobile.
4. **Stack unificada:** TypeScript em toda a camada de frontend reduz a curva de aprendizado
   e permite que a IA gere código consistente entre plataformas.

## Consequências

### Positivas
- Frontend web entregue antes do mobile, valor mais rápido para o produto
- Tipos TypeScript gerados do OpenAPI garantem contrato frontend-backend sem drift
- Base de código reutilizável quando mobile for implementado na v2.0

### A monitorar
- Experiência no mobile pode ser inferior até a v2.0 (utilizável via browser mobile)
- Quando mobile for implementado, garantir que os hooks sejam agnósticos de plataforma

## Artefatos criados/modificados

- `docs/_canon/FRONTEND_CONTRACT.md` — define stack, regras e organização de pastas
- `.contract_driven/agent_prompts/generate_frontend.prompt.md` — worker de geração de código frontend
- `docs/_canon/gates/GATES_REGISTRY.yaml` — gate `FRONTEND_CONTRACT_GATE` adicionado

## Referências

- [FRONTEND_CONTRACT.md](../FRONTEND_CONTRACT.md)
- [CODE_ARCHITECTURE.md](../CODE_ARCHITECTURE.md) — arquitetura do backend (D4)
- [ADR-026-code-architecture.md](ADR-026-code-architecture.md) — stack backend
- [FEATURE_REGISTRY.yaml](../FEATURE_REGISTRY.yaml) — features a implementar no frontend
