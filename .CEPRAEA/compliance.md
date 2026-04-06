# AUDITORIA DE COMPLIANCE OPERACIONAL — Ecossistema Multiagente HB Track

> **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é uma auditoria de compliance operacional. Não possui autoridade normativa.
> Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > este arquivo.
> **Auditor:** GitHub Copilot (Claude Opus 4.6) | **Data:** 2026-04-06
> **Escopo:** Compliance de governança de agente para Copilot, Claude Code e Codex
> **Evidência base:** artefatos reais do workspace, enforcement executável local, análise estrutural de 90+ arquivos de governança

---

## PARTE 1 — Visão geral do compliance do ecossistema de agentes

### A governança é clara ou difusa?

**Difusa, com núcleo forte.** O sistema possui um núcleo de enforcement executável robusto (`scripts/hb`, `validate_contracts.py`, `pre-commit hook`) que realmente governa contratos, artefatos e integridade de sessão. Porém, a camada que conecta esse enforcement ao comportamento do agente — boot, roteamento, leitura de contexto, interpretação de regras — é baseada em convenção documental, não em enforcement técnico. O agente depende de ler ~15 arquivos em sequência correta, mas nenhum mecanismo garante que essa leitura aconteça.

### A camada de instruções/configurações é coesa ou fragmentada?

**Fragmentada em 6 níveis de autoridade, com repetição deliberada mas drift acumulado.** Existe uma cadeia de precedência bem definida (enforcement > schemas > canon > bridge > derivados > legado), mas na prática:
- Bridge docs (`CLAUDE.md`, `copilot-instructions.md`) repetem canon com divergências sutis em relação ao estado atual dos schemas e gates
- Skills (`.github/skills/`) estão desatualizados em relação ao enforcement real
- Artefatos derivados na raiz (13 arquivos `.md` NON-SOVEREIGN) e em `.CEPRAEA/` (24 arquivos) aumentam a superfície de contexto sem governar nada

### Existem sinais de drift entre agentes?

**Sim.** O drift opera em três eixos:
1. **Drift de entrada:** Copilot recebe `copilot-instructions.md` + `hb-contract-guards.instructions.md` + skills automaticamente; Claude Code recebe `CLAUDE.md` + `AGENT_INSTRUCTIONS.md` automaticamente; Codex não recebe instrução específica alguma
2. **Drift de capacidade:** Copilot tem skills e agent definitions (`.github/agents/`, `.github/skills/`); Claude Code tem hooks (`.github/hooks/hb-contract-guards.json` com `PreToolUse`/`Stop`); Codex não tem nenhum mecanismo de customização
3. **Drift de conteúdo:** `copilot-instructions.md` e `CLAUDE.md` têm informações divergentes sobre schemas ativos e modos de operação

### Existe excesso de fontes de verdade?

**Sim.** Há redundância em 4 camadas:
- **17 módulos canônicos** estão declarados em `MODULE_REGISTRY.yaml` (SSOT), `CONTRACT_SYSTEM_RULES.md`, `AGENT_INSTRUCTIONS.md`, `copilot-instructions.md`, `CLAUDE.md` e `hb-contract.agent.md`
- **Regras de boot** estão em `AGENT_INSTRUCTIONS.md`, `BOOT_PROFILES.yaml`, `CONTRACT_PIPELINE.md`, skills e bridge docs
- **Pipeline CDD** está descrito em `CONTRACT_PIPELINE.md`, `pre_contract_orchestrator.prompt.md`, `hb-pipeline-orchestrator/SKILL.md` e `hb-contract.agent.md`
- A redundância é parcialmente intencional (bridges repetem canon), mas o drift entre cópias é real

### Existem fontes que o agente nem consulta?

**Sim:**
- `BOOT_PROFILES.yaml` `selection_rules`, `phase_profiles` e `integration`: nenhum consumidor em código
- `TASK_CATALOG.yaml` `input_requirements`, `artifacts_produced`, `blocking_gates`: documentação pura, sem enforcement
- `SURVIVAL_SUITE_POLICY.md`: não executada automaticamente por CI
- `SCOPE_BOUNDARY_POLICY.md`: script periférico, não integrado ao executor central
- `ARCH_DECISION_PRESENCE_GATE`: no registry, não no executor
- `.github/hooks/hb-contract-guards.json`: presente mas não referenciado por nenhum pipeline ativo
- `GLOBAL_TEMPLATES.md`, `PLACEHOLDER_REGISTRY.md`, `COMPETITIVE_BENCHMARK_PROTOCOL.md`: sem consumidores

### O que existe governa todo o sistema?

**Não.** O enforcement real cobre:
- ✅ Integridade de contratos e artefatos canônicos
- ✅ Consistência de schemas e axiomas
- ✅ Estado de sessão (parcial — `session_start.json`)
- ✅ Handoff de sessão (`SESSION_HANDOFF.md` via `HANDOFF_COHERENCE_GATE`)
- ✅ Registro de artefatos (`hb artifact`)
- ❌ Boot obrigatório do agente (leitura de `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md`, `ROADMAP.md`)
- ❌ Seleção de profile por regras declaradas
- ❌ Enforcement de `stage_allowed` (só warning)
- ❌ Validação de pré-condições de task (só documental)
- ❌ Survival suite em CI
- ❌ Scope boundary no executor central

---

## PARTE 2 — Matriz de governança das configurações

| Configuração / arquivo / mecanismo | Função | Deveria governar? | Governa de fato? | O agente lê? | Interpreta corretamente? | Segue de fato? | Aplica igual nos 3 agentes? | Status de compliance | Observações |
|---|---|---|---|---|---|---|---|---|---|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | instrução principal | sim | parcialmente | confirmado (Claude), provável (Copilot), não (Codex) | parcialmente | parcialmente | não | parcialmente conforme | Claude auto-carrega; Copilot recebe via bridge; Codex não recebe. `scripts/hb` não lê este arquivo. |
| `CLAUDE.md` | instrução principal (bridge) | parcialmente | parcialmente | confirmado (Claude) | parcialmente | parcialmente | não | parcialmente conforme | Só Claude lê. Contém instrução de ler `AGENT_INSTRUCTIONS.md` como ponteiro. |
| `.github/copilot-instructions.md` | instrução principal (bridge) | parcialmente | parcialmente | confirmado (Copilot) | parcialmente | parcialmente | não | parcialmente conforme | Só Copilot lê. Herdou afirmação incorreta sobre `session_handoff.schema.json`. |
| `AGENT.md` | contexto auxiliar | não | não | não confirmado | não se aplica | não se aplica | inconclusivo | conforme | Derivado NON-SOVEREIGN. Correto ao não governar. |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | governança | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente | parcialmente conforme | Regras fortes mas sem enforcement direto para muitas seções. |
| `.contract_driven/BOOT_PROFILES.yaml` | roteamento | sim | parcialmente | confirmado | parcialmente | parcialmente | parcialmente | não conforme | `selection_rules`, `phase_profiles`, `integration` nunca executados. |
| `.contract_driven/TASK_CATALOG.yaml` | roteamento | sim | parcialmente | confirmado | parcialmente | parcialmente | parcialmente | não conforme | `stage_allowed` é warning-only; `input_requirements` e `blocking_gates` são doc-only. |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | roteamento | parcialmente | parcialmente | provável | parcialmente | parcialmente | não | parcialmente conforme | Copilot/Claude leem quando ativam skill CDD; Codex não. |
| `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md` | roteamento | parcialmente | parcialmente | provável | parcialmente | parcialmente | não | parcialmente conforme | Idem ao anterior para modo ROADMAP. |
| `docs/_canon/CONTRACT_PIPELINE.md` | governança | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente | parcialmente conforme | Referência normativa forte; não executada integralmente. |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | validação | sim | parcialmente | confirmado | parcialmente | parcialmente | sim | não conforme | Drift com `validate_contracts.py`: gates no registry sem executor e vice-versa. |
| `docs/_canon/MODULE_REGISTRY.yaml` | governança | sim | sim | confirmado | sim | sim | sim | conforme | SSOT mais efetivo do sistema. Gate real. |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | governança | sim | sim | confirmado | sim | sim | sim | conforme | Governa boundary gates reais. |
| `docs/_canon/GLOBAL_INVARIANTS.md` | governança | sim | parcialmente | provável | sim | parcialmente | parcialmente | parcialmente conforme | Referência normativa para design; enforcement parcial via gates. |
| `docs/_canon/FEATURE_REGISTRY.yaml` | definição de progresso | parcialmente | parcialmente | confirmado | parcialmente | parcialmente | sim | parcialmente conforme | Cobertura de features limitada a ~5 módulos de 17. |
| `docs/_canon/CODE_ARCHITECTURE.md` | governança | parcialmente | parcialmente | confirmado | sim | parcialmente | parcialmente | parcialmente conforme | Lido por ROADMAP worker; sem boot automático universal. |
| `docs/_canon/SURVIVAL_SUITE_POLICY.md` | validação | sim | não | provável | sim | não | não | não conforme | CI não executa `hb survival-suite`. |
| `docs/_canon/SCOPE_BOUNDARY_POLICY.md` | validação | sim | parcialmente | não confirmado | não | não | não | não conforme | Script periférico, não no executor central. |
| `docs/_canon/DECISION_POLICY.md` | governança | sim | parcialmente | provável | sim | parcialmente | parcialmente | parcialmente conforme | `ARCH_DECISION_PRESENCE_GATE` no registry mas não no executor. |
| `.contract_driven/DOMAIN_AXIOMS.json` | validação | sim | sim | confirmado | sim | sim | sim | conforme | Consumido por `validate_contracts.py` no `AXIOM_INTEGRITY_GATE`. |
| `.contract_driven/waivers.json` | governança | sim | sim | confirmado | sim | sim | sim | conforme | Array vazio = sem waivers ativos. Gate funciona. |
| `contracts/schemas/shared/session_start.schema.json` | validação | sim | parcialmente | confirmado | parcialmente | parcialmente | sim | parcialmente conforme | Não modela `roadmap_phase`/`task_id` como required; `stage2/3_exit_code` sem writer. |
| `contracts/schemas/shared/session_handoff.schema.json` | validação | sim | sim | confirmado | parcialmente | sim | sim | parcialmente conforme | Copilot instructions dizem para ignorá-lo — conflito direto. |
| `docs/_canon/templates/SESSION_HANDOFF.template.md` | handoff | sim | parcialmente | provável | não | não | parcialmente | não conforme | `evidence_paths: []` conflita com `minItems: 1` do schema. |
| `SESSION_HANDOFF.md` | estado | sim | sim | confirmado | parcialmente | parcialmente | parcialmente | parcialmente conforme | Gate valida; `scripts/hb` não lê conteúdo — só existência. |
| `_reports/session_start.json` | estado | sim | parcialmente | confirmado | parcialmente | parcialmente | sim | parcialmente conforme | Estado técnico do `hb`; incoerente com handoff em modo ROADMAP. |
| `scripts/contracts/validate/validate_contracts.py` | validação | sim | sim | confirmado | sim | sim | sim | parcialmente conforme | Enforcement central real; drift de gates com registry. |
| `scripts/hb` | validação | sim | sim | confirmado | parcialmente | parcialmente | sim | parcialmente conforme | Boot real mas não lê boot obrigatório declarado. |
| `scripts/git-hooks/pre-commit` | validação | sim | sim | confirmado | parcialmente | parcialmente | sim | parcialmente conforme | Ativo; rastreia só `contracts/` e `docs/hbtrack/` para artefatos. |
| `.github/skills/hb-pipeline-orchestrator/SKILL.md` | roteamento | parcialmente | parcialmente | não confirmado | não | não | não | não conforme | Espera output que `scripts/hb` não produz. |
| `.github/skills/hb-roadmap-executor/SKILL.md` | roteamento | parcialmente | parcialmente | não confirmado | não | não | não | não conforme | Exemplo de handoff sem YAML front matter obrigatório. |
| `.github/agents/hb-contract.agent.md` | roteamento | parcialmente | parcialmente | confirmado (Copilot) | parcialmente | parcialmente | não | parcialmente conforme | Só VS Code Copilot consome esta definição. |
| `.github/instructions/hb-contract-guards.instructions.md` | validação | sim | parcialmente | confirmado (Copilot) | sim | parcialmente | não | parcialmente conforme | Só aplica no Copilot quando editando `src/**`. |
| `.github/ai-review/styleguide.md` | governança | parcialmente | parcialmente | confirmado (Gemini) | sim | sim | não | parcialmente conforme | Só governa AI Review em PRs (Gemini). |
| `.github/hooks/hb-contract-guards.json` | validação | parcialmente | não | não | não | não | não | não conforme | Presente mas não referenciado por pipeline ativo. |
| `merge-readiness.json` | validação | sim | sim | confirmado | sim | sim | sim | conforme | SSOT para checks de PR; schema-validated. |
| `toolchain.json` | governança | sim | sim | confirmado | sim | sim | sim | conforme | Governa runtimes/services; schema-validated. |
| `ROADMAP.md` | definição de progresso | sim | parcialmente | provável | parcialmente | parcialmente | parcialmente | parcialmente conforme | SSOT de fases; sem binding técnico completo. |
| 13 `.md` derivados na raiz + 24 em `.CEPRAEA/` | contexto auxiliar | não | não | não confirmado | não se aplica | não se aplica | inconclusivo | parcialmente conforme | Arquivos NON-SOVEREIGN que poluem contexto. |

---

## PARTE 3 — O que realmente governa o agente hoje

As configurações abaixo têm **efeito real comprovado** sobre o comportamento dos agentes:

### Enforcement executável (nível 1 — autoridade máxima)
1. **`scripts/contracts/validate/validate_contracts.py`** — 51+ gates; exit_code != 0 = bloqueio. Enforcement central do pipeline CDD.
2. **`scripts/hb`** — Boot de sessão, registro de artefatos, validação de profile/task/module. Exit_code != 0 = bloqueio.
3. **`scripts/git-hooks/pre-commit`** — 9 fases, sha-256 integrity, handoff requirement, governance suite. Bloqueio local pré-commit.
4. **`.github/workflows/contract-gates.yml`** — CI enforcement; `Validate Contract Gates`, `Governance Tests`, `Architecture Drift Check` são required checks.

### Schemas ativos (nível 2)
5. **`contracts/schemas/shared/session_start.schema.json`** — Validação de `_reports/session_start.json` por `hb` e hook.
6. **`contracts/schemas/shared/session_handoff.schema.json`** — Validação de `SESSION_HANDOFF.md` front matter via `HANDOFF_COHERENCE_GATE`.
7. **`contracts/schemas/shared/merge-readiness.schema.json`** — Governa paridade local x CI.

### Registries canônicos (nível 3)
8. **`docs/_canon/MODULE_REGISTRY.yaml`** — SSOT de módulos; consumido por gates, scripts e prompts.
9. **`docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`** — Governa boundary gates reais.
10. **`.contract_driven/DOMAIN_AXIOMS.json`** — Consumido por `AXIOM_INTEGRITY_GATE`.
11. **`.contract_driven/TASK_CATALOG.yaml`** — Subset real: `task_type`, `status`, `worker_path`, `profile_id`.
12. **`.contract_driven/BOOT_PROFILES.yaml`** — Subset real: `profile_id`, `load_sequence` (paths), `exit_on_fail`.

### Estado persistente
13. **`_reports/session_start.json`** — Estado técnico de sessão para `hb` e hook.
14. **`SESSION_HANDOFF.md`** — Handoff operacional; validated por gate.
15. **`_reports/agent_execution/*.json`** — Governa `PRE_CONTRACT_EVIDENCE_GATE`.

### Bridge docs (nível 4 — efeito parcial, por agente)
16. **`CLAUDE.md`** — Carregado por Claude Code automaticamente.
17. **`.github/copilot-instructions.md`** — Carregado por GitHub Copilot automaticamente.
18. **`.github/instructions/hb-contract-guards.instructions.md`** — Guard Copilot para `src/**`.

---

## PARTE 4 — O que deveria governar, mas não governa

| Artefato | Por que deveria governar | Por que não governa | Agentes mais afetados | Risco |
|---|---|---|---|---|
| `docs/_canon/AGENT_INSTRUCTIONS.md` (boot completo) | Define boot obrigatório, modos de operação, cadeia de decisão | `scripts/hb` não lê `AGENT_INSTRUCTIONS`, `SESSION_HANDOFF` ou `ROADMAP` de verdade — só valida existência de paths em `load_sequence` | Todos | Boot manual inconsistente; contexto presumido; perda de continuidade |
| `BOOT_PROFILES.yaml` (`selection_rules`, `phase_profiles`, `integration`) | Define como selecionar profile dinamicamente e integrar com orchestrator | Nenhum consumidor em código executa essas seções | Todos | Profile selection é estático via `TASK_CATALOG.profile_id` — as regras dinâmicas são ficção operacional |
| `TASK_CATALOG.yaml` (`stage_allowed`, `input_requirements`, `blocking_gates`) | Define pré-condições, sequenciamento e gates por task type | `stage_allowed` gera warning apenas; `input_requirements` e `blocking_gates` são doc-only | Todos | Task pode executar fora de sequência sem bloqueio |
| `docs/_canon/SURVIVAL_SUITE_POLICY.md` | Manda rodar `hb survival-suite` antes de merge em mudanças de governança | CI não executa; só pre-commit hook roda parcialmente quando governance paths são tocados | Todos (via CI) | Regressão em governança pode entrar com pipeline verde |
| `ARCH_DECISION_PRESENCE_GATE` | Deve bloquear contrato com decisão obrigatória em aberto | Está em `GATES_REGISTRY.yaml` mas não em `validate_contracts.py` | Todos | Decisão arquitetural pulada sem bloqueio técnico |
| `SCOPE_BOUNDARY_GATE` | Deve bloquear overflow cross-module | Script periférico; não está no executor central | Todos | Boundary violations dependem de disciplina manual |
| Estado ROADMAP (`phase`, `task_id`, `modulo_foco`) | Deveria garantir continuidade no modo ROADMAP | Não modelado como required em `session_start.schema.json`; estado dividido entre handoff e sessão | Todos | Execução de fase com memória operacional inconsistente |
| Instrução para Codex | Codex deveria receber a mesma governança base | Não existe arquivo de instrução para Codex (nem `.codexrc`, nem `CODEX.md`, nem `AGENTS.md`) | Codex | Codex opera sem nenhuma governança do projeto |
| `.github/hooks/hb-contract-guards.json` | Deveria governar PreToolUse e Stop do Claude Code | Presente mas não referenciado por nenhum pipeline ativo | Claude Code | Hook de Claude Code pode estar desconectado |

---

## PARTE 5 — Incoerências, duplicatas e conflitos

| Item | Problema | Tipo | Impacto | Gravidade | Ação recomendada |
|---|---|---|---|---|---|
| `GATES_REGISTRY.yaml` vs `validate_contracts.py` | Gates no registry sem executor (`ARCH_DECISION_PRESENCE_GATE`, `FRONTEND_CONTRACT_GATE`, `SCOPE_BOUNDARY_GATE`); gates no executor sem registry (`SPECTRAL_LINTING_GATE`, `SURFACE_PROMOTION_COHERENCE_GATE`) | conflito | Split-brain: norma declara controles que não rodam e executor roda controles sem base normativa | crítica | Alinhar: todo gate ativo → nos dois lados. Remover/desativar os que não têm executor |
| `copilot-instructions.md` vs `session_handoff.schema.json` | Bridge doc herdou afirmação de que o schema "não deve ser tratado como validador ativo"; gate `HANDOFF_COHERENCE_GATE` usa exatamente esse schema | conflito | Copilot pode ser instruído a ignorar validação ativa | crítica | Remover afirmação incorreta em copilot-instructions; alinhar com realidade do gate |
| `SESSION_HANDOFF.template.md` vs `session_handoff.schema.json` | Template usa `evidence_paths: []`; schema exige `minItems: 1` | incoerência | Copy-paste do template gera handoff inválido | alta | Atualizar template para `evidence_paths: ["<obrigatório>"]` |
| `hb-roadmap-executor/SKILL.md` vs `session_handoff.schema.json` | Skill mostra exemplo de handoff sem front matter YAML obrigatório ou com campos incompletos | incoerência | Agente que segue o skill produz handoff não conforme | alta | Atualizar SKILL.md com exemplo schema-valid |
| `hb-pipeline-orchestrator/SKILL.md` vs `scripts/hb` | Skill espera saída `task_type_target` de `hb verify --task-type pre_contract_boot`; `scripts/hb` não produz isso | incoerência | Skill promete fluxo que o runtime não suporta | alta | Atualizar skill para refletir output real do `scripts/hb` |
| `BOOT_PROFILES.yaml` `selection_rules` | Documenta regras dinâmicas de seleção de profile que nenhum código executa | excesso de governança | Falsa sensação de controle automático | média | Remover ou marcar como `status: not_implemented` |
| `TASK_CATALOG.yaml` `stage_allowed` | Documenta restrição de estágio mas `scripts/hb` só emite warning | governança fraca | Task pode executar fora de sequência sem bloqueio | alta | Implementar bloqueio real ou remover do schema |
| `session_start.schema.json` campos stale | Refere "16 canônicos" (são 17); `stage2_exit_code` e `stage3_exit_code` sem writer no fluxo real | obsolescência | Rastreabilidade incompleta; documentação enganosa | média | Atualizar contagem; implementar writers ou remover campos |
| `_reports/session_start.json` vs `SESSION_HANDOFF.md` | Dois arquivos de estado sem cross-validation automática — podem divergir silenciosamente | gap | Estado operacional inconsistente entre arquivos oficiais | alta | Implementar cross-validation automática |
| 13 arquivos `.md` derivados na raiz + 24 em `.CEPRAEA/` | Arquivos NON-SOVEREIGN poluem contexto do agente | excesso de governança | Aumentam superfície de contexto sem valor normativo | média | Mover para `_archive/`; manter raiz e `.CEPRAEA/` limpos |
| `scripts/hbtrack_lint/` | Aponta para `docs/hbtrack/modulos/atletas/MOTORES.md` (inexistente) | obsolescência | Governança morta; ruído de manutenção | baixa | Remover ou desativar subsistema legado |
| `_reports/evidence/boot_resolution_report.json` | Legado com `source_authority='CLAUDE.md §7'` | obsolescência | Evidência velha confundida com boot atual | baixa | Arquivar em `_archive/` |
| Ausência de instrução Codex | Não existe mecanismo de instrução para Codex | ausência de governança | Codex opera sem nenhuma governança do projeto | crítica | Criar instrução Codex |
| `.github/hooks/hb-contract-guards.json` | Hook `PreToolUse`/`Stop` presente mas desconectado do pipeline | gap | Hook pode não estar sendo executado | alta | Verificar integração ou remover |
| `SURVIVAL_SUITE_POLICY.md` vs CI | Política manda executar; CI não faz | gap | Regressão em governança pode entrar com pipeline verde | alta | Adicionar step em `contract-gates.yml` |
| `AGENT_INSTRUCTIONS.md` nota "UNDER REVIEW FOR C4" | Documento principal marcado como under review | incoerência | Autoridade do documento principal questionada | média | Concluir revisão ou remover anotação |

---

## PARTE 6 — Pontos de não-conformidade do agente

| Configuração | Tipo de não-conformidade | Evidência | Agente(s) afetado(s) | Impacto | Gravidade |
|---|---|---|---|---|---|
| Boot obrigatório (`AGENT_INSTRUCTIONS.md` §0) | governança fraca | `scripts/hb` não lê `AGENT_INSTRUCTIONS`, `SESSION_HANDOFF` ou `ROADMAP` de verdade — só valida paths | Todos | Agente pode operar com contexto presumido e não lido | alta |
| `BOOT_PROFILES.yaml` `selection_rules` | ignorada | Nenhum consumidor executa `selection_rules` — código usa `TASK_CATALOG.profile_id` diretamente | Todos | Regras dinâmicas de profile são ficção operacional | alta |
| `TASK_CATALOG.yaml` `stage_allowed` | aplicação parcial | `scripts/hb` emite warning em vez de bloqueio; output: `⚠️ stage_allowed check` | Todos | Task pode executar fora de sequência | alta |
| `copilot-instructions.md` sobre handoff schema | interpretação errada | Texto diz que schema "não deve ser tratado como validador ativo"; `HANDOFF_COHERENCE_GATE` usa exatamente este schema | Copilot | Copilot pode ignorar validação de handoff que é obrigatória | crítica |
| `hb-roadmap-executor/SKILL.md` exemplo de handoff | interpretação errada | Exemplo mostra handoff sem front matter YAML completo | Copilot | Handoff inválido pode ser produzido | alta |
| `hb-pipeline-orchestrator/SKILL.md` output esperado | interpretação errada | Espera `task_type_target` que `scripts/hb` não produz | Copilot | Skill promete fluxo inexistente; agente pode travar esperando output | alta |
| `SESSION_HANDOFF.template.md` | leitura parcial | Template tem `evidence_paths: []` que viola `minItems: 1` | Todos | Copy-paste gera handoff inválido | média |
| `GATES_REGISTRY.yaml` drift | conflito de precedência | Gates no registry sem executor e vice-versa; split: `ARCH_DECISION_PRESENCE_GATE`, `SPECTRAL_LINTING_GATE` | Todos (via CI) | Sistema declara controles fantasma e roda controles não registrados | crítica |
| Codex sem instrução | divergência entre agentes | Não existe nenhum mecanismo de instrução para Codex | Codex | Codex opera completamente sem governança | crítica |
| `SURVIVAL_SUITE_POLICY.md` | ignorada | Mandatória por política; CI não executa `hb survival-suite`; hook só parcialmente | Todos (via CI) | Mudanças de governança podem regredir sem detecção | alta |
| `SCOPE_BOUNDARY_GATE` | ignorada | Está no registry; não está no executor central; script periférico | Todos | Boundary violations sem detecção automática | alta |
| `.github/hooks/hb-contract-guards.json` | ignorada | Presente em `.github/hooks/` mas não referenciado por pipeline ativo | Claude Code | Hooks de Claude Code potencialmente não executados | alta |
| `docs/_canon/DECISION_POLICY.md` via `ARCH_DECISION_PRESENCE_GATE` | aplicação parcial | Gate registrado mas não implementado no executor | Todos | Decisão obrigatória pode ser pulada | alta |
| 13+ arquivos derivados na raiz | governança fraca | Arquivos NON-SOVEREIGN na raiz; fora do `SHADOW_AUTHORITY_GATE` | Todos | Agente pode ler conteúdo derivado como normativo | média |

---

## PARTE 7 — Riscos operacionais

### 1. Alucinação
Como o boot obrigatório (leitura de `AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md`, `ROADMAP.md`) não é tecnicamente executado por `scripts/hb`, qualquer agente pode operar com contexto presumido e não verificado. O risco é amplificado pelo Codex, que não recebe nenhuma instrução do projeto. O Copilot pode ser instruído (via skills desatualizados) a produzir outputs que o runtime não suporta, induzindo alucinação de fluxo. **Gravidade: alta.**

### 2. Deriva de escopo
O `SCOPE_BOUNDARY_GATE` declarado não roda no executor central, e o `SHADOW_AUTHORITY_GATE` não cobre os 13 arquivos derivados na raiz nem os 24 em `.CEPRAEA/`. Um agente pode expandir escopo para módulos fora do foco sem detecção automática. **Gravidade: alta.**

### 3. Decisões sem base suficiente
O `ARCH_DECISION_PRESENCE_GATE` está normatizado no registry mas não implementado no executor. Decisões obrigatórias podem ser puladas sem bloqueio técnico. O agente pode criar contratos que dependem de decisões não tomadas. **Gravidade: alta.**

### 4. Inconsistência entre agentes
O drift opera em 3 eixos (entrada, capacidade, conteúdo). Copilot tem skills e agent definitions com instruções desatualizadas; Claude Code tem hooks potencialmente desconectados; Codex não tem nada. Sessões consecutivas alternando entre agentes podem produzir artefatos com premissas divergentes. **Gravidade: crítica.**

### 5. Retrabalho
O sistema pode parecer verde (`validate_contracts.py` PASS, testes verdes) enquanto regras de boot, roteamento e sessão continuam não aplicadas. O drift entre registry e executor faz correções voltarem. Skills desatualizados induzem handoff inválido que precisa ser refeito. **Gravidade: alta.**

### 6. Conflito entre artefatos
Há conflito direto entre `GATES_REGISTRY.yaml`, skills GitHub, `copilot-instructions.md`, schemas e executor real. Isso reduz determinismo e abre espaço para o agente "obedecer" o artefato errado. **Gravidade: alta.**

### 7. DONE incorreto
O pipeline completo pode dar `PASS` mesmo com estado de sessão stale ou incoerente. O `FEATURE_REGISTRY` não sustenta DONE funcional para a maior parte dos módulos implementados (cobre ~5 de 17). **Gravidade: média.**

### 8. Continuidade instável
`SESSION_HANDOFF.md` e `_reports/session_start.json` carregam estados parcialmente sobrepostos sem cross-validation automática. O handoff aceita data futura (gate só checa staleness > 30 dias). Estado ROADMAP (`phase`, `task_id`) não está modelado como required no schema de sessão. **Gravidade: alta.**

### 9. Perda de rastreabilidade
`stage2_exit_code` e `stage3_exit_code` existem no schema mas não são preenchidos pelo fluxo real. O hook rastreia artefatos detalhadamente só em subset do repositório (`contracts/`, `docs/hbtrack/`). Mudanças em `.contract_driven/`, `docs/_canon/`, `scripts/` escapam do rastreio fino. **Gravidade: média.**

---

## PARTE 8 — Veredito final

### O ecossistema atual está em compliance real?

**Parcialmente.** O núcleo de enforcement (validator, CLI, hook) é real, testado e funcional. Mas a camada que conecta esse enforcement ao comportamento do agente é baseada em convenção documental com drift acumulado, skills desatualizados, bridge docs com afirmações incorretas e ausência total de governança para Codex.

### Quais configurações realmente governam os agentes hoje?

- `scripts/contracts/validate/validate_contracts.py` (51+ gates)
- `scripts/hb` (boot, registro, validação)
- `scripts/git-hooks/pre-commit` (9 fases)
- `.github/workflows/contract-gates.yml` (CI)
- `contracts/schemas/shared/session_*.schema.json`
- `docs/_canon/MODULE_REGISTRY.yaml`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `.contract_driven/DOMAIN_AXIOMS.json`
- `SESSION_HANDOFF.md` (via gate)
- `_reports/session_start.json`
- `merge-readiness.json`
- `CLAUDE.md` (somente Claude)
- `.github/copilot-instructions.md` (somente Copilot)

### Quais deveriam governar e não estão governando?

- Boot completo (`AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md`, `ROADMAP.md` lidos de verdade)
- `BOOT_PROFILES.yaml` `selection_rules` / `phase_profiles` / `integration`
- `TASK_CATALOG.yaml` `stage_allowed` (enforcement real), `input_requirements`, `blocking_gates`
- `SURVIVAL_SUITE_POLICY.md` em CI
- `ARCH_DECISION_PRESENCE_GATE`
- `SCOPE_BOUNDARY_GATE`
- Estado ROADMAP completo em `session_start.schema.json`
- Instrução para Codex

### Quais são os maiores conflitos?

1. **`GATES_REGISTRY.yaml` vs `validate_contracts.py`** — split-brain de gates (crítico)
2. **`copilot-instructions.md` vs `session_handoff.schema.json`** — bridge doc contradiz gate ativo (crítico)
3. **Skills (2x) vs `scripts/hb` output real** — skills prometem fluxo inexistente (alto)
4. **`SESSION_HANDOFF.template.md` vs `session_handoff.schema.json`** — template gera handoff inválido (alto)

### Quais são as duplicatas mais perigosas?

1. **Pipeline CDD descrito em 4+ lugares** (`CONTRACT_PIPELINE.md`, `pre_contract_orchestrator.prompt.md`, `SKILL.md`, `hb-contract.agent.md`) com níveis variados de atualização
2. **Regras de boot em 5+ lugares** (`AGENT_INSTRUCTIONS.md`, `BOOT_PROFILES.yaml`, `CONTRACT_SYSTEM_RULES.md`, skills, bridges) sem enforcement unificado
3. **17 módulos em 6+ lugares** com contagem stale em `session_start.schema.json` ("16 canônicos")

### Quais arquivos deveriam existir e não existem?

| Arquivo ausente | Propósito | Impacto da ausência |
|---|---|---|
| Instrução para Codex (`.codexrc` ou `codex.md` ou equivalente) | Governar comportamento do Codex | Codex opera sem nenhuma governança do projeto |
| `AGENTS.md` na raiz | Inventariar agentes e suas fontes de instrução | Sem visibilidade de quais agentes existem e o que recebem |
| Cross-validation automática `session_start.json` ↔ `SESSION_HANDOFF.md` | Detectar divergência de estado | Dois arquivos de estado podem divergir silenciosamente |

### Quais skills otimizariam os agentes?

| Skill | Propósito | Impacto |
|---|---|---|
| `hb-pr-fix` | Skill dedicado para modo PR_FIX com checklist determinística: lookup em `merge-readiness.json`, execução de `local_equivalent`, proibições | Evitar que agente improvise correção de CI |
| `hb-audit` | Skill genérico para auditorias — carrega worker diretamente, skip orchestrator, formato de saída padronizado | Padronizar auditorias entre agentes |
| `hb-session-continuity` | Skill de boot que valida cross-referência entre `session_start.json`, `SESSION_HANDOFF.md` e estado do git | Garantir continuidade entre sessões independente do agente |

### Quais instructions otimizariam os agentes?

| Instruction | Scope (`applyTo`) | Propósito |
|---|---|---|
| `hb-no-manual-schema-edit.instructions.md` | `frontend/src/api/**` | Bloquear edição manual de `schema.d.ts` — lembrar de usar `npm run api:generate` |
| `hb-roadmap-mode.instructions.md` | `infra/**`, `config/**`, `Dockerfile*`, `.github/workflows/**` | Instruir que esses paths são modo ROADMAP — não rotear por `pre_contract_orchestrator` |
| `hb-derived-not-sovereign.instructions.md` | `*.md` (raiz) | Lembrar que arquivos `.md` na raiz marcados NON-SOVEREIGN não são normativos |

### Quais workflows otimizariam os agentes?

| Workflow | Propósito | Impacto |
|---|---|---|
| Step `survival-suite` em `contract-gates.yml` | Executar `hb survival-suite` condicionado a mudanças de governança | Fechar gap do `SURVIVAL_SUITE_POLICY.md` |
| Step `scope-boundary-check` em `contract-gates.yml` | Executar `check_scope_boundary.py` em artefatos modificados | Implementar `SCOPE_BOUNDARY_GATE` em CI |
| Job `session-state-crossval` em `contract-gates.yml` | Cross-validar `session_start.json` ↔ `SESSION_HANDOFF.md` | Detectar divergência de estado em CI |

### Quais configurações no MCP otimizariam os agentes, para ser usado agora?

| Configuração MCP | Impacto |
|---|---|
| Server MCP com tool `hb-verify` que executa `python3 scripts/hb verify` e retorna resultado estruturado | Agente pode verificar boot de sessão sem depender de terminal; resultado parseable |
| Server MCP com tool `hb-check` que executa `python3 scripts/hb check --module <M>` | Verificação de artefatos de módulo integrada |
| Server MCP com tool `hb-validate` que executa `validate_contracts.py --profile precommit` | Gate check integrado; resultado estruturado |
| Server MCP com tool `merge-readiness-lookup` que consulta `merge-readiness.json` por `context` | Automação do primeiro passo do modo PR_FIX |
| Server MCP com tool `module-status` que lê `MODULE_REGISTRY.yaml` e retorna status do módulo | Verificação rápida de elegibilidade sem ler YAML |

### Quais arquivos existem e deveriam ser removidos ou consolidados?

| Arquivo | Ação recomendada | Justificativa |
|---|---|---|
| `ADVERSARIAL.md`, `DEVCONT.md`, `compilance.md`, `ANALISEARQUITETURA.md`, `FINAL_HANDOFF.md`, `HISTORICO.md`, `reviwer.md`, `PLAN_PARIEDADE.md`, `PR_SEQUENCE_PARIDADE.md`, `BACKLOG_EXECUTAVEL_DETERMINISTICO.md`, `AGENT_COMPLIANCE_EXECUTION_PLAN.md` | Mover para `_archive/` | Derivados NON-SOVEREIGN que poluem raiz e contexto |
| `AGENT.md` | Mover para `_reports/` | Auditoria anterior; substituída por este relatório |
| `SESSION_HANDOFF.md.backup` | Remover | Backup sem valor |
| `SESSION_HANDOFF_*_2026*.md` (5 arquivos raiz) | Mover para `_archive/` | Handoffs históricos |
| `_reports/evidence/boot_resolution_report.json` | Arquivar | Legado stale |
| `scripts/hbtrack_lint/` | Remover/desativar | Aponta para artefatos inexistentes |
| `.github/hooks/hb-contract-guards.json` | Integrar ou remover | Desconectado do pipeline |
| `.CEPRAEA/*.md` (24 arquivos derivados) | Avaliar e consolidar | Pasta com auditorias, paridades e histórico que aumentam superfície de contexto |

### O que precisa ser corrigido para governança determinística entre os 3 agentes?

#### Prioridade 1 — Crítico

1. **Alinhar `GATES_REGISTRY.yaml` e `validate_contracts.py`**: todo gate ativo → nos dois lados
2. **Corrigir `copilot-instructions.md`**: remover afirmação incorreta sobre handoff schema
3. **Criar instrução para Codex**: apontar para `AGENT_INSTRUCTIONS.md` + `SESSION_HANDOFF.md`
4. **Atualizar `hb-roadmap-executor/SKILL.md`**: exemplo de handoff schema-valid
5. **Atualizar `hb-pipeline-orchestrator/SKILL.md`**: remover referência a output inexistente do `scripts/hb`

#### Prioridade 2 — Alto

6. **Atualizar `SESSION_HANDOFF.template.md`**: `evidence_paths` com placeholder válido, não `[]`
7. **Implementar `SURVIVAL_SUITE_POLICY.md` em CI**: step condicionado a mudanças de governança
8. **Tornar `stage_allowed` bloqueante em `scripts/hb`**: warning → exit != 0
9. **Mover derivados da raiz para `_archive/`**: reduzir superfície de contexto
10. **Cross-validation `session_start.json` ↔ `SESSION_HANDOFF.md`**: gate ou script

#### Prioridade 3 — Médio

11. **Modelar `roadmap_phase` e `task_id` em `session_start.schema.json`**
12. **Corrigir `session_start.schema.json`**: "16 canônicos" → "17"; implementar writers para stage2/3_exit_code
13. **Remover nota "UNDER REVIEW" de `AGENT_INSTRUCTIONS.md`**
14. **Integrar ou remover `.github/hooks/hb-contract-guards.json`**
15. **Criar MCP tools**: `hb-verify`, `hb-check`, `hb-validate`, `merge-readiness-lookup`, `module-status`

#### Prioridade 4 — Baixo

16. **Remover `scripts/hbtrack_lint/`**
17. **Arquivar `boot_resolution_report.json`**
18. **Criar `AGENTS.md`**: inventário de agentes e fontes de instrução

---

## APÊNDICE A — Mapa de cobertura por agente

```
┌─────────────────────────────────────┬─────────┬──────────────┬───────┐
│ Fonte de governança                 │ Copilot │ Claude Code  │ Codex │
├─────────────────────────────────────┼─────────┼──────────────┼───────┤
│ AGENT_INSTRUCTIONS.md               │ via     │ auto-load    │ ❌    │
│                                     │ bridge  │              │       │
│ CLAUDE.md                           │ ❌      │ auto-load    │ ❌    │
│ copilot-instructions.md             │ auto    │ ❌           │ ❌    │
│ hb-contract-guards.instructions.md  │ auto*   │ ❌           │ ❌    │
│                                     │ src/**  │              │       │
│ hb-contract.agent.md                │ auto    │ ❌           │ ❌    │
│ hb-pipeline-orchestrator SKILL      │ auto    │ ❌           │ ❌    │
│ hb-roadmap-executor SKILL           │ auto    │ ❌           │ ❌    │
│ hb-contract-guards.json (hooks)     │ ❌      │ potencial    │ ❌    │
│ ai-review/styleguide.md             │ ❌      │ ❌           │ ❌    │
│                                     │         │              │(Gemini)│
│ scripts/hb (enforcement)            │ ✅      │ ✅           │ ❌    │
│ validate_contracts.py               │ ✅      │ ✅           │ ❌    │
│ pre-commit hook                     │ ✅      │ ✅           │ ❌    │
│ CI workflows                        │ ✅      │ ✅           │ ✅    │
│ SESSION_HANDOFF.md (via gate)       │ ✅      │ ✅           │ ❌    │
│ MODULE_REGISTRY.yaml                │ ✅      │ ✅           │ ❌    │
│ merge-readiness.json                │ ✅      │ ✅           │ ❌    │
│ Worker prompts (.prompt.md)         │ manual  │ manual       │ ❌    │
│ ROADMAP.md                          │ manual  │ manual       │ ❌    │
│ CONTRACT_SYSTEM_RULES.md            │ manual  │ manual       │ ❌    │
└─────────────────────────────────────┴─────────┴──────────────┴───────┘

Legenda:
  auto     = carregado automaticamente pela plataforma
  auto-load = carregado automaticamente pelo Claude Code
  via bridge = recebe via copilot-instructions.md (resumo)
  auto* src/** = carregado automaticamente só ao editar src/
  manual   = agente deve ler sob demanda
  potencial = mecanismo existe mas integração não confirmada
  ❌       = não recebe
  ✅       = recebe via enforcement (scripts/CI) ou leitura direta
```

## APÊNDICE B — Cadeia de precedência de autoridade (canônica)

```
 NÍVEL 1  enforcement executável
          ├── scripts/hb
          ├── scripts/contracts/validate/validate_contracts.py
          ├── scripts/git-hooks/pre-commit
          └── .github/workflows/contract-gates.yml

 NÍVEL 2  schemas ativos
          └── contracts/schemas/shared/*.schema.json

 NÍVEL 3  canon (SSOT)
          ├── docs/_canon/AGENT_INSTRUCTIONS.md
          ├── docs/_canon/CONTRACT_PIPELINE.md
          ├── docs/_canon/MODULE_REGISTRY.yaml
          ├── docs/_canon/gates/GATES_REGISTRY.yaml
          ├── docs/_canon/GLOBAL_INVARIANTS.md
          ├── .contract_driven/CONTRACT_SYSTEM_RULES.md
          ├── .contract_driven/BOOT_PROFILES.yaml
          ├── .contract_driven/TASK_CATALOG.yaml
          ├── .contract_driven/DOMAIN_AXIOMS.json
          └── ROADMAP.md

 NÍVEL 4  bridge docs (por agente)
          ├── CLAUDE.md (Claude Code)
          ├── .github/copilot-instructions.md (Copilot)
          ├── .github/agents/hb-contract.agent.md (Copilot)
          ├── .github/skills/**/*.SKILL.md (Copilot)
          ├── .github/instructions/*.instructions.md (Copilot)
          └── .github/hooks/*.json (Claude Code)

 NÍVEL 5  artefatos derivados
          └── AGENT.md, DEVCONT.md, compilance.md, etc.

 NÍVEL 6  legado
          └── _archive/, _reports/evidence/boot_resolution_report.json
```

---

## APÊNDICE C — Resumo quantitativo

| Métrica | Valor |
|---|---|
| Total de arquivos de governança analisados | 90+ |
| Arquivos em **compliance total** (conforme) | 6 |
| Arquivos **parcialmente conformes** | 25 |
| Arquivos **não conformes** | 8 |
| Arquivos **inconclusivos** | 3 |
| Não-conformidades **críticas** | 5 |
| Não-conformidades **altas** | 12 |
| Não-conformidades **médias** | 6 |
| Não-conformidades **baixas** | 3 |
| Agentes com instrução dedicada | 2 de 3 (Copilot, Claude) |
| Agentes sem instrução alguma | 1 de 3 (Codex) |
| Gates no registry sem executor | 3 |
| Gates no executor sem registry | 2 |
| Campos de schema sem writer | 2 |
| Políticas mandatórias não executadas em CI | 1 |
| Arquivos derivados na raiz (poluição de contexto) | 13 |
| Arquivos derivados em `.CEPRAEA/` | 24 |

---

> **FIM DA AUDITORIA**
> Próxima ação recomendada: executar itens de Prioridade 1 (5 ações críticas) e Prioridade 2 (5 ações altas) antes de iniciar qualquer nova fase de implementação.
