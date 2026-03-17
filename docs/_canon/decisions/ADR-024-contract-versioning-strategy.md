---
adr_id: ADR-024
title: "Contract Versioning Strategy"
status: accepted
date: "2026-03-17"
deciders: [product-owner, tech-lead]
decision: D2
tags: [versioning, contracts, api, governance]
---

# ADR-024 — Estratégia de Versionamento de Contratos

## Contexto

O HB Track usa Contract-Driven Development (CDD). À medida que o produto evolui,
mudanças nos contratos OpenAPI podem ser incompatíveis com consumidores existentes.
Antes de qualquer módulo entrar em produção, é necessário definir como gerenciar
essas mudanças.

**Decisão D2 obtida:** Opção B — SemVer sem versões paralelas.
Contratos têm número de versão (SemVer), mas apenas **uma versão ativa** é mantida
em produção. Quando uma versão quebra compatibilidade, consumidores devem migrar.

Escolhida porque o HB Track é um app interno — não há parceiros externos que
impossibilitem coordenar a migração.

## Decisão

### Estratégia: SemVer sem multi-versão

O campo `info.version` do `contracts/openapi/openapi.yaml` segue SemVer
(MAJOR.MINOR.PATCH). Existe sempre **apenas uma versão de contrato ativa**;
não há prefixo URI de versão (`/v1/`, `/v2/`).

### Política de versionamento

#### Quando incrementar MAJOR (mudança breaking)
- Remoção de campo obrigatório de request/response
- Mudança de tipo de campo existente
- Remoção de endpoint
- Mudança semântica significativa de comportamento

#### Quando incrementar MINOR (mudança aditiva)
- Adição de campo opcional em response
- Adição de novo endpoint

#### Quando incrementar PATCH (correção)
- Correções de bug sem mudança de interface
- Melhoria de descrição/documentação

### Fluxo de mudança breaking

1. O agente exibe `BLOCKED_VERSIONING_MISSING` se uma mudança breaking não tiver
   incrementado o MAJOR no `openapi.yaml`
2. O consumidor (app mobile/web) deve ser atualizado na mesma janela de release
3. Não há período de suporte à versão anterior

### Estrutura de paths

Paths mantidos diretamente em `contracts/openapi/paths/` sem prefixo de versão.
Quando necessário (pós v1.0), subdiretórios podem ser criados por feature, não
por versão.

## Consequências

### Positivas
- Manutenção simples: apenas uma versão ativa
- Sem overhead de manter N contratos paralelos em CI
- Release cadence mais rápida

### Negativas
- Mudanças breaking exigem coordenação simultânea com todos os consumers
- Não adequado se parceiros externos precisarem de janela longa de migração

### Re-avaliação
Se surgir integração com sistema externo que não pode migrar imediatamente,
reconsiderar para Opção A (ADR-024 revisão) com URI versioning multi-version.

### Gates gerados
- `VERSIONING_POLICY_GATE` — verifica conformidade com esta ADR no pipeline CI
- `BLOCKED_VERSIONING_MISSING` — emitido quando esta ADR está ausente

## Referências
- ADR-003 — Media-Type Versioning (complementar)
- ADR-014 — Deprecation Policy
- docs/_canon/API_CONVENTIONS.md
