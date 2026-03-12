# HB Track

**Plataforma sports-tech de gestão de handebol** — operações, treinamento, jogos, competições e analytics por contratos fortes.

| Item | Valor |
|------|-------|
| Status do sistema | Ativo — em desenvolvimento iterativo |
| Maturidade CDD | Nível 3 — contratos de módulo + invariantes + test matrix |
| Última revisão | 2026-03-11 |

---

## O que é o HB Track?

O HB Track é uma plataforma de gestão esportiva voltada ao handebol indoor brasileiro. Seu modelo de desenvolvimento é **contract-driven**: nenhum componente público nasce primeiro no código. Contratos OpenAPI, invariantes documentadas e schemas canônicos precedem a implementação.

| Dimensão | Descrição |
|----------|-----------|
| Tipo de sistema | Monólito modular em camadas (FastAPI) com SPA (Next.js 13+) |
| Mercado primário | Handebol indoor — Brasil |
| Usuários-alvo | Dirigentes, Coordenadores, Treinadores, Atletas e Membros |
| Modelo de governança | Contract-Driven Development (CDD) com hierarquia normativa explícita |

---

## Stack

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Backend runtime** | Python | 3.11.9 |
| **Framework HTTP** | FastAPI | latest compat. |
| **ORM** | SQLAlchemy | latest compat. |
| **Migrations** | Alembic | latest compat. |
| **Workers assíncronos** | Celery | latest compat. |
| **Broker + cache** | Redis | 7 (Alpine) |
| **Banco (VPS prod/staging)** | PostgreSQL | 15 |
| **Banco (dev local Docker)** | PostgreSQL | 12 |
| **Framework frontend** | Next.js | 13+ (App Router) |
| **Linguagem frontend** | TypeScript | latest compat. |
| **Estilo** | TailwindCSS | latest compat. |
| **Testes backend** | pytest + Schemathesis | — |
| **Testes frontend** | Jest | — |

---

## Estrutura do Repositório

```
HB TRACK/
├── Hb Track - Backend/          # API FastAPI + workers Celery
│   ├── app/
│   │   ├── api/                 # Routers FastAPI por módulo
│   │   ├── services/            # Lógica de negócio
│   │   ├── repositories/        # Acesso a dados (SQLAlchemy)
│   │   └── models/              # Modelos ORM
│   └── tests/                   # Testes backend (pytest + Schemathesis)
│
├── Hb Track - Frontend/         # SPA Next.js 13+ (App Router)
│   ├── src/app/                 # Pages e layouts (App Router)
│   ├── src/components/          # Componentes React
│   └── src/api/generated/       # Client HTTP gerado via OpenAPI generator
│
├── docs/_canon/                 # *** Documentação canônica normativa (ler primeiro) ***
│   ├── README.md                # Este guia de navegação
│   ├── SYSTEM_SCOPE.md          # Missão, atores, macrodomínios, fora do escopo
│   ├── ARCHITECTURE.md          # Stack canônica, princípios, camadas
│   ├── MODULE_MAP.md            # 16 módulos, responsabilidades, dependências
│   ├── API_CONVENTIONS.md       # Visão geral de API (SSOT em .contract_driven/templates/API_RULES/API_RULES.yaml)
│   ├── DATA_CONVENTIONS.md      # IDs, datas, enums, soft delete, convenções DB
│   ├── ERROR_MODEL.md           # Modelo canônico de erros HTTP
│   ├── GLOBAL_INVARIANTS.md     # Invariantes globais (INV-*)
│   ├── SECURITY_RULES.md        # Regras globais de segurança
│   ├── CI_CONTRACT_GATES.md     # Gates de validação de contratos
│   ├── TEST_STRATEGY.md         # Estratégia canônica de testes
│   ├── UI_FOUNDATIONS.md        # Fundamentos de UI/UX
│   ├── DESIGN_SYSTEM.md         # Design system (tokens, componentes)
│   ├── C4_CONTEXT.md            # C4 — Contexto
│   ├── C4_CONTAINERS.md         # C4 — Containers
│   └── HANDBALL_RULES_DOMAIN.md # 14 regras IHF documentadas
│
├── docs/hbtrack/modulos/        # Documentação por módulo (training, competitions, etc.)
│
├── .contract_driven/            # Sistema de contratos (regras, layout, templates)
│   ├── CONTRACT_SYSTEM_RULES.md # Regras operacionais do sistema CDD
│   ├── CONTRACT_SYSTEM_LAYOUT.md# Estrutura canônica de arquivos
│   ├── GLOBAL_TEMPLATES.md      # Templates oficiais de artefatos
│   └── API_RULES/               # SSOT de regras/templates/validações de API HTTP
│       └── API_RULES.yaml
│
├── scripts/                     # CLI de governança
│   ├── run/hb_cli.py            # CLI oficial (plan, report, verify, seal, check, gates)
│   ├── run/hb_watch.py          # Dashboard de desenvolvimento
│   └── git-hooks/pre-commit     # Enforcement de governança no commit
│
└── infra/                       # Docker Compose e infraestrutura local
    └── docker-compose.yml
```

---

## Como Navegar

Para Agentes de IA, o ponto de entrada correto é:

1. Leia **`docs/_canon/README.md`** — entenda o sistema de documentação e a hierarquia normativa
2. Leia **`docs/_canon/SYSTEM_SCOPE.md`** — entenda o escopo do sistema, os atores e os macrodomínios
3. Leia **`.contract_driven/CONTRACT_SYSTEM_RULES.md`** — entenda as regras do sistema contract-driven
4. Leia **`.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`** — entenda a estrutura canônica de arquivos e artefatos
5. Leia **`.contract_driven/GLOBAL_TEMPLATES.md`** — familiarize-se com os templates oficiais de artefatos (contratos, invariantes, etc.)
6. Leia **`.contract_driven/templates/API_RULES/API_RULES.yaml`** — SSOT para convenções/validações/templates de API HTTP (OpenAPI/JSON/URLs/paginação/erros/segurança)
7. Leia **`docs/_canon/ARCHITECTURE.md`** — entenda a arquitetura canônica, a stack e os princípios de design
8. Depois, navegue para o módulo em que for trabalhar: `docs/hbtrack/modulos/<módulo>/`

---

## 4 Regras Cardinais

1. **Contrato antes de implementação** — nenhum código sem contrato vigente. Endpoints, payloads, eventos e workflows nascem primeiro como contratos.

2. **Domínio antes de tecnologia** — regras de negócio e regras do handebol sobrepõem preferências técnicas. O domínio esportivo é a âncora, não a conveniência de implementação.

3. **Invariante imutável** — invariantes aprovadas (`INV-*`) só mudam por processo formal documentado. Constraints críticas vivem no banco, não apenas no código.

4. **SSOT único** — uma fonte de verdade por artefato. Duplicação de informação normativa é proibida. Se existe em `docs/_canon/`, não existe também no código-fonte como comentário solto.

---

## Fontes Canônicas (SSOT)

| Tema | Fonte canônica |
|------|---------------|
| Regras/templates de API HTTP (OpenAPI/JSON/URLs/paginação/erros/segurança) | `.contract_driven/templates/API_RULES/API_RULES.yaml` |
| Modelo de erro HTTP | `docs/_canon/ERROR_MODEL.md` |
| Regras globais de segurança | `docs/_canon/SECURITY_RULES.md` |
| Convenções de dados (IDs/datas/enums/soft delete/DB naming) | `docs/_canon/DATA_CONVENTIONS.md` |
| Política de mudança | `docs/_canon/CHANGE_POLICY.md` |

---

*Última revisão: 2026-03-11*
