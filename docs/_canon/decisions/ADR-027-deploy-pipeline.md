# ADR-027 — Deploy Pipeline Strategy

**Status:** accepted  
**Data:** 2026-03-17  
**Decisores:** Product Owner (D5, D6)  
**Decisões:** D5 = VPS Locaweb (Docker Compose) | D6 = Staging → aprovação → produção

## Contexto

O HB Track precisa de uma estratégia de deploy que:
1. Permita ao humano responsável ver o sistema funcionando em staging antes de ir a produção
2. Aproveite a infraestrutura VPS Locaweb já utilizada pelo Pact Broker (ADR-025)
3. Garanta rollback automático em caso de falha pós-deploy

## Decisão

**D5 — Plataforma:** VPS Locaweb com Docker Compose v2.  
Motivação: reutiliza servidor existente, elimina custo adicional de cloud, controle total sobre a infraestrutura.

**D6 — Fluxo:** Staging automático → aprovação humana explícita → produção.  
Motivação: zera risco de deploy acidental em produção; o responsável vê o sistema funcionando antes de aprovar.

## Fluxo resumido

```
push main → validate → test → build → deploy staging (auto)
         → notificação → aprovação humana → deploy production → health check
         → [falha] → rollback automático para imagem anterior
```

## Consequências

**Positivas:**
- Nenhum deploy vai direto para produção sem olhos humanos
- Rollback automático reduz tempo de recuperação para < 5 minutos
- GitHub Secrets protege todas as variáveis sensíveis
- Mesmo servidor do Pact Broker — custo zero adicional

**Negativas:**
- Aprovação manual adiciona latência ao ciclo de entrega
- VPS única = sem alta disponibilidade nativa (aceitável para fase inicial)

## Alternativas consideradas

- **A (Railway/Render/Fly.io):** descartado — custo recorrente desnecessário dado que VPS já existe
- **B (AWS/GCP/Azure):** descartado — complexidade desproporcional para o estágio atual

## Referências

- `docs/_canon/DEPLOY_PIPELINE.md` — documento normativo completo
- `.github/workflows/deploy.yml` — implementação do pipeline
- ADR-025: estratégia CDCT / Pact Broker (mesma VPS)
- ADR-026: arquitetura de código (código a ser deployado)
