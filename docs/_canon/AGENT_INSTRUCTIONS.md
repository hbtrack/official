< ⚠️  UNDER REVIEW FOR C4 CONSOLIDATION (Sovereign Integrity Audit) -->
# HB TRACK — AGENT REFERENCE
> Auto-carregado pelo Claude Code em cada sessão. Não editar sem aprovar ADR.

## 0. LEIA PRIMEIRO
Se existir `SESSION_HANDOFF.md` na raiz → leia ANTES de qualquer outra coisa.

## 1. MODO DE OPERAÇÃO
- Boot mínimo: este arquivo + SESSION_HANDOFF.md (se existir)
- Para regras detalhadas: `Read(".contract_driven/CONTRACT_SYSTEM_RULES.md")`
- Para layout canônico: `Read(".contract_driven/CONTRACT_SYSTEM_LAYOUT.md")`
- Para pipeline oficial: `Read("docs/_canon/CONTRACT_PIPELINE.md")`
- NUNCA carregar a trilogia completa de uma vez. Ler seções específicas on-demand.

## 2. SISTEMA: O QUE É
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos são SSOT antes de qualquer código.
Humano é leigo em desenvolvimento — comunicar em linguagem de produto, nunca em jargão técnico.

## 3. 17 MÓDULOS CANÔNICOS
> **SSOT**: `docs/_canon/MODULE_REGISTRY.yaml` — consulte para status atual de cada módulo

## 4. TASK TYPES → WORKERS
> **SSOT**: `.contract_driven/TASK_CATALOG.yaml` — consulte para task routing atualizado (lista completa e status)

Ponto de entrada OBRIGATÓRIO para todos: `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`

## 5. REGRAS CORE (árvore de decisão)
1. Existe SESSION_HANDOFF.md? → ler antes de qualquer outra coisa
2. task_type está no mapa (§4)? → identificar worker destino
3. módulo existe nos 17 canônicos do MODULE_REGISTRY.yaml? → prosseguir | senão → BLOCKED_MISSING_MODULE
4. artefatos obrigatórios do módulo existem? → prosseguir | senão → BLOCKED_REQUIRED_ARTIFACT_MISSING
5. decisões arquiteturais bloqueantes abertas? → Fase 2 (Decision Discovery) | senão → prosseguir
6. worker destino existe? → prosseguir | senão → BLOCKED_MISSING_AGENT_PROMPT
7. Executar worker com contexto de domínio montado na Fase 3 do orchestrator
8. **PIPELINE**: antes de iniciar qualquer tarefa de contrato → `hb verify` (DONE = exitcode 0)
9. **PIPELINE**: após criar/modificar artefato canônico → `hb artifact <path>` (DONE = exitcode 0)

## 6. COMUNICAÇÃO COM O HUMANO
- Nunca jargão sem tradução
- Decisão arquiteural → "3 opções + rec" em linguagem de produto
- Bloqueio → explicar EM PORTUGUÊS o que falta

## 7. SSOT CRÍTICOS (on-demand)
- **Module taxonomy:** `docs/_canon/MODULE_REGISTRY.yaml`
- **Task routing:** `.contract_driven/TASK_CATALOG.yaml`
- **Boot profiles:** `.contract_driven/BOOT_PROFILES.yaml`
- **Gate metadata:** `docs/_canon/gates/GATES_REGISTRY.yaml`
- **Evidence:** `_reports/session_start.json`
- **CLI:** `scripts/hb` (hb verify | hb check | hb artifact)
- **Hook:** `scripts/git-hooks/pre-commit` (via git config core.hooksPath)

Paths: [CONTRACT_PIPELINE.md](docs/_canon/CONTRACT_PIPELINE.md) | [Rules](.contract_driven/CONTRACT_SYSTEM_RULES.md) | [Workers](.contract_driven/agent_prompts)
