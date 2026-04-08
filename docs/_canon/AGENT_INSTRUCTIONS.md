# HB TRACK — AGENT REFERENCE
> Auto-carregado pelo Claude Code em cada sessão. Não editar sem aprovar ADR.

## 0. LEIA PRIMEIRO
Se existir `SESSION_HANDOFF.md` na raiz → leia ANTES de qualquer outra coisa.

## 1. MODO DE OPERAÇÃO
- Boot mínimo: este arquivo + SESSION_HANDOFF.md (se existir) + ROADMAP.md (fase atual)
- Para regras detalhadas: `Read(".contract_driven/CONTRACT_SYSTEM_RULES.md")`
- Para layout canônico: `Read(".contract_driven/CONTRACT_SYSTEM_LAYOUT.md")`
- Para pipeline oficial: `Read("docs/_canon/CONTRACT_PIPELINE.md")`
- Perfis formais de boot vivem em `.contract_driven/BOOT_PROFILES.yaml`; todos os `load_sequence` são resolvidos a partir da raiz do repositório e falham se o path não existir.
- NUNCA carregar a trilogia completa de uma vez. Ler seções específicas on-demand.
- **Dois modos de operação existem: Modo CDD (contratos) e Modo ROADMAP (implementação). Nunca misturar.**

## 2. SISTEMA: O QUE É
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos são SSOT antes de qualquer código.
Humano é leigo em desenvolvimento — comunicar em linguagem de produto, nunca em jargão técnico.

## 3. 17 MÓDULOS CANÔNICOS
> **SSOT**: `docs/_canon/MODULE_REGISTRY.yaml` — consulte para status atual de cada módulo

## 4. TASK TYPES → WORKERS
> **SSOT**: `.contract_driven/TASK_CATALOG.yaml` — consulte para task routing atualizado (lista completa e status)

Ponto de entrada para tarefas **CDD**: `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`
Para `execute_roadmap_phase`: usar worker diretamente — **NÃO passa por `pre_contract_orchestrator`**.

## 5. REGRAS CORE (árvore de decisão)
0. **Modo ROADMAP?** (`execute_roadmap_phase` / fase 0-13 / infra / CI-CD / frontend / deploy) → ler `ROADMAP.md` + `SESSION_HANDOFF.md` + worker `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md`. **STOP — regras §5.1–§5.9 não se aplicam (modo CDD).**
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
- **CLI:** `scripts/hb` (hb verify | hb check | hb artifact) — Modo CDD apenas
- **ROADMAP:** `ROADMAP.md` (fases 0-13, critérios de done, stack canônica) — Modo ROADMAP
- **Hook:** `scripts/git-hooks/pre-commit` (via git config core.hooksPath)

Paths: [CONTRACT_PIPELINE.md](docs/_canon/CONTRACT_PIPELINE.md) | [Rules](.contract_driven/CONTRACT_SYSTEM_RULES.md) | [Workers](.contract_driven/agent_prompts)

## 8. CADEIA DE PRECEDÊNCIA DE AUTORIDADE (idêntica em CONTRACT_SYSTEM_RULES.md §5.0)

Em qualquer conflito de regra, schema, gate ou política, a resolução segue esta ordem (maior autoridade primeiro):

```
1. enforcement executável     scripts/hb, validate_contracts.py, gates ativos
2. schemas ativos             contracts/schemas/shared/*.schema.json
3. canon                      docs/_canon/ + .contract_driven/CONTRACT_SYSTEM_RULES.md
4. bridge docs                .github/copilot-instructions.md, CLAUDE.md, skills/**
5. artefatos derivados        _archive/DEVCONT.md, _archive/compilance.md, _archive/ADVERSARIAL.md, _archive/ANALISEARQUITETURA.md
6. legado                     _archive/, _reports/evidence/, docs/guias/
```

**Regra de ouro**: bridge docs e artefatos derivados (níveis 4–6) **nunca** podem redefinir, sobrepor ou contradizer os itens dos níveis 1–3. Bridge docs só podem **repetir** o que o enforcement e o canon já estabelecem. Qualquer divergência é resolvida sempre a favor do nível mais alto.
