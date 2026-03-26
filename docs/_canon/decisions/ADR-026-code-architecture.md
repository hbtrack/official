---
adr_id: ADR-026
title: "Code Architecture — Clean Architecture + Ports & Adapters"
status: superseded
date: "2026-03-17"
deciders: [product-owner, tech-lead]
decision: D4
state_semantics: governance
supersedes: []
superseded_by: [ADR-031]
related_adrs: [ADR-030]
tags: [architecture, clean-architecture, fastapi, python, postgresql]
---

# ADR-026 — Arquitetura de Código

> Status operacional: `superseded` para definição de stack desde 2026-03-17 por [ADR-031](ADR-031-backend-framework.md).
> Este ADR permanece apenas como registro da decisão original e dos princípios de organização em camadas.

## Contexto

Com a decisão D4 (stack tecnológica = Python/FastAPI/PostgreSQL/React Native),
é necessário documentar formalmente como o código será organizado para garantir:
1. Coerência entre os contratos OpenAPI (SSOT) e o código gerado
2. Testabilidade e manutenibilidade a longo prazo
3. Separação clara entre regras de negócio e infraestrutura

## Decisão

### Clean Architecture com Ports & Adapters

Adotar Clean Architecture em 4 camadas:
- **Domain** — entidades, regras de negócio, FSM, invariantes
- **Application** — use cases (um por feature do FEATURE_REGISTRY)
- **Infrastructure** — repositórios SQLAlchemy, modelos ORM
- **Interface** — FastAPI routers (implementam os Ports do contrato OpenAPI)

Os contratos OpenAPI em `contracts/openapi/` são os **Ports** da camada Interface.
Nenhuma lógica de negócio vive no router. Nenhum detalhe de infra vive no domain.

### Stack completa

> Conteúdo histórico. A stack abaixo não é mais a stack vigente do repositório.

Backend: Python 3.12 + FastAPI + SQLAlchemy 2.x async + PostgreSQL 16 + Alembic
Frontend: React Native (Expo)
Testes backend: pytest + httpx (async)
Testes frontend: Jest + React Native Testing Library
Containerização: Docker + Docker Compose

## Consequências

### Positivas
- Domínio testável em isolamento (sem banco, sem HTTP)
- Contratos como contrato formal entre Interface e consumidores
- Geração de código orientada por artefatos já existentes (schemas, contratos)
- Alinhamento com o ecossistema Python já usado nos scripts do projeto

### Negativas
- Mais arquivos do que uma estrutura flat — mitigado pelo worker generate_code
- React Native Expo requer Node.js no ambiente de dev

## Artefato normativo

Ver `docs/_canon/CODE_ARCHITECTURE.md` para detalhes de estrutura de pastas,
nomenclatura, regras de geração e configuração de serviços.

## Referências
- ADR-019 — Layer Separation (Domain / DTO / ViewModel)
- ADR-025 — CDCT Pact Strategy (testes de integração)
- `docs/_canon/CODE_ARCHITECTURE.md`
- `docs/_canon/FEATURE_REGISTRY.yaml`
