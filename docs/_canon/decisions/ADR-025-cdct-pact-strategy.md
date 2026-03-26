---
adr_id: ADR-025
title: "CDCT — Pact Strategy"
status: accepted
date: "2026-03-17"
deciders: [product-owner, tech-lead]
decisions: [D1, D3]
tags: [testing, pact, cdct, integration, vps]
---

# ADR-025 — Estratégia de Testes de Contrato entre Consumidor e Provedor (CDCT)

## Contexto

O HB Track usa os contratos OpenAPI como fonte primária da verdade (SSOT).
Para garantir que o consumidor (app) não quebre quando a API muda, adotamos
Consumer-Driven Contract Testing (CDCT) com Pact.

**Decisão D1 obtida:** Opção A — Apenas o próprio app HB Track consome a API.
Um único consumer registrado: `hbtrack-app`.

**Decisão D3 obtida:** Pact Broker auto-hospedado na VPS Locaweb com Docker.
Gratuito, controlado pela equipe, sem dependência de serviço externo pago.

## Decisão

### Consumers registrados

| Consumer | Tipo | Repositório |
|----------|------|-------------|
| `hbtrack-app` | App mobile/web HB Track | (definido na Fase 13) |

### Broker

- **Tipo:** Pact Broker OSS (auto-hospedado)
- **Infraestrutura:** VPS Locaweb — Docker Compose (ver `VPS/`)
- **URL interna:** `http://<VPS_IP>:9292` (configurar em CI via env var `PACT_BROKER_BASE_URL`)
- **Credenciais:** gerenciadas via secrets (ADR-012)

### Estrutura de artefatos

```
contracts/consumers/
  hbtrack-app/
    README.md        ← instruções de geração do consumer contract
    .gitkeep         ← placeholder até o app gerar o contrato
```

Consumer contracts (arquivos `.json` gerados pelo app) são publicados diretamente
no Pact Broker — NÃO versionados no repositório de contratos.

### Fluxo CDCT

```
APP (consumer) roda testes Pact
  → gera consumer contract (JSON)
  → publica no Pact Broker (VPS Locaweb)

API (provider) — no pipeline CI:
  → Pact Broker verifica se provider satisfaz consumer contract
  → PACT_PROVIDER_GATE: PASS | FAIL
```

### Gate de CI

`PACT_PROVIDER_GATE` — SKIP_NOT_APPLICABLE quando Pact Broker não está configurado
(env var `PACT_BROKER_BASE_URL` ausente). PASS quando provider satisfaz todos os
consumer contracts publicados no broker. FAIL → BLOCKED_PACT_MISSING.

O gate é **não-bloqueante** na fase atual (consumer contract ainda não existe).
Torna-se bloqueante quando o primeiro consumer contract for publicado no broker.

## Consequências

### Positivas
- Sem custo mensal (VPS já é pago)
- Controle total dos dados de contrato (sem enviar a serviço externo)
- Docker Compose facilita atualização e backup

### Negativas
- Manutenção do Pact Broker (atualizações de imagem Docker, backup do banco)
- VPS precisa estar online para CI funcionar (mitigar com health check)

### Ativação

O Pact Broker fica configurado mas não-bloqueante até:
1. O app (consumer) gerar e publicar o primeiro consumer contract
2. O provider (API) rodar verificação Pact pela primeira vez

Nesse momento, `PACT_PROVIDER_GATE` passa a ser bloqueante.

## Referências
- ADR-012 — Secrets Policy
- ADR-024 — Contract Versioning Strategy
- [Pact OSS Docs](https://docs.pact.io)
- `VPS/` — infraestrutura da VPS Locaweb
