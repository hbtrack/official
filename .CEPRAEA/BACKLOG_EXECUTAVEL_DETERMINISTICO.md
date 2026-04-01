# BACKLOG_EXECUTAVEL_DETERMINISTICO

## 0. Objetivo

Este backlog transforma o plano de [PIPELINEFINAL.md](/home/davis/HB-TRACK/.CEPRAEA/PIPELINEFINAL.md) em execucao deterministica, validada contra o sistema atual do HB Track.

Regra de leitura:

- cada item abaixo e atomico
- cada item tem dependencia explicita
- cada item define arquivos, comandos, criterio de saida e rollback
- nao existe "ajustar depois"
- se um item falhar, o proximo nao comeca

## 1. Baseline validado do sistema atual

Estado confirmado antes de abrir este backlog:

- `_reports/contract_gates/latest.json` esta `PASS`
- gates ainda `SKIP_NOT_APPLICABLE`:
  - `HTTP_RUNTIME_CONTRACT_GATE`
  - `PACT_PROVIDER_GATE`
  - `READINESS_HUMAN_CONFIRMATION_GATE`
- `main` usa ruleset GitHub ativo `contract-gates`
- o ruleset exige apenas o status check `Validate Contract Gates`
- todos os 17 modulos de negocio em `docs/_canon/MODULE_REGISTRY.yaml` estao em `implemented`
- `src/<module>/api.py`, `migrations/` e `tests/` existem para 17 modulos
- nao existe backend codegen deterministico oficial
- `generate_code` ainda aceita `status>=validated_contract`
- `ARCH_DECISION_PRESENCE_GATE` segue `deferred`

Implicacao operacional:

- este backlog comeca por governanca, sincronismo e compiler
- este backlog nao autoriza apagar `src/` inteiro agora
- a migracao para codigo gerado deve ser modular

## 2. Regras de execucao do backlog

### 2.1 Regras globais

- nao editar manualmente artefato marcado como derivado
- nao criar novo source master sem registrar em `SOURCE_AUTHORITY_GRAPH.yaml`
- nao iniciar tarefa dependente sem a anterior em `PASS`
- toda tarefa precisa deixar teste ou gate novo ativo
- toda tarefa precisa deixar rollback definido

### 2.2 Comandos obrigatorios por fechamento de tarefa

Toda tarefa que altera governanca, validator, hooks, schemas ou workflows deve fechar com:

```bash
python3 scripts/validate_contracts.py --profile ci
pytest tests/pipeline_gates -q
```

Toda tarefa que altera `src/**` ou codegen deve fechar com:

```bash
pytest -q -m "not slow" --tb=short
python3 scripts/validate_contracts.py --profile ci
```

Toda tarefa que altera workflow GitHub deve fechar com:

```bash
python3 scripts/validate_contracts.py --profile ci
pytest tests/pipeline_gates -q
python3 scripts/audit/check_architecture_docs.py --json
```

## 3. No-Go explicito

Estas acoes estao proibidas neste backlog:

- apagar `src/` inteiro
- editar manualmente todos os contratos para "alinhar"
- mover regra substantiva para prompt sem source soberano correspondente
- fazer big-bang rewrite do backend
- declarar "100 por cento" antes de source graph + compiler + codegen + parity harness + ruleset endurecido

## 4. Backlog executavel

## B-ENV. Reprodutibilidade local obrigatoria

### B-ENV-001 - Criar bootstrap local unico para validacao e governanca

Objetivo:

- garantir que os comandos de validacao do backlog rodam de forma reprodutivel no workspace local

Justificativa validada:

- hoje `python3 scripts/hb survival-suite` falha localmente por falta de `pytest`
- portanto, antes do backlog principal, o ambiente local precisa de bootstrap deterministico

Dependencias:

- nenhuma

Arquivos a criar:

- `scripts/bootstrap/dev_contract_env.sh`
- `scripts/bootstrap/dev_contract_env.ps1`

Arquivos a editar:

- `scripts/hb`
- `.CEPRAEA/PIPELINEFINAL.md` se quiser referenciar o bootstrap

Comportamento obrigatorio do bootstrap:

- instalar dependencias Python minimas para governanca e testes
- instalar dependencias Node necessarias para validator
- verificar `oasdiff`, `spectral`, `redocly`, `asyncapi`, `schemathesis`
- emitir resumo final `PASS/FAIL`

Validacao:

```bash
bash scripts/bootstrap/dev_contract_env.sh
python3 scripts/hb survival-suite
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- o ambiente local consegue reproduzir a suite de governanca sem erro de dependencia ausente

Rollback:

- remover scripts de bootstrap

Subtarefas imediatas:

#### B-ENV-001.1

- arquivo: `scripts/bootstrap/dev_contract_env.sh`
- mudanca:
  - criar script idempotente
  - verificar `python3`, `node`, `npm`
  - instalar dependencias Python minimas para `validate_contracts.py`, `pytest`, `schemathesis`
  - instalar dependencias Node via `npm ci`
  - verificar `oasdiff`, `redocly`, `spectral`, `asyncapi`
  - emitir resumo final `PASS/FAIL`
- teste:
  - criar `tests/pipeline_gates/test_dev_contract_env_script_exists.py`
- comando:
```bash
bash scripts/bootstrap/dev_contract_env.sh
pytest tests/pipeline_gates/test_dev_contract_env_script_exists.py -q
```
- criterio de aceite:
  - script existe
  - script encerra com `0` quando o ambiente esta pronto
  - script falha com mensagem acionavel quando faltar dependencia

#### B-ENV-001.2

- arquivo: `scripts/bootstrap/dev_contract_env.ps1`
- mudanca:
  - criar equivalente PowerShell do bootstrap Linux
  - manter mesma ordem de verificacao e mesma semantica de `PASS/FAIL`
- teste:
  - criar `tests/pipeline_gates/test_dev_contract_env_ps1_exists.py`
- comando:
```bash
pytest tests/pipeline_gates/test_dev_contract_env_ps1_exists.py -q
```
- criterio de aceite:
  - script PowerShell existe
  - flags e objetivo sao equivalentes ao `.sh`

#### B-ENV-001.3

- arquivo: `scripts/bootstrap/requirements-contract-dev.txt`
- mudanca:
  - criar manifest Python minimo e pinned para governanca local
  - incluir `pytest`, `schemathesis` e deps necessarias do validator
- teste:
  - criar `tests/pipeline_gates/test_contract_dev_requirements_pinned.py`
- comando:
```bash
pytest tests/pipeline_gates/test_contract_dev_requirements_pinned.py -q
```
- criterio de aceite:
  - todas as deps do bootstrap Python estao pinadas
  - `survival-suite` deixa de falhar por `pytest` ausente apos bootstrap

### B-ENV-002 - Integrar bootstrap ao fluxo local do `hb`

Objetivo:

- impedir execucao local sem ambiente minimamente valido

Dependencias:

- B-ENV-001

Arquivos a editar:

- `scripts/hb`

Teste a criar:

- `tests/pipeline_gates/test_hb_bootstrap_guard.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_hb_bootstrap_guard.py -q
python3 scripts/hb survival-suite
```

Criterio de saida:

- `hb survival-suite` e comandos criticos detectam ambiente ausente e falham com mensagem unica e acionavel

Rollback:

- remover precheck do `hb`

Subtarefas imediatas:

#### B-ENV-002.1

- arquivo: `scripts/hb`
- mudanca:
  - criar funcao `check_local_contract_env()` antes de `survival-suite`, `stage3` e demais comandos de validacao total
  - detectar falta de `pytest`, `schemathesis`, `npm ci` ou ferramenta critica
  - imprimir comando de bootstrap recomendado
- teste:
  - `tests/pipeline_gates/test_hb_bootstrap_guard.py`
- comando:
```bash
pytest tests/pipeline_gates/test_hb_bootstrap_guard.py -q
```
- criterio de aceite:
  - erro local de ambiente deixa de aparecer como stacktrace solto
  - `hb` aponta para `scripts/bootstrap/dev_contract_env.sh`

#### B-ENV-002.2

- arquivo: `scripts/hb`
- mudanca:
  - padronizar codigo de saida para ambiente ausente
  - diferenciar `BLOCKED_LOCAL_TOOLCHAIN_MISSING` de falha real de gate
- teste:
  - ampliar `tests/pipeline_gates/test_hb_bootstrap_guard.py`
- comando:
```bash
pytest tests/pipeline_gates/test_hb_bootstrap_guard.py -q
```
- criterio de aceite:
  - ambiente ausente e distinguivel de gate FAIL

### B-ENV-003 - Paridade local x CI do bootstrap de governanca

Objetivo:

- garantir que o bootstrap local reflita o ambiente de CI e nao vire nova fonte de drift

Dependencias:

- B-ENV-001
- B-ENV-002

Arquivos a editar:

- `.github/workflows/contract-gates.yml`
- `.github/workflows/ci.yml`

Testes a criar:

- `tests/pipeline_gates/test_bootstrap_ci_local_parity.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_bootstrap_ci_local_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- toolchain minima exigida localmente bate com a toolchain minima da CI para governanca e validator

Rollback:

- remover teste de paridade e voltar ao acoplamento solto anterior

Subtarefas imediatas:

#### B-ENV-003.1

- arquivo: `.github/workflows/contract-gates.yml`
- mudanca:
  - adicionar comentario/etapa referenciando o bootstrap local como paridade de setup
  - consolidar lista minima de tooling usada pelo bootstrap
- teste:
  - `tests/pipeline_gates/test_bootstrap_ci_local_parity.py`
- comando:
```bash
pytest tests/pipeline_gates/test_bootstrap_ci_local_parity.py -q
```
- criterio de aceite:
  - workflow e bootstrap compartilham a mesma lista minima de ferramentas

#### B-ENV-003.2

- arquivo: `.github/workflows/ci.yml`
- mudanca:
  - alinhar validate job com os prerequisitos minimos do bootstrap
  - nao deixar `ci.yml` divergir silenciosamente do ambiente minimo local
- teste:
  - `tests/pipeline_gates/test_bootstrap_ci_local_parity.py`
- comando:
```bash
pytest tests/pipeline_gates/test_bootstrap_ci_local_parity.py -q
```
- criterio de aceite:
  - mudanca no setup de CI quebra o teste de paridade se o bootstrap local nao for atualizado

## B0. Governanca e autoridade

### B0-001 - Criar grafo de autoridade soberana

Objetivo:

- eliminar ambiguidade de source master

Dependencias:

- nenhuma

Arquivos a criar:

- `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml`

Arquivos a editar:

- `docs/_canon/AGENT_INSTRUCTIONS.md`
- `docs/_canon/CONTRACT_PIPELINE.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`

Conteudo obrigatorio:

- owner source por conceito
- regra de conflito
- classificacao `sovereign`, `derived`, `bridge`, `runtime_extension`

Validacao:

```bash
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- nenhum conceito critico do sistema fica sem owner source
- os tres arquivos acima citam o mesmo grafo como autoridade

Rollback:

- remover `SOURCE_AUTHORITY_GRAPH.yaml`
- reverter os tres arquivos ao estado anterior

### B0-002 - Tornar `docs/guias/**` explicitamente nao normativo

Objetivo:

- impedir que documentacao stale continue competindo com o canon

Dependencias:

- B0-001

Arquivos a editar:

- `docs/guias/README.md` se existir
- `docs/guias/pipeline/PIPELINE.md`
- `docs/guias/produto/CODE.md`
- demais arquivos em `docs/guias/**` que hoje soam normativos

Acoes:

- adicionar banner padrao `DERIVED_OR_ANALYSIS_ONLY`
- remover linguagem de autoridade soberana
- apontar para o source master correspondente

Teste a criar:

- `tests/pipeline_gates/test_docs_guias_non_sovereign.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_docs_guias_non_sovereign.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- nenhum arquivo em `docs/guias/**` se apresenta como fonte soberana

Rollback:

- reverter banners e teste

### B0-003 - Expandir GOVERNANCE_PATHS para todas as superficies reais de agente

Objetivo:

- trazer `.github/agents/**`, `.github/instructions/**`, `CLAUDE.md` e `.codex` para a mesma governanca

Dependencias:

- B0-001

Arquivos a editar:

- `.github/workflows/contract-gates.yml`
- `scripts/git-hooks/pre-commit`

Acoes:

- incluir:
  - `.github/agents/**`
  - `.github/instructions/**`
  - `CLAUDE.md`
  - `.codex`

Validacao:

```bash
pytest tests/pipeline_gates/test_agent_compliance_phase0.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- mudanca nessas superficies dispara os jobs de governanca

Rollback:

- restaurar filtros anteriores

### B0-004 - Criar manifesto obrigatorio de uso e freshness de documentacao

Objetivo:

- garantir que nenhum arquivo em `docs/_canon` ou `docs/hbtrack` fique sem consumidor, sem owner de freshness ou sem trigger de atualizacao

Dependencias:

- nenhuma

Nota de ordem real:

- este item foi antecipado e validado no sistema atual antes de `B0-001`
- apos `B0-001`, o manifesto deve ser apenas revalidado e refinado, nao refeito

Arquivos a criar:

- `docs/_canon/DOC_USAGE_MANIFEST.yaml`

Cobertura obrigatoria do manifesto:

- todo arquivo em `docs/_canon/**`
- todo arquivo em `docs/hbtrack/modulos/**`

Campos obrigatorios por documento:

- `path`
- `class`
- `owner_source`
- `consumers`
- `freshness_mode`
- `update_triggers`
- `generated_by` quando for derivado

Validacao:

```bash
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- nenhum arquivo em `docs/_canon` e `docs/hbtrack` fica fora do manifesto

Rollback:

- remover o manifesto

## B1. Endurecimento do enforcement atual

### B1-001 - Tornar `stage_allowed` bloqueio hard

Objetivo:

- remover aviso informativo e impedir roteamento fora do stage permitido

Dependencias:

- B0-003

Arquivos a editar:

- `scripts/hb`
- `.contract_driven/TASK_CATALOG.yaml` se necessario
- `.github/instructions/hb-contract-guards.instructions.md`

Testes a criar/editar:

- `tests/pipeline_gates/test_stage_allowed_enforcement.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_stage_allowed_enforcement.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- task executada fora do stage permitido falha com codigo de bloqueio explicito

Rollback:

- restaurar comportamento warning-only

### B1-002 - Restringir `generate_code` para `implementation_ready+`

Objetivo:

- alinhar implementacao com o lifecycle formal

Dependencias:

- B1-001

Arquivos a editar:

- `scripts/hb`
- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/agent_prompts/generate_code.prompt.md`
- `.github/instructions/hb-contract-guards.instructions.md`
- `docs/_canon/CONTRACT_PIPELINE.md`

Testes a criar/editar:

- `tests/pipeline_gates/test_generate_code_requires_implementation_ready.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_generate_code_requires_implementation_ready.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- `hb verify --task-type generate_code --module <mod>` falha quando `<mod>` esta abaixo de `implementation_ready`

Rollback:

- restaurar elegibilidade atual

### B1-003 - Tornar `check_backend_gate.py` fail-closed

Objetivo:

- impedir bypass por erro de parse ou excecao

Dependencias:

- B1-002

Arquivos a editar:

- `scripts/hooks/check_backend_gate.py`

Testes a criar:

- `tests/pipeline_gates/test_backend_hook_fail_closed.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_backend_hook_fail_closed.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- qualquer excecao interna no hook resulta em bloqueio, nao em sucesso silencioso

Rollback:

- restaurar comportamento anterior

### B1-004 - Implementar `ARCH_DECISION_PRESENCE_GATE`

Objetivo:

- fechar DSS end-to-end no validator

Dependencias:

- B1-002

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`
- `.contract_driven/agent_prompts/decision_discovery.prompt.md`
- `.contract_driven/agent_prompts/readiness_promotion.prompt.md`

Testes a criar:

- `tests/pipeline_gates/test_arch_decision_presence_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- modulo/feature com decisao obrigatoria aberta nao pode ser promovido nem implementado

Rollback:

- voltar o gate para `deferred`
- remover invocacao do executor

Subtarefas imediatas:

#### B1-004.1

- arquivo: `docs/_canon/gates/GATES_REGISTRY.yaml`
- mudanca:
  - tirar `ARCH_DECISION_PRESENCE_GATE` de `deferred`
  - definir `order`, `severity`, `blocking`, `applies_when`, `depends_on`, `blocking_codes`
- teste:
  - `tests/pipeline_gates/test_gate_registry_parity.py`
- comando:
```bash
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
```
- criterio de aceite:
  - gate aparece no registry como ativo e consistente com o executor esperado

#### B1-004.2

- arquivo: `scripts/contracts/validate/validate_contracts.py`
- mudanca:
  - implementar `_g_arch_decision_presence(...)`
  - ler backlog arquitetural
  - detectar decisoes `open` ou `blocked` com criticidade obrigatoria
  - falhar quando houver decisao obrigatoria pendente para modulo/escopo afetado
- teste:
  - `tests/pipeline_gates/test_arch_decision_presence_gate.py`
- comando:
```bash
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
```
- criterio de aceite:
  - backlog com decisao obrigatoria aberta gera FAIL bloqueante
  - backlog sem pendencia obrigatoria gera PASS ou SKIP claramente justificado

#### B1-004.3

- arquivo: `scripts/contracts/validate/validate_contracts.py`
- mudanca:
  - inserir o gate no `gate_plan` do profile `ci`
  - garantir que o gate apareca no report final
- teste:
  - `tests/pipeline_gates/test_gate_registry_parity.py`
  - `tests/pipeline_gates/test_arch_decision_presence_gate.py`
- comando:
```bash
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
python3 scripts/validate_contracts.py --profile ci
```
- criterio de aceite:
  - `latest.json` passa a conter `ARCH_DECISION_PRESENCE_GATE`

#### B1-004.4

- arquivo: `.contract_driven/agent_prompts/decision_discovery.prompt.md`
- mudanca:
  - alinhar wording do prompt ao comportamento real do gate
  - proibir linguagem mais fraca que o validator
- teste:
  - `tests/pipeline_gates/test_arch_decision_presence_gate.py`
- comando:
```bash
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
```
- criterio de aceite:
  - prompt e gate bloqueiam com a mesma semantica

#### B1-004.5

- arquivo: `.contract_driven/agent_prompts/readiness_promotion.prompt.md`
- mudanca:
  - incluir `ARCH_DECISION_PRESENCE_GATE` como precondicao explicita da promocao
  - remover qualquer ambiguidade entre prompt e validator
- teste:
  - `tests/pipeline_gates/test_arch_decision_presence_gate.py`
- comando:
```bash
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
```
- criterio de aceite:
  - promocao para `implementation_ready` nao avanca com decisao obrigatoria aberta

#### B1-004.6

- arquivo: `tests/pipeline_gates/test_arch_decision_presence_gate.py`
- mudanca:
  - cobrir ao menos 4 cenarios:
    - decisao obrigatoria aberta global
    - decisao obrigatoria aberta por modulo
    - decisao resolvida
    - gate listado no report final
- teste:
  - o proprio arquivo
- comando:
```bash
pytest tests/pipeline_gates/test_arch_decision_presence_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```
- criterio de aceite:
  - regressao no gate e detectada por teste e por report

### B1-005 - Implementar `DOC_USAGE_GATE`

Objetivo:

- bloquear documentacao orfa, sem uso real ou sem regra de freshness

Dependencias:

- B0-004

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Teste a criar:

- `tests/pipeline_gates/test_doc_usage_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_doc_usage_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- qualquer doc sem consumer, sem owner source ou sem trigger de freshness falha no pipeline

Rollback:

- remover gate e manifesto do executor

### B1-006 - Implementar `CANON_CONTRACT_DRIVEN_PARITY_GATE`

Objetivo:

- garantir que `docs/_canon` fique sempre alinhado aos SSOTs operacionais de `.contract_driven`

Dependencias:

- B0-004

Escopo minimo obrigatorio:

- `docs/_canon/AGENT_INSTRUCTIONS.md` <-> `.contract_driven/BOOT_PROFILES.yaml` e `.contract_driven/TASK_CATALOG.yaml`
- `docs/_canon/CONTRACT_PIPELINE.md` <-> `.contract_driven/TASK_CATALOG.yaml` e `scripts/hb`
- `docs/_canon/DECISION_POLICY.md` <-> `.contract_driven/agent_prompts/decision_discovery.prompt.md`
- `docs/_canon/gates/GATES_REGISTRY.yaml` <-> `scripts/contracts/validate/validate_contracts.py`

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Teste a criar:

- `tests/pipeline_gates/test_canon_contract_driven_parity_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_canon_contract_driven_parity_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- deriva operacional entre `docs/_canon` e `.contract_driven` vira falha tecnica

Rollback:

- remover gate novo

### B1-007 - Implementar `HBTRACK_CANON_PARITY_GATE`

Objetivo:

- garantir que `docs/hbtrack/modulos` nunca contradiga `docs/_canon`

Dependencias:

- B0-004

Escopo minimo obrigatorio:

- `MODULE_SCOPE_*` respeita `MODULE_REGISTRY` e `MODULE_SOURCE_AUTHORITY_MATRIX`
- `DOMAIN_RULES_*`, `INVARIANTS_*`, `PERMISSIONS_*`, `STATE_MODEL_*`, `ERRORS_*`, `TEST_MATRIX_*` nao contradizem politicas globais
- docs de modulo com regra compartilhada apontam para canon quando a regra for global

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Teste a criar:

- `tests/pipeline_gates/test_hbtrack_canon_parity_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_hbtrack_canon_parity_gate.py -q
pytest tests/contracts/test_module_doc_governance.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- contradicao entre doc de modulo e canon global falha no pipeline

Rollback:

- remover gate novo

### B1-008 - Gerar `RUNTIME_CURRENT_STATE.md` automaticamente

Objetivo:

- garantir que os current-state docs do canon reflitam sempre o sistema real

Dependencias:

- B0-004

Arquivos a criar:

- `scripts/generate/docs/gen_runtime_current_state.py`

Arquivos a editar:

- `docs/_canon/RUNTIME_CURRENT_STATE.md`
- `scripts/audit/check_architecture_docs.py`

Teste a criar:

- `tests/pipeline_gates/test_runtime_current_state_generator.py`

Validacao:

```bash
python3 scripts/generate/docs/gen_runtime_current_state.py --check
pytest tests/pipeline_gates/test_runtime_current_state_generator.py -q
python3 scripts/audit/check_architecture_docs.py --json
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- `RUNTIME_CURRENT_STATE.md` deixa de ser mantido manualmente
- drift factual entre sistema atual e current-state doc vira falha

Rollback:

- remover generator e voltar ao fluxo manual anterior

## B2. Source graph e compiler

### B2-001 - Definir IR estruturado global

Objetivo:

- tirar regra critica de markdown livre

Dependencias:

- B0-001

Arquivos a criar:

- `docs/_canon/graph/global_rules.yaml`
- `docs/_canon/graph/global_policies.yaml`
- `docs/_canon/graph/lifecycle.yaml`
- `docs/_canon/graph/source_map.yaml`

Arquivos a editar:

- `docs/_canon/AGENT_INSTRUCTIONS.md`
- `docs/_canon/CONTRACT_PIPELINE.md`

Teste a criar:

- `tests/pipeline_gates/test_source_graph_global_integrity.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_source_graph_global_integrity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- toda regra global citada pelo pipeline e referenciavel no IR global

Rollback:

- remover IR global e restaurar referencias

### B2-002 - Definir IR estruturado de modulo piloto `reports`

Racional do piloto:

- `reports` esta `implemented`
- `reports` tem conjunto pequeno de `expected_surfaces`
- `reports` e modulo menos acoplado do que `training`, `video` ou `identity_access`

Dependencias:

- B2-001

Arquivos a criar:

- `docs/hbtrack/modulos/reports/graph/module_manifest.yaml`
- `docs/hbtrack/modulos/reports/graph/entities.yaml`
- `docs/hbtrack/modulos/reports/graph/endpoints.yaml`
- `docs/hbtrack/modulos/reports/graph/errors.yaml`
- `docs/hbtrack/modulos/reports/graph/test_obligations.yaml`

Arquivos a editar:

- `docs/hbtrack/modulos/reports/README.md`
- `docs/hbtrack/modulos/reports/DOMAIN_RULES_REPORTS.md`
- `docs/hbtrack/modulos/reports/TEST_MATRIX_REPORTS.md`

Teste a criar:

- `tests/pipeline_gates/test_reports_source_graph_integrity.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_reports_source_graph_integrity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- o modulo `reports` passa a ter representacao funcional estruturada suficiente para compilar contrato

Rollback:

- remover pasta `graph/` de `reports`

### B2-003 - Implementar compiler de source graph

Objetivo:

- gerar derivados a partir de source unico

Dependencias:

- B2-001
- B2-002

Arquivos a criar:

- `scripts/compile/compile_source_graph.py`
- `scripts/compile/__init__.py`

Arquivos a editar:

- `scripts/hb`
- `.github/workflows/contract-gates.yml`

Saidas obrigatorias do compiler:

- `impact_report.json`
- bundles derivados de `reports`
- views derivadas necessarias para `contracts/`

Teste a criar:

- `tests/pipeline_gates/test_source_graph_compiler_reports.py`

Validacao:

```bash
python3 scripts/compile/compile_source_graph.py --module reports
pytest tests/pipeline_gates/test_source_graph_compiler_reports.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- source graph de `reports` compila sem ambiguidade e produz `impact_report.json`

Rollback:

- remover compiler e artefatos gerados

## B3. Contratos derivados e equivalencia semantica

### B3-001 - Eliminar projecao manual de `reports` no OpenAPI

Objetivo:

- provar a trilha source graph -> contract sem projection drift

Dependencias:

- B2-003

Arquivos a editar ou regenerar:

- `contracts/openapi/components/schemas/reports/report_job.yaml`
- `contracts/openapi/paths/reports.yaml`
- `contracts/schemas/reports/report_job.schema.json` se o source graph apontar correcao necessaria

Teste a criar:

- `tests/pipeline_gates/test_reports_openapi_schema_equivalence.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_reports_openapi_schema_equivalence.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- toda diferenca restante entre OpenAPI e schema soberano de `reports` fica:
  - eliminada
  - ou justificada em mapa de equivalencia gerado

Rollback:

- restaurar contrato anterior de `reports`

### B3-002 - Criar `OPENAPI_SCHEMA_EQUIVALENCE_GATE`

Objetivo:

- transformar equivalencia semantica em gate tecnico

Dependencias:

- B3-001

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Teste a criar:

- `tests/pipeline_gates/test_openapi_schema_equivalence_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_openapi_schema_equivalence_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- projection drift vira erro tecnico detectavel no pipeline

Rollback:

- remover gate do executor e do registry

## B4. Codegen backend deterministico

### B4-001 - Criar layout `generated/` para modulo piloto `reports`

Objetivo:

- separar zona gerada da zona manual

Dependencias:

- B3-002

Arquivos a criar:

- `src/reports/generated/__init__.py`
- `src/reports/generated/domain/__init__.py`
- `src/reports/generated/application/__init__.py`
- `src/reports/generated/infrastructure/__init__.py`
- `src/reports/generated/tests/__init__.py`

Arquivos a editar:

- `docs/_canon/CODE_ARCHITECTURE.md`

Teste a criar:

- `tests/pipeline_gates/test_generated_layout_reports.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_generated_layout_reports.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- o modulo piloto passa a ter layout oficial para codigo gerado

Rollback:

- remover `src/reports/generated/`

### B4-002 - Implementar `backend_codegen.py` para `reports`

Objetivo:

- gerar backend estrutural deterministico do modulo piloto

Dependencias:

- B4-001

Arquivos a criar:

- `scripts/generate/backend_codegen.py`

Arquivos a gerar para o piloto:

- `src/reports/generated/schemas.py`
- `src/reports/generated/api.py`
- `src/reports/generated/domain/entities.py`
- `src/reports/generated/application/use_cases.py`
- `src/reports/generated/infrastructure/repository.py`
- `src/reports/generated/tests/test_codegen_contract.py`

Teste a criar:

- `tests/pipeline_gates/test_backend_codegen_reports.py`

Validacao:

```bash
python3 scripts/generate/backend_codegen.py --module reports
pytest tests/pipeline_gates/test_backend_codegen_reports.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- duas execucoes seguidas produzem hash identico
- o codigo gerado compila

Rollback:

- remover artefatos gerados e script

### B4-003 - Criar parity harness para `reports`

Objetivo:

- provar que o codigo gerado preserva comportamento util

Dependencias:

- B4-002

Arquivos a criar:

- `tests/parity/test_reports_codegen_parity.py`
- `tests/parity/fixtures/reports/*.json` se necessario

Comparacoes obrigatorias:

- contratos HTTP
- serializacao de payload
- erros esperados
- casos positivos e negativos de `reports`

Validacao:

```bash
pytest tests/parity/test_reports_codegen_parity.py -q
pytest -q -m "not slow" --tb=short
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- implementacao gerada e antiga produzem o mesmo comportamento nos cenarios cobertos

Rollback:

- manter apenas implementacao antiga e remover parity suite

### B4-004 - Fazer cutover controlado de `reports`

Objetivo:

- usar o codigo gerado no runtime real do modulo piloto

Dependencias:

- B4-003

Arquivos a editar:

- `src/reports/api.py`
- `src/reports/schemas.py`
- `src/reports/models.py` se necessario

Regra:

- os adaptadores canonicos passam a importar/compor `src/reports/generated/**`

Validacao:

```bash
pytest tests/parity/test_reports_codegen_parity.py -q
pytest -q -m "not slow" --tb=short
python3 scripts/validate_contracts.py --profile ci
```

Saida obrigatoria extra:

- registrar evidencias em `SESSION_HANDOFF.md`

Criterio de saida:

- `reports` roda via camada gerada sem regressao observada

Rollback:

- restaurar `src/reports/*` para implementacao anterior

## B5. Lifecycle formal

### B5-001 - Criar `implementation_promotion`

Objetivo:

- formalizar `implementation_ready -> implemented`

Dependencias:

- B4-004

Arquivos a criar/editar:

- `.contract_driven/agent_prompts/implementation_promotion.prompt.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `docs/_canon/CONTRACT_PIPELINE.md`
- `docs/_canon/MODULE_REGISTRY.yaml`

Teste a criar:

- `tests/pipeline_gates/test_implementation_promotion.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_implementation_promotion.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- nenhum modulo vira `implemented` fora do worker formal

Rollback:

- remover worker e restaurar catalogo

Status atual validado no sistema:

- `.contract_driven/agent_prompts/implementation_promotion.prompt.md` criado
- `.contract_driven/TASK_CATALOG.yaml` atualizado com worker `implementation_promotion` ativo
- `docs/_canon/CONTRACT_PIPELINE.md` atualizado para exigir promocao formal em `implementation_ready -> implemented`
- `docs/_canon/MODULE_REGISTRY.yaml` atualizado para declarar `implementation_promotion` como caminho formal
- `contracts/schemas/shared/session_start.schema.json` e `generated/contracts/schemas/shared/session_start.schema.json` atualizados com o novo `task_type`
- `scripts/hb` endurecido com `BLOCKED_IMPLEMENTATION_PROMOTION_INELIGIBLE` e `write_scope=docs`
- `tests/pipeline_gates/test_implementation_promotion.py` criado e verde
- `python3 scripts/repair_manifests.py` executado para sincronizar manifests de rastreabilidade
- `python3 scripts/generate/docs/gen_runtime_current_state.py --write` executado para ressincronizar derivado canônico
- `python3 scripts/compile/compile_source_graph.py --module reports` executado para ressincronizar o piloto
- `python3 scripts/hb verify --task-type generate_code --module reports` em `PASS` para restaurar coerencia de sessao
- `python3 scripts/validate_contracts.py --profile ci` em `PASS`
- subset critica de regressao (`runtime_current_state`, `source_graph`, `context_budgets`, `session_state_phase3`, `architecture_drift`) em `PASS`

### B5-002 - Criar `staging_promotion` e `release_promotion`

Objetivo:

- formalizar o restante do lifecycle

Dependencias:

- B5-001

Arquivos a criar/editar:

- `.contract_driven/agent_prompts/staging_promotion.prompt.md`
- `.contract_driven/agent_prompts/release_promotion.prompt.md`
- `.contract_driven/TASK_CATALOG.yaml`
- `docs/_canon/CONTRACT_PIPELINE.md`

Teste a criar:

- `tests/pipeline_gates/test_runtime_promotions.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_runtime_promotions.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- `staging_validated` e `released` nao dependem mais de semantica dispersa

Rollback:

- remover workers e restaurar catalogo

Status atual validado no sistema:

- `.contract_driven/agent_prompts/staging_promotion.prompt.md` criado
- `.contract_driven/agent_prompts/release_promotion.prompt.md` criado
- `.contract_driven/TASK_CATALOG.yaml` atualizado com `staging_promotion` e `release_promotion` ativos
- `docs/_canon/CONTRACT_PIPELINE.md` atualizado para exigir promocao formal em `implemented -> staging_validated` e `staging_validated -> released`
- `docs/_canon/MODULE_REGISTRY.yaml` atualizado para declarar `staging_promotion` e `release_promotion` como caminhos formais
- `.contract_driven/CONTRACT_SYSTEM_RULES.md` atualizado com os novos `task_type`
- `scripts/hb` endurecido com `BLOCKED_STAGING_PROMOTION_INELIGIBLE` e `BLOCKED_RELEASE_PROMOTION_INELIGIBLE`
- `contracts/schemas/shared/session_start.schema.json` e `generated/contracts/schemas/shared/session_start.schema.json` atualizados com os novos `task_type`
- `tests/pipeline_gates/test_runtime_promotions.py` criado e verde
- `python3 scripts/repair_manifests.py` executado para sincronizar manifests de rastreabilidade
- `python3 scripts/generate/docs/gen_runtime_current_state.py --write` executado para ressincronizar derivado canônico
- `python3 scripts/compile/compile_source_graph.py --module reports` executado para ressincronizar o piloto
- `python3 scripts/hb verify --task-type generate_code --module reports` em `PASS` para restaurar coerencia de sessao
- `pytest tests/pipeline_gates/test_runtime_promotions.py -q` em `PASS`
- `pytest tests/pipeline_gates -q` em `PASS`
- `python3 scripts/validate_contracts.py --profile ci` em `PASS`

## B6. Sincronismo automatico

### B6-001 - Criar `SYNC_MANIFEST.yaml`

Objetivo:

- declarar propagacao obrigatoria por tipo de mudanca

Dependencias:

- B2-003

Arquivos a criar:

- `docs/_canon/SYNC_MANIFEST.yaml`

Teste a criar:

- `tests/pipeline_gates/test_sync_manifest_integrity.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_sync_manifest_integrity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- cada source master possui lista explicita de consumers obrigatorios

Rollback:

- remover manifest e teste

### B6-002 - Implementar `IMPACT_ANALYSIS_GATE` e `PARTIAL_UPDATE_GATE`

Objetivo:

- bloquear mudanca parcial e exigir propagacao completa

Dependencias:

- B6-001

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Testes a criar:

- `tests/pipeline_gates/test_impact_analysis_gate.py`
- `tests/pipeline_gates/test_partial_update_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_impact_analysis_gate.py -q
pytest tests/pipeline_gates/test_partial_update_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- alteracao normativa sem consumidores atualizados falha no pipeline

Rollback:

- remover gates do executor e do registry

## B-OPS. Contratos operacionais deterministicos

### B-OPS-001 - Definir SSOT estruturado para ambiente, secrets e deploy

Objetivo:

- tirar configuracao operacional critica de markdown livre e de shell inline

Dependencias:

- B0-001
- B0-004

Arquivos a criar:

- `docs/_canon/graph/ops/environment_catalog.yaml`
- `docs/_canon/graph/ops/secrets_catalog.yaml`
- `docs/_canon/graph/ops/service_topology.yaml`
- `docs/_canon/graph/ops/deploy_contract.yaml`
- `docs/_canon/graph/ops/runtime_endpoints.yaml`
- `docs/_canon/graph/ops/github_actions_catalog.yaml`

Arquivos a editar:

- `docs/_canon/DEPLOY_PIPELINE.md`
- `docs/_canon/VPS_SETUP.md`
- `docs/_canon/OPERATIONS.md`
- `docs/_canon/decisions/ADR-012-secrets-policy.md`

Cobertura minima obrigatoria:

- ambientes `development`, `staging`, `production`
- catalogo canonico de variaveis de ambiente
- catalogo canonico de secrets GitHub
- topologia de servicos: api, postgres, redis, worker, beat, nginx, pact broker
- contrato de deploy: pre-checks, health, rollback, promotion, evidencias
- endpoints canonicos de runtime: `/health`, OpenAPI, Pact Broker, hostnames por ambiente

Teste a criar:

- `tests/pipeline_gates/test_ops_source_graph_integrity.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_ops_source_graph_integrity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- nenhum conceito operacional critico fica apenas em markdown livre ou em YAML de workflow

Rollback:

- remover `docs/_canon/graph/ops/` e restaurar docs ao estado anterior

### B-OPS-002 - Implementar compiler dos contratos operacionais

Objetivo:

- gerar artefatos operacionais a partir do source unico de ops

Dependencias:

- B-OPS-001
- B2-003

Arquivos a criar:

- `scripts/compile/compile_ops_contracts.py`
- `scripts/compile/ops/__init__.py`
- `compiled_ops/.gitkeep`

Artefatos gerados obrigatorios:

- `infra/env/.env.staging.template`
- `infra/env/.env.production.template`
- `compiled_ops/deploy/staging.env.fragment`
- `compiled_ops/deploy/production.env.fragment`
- `compiled_ops/deploy/secrets_catalog.json`
- `compiled_ops/deploy/runtime_topology.json`
- `compiled_ops/deploy/impact_report.json`

Arquivos a editar:

- `scripts/hb`
- `.github/workflows/contract-gates.yml`

Teste a criar:

- `tests/pipeline_gates/test_ops_contract_compiler.py`

Validacao:

```bash
python3 scripts/compile/compile_ops_contracts.py --check
pytest tests/pipeline_gates/test_ops_contract_compiler.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- templates de ambiente e fragments de deploy passam a nascer do compiler

Rollback:

- remover compiler e artefatos gerados de `compiled_ops/`

Evidencia implementada e validada no sistema atual:

- `scripts/compile/compile_ops_contracts.py` criado e integrado ao `hb` e ao workflow `contract-gates`
- `infra/env/.env.staging.template` e `infra/env/.env.production.template` agora sao derivados do SSOT `docs/_canon/graph/ops/environment_catalog.yaml`
- `compiled_ops/deploy/{staging.env.fragment,production.env.fragment,secrets_catalog.json,runtime_topology.json,impact_report.json}` gerados e versionados
- `SOURCE_AUTHORITY_GRAPH.yaml` e `SYNC_MANIFEST.yaml` atualizados para tratar os artefatos gerados como consumidores bloqueantes do source master operacional
- `./.venv-contract/bin/python scripts/compile/compile_ops_contracts.py --check` em `PASS`
- `./.venv-contract/bin/python scripts/hb compile-ops-contracts --check` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_contract_compiler.py -q` em `PASS`
- `./.venv-contract/bin/python scripts/validate_contracts.py --profile ci` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates -q` em `PASS` com `472 passed`

### B-OPS-003 - Implementar gates de paridade operacional

Objetivo:

- bloquear drift entre canon operacional, templates, workflow e runtime config

Dependencias:

- B-OPS-002
- B6-002

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Gates minimos obrigatorios:

- `OPS_CANON_PARITY_GATE`
- `ENV_TEMPLATE_EQUIVALENCE_GATE`
- `DEPLOY_WORKFLOW_ENV_PARITY_GATE`
- `SECRETS_CATALOG_GATE`
- `SERVICE_TOPOLOGY_PARITY_GATE`

Testes a criar:

- `tests/pipeline_gates/test_ops_canon_parity_gate.py`
- `tests/pipeline_gates/test_env_template_equivalence_gate.py`
- `tests/pipeline_gates/test_deploy_workflow_env_parity_gate.py`
- `tests/pipeline_gates/test_secrets_catalog_gate.py`
- `tests/pipeline_gates/test_service_topology_parity_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_ops_canon_parity_gate.py -q
pytest tests/pipeline_gates/test_env_template_equivalence_gate.py -q
pytest tests/pipeline_gates/test_deploy_workflow_env_parity_gate.py -q
pytest tests/pipeline_gates/test_secrets_catalog_gate.py -q
pytest tests/pipeline_gates/test_service_topology_parity_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- alteracao em contrato operacional sem propagacao completa falha no pipeline

Rollback:

- remover gates novos do executor e do registry

Evidencia implementada e validada no sistema atual:

- `OPS_CANON_PARITY_GATE`, `ENV_TEMPLATE_EQUIVALENCE_GATE`, `DEPLOY_WORKFLOW_ENV_PARITY_GATE`, `SECRETS_CATALOG_GATE` e `SERVICE_TOPOLOGY_PARITY_GATE` ativados em `scripts/contracts/validate/validate_contracts.py`
- os cinco gates registrados como `active` em `docs/_canon/gates/GATES_REGISTRY.yaml`
- `tests/pipeline_gates/test_ops_canon_parity_gate.py` em `PASS`
- `tests/pipeline_gates/test_env_template_equivalence_gate.py` em `PASS`
- `tests/pipeline_gates/test_deploy_workflow_env_parity_gate.py` em `PASS`
- `tests/pipeline_gates/test_secrets_catalog_gate.py` em `PASS`
- `tests/pipeline_gates/test_service_topology_parity_gate.py` em `PASS`
- `tests/pipeline_gates/test_gate_registry_parity.py` em `PASS`
- `tests/pipeline_gates/test_ops_contract_compiler.py` revalidado em `PASS`
- `tests/pipeline_gates/test_ops_source_graph_integrity.py` revalidado em `PASS`
- `tests/pipeline_gates/test_runtime_current_state_generator.py` revalidado em `PASS`
- `tests/pipeline_gates/test_architecture_drift.py::TestFullPassOnValidState::test_all_checks_pass_on_real_repo` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates -q` em `PASS` com `482 passed`
- `./.venv-contract/bin/python scripts/validate_contracts.py --profile ci` em `PASS` com os cinco gates operacionais ativos
- `./.venv-contract/bin/python scripts/compile/compile_ops_contracts.py` executado para ressincronizar `compiled_ops/deploy/runtime_topology.json` e `compiled_ops/deploy/impact_report.json`
- `./.venv-contract/bin/python scripts/generate/docs/gen_runtime_current_state.py --write` executado para manter `docs/_canon/RUNTIME_CURRENT_STATE.md` em paridade com o gerador
- baseline operacional restaurado com `./.venv-contract/bin/python scripts/hb verify --task-type generate_code --module reports`, deixando `_reports/session_start.json` e `SESSION_HANDOFF.md` coerentes em `CDD/reports`

### B-OPS-004 - Eliminar geracao inline de `.env` no workflow de deploy

Objetivo:

- impedir que `.github/workflows/deploy.yml` concorra com os templates e SSOTs de ops

Dependencias:

- B-OPS-003

Arquivos a criar:

- `scripts/deploy/inject_env.sh`
- `scripts/deploy/render_env_from_contract.py`

Arquivos a editar:

- `.github/workflows/deploy.yml`
- `docs/_canon/VPS_SETUP.md`
- `docs/_canon/decisions/ADR-012-secrets-policy.md`

Acoes:

- remover `echo VAR=...` inline do workflow
- passar a renderizar `.env` a partir do contract compiler + secrets reais do ambiente
- falhar se houver variavel exigida no catalogo sem valor disponivel no ambiente alvo

Teste a criar:

- `tests/pipeline_gates/test_deploy_env_rendering_flow.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_deploy_env_rendering_flow.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- workflow de deploy deixa de ser source manual de variaveis operacionais

Rollback:

- restaurar workflow anterior e remover os scripts de renderizacao

Evidencia implementada e validada no sistema atual:

- `scripts/deploy/render_env_from_contract.py` criado para renderizar `.env` a partir de `infra/env/.env.<env>.template` + `compiled_ops/deploy/<env>.env.fragment` + valores reais do ambiente
- `scripts/deploy/inject_env.sh` criado como wrapper deterministico de injecao para deploy
- `.github/workflows/deploy.yml` deixou de gerar/regenerar `.env` inline e passou a renderizar `staging` e `production` via `scripts/deploy/inject_env.sh`
- o workflow agora sincroniza `.deploy/staging.env` e `.deploy/production.env` para a VPS, em vez de usar `echo VAR=...` inline
- o output `needs.build.outputs.image_tag` passou a ser o short SHA canonico de deploy, evitando usar a lista de tags do `docker/metadata-action`
- `deploy-production` passou a sincronizar `infra/` e o `.env` renderizado antes do deploy, alinhando producao ao mesmo contrato operacional do staging
- `docs/_canon/graph/ops/deploy_contract.yaml` ganhou `env_rendering` e removeu o desvio conhecido de bootstrap inline
- `docs/_canon/graph/ops/github_actions_catalog.yaml` e `docs/_canon/graph/ops/secrets_catalog.yaml` foram atualizados para refletir os secrets reais usados no render deterministico
- `docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml` e `docs/_canon/SYNC_MANIFEST.yaml` agora tratam `.github/workflows/deploy.yml`, `scripts/deploy/*` e `tests/pipeline_gates/test_deploy_env_rendering_flow.py` como consumers bloqueantes do source master operacional
- `docs/_canon/DEPLOY_PIPELINE.md`, `docs/_canon/VPS_SETUP.md` e `docs/_canon/decisions/ADR-012-secrets-policy.md` foram atualizados para refletir o estado atual sem bootstrap inline
- `scripts/contracts/validate/validate_contracts.py` foi endurecido para bloquear workflow sem `inject_env.sh`, sem os artefatos `.deploy/*.env` esperados ou com bootstrap inline legado
- `scripts/compile/compile_ops_contracts.py` foi atualizado para validar e propagar `env_rendering` no contrato operacional compilado
- `tests/pipeline_gates/test_deploy_env_rendering_flow.py` criado e em `PASS`
- `./.venv-contract/bin/python scripts/compile/compile_ops_contracts.py` executado com regeneracao de `compiled_ops/deploy/secrets_catalog.json`, `compiled_ops/deploy/runtime_topology.json` e `compiled_ops/deploy/impact_report.json`
- `./.venv-contract/bin/python scripts/compile/compile_source_graph.py --module reports` executado para ressincronizar `generated/source_graph/reports/*` apos as mudancas globais
- `./.venv-contract/bin/python scripts/generate/docs/gen_runtime_current_state.py --write` executado para manter `docs/_canon/RUNTIME_CURRENT_STATE.md` em paridade
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_deploy_env_rendering_flow.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_source_graph_integrity.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_contract_compiler.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_deploy_workflow_env_parity_gate.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_source_graph_compiler_reports.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_module_lifecycle_governance.py::test_deploy_pipeline_marks_automation_as_partial_until_assets_exist -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates -q` em `PASS` com `485 passed`
- `./.venv-contract/bin/python scripts/hb verify --task-type generate_code --module reports` executado ao final para restaurar o baseline `CDD/reports`
- `./.venv-contract/bin/python scripts/validate_contracts.py --profile ci` em `PASS` com o fluxo de renderizacao de `.env` ativo

### B-OPS-005 - Formalizar contratos de rotacao, presenca e uso de secrets

Objetivo:

- transformar secrets de ambiente em contrato operacional verificavel

Dependencias:

- B-OPS-003

Arquivos a criar:

- `scripts/ops/rotate_keys.sh`
- `tests/pipeline_gates/test_secret_rotation_contract.py`

Arquivos a editar:

- `docs/_canon/graph/ops/secrets_catalog.yaml`
- `docs/_canon/graph/ops/github_actions_catalog.yaml`
- `docs/_canon/graph/ops/environment_catalog.yaml`
- `docs/_canon/decisions/ADR-012-secrets-policy.md`
- `docs/_canon/SECURITY_RULES.md`
- `.github/workflows/deploy.yml`

Cobertura minima obrigatoria:

- presenca de todos os secrets catalogados para staging/producao
- proibicao de secret hardcoded em workflow
- politica de rotacao ligada ao catalogo
- validacao de que nenhum secret obrigatorio existe apenas em prose

Validacao:

```bash
pytest tests/pipeline_gates/test_secret_rotation_contract.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- secrets, rotacao e uso por ambiente passam a ser rastreaveis por contrato

Rollback:

- remover script e restaurar politica anterior

Evidencia de implementacao validada:

- `scripts/ops/rotate_keys.sh` criado como entrada deterministica de planejamento/verificacao de rotacao
- `docs/_canon/graph/ops/secrets_catalog.yaml` endurecido com metadata de rotacao apenas para secrets/credenciais ativos no sistema atual
- `docs/_canon/graph/ops/github_actions_catalog.yaml` alinhado ao consumo real de deploy (`JWT_*`, `POSTGRES_PASSWORD`, `CLOUDINARY_URL`)
- `docs/_canon/graph/ops/environment_catalog.yaml` alinhado ao runtime real (`JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`, `CLOUDINARY_URL`)
- `docs/_canon/SECURITY_RULES.md` e `docs/_canon/decisions/ADR-012-secrets-policy.md` passaram a apontar para catalogo estruturado e a distinguir segredos ativos vs. nao operacionalizados
- `.github/workflows/deploy.yml` endurecido sem hardcode operacional nos jobs de deploy, mantendo fixtures dummy apenas no job de testes
- `scripts/contracts/validate/validate_contracts.py` endurecido para:
  - bloquear metadata de rotacao incompleta
  - bloquear inventario ADR divergente do catalogo estruturado
  - bloquear bind hardcoded de `HB_ENV_*` nos steps de deploy
  - bloquear `runtime_secret_inputs` fora de `github_actions.secrets`
- `scripts/compile/compile_ops_contracts.py` endurecido para falhar sem metadata de rotacao nos segredos ativos
- `tests/pipeline_gates/test_secret_rotation_contract.py` criado e validado
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_secret_rotation_contract.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_secrets_catalog_gate.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_deploy_workflow_env_parity_gate.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_contract_compiler.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_source_graph_integrity.py -q` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_source_graph_compiler_reports.py -q` em `PASS`
- `./.venv-contract/bin/python scripts/compile/compile_ops_contracts.py` em `PASS`
- `./.venv-contract/bin/python scripts/compile/compile_source_graph.py --module reports` em `PASS`
- `./.venv-contract/bin/python scripts/hb verify --task-type generate_code --module reports` executado ao final para restaurar baseline `CDD/reports`
- `./.venv-contract/bin/python scripts/validate_contracts.py --profile ci` em `PASS` apos restaurar baseline e regenerar `RUNTIME_CURRENT_STATE.md`

### B-OPS-006 - Criar bundle operacional compilado para tasks de roadmap/deploy

Objetivo:

- impedir inferencia do agente em tarefas de VPS, deploy, CI/CD e ambiente

Dependencias:

- B-OPS-003
- B7-001

Arquivos a criar:

- `compiled_context/ops/deploy.json`
- `compiled_context/ops/runtime.json`

Arquivos a editar:

- `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md`
- `.github/skills/hb-roadmap-executor/SKILL.md`
- `CLAUDE.md`

Teste a criar:

- `tests/pipeline_gates/test_ops_bundle_required_for_roadmap.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_ops_bundle_required_for_roadmap.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- tasks de infra/deploy/CI-CD nao podem iniciar sem bundle operacional fresco

Rollback:

- restaurar leitura direta dos artefatos operacionais dispersos

Estado atual no sistema:

- implementado e validado em 2026-04-01

Evidencias validadas:

- `compiled_context/ops/deploy.json` criado com inputs de `docs/_canon/graph/ops/` (hashes validados)
- `compiled_context/ops/runtime.json` criado com inputs de topologia/endpoints (hashes validados)
- `execute_roadmap_phase.prompt.md` atualizado com pré-requisito P5 (bundle ops)
- `SKILL.md` do hb-roadmap-executor atualizado com checklist P5 e `BLOCKED_OPS_BUNDLE_STALE`
- `CLAUDE.md` atualizado com regra transversal de bundle ops
- `pytest tests/pipeline_gates/test_ops_bundle_required_for_roadmap.py -q` em `PASS` com `15 passed`
- `pytest tests/pipeline_gates/test_context_bundle_freshness_gate.py -q` em `PASS` com `10 passed` (sem regressão)

## B7. Bundle compilado para o agente

### B7-001 - Criar compiler de bundle por modulo/feature

Objetivo:

- fazer o agente consumir bundle fechado e rastreavel

Dependencias:

- B6-002

Arquivos a criar:

- `scripts/compile/compile_context_bundle.py`
- `compiled_context/.gitkeep`

Arquivos a editar:

- `scripts/hb`
- `.github/workflows/contract-gates.yml`
- `docs/_canon/SYNC_MANIFEST.yaml`

Saidas obrigatorias:

- `compiled_context/reports/<feature>.json` para o piloto

Teste a criar:

- `tests/pipeline_gates/test_context_bundle_reports.py`

Validacao:

```bash
python3 scripts/compile/compile_context_bundle.py --module reports
pytest tests/pipeline_gates/test_context_bundle_reports.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- existe bundle deterministico suficiente para dirigir implementacao de `reports`

Rollback:

- remover bundles e compiler

Estado atual no sistema:

- implementado e validado no piloto `reports`

Evidencias validadas:

- `./.venv-contract/bin/python scripts/compile/compile_context_bundle.py --module reports` em `PASS`
- `./.venv-contract/bin/python scripts/compile/compile_context_bundle.py --module reports --check --format json` em `PASS`
- `./.venv-contract/bin/python scripts/hb compile-context-bundle --module reports --check` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_context_bundle_reports.py -q` em `PASS` com `8 passed`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_sync_manifest_integrity.py -q` em `PASS`
- `./.venv-contract/bin/python scripts/validate_contracts.py --profile ci` em `PASS`

### B7-002 - Criar `CONTEXT_BUNDLE_FRESHNESS_GATE`

Objetivo:

- impedir uso de bundle stale

Dependencias:

- B7-001

Arquivos a editar:

- `docs/_canon/gates/GATES_REGISTRY.yaml`
- `scripts/contracts/validate/validate_contracts.py`

Teste a criar:

- `tests/pipeline_gates/test_context_bundle_freshness_gate.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_context_bundle_freshness_gate.py -q
pytest tests/pipeline_gates/test_gate_registry_parity.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- bundle defasado bloqueia tasks de implementacao

Rollback:

- remover gate e restaurar bundle flow anterior

Estado atual no sistema:

- implementado e validado em 2026-04-01

Evidencias validadas:

- `BLOCKED_CONTEXT_BUNDLE_STALE` adicionado em `validate_contracts.py`
- `_g_context_bundle_freshness()` implementado e adicionado ao `gate_plan`, `_precommit_ids` e `_local_ids`
- Gate registrado em `GATES_REGISTRY.yaml` (ordem `20J`, `blocking: true`, `status: active`)
- `pytest tests/pipeline_gates/test_context_bundle_freshness_gate.py -q` em `PASS` com `10 passed`
- `pytest tests/pipeline_gates/test_gate_registry_parity.py -q` em `PASS` com `8 passed`
- `python3 scripts/validate_contracts.py --profile ci` — `CONTEXT_BUNDLE_FRESHNESS_GATE` → `PASS`
- commit `dbfa8e3` em `main`

## B8. Runtime real e merge hardening

### B8-001 - Endurecer ruleset do GitHub

Objetivo:

- mover governanca real para merge-blocking

Dependencias:

- B1-004
- B6-002
- B-OPS-003

Fora do repositorio:

- atualizar ruleset `contract-gates` via GitHub API ou interface

Checks obrigatorios a exigir:

- `Validate Contract Gates`
- `Governance Tests`
- `Architecture Drift Check`
- `CI / Validate Contracts`
- `CI / Tests`

Regras obrigatorias:

- `required_approving_review_count = 1`
- `required_review_thread_resolution = true`

Validacao:

```bash
gh api repos/hbtrack/official/rules/branches/main
```

Criterio de saida:

- merge em `main` sem esses checks deixa de ser possivel

Rollback:

- restaurar ruleset anterior

### B8-002 - Ativar Pact e validacao live obrigatoria

Objetivo:

- fechar validacao de mundo real

Dependencias:

- B8-001
- B-OPS-004

Arquivos a editar:

- `.github/workflows/deploy.yml`
- `docs/_canon/CONTRACT_PIPELINE.md`
- configuracao operacional do broker Pact

Acoes:

- configurar `PACT_BROKER_BASE_URL`
- tornar `HTTP_RUNTIME_CONTRACT_GATE` obrigatorio antes de promotion para `released`
- registrar evidencia de staging

Validacao:

```bash
python3 scripts/validate_contracts.py --profile ci
```

Evidencia externa obrigatoria:

- run de staging verde
- contract conformance verde
- Pact provider verde

Criterio de saida:

- os dois skips atuais de runtime deixam de ser skips operacionais

Rollback:

- reverter workflow e variaveis operacionais

## B9. Fechamento explicito dos criterios adversariais

### B9-001 - Implementar a bateria adversarial forte completa

Objetivo:

- transformar `CA` em evidência executável e bloqueante

Dependencias:

- B1-004
- B3-002
- B6-002
- B7-002
- B8-001

Suites obrigatorias a existir como testes e/ou gates:

- authority drift suite
- source graph ambiguity suite
- partial update suite
- prompt/schema parity suite
- doc/contract parity suite
- contract/code parity suite
- projection drift suite
- promotion coherence suite
- DSS traceability suite
- runtime conformance suite
- stale bundle suite
- merge-rules enforcement suite

Arquivos a criar/editar:

- `tests/adversarial/`
- `tests/pipeline_gates/` suites faltantes
- `docs/_canon/gates/GATES_REGISTRY.yaml` quando a suite virar gate
- `scripts/contracts/validate/validate_contracts.py` quando a suite virar gate

Validacao:

```bash
pytest tests/adversarial -q
pytest tests/pipeline_gates -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- toda suite adversarial obrigatoria existe
- toda suite adversarial roda em CI
- nenhuma suite obrigatoria fica apenas como "plano"

Rollback:

- remover apenas suites novas que quebrarem falsamente o baseline

### B9-002 - Implementar politica `warnings = failure`

Objetivo:

- satisfazer a parte "sem warnings" do `CA`

Dependencias:

- B9-001

Arquivos a editar:

- `scripts/contracts/validate/validate_contracts.py`
- `.github/workflows/contract-gates.yml`
- `.github/workflows/ci.yml`

Acoes:

- converter warnings adversariais e de sincronismo em falha bloqueante
- explicitar quais categorias podem continuar `SKIP_NOT_APPLICABLE`
- proibir warning silencioso nas suites de aceite

Teste a criar:

- `tests/pipeline_gates/test_warning_free_acceptance.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_warning_free_acceptance.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- `CA` so passa quando a execucao estiver sem warnings relevantes

Rollback:

- restaurar politica de warning anterior

## B10. Rollout full-fleet para todo o sistema

### B10-001 - Migrar source graph para todos os modulos

Objetivo:

- satisfazer a parte "todo o sistema" do `CA2`

Dependencias:

- B2-003

Ordem obrigatoria de migracao de modulos:

1. `reports`
2. `analytics`
3. `exercises`
4. `notifications`
5. `wellness`
6. `medical`
7. `ai_ingestion`
8. `seasons`
9. `teams`
10. `competitions`
11. `users`
12. `matches`
13. `scout`
14. `video`
15. `audit`
16. `identity_access`
17. `training`

Regra:

- cada modulo so entra na fila seguinte apos `PASS` do modulo anterior no compiler, equivalence gate e bundle freshness

Artefatos obrigatorios por modulo:

- `docs/hbtrack/modulos/<module>/graph/*.yaml`
- bundle compilado por feature
- contrato compilado
- impact report do modulo

Validacao:

```bash
python3 scripts/compile/compile_source_graph.py --all
python3 scripts/compile/compile_context_bundle.py --all
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- todos os 17 modulos estao no source graph soberano

Rollback:

- reverter apenas o modulo mais recente da fila

### B10-002 - Migrar codegen e cutover para todos os modulos

Objetivo:

- satisfazer a parte "pronto para desenvolver todo o sistema" do `CA2`

Dependencias:

- B10-001
- B4-004

Regra:

- repetir por modulo a mesma sequencia usada no piloto:
  - gerar
  - parity
  - staging
  - cutover
  - remocao do legado manual daquele modulo

Validacao:

```bash
pytest tests/parity -q
pytest -q -m "not slow" --tb=short
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- todos os modulos possuem camada `generated/` validada e adaptador canonico apontando para ela

Rollback:

- rollback por modulo, nunca rollback full-fleet

### B10-003 - Fechar validacao de mundo real para todos os ciclos de negocio

Objetivo:

- satisfazer a parte "validado para o mundo real" do `CA2`

Dependencias:

- B8-002
- B10-002

Acoes:

- criar dataset seeded de staging para cada modulo
- criar replay pack por ciclo de negocio:
  - identidade e acesso
  - operacao de equipe e temporada
  - partida e competicao
  - scout e video
  - treino e wellness
  - notificacao, analytics e relatorios
- tornar replay de staging obrigatorio antes de release

Artefatos a criar:

- `tests/replay/staging/`
- `scripts/replay/`

Validacao:

```bash
pytest tests/replay/staging -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- todo ciclo principal de negocio roda em staging com evidência persistida

Rollback:

- desabilitar apenas replay suites instaveis e restaurar staging gate anterior

## B11. Operabilidade total do agente

### B11-001 - Tornar bundle compilado a unica entrada operacional permitida para implementacao

Objetivo:

- satisfazer a parte central do `CA3`

Dependencias:

- B7-002
- B10-001

Arquivos a editar:

- `.contract_driven/TASK_CATALOG.yaml`
- `.contract_driven/agent_prompts/*.prompt.md` aplicaveis
- `.github/agents/hb-contract.agent.md`
- `.github/skills/hb-pipeline-orchestrator/SKILL.md`
- `CLAUDE.md`

Regra:

- tasks de implementacao, evolucao e novo modulo so podem iniciar com bundle compilado fresco

Teste a criar:

- `tests/pipeline_gates/test_bundle_required_for_implementation.py`

Validacao:

```bash
pytest tests/pipeline_gates/test_bundle_required_for_implementation.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- agente nao consegue iniciar implementacao sem bundle fresco

Rollback:

- restaurar leitura direta dos artefatos antigos

### B11-002 - Cobrir explicitamente `feature update`, `new module` e `contract revision`

Objetivo:

- garantir que o agente saiba desenvolver features, atualizacoes e novos modulos sem inferencia

Dependencias:

- B11-001

Arquivos a criar/editar:

- templates de bundle para:
  - `new_module`
  - `feature_update`
  - `contract_revision`
- prompts correspondentes em `.contract_driven/agent_prompts/`
- testes de roteamento e operabilidade

Teste a criar:

- `tests/pipeline_gates/test_agent_operability_matrix.py`

Matriz minima obrigatoria:

- novo modulo
- nova feature em modulo existente
- alteracao de regra global
- revisao de contrato sem mudanca de codigo
- mudanca de codigo derivada de contrato

Validacao:

```bash
pytest tests/pipeline_gates/test_agent_operability_matrix.py -q
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- o agente recebe trilha fechada para cada tipo de trabalho relevante

Rollback:

- desabilitar tipos novos e restaurar operacao antiga

### B11-003 - Criar certificacao final de compliance do agente

Objetivo:

- dar fechamento formal ao `CA3`

Dependencias:

- B9-002
- B10-003
- B11-002

Arquivos a criar:

- `scripts/certify/certify_agent_operability.py`
- `_reports/compliance/agent_operability_latest.json`

Conteudo obrigatorio da certificacao:

- suites adversariais
- gates de sincronismo
- bundle freshness
- DSS traceability
- runtime replay
- merge-rules enforcement
- operability matrix verde

Validacao:

```bash
python3 scripts/certify/certify_agent_operability.py
python3 scripts/validate_contracts.py --profile ci
```

Criterio de saida:

- so ha certificacao `PASS` quando `CA`, `CA2` e `CA3` estiverem demonstrados por evidência executável

Rollback:

- remover certificacao e restaurar status anterior

## 5. Ordem real de implementacao validada no sistema atual

Esta secao reflete a ordem real ja executada e validada no repositório em `2026-03-31`.

Itens ja implementados e validados:

1. B-ENV-001
2. B-ENV-002
3. B-ENV-003
4. B0-004
5. B1-005
6. B0-001
7. B0-002
8. B0-003
9. B1-001
10. B1-002
11. B1-003
12. B1-004
13. B1-006
14. B1-007
15. B1-008
16. B2-001
17. B2-002
18. B2-003
19. B3-001
20. B3-002
21. B4-001
22. B4-002
23. B4-003
24. B4-004
25. B5-001
26. B5-002
27. B6-001
28. B6-002

Evidencia minima ja confirmada para os itens acima:

- `python3 scripts/validate_contracts.py --profile ci` em `PASS`
- `.venv-contract/bin/python -m pytest tests/pipeline_gates -q` em `PASS`
- `DOC_USAGE_GATE` ativo no executor e no registry
- `tests/pipeline_gates/test_docs_guias_non_sovereign.py` em `PASS`
- `tests/pipeline_gates/test_hook_governance_enforcement_phase5.py` em `PASS`
- `tests/pipeline_gates/test_agent_compliance_phase0.py` em `PASS`
- `tests/pipeline_gates/test_stage_allowed_enforcement.py` em `PASS`
- `tests/pipeline_gates/test_generate_code_requires_implementation_ready.py` em `PASS`
- `tests/pipeline_gates/test_backend_hook_fail_closed.py` em `PASS`
- `tests/pipeline_gates/test_arch_decision_presence_gate.py` em `PASS`
- `tests/pipeline_gates/test_canon_contract_driven_parity_gate.py` em `PASS`
- `tests/pipeline_gates/test_hbtrack_canon_parity_gate.py` em `PASS`
- `tests/pipeline_gates/test_runtime_current_state_generator.py` em `PASS`
- `tests/contracts/test_module_doc_governance.py` em `PASS`
- `HBTRACK_CANON_PARITY_GATE` ativo no executor e no registry
- `python3 scripts/generate/docs/gen_runtime_current_state.py --check` em `PASS`
- `python3 scripts/audit/check_architecture_docs.py --json` em `PASS`
- `RUNTIME_CURRENT_STATE.md` gerado automaticamente e sincronizado com o gerador canônico
- `tests/pipeline_gates/test_source_graph_global_integrity.py` em `PASS`
- `tests/pipeline_gates/test_reports_source_graph_integrity.py` em `PASS`
- `tests/pipeline_gates/test_source_graph_compiler_reports.py` em `PASS`
- `docs/_canon/graph/*.yaml` criados, validados e cobertos por manifesto
- `docs/hbtrack/modulos/reports/graph/*.yaml` criados, validados e cobertos por manifesto
- `python3 scripts/compile/compile_source_graph.py --module reports` em `PASS`
- `python3 scripts/compile/compile_source_graph.py --module reports --check --format json` em `PASS`
- `python3 scripts/hb compile-source-graph --module reports --check` em `PASS`
- `generated/source_graph/reports/impact_report.json` gerado e validado
- `generated/source_graph/reports/*.yaml` gerados e validados
- `tests/pipeline_gates/test_reports_openapi_schema_equivalence.py` em `PASS`
- `tests/pipeline_gates/test_openapi_schema_equivalence_gate.py` em `PASS`
- `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json` em `PASS`
- `python3 scripts/validate_contracts.py --profile ci` com `OPENAPI_SCHEMA_EQUIVALENCE_GATE` em `PASS`
- `tests/pipeline_gates/test_gate_registry_parity.py` em `PASS`
- `contracts/openapi/components/schemas/reports/report_job.yaml` promovido para ref direto ao schema soberano
- `contracts/openapi/paths/reports.yaml` ajustado para overlay runtime sem projection drift de `jobId/status/createdAt`
- `OPENAPI_SCHEMA_EQUIVALENCE_GATE` ativo no executor e no registry
- `tests/pipeline_gates/test_generated_layout_reports.py` em `PASS`
- `src/reports/generated/` criado como layout oficial do piloto `reports`
- `docs/_canon/CODE_ARCHITECTURE.md` atualizado para tratar `generated/` como zona derivada, nao soberana
- `python3 scripts/generate/backend_codegen.py --module reports --format json` em `PASS`
- `python3 scripts/generate/backend_codegen.py --module reports --check --format json` em `PASS`
- `tests/pipeline_gates/test_backend_codegen_reports.py` em `PASS`
- `pytest src/reports/generated/tests/test_codegen_contract.py -q` em `PASS`
- `src/reports/generated/schemas.py` gerado deterministicamente
- `src/reports/generated/api.py` gerado deterministicamente
- `src/reports/generated/domain/entities.py` gerado deterministicamente
- `src/reports/generated/application/use_cases.py` gerado deterministicamente
- `src/reports/generated/infrastructure/repository.py` gerado deterministicamente
- `src/reports/generated/tests/test_codegen_contract.py` gerado deterministicamente
- duas execucoes seguidas do backend codegen produziram `combined_sha256` identico para `reports`
- `tests/parity/test_reports_codegen_parity.py` em `PASS`
- `pytest -q -m "not slow" --tb=short -W error` em `PASS`
- superficie HTTP de `src/reports/api.py` e `src/reports/generated/api.py` comprovada em paridade por AST
- serializacao `ReportJobOut.from_domain(...)` manual x gerada comprovada em paridade
- casos positivos e negativos de `GetReportJob`, `ListReportJobs`, `CreateReportJob`, `UpdateReportJob` e `DownloadReportArtifact` comprovados em paridade
- warnings estruturais eliminados em `src/wellness/domain/entities.py`, `src/competitions/domain/entities.py` e `src/seasons/schemas.py`
- `src/reports/api.py` promovido para compor `generated.application/use_cases` e `generated.infrastructure.repository`
- `src/reports/schemas.py` promovido para adapter canônico da camada gerada
- `SESSION_HANDOFF.md` atualizado com evidências do piloto `reports`
- `python3 scripts/hb verify --task-type generate_code --module reports` em `PASS`
- `pytest -q -m "not slow" --tb=short -W error` em `PASS` após o cutover
- `python3 scripts/validate_contracts.py --profile ci` em `PASS` após o cutover
- `tests/pipeline_gates/test_implementation_promotion.py` em `PASS`
- `implementation_promotion` registrado como worker formal ativo em `TASK_CATALOG.yaml`
- `tests/pipeline_gates/test_runtime_promotions.py` em `PASS`
- `staging_promotion` e `release_promotion` registrados como workers formais ativos em `TASK_CATALOG.yaml`
- `tests/pipeline_gates/test_sync_manifest_integrity.py` em `PASS`
- `docs/_canon/SYNC_MANIFEST.yaml` criado, ativo e coberto por `DOC_USAGE_MANIFEST.yaml`
- `tests/pipeline_gates/test_impact_analysis_gate.py` em `PASS`
- `tests/pipeline_gates/test_partial_update_gate.py` em `PASS`
- `IMPACT_ANALYSIS_GATE` ativo no executor e no registry
- `PARTIAL_UPDATE_GATE` ativo no executor e no registry
- `python3 scripts/validate_contracts.py --profile ci` em `PASS` com os gates de sincronismo ativos
- `tests/pipeline_gates/test_ops_source_graph_integrity.py` em `PASS`
- `docs/_canon/graph/ops/*.yaml` criados, ativos e cobertos por manifesto
- `docs/_canon/DEPLOY_PIPELINE.md`, `docs/_canon/VPS_SETUP.md`, `docs/_canon/OPERATIONS.md` e `ADR-012` alinhados ao source graph operacional
- `python3 scripts/generate/docs/gen_runtime_current_state.py --check` em `PASS` apos o endurecimento operacional
- `python3 scripts/validate_contracts.py --profile ci` em `PASS` com `B-OPS-001` ativo
- `scripts/compile/compile_ops_contracts.py` ativo, integrado ao `hb` e ao workflow `contract-gates`
- `infra/env/.env.staging.template` e `infra/env/.env.production.template` gerados a partir do source graph operacional
- `compiled_ops/deploy/{staging.env.fragment,production.env.fragment,secrets_catalog.json,runtime_topology.json,impact_report.json}` gerados e cobertos por teste dedicado
- `SOURCE_AUTHORITY_GRAPH.yaml` e `SYNC_MANIFEST.yaml` atualizados para tratar derivados operacionais como consumidores bloqueantes
- `./.venv-contract/bin/python scripts/compile/compile_ops_contracts.py --check` em `PASS`
- `./.venv-contract/bin/python scripts/hb compile-ops-contracts --check` em `PASS`
- `./.venv-contract/bin/python -m pytest tests/pipeline_gates/test_ops_contract_compiler.py -q` em `PASS`
- `.venv-contract/bin/python -m pytest tests/pipeline_gates -q` em `PASS` com 472 testes verdes

Ordem remanescente obrigatoria a partir do estado atual:

29. ~~B7-002~~ — DONE (2026-04-01, commit dbfa8e3)
30. ~~B-OPS-006~~ — DONE (2026-04-01)
31. B8-001
32. B8-002
33. B9-001
34. B9-002
35. B10-001
36. B10-002
37. B10-003
38. B11-001
39. B11-002
40. B11-003

Regras de interpretacao desta ordem:

- `B0-004` e `B1-005` nao devem ser repetidos; devem apenas ser mantidos e revalidados quando novos gates de paridade entrarem
- `B0-002` e `B0-003` entram como baseline permanente de documentação não soberana e cobertura real de superfícies de agente
- `B1-001` entra como baseline permanente de roteamento hard por stage
- `B1-002` entra como baseline permanente: `generate_code` só existe em `implementation_ready+`
- `B1-003` entra como baseline permanente: backend hook fail-closed em parse/erro interno
- `B1-004` entra como baseline permanente: decisões arquiteturais obrigatórias pendentes bloqueiam contrato/readiness/generate_code
- `B1-006` entra como baseline permanente: deriva canon↔.contract_driven vira falha técnica
- `B1-007` entra como baseline permanente: docs de módulo não podem divergir do canon global em autoridade de auth/authz e âncoras de state model
- `B1-008` entra como baseline permanente: `RUNTIME_CURRENT_STATE.md` deixa de ser manual e passa a ser verificado contra gerador canônico
- `B5-001` entra como baseline permanente: promoção `implementation_ready -> implemented` só ocorre via `implementation_promotion`
- `B5-002` entra como baseline permanente: promoções `implemented -> staging_validated -> released` só ocorrem via `staging_promotion` e `release_promotion`
- `B6-001` entra como baseline permanente: source masters soberanos e source graphs ativos possuem manifesto determinístico de propagação obrigatória
- `B6-002` entra como baseline permanente: changeset em `source_master` soberano deve passar por `IMPACT_ANALYSIS_GATE` e `PARTIAL_UPDATE_GATE`
- `B-OPS-001` entra como baseline permanente: ambiente, secrets, topologia, deploy e endpoints de runtime passam a ter SSOT estruturado em `docs/_canon/graph/ops/`
- `B-OPS-002` entra como baseline permanente: templates de ambiente e artefatos compilados de deploy passam a nascer exclusivamente do compiler operacional
- `B-OPS-003` entra como baseline permanente: drift entre source graph operacional, workflow de deploy, catálogo de secrets, templates de ambiente e topologia runtime passa a falhar tecnicamente no validator
- `B-OPS-004` entra como baseline permanente: `.env` de staging/producao deixa de ser bootstrapado inline e passa a ser renderizado deterministicamente do contrato operacional, com falha fechada se faltar valor obrigatorio
- `B-OPS-005` entra como baseline permanente: segredos operacionais ativos passam a exigir metadata estruturada de rotacao/presenca/uso e ADR nao pode carregar secret obrigatorio apenas em prose
- `B7-001` entra como baseline permanente: implementacao do agente em modulo/feature passa a ter bundle compilado e rastreavel em `compiled_context/<module>/<feature>.json`
- `B7-002` entra como baseline permanente: bundle stale bloqueia tasks de implementacao via `CONTEXT_BUNDLE_FRESHNESS_GATE` (DONE 2026-04-01)
- `B-OPS-006` entra como baseline permanente: tasks de infra/deploy/CI-CD/VPS devem consumir `compiled_context/ops/deploy.json` e `compiled_context/ops/runtime.json` sem inferência — `BLOCKED_OPS_BUNDLE_STALE` se stale (DONE 2026-04-01)
- a proxima acao correta no sistema atual passa a ser `B8-001`
- qualquer mudanca na ordem acima exige nova validacao completa do pipeline e atualizacao desta secao

## 6. Definition of Done do backlog

Este backlog so pode ser declarado concluido quando:

- existe source master unico por conceito
- `contracts/**` nasce do compiler
- `reports` roda via codigo gerado com parity PASS
- `generate_code` exige `implementation_ready+`
- `implementation_promotion` existe e esta ativo
- `IMPACT_ANALYSIS_GATE` e `PARTIAL_UPDATE_GATE` estao ativos
- `DOC_USAGE_GATE`, `CANON_CONTRACT_DRIVEN_PARITY_GATE` e `HBTRACK_CANON_PARITY_GATE` estao ativos
- `RUNTIME_CURRENT_STATE.md` e gerado e checado automaticamente
- contratos operacionais de ambiente, secrets, deploy e topologia possuem SSOT estruturado
- templates `.env`, fragments de deploy e inventario de secrets nascem do compiler operacional
- workflow de deploy nao gera `.env` inline fora do source graph de ops
- gates operacionais de paridade e freshness estao ativos
- bundles compilados existem e sao obrigatorios
- ruleset do GitHub exige governanca e CI reais
- Pact e runtime live validation deixaram de ser skip estrutural
- todas as suites adversariais obrigatorias existem e estao verdes sem warnings
- os 17 modulos foram migrados para source graph e trilha de codegen/cutover
- a certificacao final de operabilidade do agente esta `PASS`

## 7. Resultado esperado

Quando este backlog estiver concluido:

- o HB Track deixa de depender de leitura dispersa e inferencia estrutural para evoluir
- o agente recebe contexto compilado e verificavel
- contratos deixam de ser parcialmente manuais
- configuracao operacional deixa de depender de workflow inline, prose solta e inferencia do agente
- o backend comeca a migrar de implementacao manual para implementacao gerada e validada
- o sistema fica preparado para substituir o legado manual modulo a modulo, sem quebrar o runtime
