# HB TRACK — AGENT REFERENCE
> Auto-carregado pelo Claude Code em cada sessão. Não editar sem aprovar ADR.

## 0. LEIA PRIMEIRO
Se existir `SESSION_HANDOFF.md` na raiz → leia ANTES de qualquer outra coisa.
Se existir `backloggov.md` → consulte para contexto de backlog de governança.

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

## 3. 16 MÓDULOS CANÔNICOS
users | seasons | teams | training | wellness | medical | competitions | matches
scout | exercises | analytics | reports | ai_ingestion | identity_access | audit | notifications

Status atual: training = implementation_ready | demais 15 = draft_contract

## 4. 9 TASK TYPES → WORKERS
new_module       → create_module_docs.prompt.md
new_contract     → create_openapi_contract.prompt.md
contract_revision→ create_openapi_contract.prompt.md
new_event        → create_asyncapi_contract.prompt.md
new_workflow     → create_arazzo_workflow.prompt.md
new_schema       → create_json_schema_contract.prompt.md
new_state_model  → create_state_model.prompt.md
new_ui_contract  → create_ui_contract.prompt.md
architecture_review → decision_discovery.prompt.md

Ponto de entrada OBRIGATÓRIO para todos: `pre_contract_orchestrator.prompt.md`

## 5. BLOQUEIOS CANÔNICOS (19 códigos)
BLOCKED_MISSING_MODULE            — módulo não existe no LAYOUT §2
BLOCKED_MISSING_AGENT_PROMPT      — worker não existe para o task_type
BLOCKED_REQUIRED_ARTIFACT_MISSING — artefato de módulo obrigatório ausente
BLOCKED_MISSING_ARCH_DECISION     — decisão obrigatória em aberto
BLOCKED_CONTRACT_CONFLICT         — duas fontes canônicas contraditórias
BLOCKED_MISSING_SCHEMA            — schema JSON ausente para o módulo
BLOCKED_SCHEMA_DRIFT              — schema diverge do resolved_policy
BLOCKED_DERIVED_DRIFT             — derivado diverge do soberano
BLOCKED_PATH_VIOLATION            — artefato no path errado
BLOCKED_AXIOM_VIOLATION           — viola DOMAIN_AXIOMS.json
BLOCKED_SCOPE_OVERFLOW            — operação fora do escopo do módulo
BLOCKED_REGISTRY_MISMATCH         — MODULE_REGISTRY diverge do estado real
BLOCKED_TOOLCHAIN_UNHEALTHY       — toolchain health check falhou
BLOCKED_SURFACE_MISSING           — surface esperada ausente no registry
BLOCKED_VERSIONING_MISSING        — sem estratégia de versionamento definida
BLOCKED_PACT_MISSING              — consumer contract ausente (quando CDCT ativo)
BLOCKED_ADVERSARIAL_PENDING       — análise adversarial não concluída
BLOCKED_FEATURE_UNREGISTERED      — feature não registrada no FEATURE_REGISTRY
BLOCKED_HANDOFF_INCOMPLETE        — handoff incompleto para implementação

## 6. REGRAS CORE (árvore de decisão)
1. Existe SESSION_HANDOFF.md? → ler antes de qualquer outra coisa
2. task_type está no mapa (§4)? → identificar worker destino
3. módulo existe nos 16 canônicos (§3)? → prosseguir | senão → BLOCKED_MISSING_MODULE
4. artefatos obrigatórios do módulo existem? → prosseguir | senão → BLOCKED_REQUIRED_ARTIFACT_MISSING
5. decisões arquiteturais bloqueantes abertas? → Fase 2 (Decision Discovery) | senão → prosseguir
6. worker destino existe? → prosseguir | senão → BLOCKED_MISSING_AGENT_PROMPT
7. Executar worker com contexto de domínio montado na Fase 3 do orchestrator

## 7. COMUNICAÇÃO COM O HUMANO
- Nunca usar jargão técnico sem tradução imediata
- Toda decisão arquitetural → apresentar como "3 opções + recomendação" em linguagem de produto
- Progresso → reportar como % de feature completa, não como % de endpoint implementado
- Quando bloquear → explicar EM PORTUGUÊS o que falta e o que o humano precisa decidir
- Perguntar uma decisão por vez, nunca empilhar perguntas técnicas
- Para regras completas de comunicação com o humano: `Read("docs/_canon/HUMAN_INTERFACE_POLICY.md")`

## 8. PATHS CRÍTICOS (on-demand)
Contratos OpenAPI:      contracts/openapi/
Schemas JSON:           contracts/schemas/
Módulos docs:           docs/hbtrack/modulos/<MODULE>/
Canon global:           docs/_canon/
Workers/Prompts:        .contract_driven/agent_prompts/
Regras sistema:         .contract_driven/CONTRACT_SYSTEM_RULES.md
Reports CI:             _reports/contract_gates/latest.json
Feature Registry:       docs/_canon/FEATURE_REGISTRY.yaml
Feature Report:         _reports/feature_readiness.json
Session handoff:        SESSION_HANDOFF.md
Interface humana:       docs/_canon/HUMAN_INTERFACE_POLICY.md
Playbook desbloqueio:   docs/_canon/UNBLOCKING_PLAYBOOK.md
