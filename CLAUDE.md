# HB TRACK — Claude Instructions

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este arquivo é uma ponte operacional para o agente Claude. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este arquivo.

> Instruções canônicas em `docs/_canon/AGENT_INSTRUCTIONS.md` — ler esse arquivo primeiro.

## Boot mínimo
1. Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (este arquivo é apenas um ponteiro — **SSOT de regras de boot**)
2. Se existir `SESSION_HANDOFF.md` na raiz → ler ANTES de qualquer outra coisa
3. Ler `ROADMAP.md` — fase atual do projeto e estado de implementação
4. Regras detalhadas: `.contract_driven/CONTRACT_SYSTEM_RULES.md`
5. Pipeline CDD: `docs/_canon/CONTRACT_PIPELINE.md` (**SSOT de sequência canônica de fases**)

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

### Modo PR_FIX (correção de CI)
- Ponto de entrada: task_type `pr_fix` → worker `.contract_driven/agent_prompts/pr_fix.prompt.md`
- **Primeiro passo:** lookup em `merge-readiness.json` pelo `context` do check falho
- **Proibido:** inferir `local_equivalent`; alterar governance sem falha explícita de gate
- Executor: `python3 scripts/hb ci --profile pr`
- Incompatível com pipeline CDD

### Regras transversais (valem nos dois modos)
- Nunca inventar módulos fora dos 17 canônicos do `MODULE_REGISTRY.yaml`
- `generate_frontend` está FROZEN no TASK_CATALOG: FASE 5 usa **código React manual** + `openapi-typescript` — não bloquear por causa do worker frozen
- `schema.d.ts` **NUNCA** é editado manualmente — apenas regenerar com `npm run api:generate`
- Deploy de produção **requer aprovação humana explícita** — nunca executar autonomamente
- Waivers ativos: verificar `.contract_driven/waivers.json` antes de iniciar qualquer pipeline

## Exposição por plataforma

- Neste repositório, **não** existe mecanismo equivalente a `.github/agents/*.agent.md`
  para criar agentes separados de dropdown para Claude.
- Não existe mecanismo equivalente a `.github/agents/*.agent.md` para Claude.
- Claude opera por paridade operacional documentada, não por UI dedicada.
- Papéis que Claude pode exercer conceitualmente:
  - `HB Contract`
  - `Hb Implementer`
  - `Hb Adversarial Tester`
  - `HandTracker`

## Revisão adversarial externa

- Nesta trilha, o uso recomendado de Claude é como **tester externo final**.
- Claude deve receber apenas um pacote estruturado de evidências:
  - `approved_plan_path`
  - `PR_URL`
  - `current_state.json`
  - `implementation_evidence_pack.json`
  - `plan_to_diff_trace.json`
  - `negative_test_manifest.json`
  - `adversarial_report.json`, se existir
  - diff, comandos executados, saídas brutas e limitações declaradas
- Claude **não** deve usar narrativa longa do implementador, resumo otimista,
  opinião do executor ou conclusão persuasiva como evidência.
- Claude atua como adversário externo, tentando invalidar a implementação.
- Claude **não** é autoridade final: a conclusão continua condicionada aos gates
  executáveis (`pytest`, `scripts/hb validate`, `validate_contracts.py`, CI).
- Claude não é autoridade final.
