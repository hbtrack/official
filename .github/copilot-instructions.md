# HB TRACK — Copilot Instructions

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este arquivo é uma ponte operacional para o agente Copilot. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este arquivo.

## Produto
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos governam autoria antes de código.
Comunicar em português claro.

## Fontes de verdade
- `docs/_canon/AGENT_INSTRUCTIONS.md`
- `docs/_canon/CONTRACT_PIPELINE.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/BOOT_PROFILES.yaml`
- `docs/_canon/MODULE_REGISTRY.yaml`
- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/hb`
- `scripts/contracts/validate/validate_contracts.py`
- `ROADMAP.md` (fases 0-13, critérios de done, stack canônica — Modo ROADMAP)

## Regra de boot
1. Se existir `SESSION_HANDOFF.md` na raiz, ler antes de qualquer ação.
2. Se não existir, continuar como sessão nova; não inventar contexto ausente.
3. Ler `ROADMAP.md` — fase atual do projeto e estado de implementação.

## Dois modos de operação

### Modo CDD (contratos)
Ponto de entrada: `pre_contract_orchestrator`. Usar `hb verify` + `hb artifact`. Ver "Regra operacional para tarefas de contrato" abaixo.

### Modo ROADMAP (implementação — fases 0-13)
Ponto de entrada: `ROADMAP.md` + `SESSION_HANDOFF.md` + `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md`.
- `hb verify --task-type execute_roadmap_phase --roadmap-phase <N>` **pode** ser usado para registrar estado de sessão (opcional mas recomendado)
- **NÃO** executar `hb check` nem `hb artifact` sobre artefatos de infraestrutura
- **NÃO** passar por `pre_contract_orchestrator`
- Verificar Critério de Done da fase N-1 antes de iniciar fase N
- Bloqueios: `BLOCKED_PHASE_DEPENDENCY` | `BLOCKED_CDD_PIPELINE_FAIL` | `BLOCKED_DEPLOY_REQUIRES_HUMAN` | `BLOCKED_MISSING_STACK_DECISION`

**Nunca misturar os dois modos.**

## Regra operacional para tarefas de contrato

Para tarefas que criam ou alteram artefatos governados:

```text
BOOT     -> ler AGENT_INSTRUCTIONS + SESSION_HANDOFF.md se existir
FASE 0   -> python3 scripts/hb verify --task-type <T> --module <M>
FASE 1   -> python3 scripts/hb check --module <M>
FASE 2   -> ler worker prompt -> criar artefatos -> python3 scripts/hb artifact <path>
COMPILE  -> compile_api_policy.py somente quando contrato/policy mudou
FASE 3   -> python3 scripts/contracts/validate/validate_contracts.py
FASE 4+  -> readiness/adversarial/generate_code somente se o task_type ou pré-condições exigirem
FECHAMENTO -> atualizar SESSION_HANDOFF.md
VCS      -> commit opcional conforme objetivo da sessão; o pre-commit adiciona um checkpoint extra
PRE-PUSH -> python3 scripts/hb preflight   (obrigatório antes de git push; reproduz CI localmente)
PUSH     -> git push somente após preflight PASS
```

## Sem falsa autonomia

- Worker = prompt especializado carregado pelo mesmo agente.
- Não assumir subagente autônomo, fila ou runtime distribuído.
- Não assumir que commit é o que faz os gates rodarem; os gates já rodam via `hb` e `validate_contracts.py`.

## Handoff

- `SESSION_HANDOFF.md` é o handoff operacional atual.
- `contracts/schemas/shared/session_handoff.schema.json` **é** o validador ativo do front matter YAML de `SESSION_HANDOFF.md` — usado pelo `HANDOFF_COHERENCE_GATE` em `validate_contracts.py`.
- O front matter deve ser válido contra esse schema; usar `docs/_canon/templates/SESSION_HANDOFF.template.md` como base.

## Bloqueios canônicos

Quando houver `BLOCKED_*`, informar o humano em português:

**Modo CDD:**
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_AGENT_PROMPT`
- `BLOCKED_REQUIRED_ARTIFACT_MISSING`
- `BLOCKED_MISSING_ARCH_DECISION`
- `BLOCKED_SCOPE_OVERFLOW`
- `BLOCKED_CONTRACT_CONFLICT`

**Modo ROADMAP:**
- `BLOCKED_PHASE_DEPENDENCY` — Critério de Done da fase N-1 não atingido
- `BLOCKED_CDD_PIPELINE_FAIL` — Pipeline CDD em FAIL e fase ≥ 4
- `BLOCKED_DEPLOY_REQUIRES_HUMAN` — Deploy de produção (fases 6, 9, 12) requer aprovação
- `BLOCKED_MISSING_STACK_DECISION` — Stack não definida para o artefato a criar

## Regras de ouro

**Modo CDD:**
- Nunca pular `hb verify` antes de authoring.
- Nunca criar artefato fora de path canônico.
- Sempre registrar artefato com `hb artifact`.
- Sempre ler o worker prompt correspondente.
- Sempre atualizar `SESSION_HANDOFF.md` ao fechar a sessão.
- Sempre executar `python3 scripts/hb preflight` antes de `git push` — garante paridade local=CI (63 gates, 7 test suites, 3 compilers).
- Nunca fazer `git push` sem preflight PASS.
- Nunca reescrever a força dos gates por conveniência.
- Nunca usar comandos destrutivos de git (`reset`, `rebase`, `commit --amend`) para mascarar estado.

**Modo ROADMAP:**
- Nunca iniciar fase N sem confirmar Critério de Done da fase N-1.
- Nunca editar `frontend/src/api/schema.d.ts` manualmente — regenerar com `npm run api:generate`.
- Nunca executar deploy de produção autonomamente (fases 6, 9, 12 — requer aprovação humana).
- Nunca usar worker `generate_frontend` (frozen) — FASE 5 usa código React direto.
- Nunca criar artefatos fora dos paths canônicos definidos em `execute_roadmap_phase.prompt.md`.
- Sempre executar `python3 scripts/hb preflight` antes de `git push` — garante paridade local=CI.
- Nunca fazer `git push` sem preflight PASS.
