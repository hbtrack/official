# ADR-029 — Runtime Contract Monitoring Strategy

**Status:** accepted
**Data:** 2026-03-17
**Decisores:** Equipe técnica (sem decisão humana adicional necessária)
**Stack:** OpenTelemetry + Prometheus + Grafana + Sentry + FastAPI middleware

## Contexto

Um contrato OpenAPI define o comportamento esperado da API. Após o deploy, é necessário
garantir que o comportamento real em produção não divirja do contrato — caso contrário,
consumers (o app mobile) podem quebrar silenciosamente.

## Decisão

**Abordagem:** monitoramento em camadas — middleware de validação inline + observabilidade externa.

1. **FastAPI middleware** valida request/response contra o OpenAPI no momento da chamada
2. **OpenTelemetry** instrumenta todos os traces sem vendor lock-in
3. **Prometheus + Grafana** coleta métricas de SLA e error rates
4. **Sentry** captura exceções de runtime e contract violations

**Modo de operação por ambiente:**
- Desenvolvimento e Staging: modo bloqueante (error 500 se violação)
- Produção: modo observação (loga violation + header, nunca bloqueia usuário)

**Critério de alerta:** violação de contrato detectada em produção → BLOCKED_CONTRACT_CONFLICT
automaticamente registrado + worker `contract_revision` acionado.

## Consequências

**Positivas:**
- Divergências entre contrato e implementação são detectadas antes de afetarem usuários
- OpenTelemetry garante portabilidade — sem lock-in em Datadog, New Relic, etc.
- Modo observação em produção é seguro — nunca bloqueia o usuário

**Negativas:**
- Middleware de validação adiciona ~1-3ms de latência por request (aceitável)
- Requer infraestrutura adicional (Prometheus, Grafana) na VPS Locaweb

## Alternativas consideradas

- **Só Sentry:** descartado — não tem contract validation nativa
- **Optic exclusivo:** descartado — requer proxy externo no tráfego
- **Sem monitoramento:** descartado — impossível detectar regression sem observabilidade

## Referências

- `docs/_canon/RUNTIME_CONTRACT_MONITORING_POLICY.md` — política normativa completa
- ADR-026: arquitetura de código (middleware no layer Interface)
- ADR-027: deploy pipeline (rollback conectado ao monitoramento)
