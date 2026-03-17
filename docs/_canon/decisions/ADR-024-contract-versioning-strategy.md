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
essas mudanças sem quebrar os consumidores.

**Decisão D2 obtida:** Opção A — Manter versão antiga funcionando por 6 meses
(URI versioning com suporte paralelo de versões).

Escolhida porque o HB Track planeja integrações com sistemas externos (clubes,
federações) e não pode forçar migração imediata.

## Decisão

### Estratégia: URI Versioning com Versões Paralelas

Todos os endpoints do HB Track são prefixados com a versão major da API:

```
/v1/training/sessions
/v2/training/sessions   (quando v2 for lançada)
```

### Política de versionamento

#### Quando criar nova versão major (vN → vN+1)
- Remoção de campo obrigatório de request/response
- Mudança de tipo de campo existente
- Remoção de endpoint
- Mudança semântica significativa de comportamento

#### Versões menores e patches (sem quebra de compatibilidade)
- Adição de campo opcional em response (SemVer minor: 1.1.0)
- Correções de bug sem mudança de interface (SemVer patch: 1.0.1)
- Adição de novo endpoint na mesma versão major

#### Janela de suporte
- Versão anterior permanece ativa por **mínimo de 6 meses** após o lançamento da nova major
- Endpoint deprecado recebe header `Sunset: <data>` em toda resposta
- Header `Deprecation: true` + `Link: </v2/...>; rel="successor-version"` são obrigatórios

### Versionamento do arquivo openapi.yaml

O campo `info.version` segue SemVer (MAJOR.MINOR.PATCH):
- MAJOR = versão da API (alinhado ao prefixo URI /v{MAJOR}/)
- MINOR = mudanças aditivas retrocompatíveis
- PATCH = correções sem mudança de interface

Versão atual ao adotar esta política: **1.0.0** (primeira versão estável formal)

### Estrutura de paths

```
contracts/openapi/paths/
  v1/
    training.yaml
    users.yaml
    ...
  v2/               ← criado quando primeira versão major nova for necessária
    training.yaml
    ...
```

A versão atual (`v1`) é mantida diretamente em `contracts/openapi/paths/` por
retrocompatibilidade com o baseline existente. Nova versão major cria subdiretório.

## Consequências

### Positivas
- Consumidores externos (clubes, federações) têm 6 meses para migrar
- Nenhuma surpresa: mudanças quebradas sempre têm nova URI
- Auditabilidade: cada versão de contrato é um artefato rastreável

### Negativas
- Custo de manutenção: duas versões da mesma feature ativas por até 6 meses
- Complexidade de testes: ambas as versões precisam ser testadas

### Gates gerados
- `VERSIONING_POLICY_GATE` — verifica conformidade com esta ADR no pipeline CI
- `BLOCKED_VERSIONING_MISSING` — emitido quando esta ADR está ausente

## Referências
- ADR-003 — Media-Type Versioning (complementar)
- ADR-014 — Deprecation Policy
- [RFC 8594 — The Sunset HTTP Header](https://www.rfc-editor.org/rfc/rfc8594)
- docs/_canon/API_CONVENTIONS.md
