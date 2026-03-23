---
name: hb-pipeline-orchestrator
description: >
  HB Track CDD Pipeline Orchestrator. USE FOR: any contract task (new_contract,
  contract_revision, new_event, new_workflow, new_schema, new_state_model,
  new_ui_contract, new_module, architecture_review, decision_discovery,
  adversarial_analysis, readiness_promotion, generate_code).
  Enforces the pipeline: Boot → PRÉ-0 (pre_contract_boot) → FASE 0 (hb verify) →
  FASE 1 (hb check) → Decision Discovery → FASE 2 (worker + hb artifact) →
  COMPILE → FASE 3 (validate_contracts) → FASE 4+ (task-specific follow-up) → FASE 5 (handoff).
  DO NOT USE FOR: general questions, code review, debugging, audits (audit_*),
  execute_roadmap_phase (use hb-roadmap-executor skill instead).
  For audits: load the audit worker directly, skip pre_contract_orchestrator.
---

# HB Track — Pipeline Orchestrator (CDD)

Este skill implementa o protocolo completo do pipeline Contract-Driven Development.
**Toda tarefa de contrato DEVE seguir esta checklist na ordem exata.**

Worker = prompt especializado carregado pelo mesmo agente.
Nao presumir subagentes autonomos, fila ou runtime distribuido.

O humano é leigo em desenvolvimento — comunicar SEMPRE em português, linguagem de produto, nunca jargão técnico.

---

## FASE BOOT — Contexto de Sessão

**Obrigatório ANTES de qualquer outra ação.**

### Checklist Boot

- [ ] **B1** — Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (seções §0-§6)
- [ ] **B2** — Verificar se existe `SESSION_HANDOFF.md` na raiz do workspace
  - Se existe → ler ANTES de qualquer outra ação
  - Se não existe → continuar sem contexto anterior (registrar)
- [ ] **B_MODO** — O pedido é execução de fase do ROADMAP? (infra / CI-CD / frontend / deploy / fase 0-13)
  - Se **sim** → **PARAR este skill**. Usar skill `hb-roadmap-executor` em vez deste. Este skill CDD não se aplica a `execute_roadmap_phase`.
  - Se **não** → continuar para B3.
- [ ] **B3** — Identificar `task_type` e `module` a partir do pedido do humano
  - Se ambíguo → **perguntar explicitamente** (nunca inferir)
  - task_type válidos: `pre_contract_boot` (primeira execução opcional de boot guiado), `new_contract`, `contract_revision`, `new_event`, `new_workflow`, `new_schema`, `new_state_model`, `new_ui_contract`, `new_module`, `architecture_review`, `decision_discovery`, `adversarial_analysis`, `readiness_promotion`, `generate_code`
  - task_type de auditoria (carregam worker diretamente, sem este skill): `audit_sovereign_integrity`, `audit_context_efficiency`, `audit_red_team_pipeline`, `audit_gate_coverage`, `audit_domain_completeness`

### Mapeamento de pedido para task_type

| Pedido do humano (exemplos) | task_type |
|---|---|
| "criar módulo X", "quero criar o módulo X" | `new_contract` (se módulo já tem docs) ou `new_module` (se não) |
| "revisar contrato de X", "alterar API de X" | `contract_revision` |
| "criar eventos para X" | `new_event` |
| "criar workflow de X" | `new_workflow` |
| "criar schema de X" | `new_schema` |

---

## FASE PRÉ-0 — Pre-Contract Boot (Obrigatório — executar PRIMEIRO)

**Validar entrada, determinar task_type correto e roteamento antes de qualquer outra tarefa de contrato.**

### Checklist Fase Pré-0

- [ ] **PRE0.1** — Executar no terminal para determinar o task_type correto:
  ```bash
  python3 scripts/hb verify --task-type pre_contract_boot --module <MODULE>
  ```
  Passar o módulo identificado em B3.
- [ ] **PRE0.2** — Verificar exitcode = 0
  - Se exitcode ≠ 0 → ler mensagem de erro, corrigir e-executar
  - Este passo valida que: (a) módulo existe, (b) task_type será permitido, (c) worker correspondente existe
- [ ] **PRE0.3** — Confirmar saída:
  ```
  ✅ Pre-contract boot validado: module=<M>, task_type_target=<T>, worker=<W>
  ```
- [ ] **PRE0.4** — Avançar para FASE 0 com o task_type específico confirmado

### Bloqueios possíveis nesta fase

| Código | Significado | Ação |
|---|---|---|
| `BLOCKED_MISSING_MODULE` | Módulo não está nos 17 canônicos | Informar humano, perguntar módulo correto |
| `BLOCKED_MISSING_AGENT_PROMPT` | Task_type não existe ou está congelado | Informar humano, listar task_types ativos |

---

## FASE 0 — Session Boot (Bloqueante)

**Executar `hb verify` no terminal. Se exitcode ≠ 0 → corrigir, re-executar.**

### Checklist Fase 0

- [ ] **F0.1** — Executar no terminal:
  ```bash
  python3 scripts/hb verify --task-type <TASK_TYPE> --module <MODULE>
  ```
  Substituir `<TASK_TYPE>` e `<MODULE>` pelos valores identificados em B3.
- [ ] **F0.2** — Verificar exitcode = 0
  - Se exitcode ≠ 0 → ler mensagem de erro, corrigir, re-executar
  - Erros comuns: task_type inválido, module não existe, worker ausente
- [ ] **F0.3** — Confirmar que `_reports/session_start.json` foi criado/atualizado com o module e task_type corretos
- [ ] **F0.4** — Ler o `boot_profile_id` retornado (geralmente `contract_execution`)
- [ ] **F0.5** — Emitir para o humano:
  ```
  ✅ Sessão iniciada: task_type=<T>, module=<M>, profile=<P>
  ```

### Bloqueios possíveis nesta fase

| Código | Significado | Ação |
|---|---|---|
| `BLOCKED_MISSING_MODULE` | Módulo não está nos 17 canônicos | Informar humano |
| `BLOCKED_MISSING_AGENT_PROMPT` | Worker prompt não existe ou task_type congelado | Informar humano |

---

## FASE 1 — Discovery (Bloqueante)

**Verificar que o módulo tem todos os artefatos obrigatórios.**

### Checklist Fase 1

- [ ] **F1.1** — Executar no terminal:
  ```bash
  python3 scripts/hb check --module <MODULE>
  ```
- [ ] **F1.2** — Verificar exitcode = 0
  - Se exitcode ≠ 0 → identificar artefatos faltantes, informar humano
- [ ] **F1.3** — Ler docs do módulo alvo (carregar para contexto):
  - `docs/hbtrack/modulos/<module>/README.md`
  - `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE_UPPER>.md`
  - `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE_UPPER>.md`
  - `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE_UPPER>.md`
  - `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE_UPPER>.md`
- [ ] **F1.4** — Verificar `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` para decisões abertas do módulo
  - Se existem decisões obrigatórias abertas → ir para DECISION DISCOVERY
  - Se não existem → continuar para FASE 2
- [ ] **F1.5** — Se o contrato terá referências cross-module ($ref para outros módulos):
  ```bash
  python3 scripts/gates/check_scope_boundary.py <artifact_path>
  ```
  (Executar após criar o artefato, antes da validação)

### Bloqueios possíveis nesta fase

| Código | Significado |
|---|---|
| `BLOCKED_REQUIRED_ARTIFACT_MISSING` | Doc obrigatória ausente |
| `BLOCKED_SCOPE_OVERFLOW` | Referência cross-module não autorizada |

---

## DECISION DISCOVERY (Condicional)

**Ativado quando: decisão obrigatória aberta, AUTH/AUTHZ envolvido, eventos assíncronos, semântica de handebol.**

### Checklist Decision Discovery

- [ ] **DD.1** — Ler o worker de decisões:
  ```
  .contract_driven/agent_prompts/decision_discovery.prompt.md
  ```
- [ ] **DD.2** — Ler fontes obrigatórias:
  - `docs/_canon/DECISION_POLICY.md`
  - `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
  - `.contract_driven/COMPETITIVE_BENCHMARK_PROTOCOL.md`
  - ADRs relevantes em `docs/_canon/decisions/`
  - `docs/_canon/SECURITY_RULES.md` (se AUTH/dados sensíveis)
  - `docs/_canon/DATA_CONVENTIONS.md` (se datetime/IDs)
  - `docs/_canon/HANDBALL_RULES_DOMAIN.md` (se semântica esportiva)
- [ ] **DD.3** — Para cada decisão pendente, executar **benchmark competitivo**:
  - Pesquisar como outras plataformas esportivas resolvem a questão
  - Documentar achados antes de apresentar opções
- [ ] **DD.4** — Apresentar ao humano no formato:
  ```
  📊 Benchmark de mercado: [resumo do que outros fazem]

  🎯 3 caminhos:
    A) [opção conservadora] — [descrição em linguagem de produto]
    B) [opção intermediária] — [descrição]
    C) [opção completa] — [descrição]

  ⭐ Recomendação: [X] porque [justificativa baseada no benchmark + domínio]
  ```
- [ ] **DD.5** — **AGUARDAR aprovação explícita** do humano (nunca avançar sem confirmação)
- [ ] **DD.6** — Após aprovação, criar:
  - `DECISION_IR_<MODULE>.yaml` em `.contract_driven/decisions/`
  - ADR formal: `docs/_canon/decisions/ADR-NNN-slug.md` (obter próximo número)
  - Atualizar `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`

---

## FASE 2 — Authoring (Worker Especializado)

**Carregar o worker prompt correto e seguir suas instruções específicas.**

### Checklist Fase 2

- [ ] **F2.1** — Identificar o worker correto via `TASK_CATALOG.yaml`:

  | task_type | worker_path |
  |---|---|
  | `new_contract` / `contract_revision` | `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` |
  | `new_event` | `.contract_driven/agent_prompts/create_asyncapi_contract.prompt.md` |
  | `new_workflow` | `.contract_driven/agent_prompts/create_arazzo_workflow.prompt.md` |
  | `new_schema` | `.contract_driven/agent_prompts/create_json_schema_contract.prompt.md` |
  | `new_state_model` | `.contract_driven/agent_prompts/create_state_model.prompt.md` |
  | `new_ui_contract` | `.contract_driven/agent_prompts/create_ui_contract.prompt.md` |
  | `new_module` | `.contract_driven/agent_prompts/create_module_docs.prompt.md` |
  | `adversarial_analysis` | `.contract_driven/agent_prompts/adversarial_analysis.prompt.md` |
  | `readiness_promotion` | `.contract_driven/agent_prompts/readiness_promotion.prompt.md` |

- [ ] **F2.2** — **LER o worker prompt** (obrigatório antes de criar qualquer artefato)
- [ ] **F2.3** — Ler fontes SSOT na ordem prescrita pelo worker:
  - `.contract_driven/CONTRACT_SYSTEM_RULES.md` (seções relevantes, não inteiro)
  - `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` (para paths canônicos)
  - `.contract_driven/templates/api/api_rules.yaml` (para OpenAPI)
  - `.contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml`
  - Política resolvida: `generated/resolved_policy/<module>.*.resolved.yaml` (se existir)
- [ ] **F2.4** — Criar artefato(s) nos paths canônicos corretos
- [ ] **F2.5** — **Para CADA artefato criado**, registrar no terminal:
  ```bash
  python3 scripts/hb artifact <caminho_relativo_do_artefato>
  ```
  Exemplo: `python3 scripts/hb artifact contracts/openapi/paths/scout.yaml`
- [ ] **F2.6** — Se é OpenAPI (new_contract/contract_revision):
  - Atualizar `contracts/openapi/openapi.yaml` com novos `$ref` se necessário
  - Criar/atualizar schema em `contracts/openapi/components/schemas/<module>/`
- [ ] **F2.7** — Se é AsyncAPI (new_event):
  - Criar channel, message, payload em `contracts/asyncapi/`
  - Atualizar `contracts/asyncapi/asyncapi.yaml` com novos channels
- [ ] **F2.8** — Se é Arazzo (new_workflow):
  - Criar em `contracts/workflows/<module>/`

---

## FASE 2.5 — Compilação Determinística (Pós-Authoring)

**Obrigatório após criar/modificar qualquer contrato.**

### Checklist Compilação

- [ ] **C.1** — Se modificou contrato de UM módulo:
  ```bash
  python3 scripts/contracts/validate/api/compile_api_policy.py --module <MODULE> --surface sync
  ```
- [ ] **C.2** — Se modificou contratos de MÚLTIPLOS módulos ou arquivos globais:
  ```bash
  python3 scripts/contracts/validate/api/compile_api_policy.py --all
  ```
- [ ] **C.3** — Verificar exitcode = 0
  - Se exit 2 → DERIVED_DRIFT: recompilar com `--all`
- [ ] **C.4** — Atualizar `CANONICAL_TYPE_REGISTRY.yaml` se novos tipos semânticos foram criados

---

## FASE 3 — Validation (44 Gates)

### Checklist Validation

- [ ] **V.1** — Executar no terminal:
  ```bash
  python3 scripts/contracts/validate/validate_contracts.py
  ```
- [ ] **V.2** — Verificar `overall_status: PASS` no output
  - Se FAIL → ler gates que falharam, corrigir, recompilar (Fase 2.5), re-validar
- [ ] **V.3** — Confirmar que `_reports/contract_gates/latest.json` mostra PASS
- [ ] **V.4** — Confirmar que `_reports/pipeline_history.jsonl` tem nova entrada

---

## FASE 4 — Readiness

### Checklist Readiness

- [ ] **R.1** — Atualizar `docs/_canon/MODULE_REGISTRY.yaml`:
  - Status do módulo: `draft_contract` → `validated_contract`
  - `expected_surfaces`: atualizar lista com todas as surfaces criadas
- [ ] **R.2** — Atualizar `_reports/evidence/module_readiness_scorecard.json` (se aplicável)
- [ ] **R.3** — Atualizar roadmap se existir (`docs/guias/MODULE_ROADMAP_*.md`)

---

## FASE 5 — Handoff

**Obrigatório ao final de toda sessão de contrato.**

`SESSION_HANDOFF.md` e o handoff operacional atual.
Nao tratar `contracts/schemas/shared/session_handoff.schema.json` como o validador ativo desse markdown.

### Checklist Handoff

- [ ] **H.1** — Criar ou atualizar `SESSION_HANDOFF.md` na raiz com:
  ```markdown
  # SESSION HANDOFF — HB TRACK
  ## Estado Geral
  **Data:** <YYYY-MM-DD> | **Branch:** <branch> | **CI:** <status>
  **Módulo trabalhado:** <module>
  **Task type:** <task_type>
  **Resultado:** Pipeline PASS/FAIL

  ## O que foi feito
  - [lista de artefatos criados/modificados]

  ## Decisões tomadas
  - [lista de decisões com referência ao DECISION_IR]

  ## Próximos passos
  - [o que falta fazer]

  ## Bloqueios ativos
  - [se houver]
  ```
- [ ] **H.2** — Informar humano do resultado final em linguagem de produto

---

## FASE 6 — Commit (Fechamento de versionamento)

Use commit quando a sessão precisar persistir artefatos em git.
O pipeline já executa checkpoints via `hb` e `validate_contracts.py`; o commit adiciona o checkpoint do hook `pre-commit`.

### Checklist Commit

- [ ] **C6.1** — Stagear APENAS os artefatos da sessão (nunca `git add -A`):
  ```bash
  git add SESSION_HANDOFF.md
  git add docs/_canon/MODULE_REGISTRY.yaml
  git add <todos os artefatos listados em stage2_artifacts>
  ```
- [ ] **C6.2** — Verificar o que será commitado:
  ```bash
  git status
  git diff --cached --stat
  ```
  Confirmar que nenhum arquivo sensível (`.env`, credenciais) está staged.
- [ ] **C6.3** — Executar o commit com mensagem canônica:
  ```bash
  git commit -m "feat(contract): <module> — <task_type> pipeline PASS

  Artefatos: <lista resumida>
  Gates: PASS (<N> gates verificados)
  Decisões: <ADR refs se houver>"
  ```
- [ ] **C6.4** — Verificar que o pre-commit hook passou (exitcode 0):
  - Se o hook **bloquear** → ler a mensagem de erro, corrigir o problema, repetir a partir do passo que falhou
  - Se o hook passar → commit concluído
- [ ] **C6.5** — Confirmar ao humano:
  ```
  ✅ Commit realizado: <hash curto> — "<mensagem>"
  Branch: <branch>
  Próximo passo: abrir PR para main quando a feature estiver completa.
  ```

### Bloqueios possíveis nesta fase

| Código do hook | Causa | Ação |
|---|---|---|
| `BLOCKED_PROMOTION_PENDING` | Módulo com todas as surfaces mas status não atualizado | Atualizar MODULE_REGISTRY.yaml + `hb artifact` |
| `BLOCKED_REGISTRY_MISMATCH` | Artefato staged sem `hb artifact` registrado | Executar `hb artifact <path>` |
| Hash mismatch | Arquivo modificado após `hb artifact` | Re-executar `hb artifact <path>` |
| `SESSION_HANDOFF.md` ausente | FASE 5 não concluída | Completar FASE 5 primeiro |
| `validate_contracts` FAIL | Gate bloqueante ainda aberto | Corrigir violação, recompilar, revalidar |

---

## REGRAS DE OURO

1. **NUNCA pular fases** — cada fase depende da anterior
2. **NUNCA inferir** — se falta artefato canônico, emitir código de bloqueio BLOCKED_*
3. **SEMPRE executar hb verify ANTES de criar artefatos**
4. **SEMPRE executar hb artifact APÓS criar cada artefato**
5. **SEMPRE ler o worker prompt ANTES de criar o artefato**
6. **SEMPRE compilar (compile_api_policy) ANTES de validar (validate_contracts)**
7. **SEMPRE atualizar SESSION_HANDOFF ao final**
8. **SE a sessão for ser persistida em git, fazer o commit ao final**
9. **Comunicação em português**, linguagem de produto, nunca jargão técnico
