# HB TRACK — Claude Instructions

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este arquivo é uma ponte operacional para o agente Claude. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este arquivo.

> Instruções canônicas em `docs/_canon/AGENT_INSTRUCTIONS.md` — ler esse arquivo primeiro.

## Boot mínimo
1. Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (SSOT de regras de boot)
2. Se existir `SESSION_HANDOFF.md` na raiz → ler ANTES
3. Ler `ROADMAP.md` — fase atual
4. Regras detalhadas: `.contract_driven/CONTRACT_SYSTEM_RULES.md`
5. Pipeline CDD: `docs/_canon/CONTRACT_PIPELINE.md` (sequência canônica)

## Resumo rápido
- **Produto:** HB Track — plataforma para handebol
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
- **Primeiro:** lookup em `merge-readiness.json` pelo `context` do check falho
- **Proibido:** inferir `local_equivalent`; alterar governance sem falha explícita
- Executor: `python3 scripts/hb ci --profile pr`

### Regras transversais (valem nos dois modos)
- Nunca inventar módulos fora dos 17 canônicos do `MODULE_REGISTRY.yaml`
- `generate_frontend` está FROZEN: FASE 5 usa **código React manual** + `openapi-typescript`
- `schema.d.ts` **NUNCA** é editado manualmente — apenas regenerar com `npm run api:generate`
- Deploy de produção **requer aprovação humana explícita**
- Verificar `.contract_driven/waivers.json` antes de iniciar qualquer pipeline

## Exposição por plataforma

Claude opera por paridade operacional documentada, não por UI dedicada. Papéis possíveis: `HB Contract`, `Hb Implementer`, `Hb Adversarial Tester`, `HandTracker`.

## Revisão adversarial externa

Claude atua como **tester externo final** usando apenas pacote estruturado de evidências: `approved_plan_path`, `PR_URL`, `current_state.json`, `implementation_evidence_pack.json`, `plan_to_diff_trace.json`, `negative_test_manifest.json`, `adversarial_report.json`, diff, comandos e saídas brutas. Sem narrativa, otimismo ou opinião do executor. Conclusão condicionada a gates executáveis.
