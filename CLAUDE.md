# HB TRACK — Claude Instructions

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este arquivo é uma ponte operacional para o agente Claude. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este arquivo.

> Instruções canônicas em `docs/_canon/AGENT_INSTRUCTIONS.md` — ler esse arquivo primeiro.

## Boot mínimo
1. Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (este arquivo é apenas um ponteiro)
2. Se existir `SESSION_HANDOFF.md` na raiz → ler ANTES de qualquer outra coisa
3. Ler `ROADMAP.md` — fase atual do projeto e estado de implementação
4. Regras detalhadas: `.contract_driven/CONTRACT_SYSTEM_RULES.md`

## Resumo rápido
- **Produto:** HB Track — plataforma de gestão esportiva para handebol
- **Metodologia:** CDD (Contract-Driven Development) — contratos são SSOT antes de código
- **Humano:** leigo em desenvolvimento — comunicar em linguagem de produto, nunca jargão
- **17 módulos canônicos** → ver `docs/_canon/MODULE_REGISTRY.yaml` (SSOT)
- **Task types → workers** → ver `.contract_driven/TASK_CATALOG.yaml` (SSOT — não usar número fixo)
- **Pipeline obrigatório:** `hb verify` antes de tarefas de contrato; `hb artifact <path>` após artefato canônico

## Dois modos de operação

### Modo CDD (contratos)
Tarefas de criação, revisão ou validação de contratos (OpenAPI, AsyncAPI, Schemas, State Models, UI Contracts).
- Ponto de entrada: `pre_contract_orchestrator`
- Rotear via `.contract_driven/TASK_CATALOG.yaml`
- Executar `hb verify` antes; `hb artifact <path>` após

### Modo ROADMAP (implementação)
Tarefas de implementação de fases do produto: ambiente, infraestrutura, código de aplicação, CI/CD, frontend, deploy.
- Ponto de entrada: ler `ROADMAP.md` + fase declarada no `SESSION_HANDOFF.md`
- **Não** rotear por `pre_contract_orchestrator` — são modos distintos e incompatíveis
- Fases são sequenciais e bloqueantes: não iniciar fase N sem critério de Done da fase N-1 confirmado
- Fase atual do projeto: verificar `SESSION_HANDOFF.md` + seção "Estado atual" do `ROADMAP.md`

### Regras transversais (valem nos dois modos)
- Nunca inventar módulos fora dos 17 canônicos do `MODULE_REGISTRY.yaml`
- `generate_frontend` está FROZEN no TASK_CATALOG: FASE 5 usa **código React manual** + `openapi-typescript` — não bloquear por causa do worker frozen
- `schema.d.ts` **NUNCA** é editado manualmente — apenas regenerar com `npm run api:generate`
- Deploy de produção **requer aprovação humana explícita** — nunca executar autonomamente
- Waivers ativos: verificar `.contract_driven/waivers.json` antes de iniciar qualquer pipeline
- **Tasks de infra/deploy/CI-CD/VPS:** ler bundles operacionais frescos antes de qualquer ação:
  - `compiled_context/ops/deploy.json` → secrets, CI/CD, fluxo de deploy, ambientes
  - `compiled_context/ops/runtime.json` → topologia de serviços, endpoints, VPS
  - Nunca inferir dados de infra sem bundle fresco. Se ausente ou stale: emitir `BLOCKED_OPS_BUNDLE_STALE`
