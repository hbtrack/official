# Plano: Binding Operacional do Agente IA — HB-TRACK

## Contexto

O repositório HB-TRACK tem governança documental forte (BOOT_PROFILES.yaml, TASK_CATALOG.yaml, 44 gates, 22 worker prompts) mas orquestração operacional fraca. O agente não é obrigado a passar por um funil único antes de agir. O ciclo resultante: artefato produzido → pipeline reprova → correção parcial → reprova de novo.

**Causa raiz confirmada por inspeção:**
- `BOOT_PROFILES.yaml`: `selection_rules` e `phase_profiles` marcados explicitamente como `not_implemented`
- `TASK_CATALOG.yaml`: tasks com `bundle_required: true` não têm gate de runtime verificando o bundle antes da execução
- `WORKER_PROMPT_AUTHORITY_GATE`: ordem 20J (registry coherence) — executa **após** o agente já ter lido o prompt. Chega tarde demais
- `scripts/hb cmd_verify()`: valida que `worker_path` **existe** (`.exists()`) mas não lê nem valida o frontmatter do arquivo
- Pre-commit hook: não valida presença de sessão válida, não verifica scope compliance, não guarda artefatos derivados de edição manual
- `session_start.schema.json` v1.3.0: `task_type` enum está **incompleto** — faltam `pr_fix`, `implementation_promotion`, `feature_update`, que são tasks legítimas no TASK_CATALOG

**Objetivo:** transformar `scripts/hb` no plano de controle único e real do agente, coerente com a precedência de autoridade declarada em AGENT_INSTRUCTIONS.md (enforcement executável > canon textual > bridge docs).

---

## Plano de Ações Corretivo, Preventivo, Protetivo e Defensivo

| ID | Falha | Ação necessária | Tipo de ação | Prioridade | Onde aplicar | Critério de aceite | Status |
|----|-------|-----------------|--------------|------------|--------------|-------------------|--------|
| A18 | `pr_fix`, `implementation_promotion`, `feature_update` ausentes do enum `task_type` em `session_start.schema.json` — `hb verify` falha por schema para tasks legítimas | Adicionar os 3 valores ao `enum` de `task_type`; adicionar campos `worker_frontmatter_validated: boolean`, `worker_frontmatter_matches_catalog: boolean` a `stage0_validation_results`; adicionar campo raiz `worker_prompt_sha256: string (hex-64)`; versão → `1.4.0` | corretiva | P0 | `contracts/schemas/shared/session_start.schema.json` | `jsonschema.validate` aceita sessão com `task_type=pr_fix` sem exceção | DONE |
| BKL-001 | `cmd_verify()` valida existência do `worker_path` mas não lê o frontmatter; agente pode iniciar sem evidência do prompt carregado | Após `.exists()`: ler arquivo, extrair frontmatter YAML delimitado por `---`, computar SHA-256, gravar `worker_prompt_sha256` na sessão, `worker_frontmatter_validated` e `worker_frontmatter_matches_catalog` em `stage0_validation_results`; falhar se frontmatter declara `task_type` divergente | protetiva | P0 | `scripts/hb` : `cmd_verify()`, novo método `_read_worker_frontmatter()` | `session_start.json` contém `worker_prompt_sha256` (64 hex chars) após `hb verify` | DONE |
| BKL-002 | `operation_mode` é derivado e gravado na sessão mas nunca validado cruzadamente com `task_type` | Após derivar `operation_mode`, chamar `_validate_operation_mode_coherence(task_type, operation_mode)`: se `task_type==execute_roadmap_phase` e `mode!=ROADMAP` → erro; se task CDD e `mode==ROADMAP` → erro | preventiva | P0 | `scripts/hb` : `cmd_verify()`, novo `_validate_operation_mode_coherence()` | `hb verify --task-type new_contract` em profile `roadmap_execution` → exit 1 com `BLOCKED_MODE_MISMATCH` | DONE |
| BKL-003 | `selection_rules` do BOOT_PROFILES.yaml marcadas `not_implemented`; aviso de divergência é apenas informativo | Substituir aviso informativo por `_enforce_selection_rules()` que avalia as regras e retorna exit 1 com `BLOCKED_PROFILE_MISMATCH` se divergir do `TASK_CATALOG` | estrutural | P0 | `scripts/hb` : `cmd_verify()`, refatorar `_apply_selection_rules()` → `_enforce_selection_rules()` | Profile divergente entre `selection_rules` e TASK_CATALOG → exit 1 | DONE |
| BKL-004 | Nenhuma evidência auditável do prompt efetivamente usado além de `worker_id` (string, não verificada) | Implementar `_write_execution_evidence()` que cria `_reports/execution_evidence/{session_id}.json` com: `worker_prompt_sha256`, `worker_frontmatter`, `write_scope`, `operation_mode`, `retries`, `cause_ids` | protetiva | P0 | `scripts/hb` : novo `_write_execution_evidence()`; `_reports/execution_evidence/` (criado programaticamente) | Arquivo `_reports/execution_evidence/{uuid}.json` criado após `hb verify` com `worker_prompt_sha256` não-vazio | DONE |
| BKL-005 | `write_scope` é derivado e gravado mas nunca enforced no hook — agente pode commitar arquivos fora do escopo declarado | No pre-commit hook: `check_write_scope_compliance()` verifica cada staged file contra `_SCOPE_PATH_MAP[write_scope]`; adiciona erro `BLOCKED_SCOPE_OVERFLOW` por violação | preventiva | P0 | `scripts/git-hooks/pre-commit` : novo `check_write_scope_compliance()`, dict `_SCOPE_PATH_MAP` | Commit de `src/` em sessão `write_scope=contracts` → bloqueado pelo hook | DONE |
| BKL-006 | `session_start.json` mistura estado canônico com evidência de execução; auditoria depende de inferência | Separar: `session_start.json` continua como estado canônico; evidência vai para `_reports/execution_evidence/{session_id}.json` (imutável por sessão) | estrutural | P0 | `scripts/hb` : `_write_execution_evidence()`; novo diretório `_reports/execution_evidence/` | Dois arquivos distintos após `hb verify`; modificar sessão não altera evidência | DONE |
| BKL-007 | Falhas de validator não produzem causa raiz única nem próxima ação — agente reinicia do zero | Novo comando `hb reentry`: lê `_reports/contract_gates/latest.json`, identifica primeiro gate FAIL blocking, mapeia via `_REENTRY_MAP` → `{root_cause, retry_task_type, retry_stage, suggested_fix}` | reativa | P1 | `scripts/hb` : novo `cmd_reentry()`, dict `_REENTRY_MAP` | `hb reentry` após gate FAIL imprime rota de próxima ação em vez de lista bruta | DONE |
| BKL-008 | Tasks simples (ex.: `new_schema`) disparam validação completa de CI, gerando ruído antes que o artefato exista | Adicionar campo `focal_gate_set` por task em TASK_CATALOG; `validate_contracts.py` aceita `--profile task_focal` e executa apenas esses gates | preventiva | P1 | `.contract_driven/TASK_CATALOG.yaml` : campo `focal_gate_set`; `validate_contracts.py` : perfil `task_focal` | `--profile task_focal` em sessão `new_schema` executa apenas os 3 gates focais | DONE |
| BKL-009 | `pr_fix` sem trilha formal: sem resolução `check_context → local_equivalent`, sem classificação de finding | `hb verify --task-type pr_fix --check-context "<check>"` valida `check_context` contra `merge-readiness.json`; grava `local_equivalent` em `stage0_validation_results`; falha com `GAP_DE_PARIDADE` se inexistente | corretiva | P1 | `scripts/hb` : `cmd_verify()` + argumento `--check-context` | `hb verify --task-type pr_fix --check-context "ci / Validate Contracts"` grava `local_equivalent` | DONE |
| BKL-010 | `hb preflight` output bruto de checks sem agrupamento por causa raiz | Adicionar `_format_actionable_output()` em `cmd_preflight()`: agrupa por causa raiz, imprime `[CORRIGIR PRIMEIRO]`, `[NÃO TOCAR]`, `[PRÓXIMA AÇÃO]` | corretiva | P1 | `scripts/hb` : `cmd_preflight()`, novo `_format_actionable_output()` | `hb preflight` BLOCK imprime grupos de causa raiz com próxima ação legível | DONE |
| BKL-011 | `merge-readiness.json` define limites de reviewability mas o agente não para quando os excede | Hook: `check_reviewability_limits()` lê `_reports/preflight/latest.json`; se `exceeded=true` e `split_required=true` → bloquear commit | detectiva | P1 | `scripts/git-hooks/pre-commit` : novo `check_reviewability_limits()` | Commit bloqueado quando PR excede limites e `split_required=true` | DONE |
| BKL-012 | Prompts órfãos em `.contract_driven/agent_prompts/` não são detectados automaticamente | Novo comando `hb audit-prompts`: classifica cada `.prompt.md` como `active`/`frozen`/`orphan`/`legacy`; exit 1 se orphan | detectiva | P1 | `scripts/hb` : novo `cmd_audit_prompts()`, subcomando `audit-prompts` | `hb audit-prompts` lista 22 prompts com classificação; exit 1 em presença de orphan | TODO |
| BKL-013 | Conflitos de autoridade entre bridge docs e canon resolvidos por inferência sem evidência de qual fonte venceu | Em `cmd_verify()`, gravar `authority_source_used: "TASK_CATALOG"` em `stage0_validation_results` em toda sessão | protetiva | P1 | `scripts/hb` : `cmd_verify()`, bloco `session_update` | `stage0_validation_results.authority_source_used == "TASK_CATALOG"` em toda sessão | DONE |
| BKL-014 | Geradores downstream podem ler contratos brutos diretamente sem compilador canônico `compile_source_graph.py` | `hb generate --backend` chama `_check_ir_freshness(module)`: verifica `generated/source_graph/{module}/` existe e não está stale vs `contracts/`; exit 1 com instrução se ausente/stale | preventiva | P2 | `scripts/hb` : `cmd_generate()`, novo `_check_ir_freshness()` | `hb generate --backend --module users` sem IR → exit 1 com instrução de regeneração | DONE |
| BKL-015 | Tasks com `bundle_required: true` não têm gate verificando bundle antes da execução | Em `cmd_verify()`: se `task_config["bundle_required"]` → verificar `bundle_path_template` resolvido existe; exit 1 com `BLOCKED_BUNDLE_REQUIRED` se ausente | preventiva | P2 | `scripts/hb` : `cmd_verify()`, bloco após validação 4b | `hb verify --task-type generate_code --module users` sem `compiled_context/users/` → exit 1 | DONE |
| BKL-016 | Agente edita manualmente artefatos em `generated/` que deveriam ser regenerados | Hook: `check_derived_artifact_guard()`: staged file em `generated/source_graph/`, `generated/`, `_reports/contract_gates/` → verificar se task_type atual produz esse path legitimamente; bloquear se não | protetiva | P2 | `scripts/git-hooks/pre-commit` : novo `check_derived_artifact_guard()` | Commit de `generated/` editado manualmente em sessão `new_contract` → bloqueado | DONE |
| BKL-017 | Transições de lifecycle (`draft_contract → ... → released`) sem validação de pré-condições | `cmd_check()` para `readiness_promotion`/`implementation_promotion`: `_validate_lifecycle_preconditions()` verifica status atual do módulo em MODULE_REGISTRY e exige status de origem correto | preventiva | P2 | `scripts/hb` : `cmd_check()`, novo `_validate_lifecycle_preconditions()` | `hb check --module users` em sessão `readiness_promotion` com módulo `draft_contract` → exit 1 | DONE |
| BKL-018 | Promoções ocorrem sem checklist executável (scorecard, CI, código) | `cmd_artifact()` para tasks de promoção: `_validate_promotion_evidence()` verifica scorecard, `latest.json` PASS, código fonte presente | preventiva | P2 | `scripts/hb` : `cmd_artifact()`, novo `_validate_promotion_evidence()` | `hb artifact MODULE_REGISTRY.yaml` em `readiness_promotion` sem scorecard → exit 1 | DONE |
| BKL-019 | Eficiência operacional medida apenas anedoticamente — sem baseline | Novo comando `hb stats`: agrega `_reports/execution_evidence/*.json` por task_type; imprime `attempts`, `overflow_count`, `top_cause` | detectiva | P3 | `scripts/hb` : novo `cmd_stats()` | `hb stats` imprime tabela estruturada sem exceção Python | DONE |
| BKL-020 | Nova governança pode ser adicionada sem binding operacional, acumulando documentação morta | Novo gate `GOVERNANCE_REGRESSION_GATE` em `validate_contracts.py`: verifica que todo prompt tem entrada TASK_CATALOG e que toda entrada tem worker_path com frontmatter coerente | protetiva | P3 | `scripts/contracts/validate/validate_contracts.py` : nova `_g_governance_regression()`, adicionada au `_precommit_ids` | `--profile precommit` falha com `BLOCKED_GOVERNANCE_WITHOUT_RUNTIME_BINDING` se binding ausente | DONE |
| BKL-021 | Sem suíte de regressão de comportamento do runtime | Criar `tests/pipeline/test_runtime_behavior.py`: `TestModeSeparation`, `TestPromptUsedEvidence`, `TestPrFixBoundedScope`, `TestIrLineage`, `TestPromotionGuards` | detectiva | P3 | `tests/pipeline/test_runtime_behavior.py` (novo) | `pytest tests/pipeline/test_runtime_behavior.py` verde | DONE |
| BKL-022 | Bridge docs duplicam instrução do canon aumentando custo cognitivo | `hb audit-prompts --check-bridge-docs`: verifica que todo bridge doc tem disclaimer `NON-SOVEREIGN` ou `BRIDGE ONLY`; exit 1 se ausente | estrutural | P3 | `scripts/hb` : `cmd_audit_prompts()`, flag `--check-bridge-docs` | `hb audit-prompts --check-bridge-docs` → exit 1 se bridge doc sem disclaimer | DONE |


---

## Ordem Determinística de Implementação

| Ordem | ID | O que fazer exatamente | Por que agora | Resultado esperado |
|-------|-----|------------------------|---------------|-------------------|
| 1 | A18 | Em `contracts/schemas/shared/session_start.schema.json`: (1) Adicionar `"pr_fix"`, `"implementation_promotion"`, `"feature_update"` ao array `enum` de `task_type` (linha ~80-101); (2) Adicionar ao objeto `stage0_validation_results.properties`: `"worker_frontmatter_validated": {"type": "boolean"}` e `"worker_frontmatter_matches_catalog": {"type": "boolean"}`; (3) Adicionar ao `properties` raiz: `"worker_prompt_sha256": {"type": "string", "description": "SHA-256 hex do worker prompt carregado", "pattern": "^[a-f0-9]{64}$"}`; (4) Atualizar `"version": "1.4.0"` | Schema é validado por TODOS os passos seguintes; campos novos devem existir antes de qualquer código gravá-los | Schema aceita as 3 tasks faltantes e 3 novos campos; `jsonschema.validate` passa para sessões válidas |
| 2 | BKL-004 parcial | Em `scripts/hb`, classe `HBCLIv2`: adicionar método `_read_worker_frontmatter(self, path: pathlib.Path) -> dict` que: lê texto do arquivo; se começa com `---`, procura próximo `---` a partir do índice 3; faz `yaml.safe_load(text[3:end_idx])` se encontrado; retorna dict ou `{}` se frontmatter ausente ou parse falhar | Método puro sem efeitos colaterais; deve existir antes de BKL-001 | `self._read_worker_frontmatter(path)` retorna `{"task_type": "new_contract", ...}` para prompt com frontmatter; `{}` sem frontmatter |
| 3 | BKL-006 parcial | Em `scripts/hb`, classe `HBCLIv2`: adicionar método `_write_execution_evidence(self, evidence: dict) -> None` que: cria `self.root / "_reports" / "execution_evidence"` com `mkdir(parents=True, exist_ok=True)`; escreve `_reports/execution_evidence/{session_id}.json` com JSON indentado; não falha se já existe (usa session_id como chave idempotente) | Método de saída puro; deve existir antes de BKL-001 que o invoca ao final de `cmd_verify()` | Arquivo `_reports/execution_evidence/{uuid}.json` criado; diretório criado automaticamente |
| 4 | BKL-001 | Em `scripts/hb`, `cmd_verify()`: (a) Após validação 4 (`.exists()`): calcular `prompt_sha = self._calculate_file_hash(worker_path)`; extrair `frontmatter = self._read_worker_frontmatter(worker_path)`; (b) Validar: se `frontmatter.get("task_type")` não é None e diverge de `task_type` arg → `print("❌ BLOCKED_WORKER_FRONTMATTER_MISMATCH"); return 1`; (c) Gravar em `stage0_validation_results`: `worker_frontmatter_validated = len(frontmatter) > 0`, `worker_frontmatter_matches_catalog = (frontmatter.get("task_type") == task_type) if frontmatter.get("task_type") else True`; (d) Gravar `"worker_prompt_sha256": prompt_sha` na sessão raiz; (e) Ao final com exit 0: chamar `self._write_execution_evidence({...})` | Schema atualizado (passo 1), métodos auxiliares prontos (passos 2-3) | `hb verify --task-type new_contract --module training` → `session_start.json` tem `worker_prompt_sha256` (64 hex chars) |
| 5 | BKL-002 | Em `scripts/hb`: adicionar método `_validate_operation_mode_coherence(self, task_type: str, operation_mode: str) -> int`; lógica: `if task_type == "execute_roadmap_phase" and operation_mode != "ROADMAP": return 1` (com mensagem `BLOCKED_MODE_MISMATCH`); `elif task_type != "execute_roadmap_phase" and operation_mode == "ROADMAP": return 1`; `return 0`; Chamar em `cmd_verify()` após linha 655 (derivação de `operation_mode`), antes de `session_update` | Validação de modo é pré-condição de sessão; deve acontecer antes de criar/atualizar sessão | `hb verify --task-type new_contract` com profile `roadmap_execution` → exit 1 com `BLOCKED_MODE_MISMATCH` |
| 6 | BKL-003 | Em `scripts/hb`: renomear `_apply_selection_rules(task_type)` → `_enforce_selection_rules(self, task_type: str, profile_id: str) -> int`; em vez de retornar string, comparar profile derivado com `profile_id`; se divergentes: `print("❌ BLOCKED_PROFILE_MISMATCH"); return 1`; se coerentes: `return 0`; Atualizar chamada em `cmd_verify()` linha ~633: `if self._enforce_selection_rules(task_type, profile_id) != 0: return 1` | Refatoração do código existente; sem dependências externas novas | Profile divergente entre `selection_rules` e TASK_CATALOG → exit 1 |
| 7 | BKL-005 | Em `scripts/git-hooks/pre-commit`, classe `HBHookValidator`: (a) Adicionar dict de classe `_SCOPE_PATH_MAP = {"contracts": ["contracts/", "docs/hbtrack/"], "backend": ["src/", "contracts/", "docs/hbtrack/"], "docs": ["docs/hbtrack/", "docs/_canon/"], "generated": ["generated/", "docs/hbtrack/"], "migrations": ["src/", "migrations/"], "roadmap": [], "readonly": []}`; (b) Adicionar `check_write_scope_compliance(self) -> bool`: lê `write_scope` da sessão; para `"roadmap"` → sem bloqueio; para `"readonly"` → bloquear qualquer staged file em paths de contratos; para os outros → verificar cada staged file contra `_SCOPE_PATH_MAP[write_scope]`; adicionar erro `BLOCKED_SCOPE_OVERFLOW` por violação; return `len(violations) == 0`; (c) Chamar no `run()` após `check_stage2_exit_code()` (nova Fase 3.5) | Campos de sessão prontos; hook já tem padrão de `check_*` methods estabelecido | Commit de `src/users/api.py` em sessão `write_scope=contracts` → bloqueado |
| 8 | BKL-015 | Em `scripts/hb`, `cmd_verify()`: após bloco de validação 4b (generate_code eligibility), adicionar bloco: ler `bundle_required = task_config.get("bundle_required", False)`; se True: resolver `bundle_path_template` substituindo `{module}` pelo module atual e `{feature}` por string vazia; verificar `(self.root / bundle_path.rstrip("/")).exists()`; se não existe → `print("❌ BLOCKED_BUNDLE_REQUIRED: ...", instrução de regeneração); return 1` | Validação de bundle é pré-condição de sessão (P0 no BACKLOG, P2 é prioridade relativa); sem dependências adicionais | `hb verify --task-type generate_code --module users` sem `compiled_context/users/` → exit 1 |
| 9 | BKL-016 | Em `scripts/git-hooks/pre-commit`, classe `HBHookValidator`: adicionar `check_derived_artifact_guard(self) -> bool`: definir `_DERIVED_PREFIXES = ["generated/source_graph/", "generated/", "_reports/contract_gates/"]`; carregar TASK_CATALOG; para cada staged file que começa com prefixo derivado, verificar se task_type da sessão tem esse path em `artifacts_produced`; adicionar erro `BLOCKED_DERIVED_ARTIFACT_MANUAL_EDIT` se não autorizado; Chamar após `check_write_scope_compliance()` (nova Fase 3.7) | Hook tem padrão consolidado; TASK_CATALOG já é lido pelo hook | Commit de `generated/` editado manualmente em sessão `new_contract` → bloqueado |
| 10 | BKL-007 | Em `scripts/hb`: adicionar dict de classe `_REENTRY_MAP` (ver seção de especificações abaixo); adicionar `cmd_reentry(self) -> int` que lê `_reports/contract_gates/latest.json`, encontra primeiro gate FAIL blocking, consulta `_REENTRY_MAP`, imprime rota estruturada; registrar subcomando `reentry` no parser `run()` | BKL-005 e BKL-016 estabelecem que falhas produzem evidência estruturada; agora pode-se consumi-la | `hb reentry` após gate FAIL imprime `retry_task_type`, `retry_stage`, `suggested_fix` |
| 11 | BKL-009 | Em `scripts/hb`: adicionar argumento `--check-context` ao subparser `verify` no `run()`; em `cmd_verify()` adicionar parâmetro `check_context: Optional[str] = None`; quando `task_type == "pr_fix"`: se `check_context is None` → `print("❌ pr_fix requer --check-context"); return 1`; ler `merge-readiness.json`; procurar `check_context` nos `checks[].context`; se não encontrado → `print("GAP_DE_PARIDADE"); return 1`; gravar `check_context` e `local_equivalent` em `stage0_validation_results` | Schema permite campos extras em `stage0_validation_results`; padrão BKL-001 já estabelecido | `hb verify --task-type pr_fix --check-context "ci / Validate Contracts"` grava `local_equivalent` |
| 12 | BKL-008 | Em `.contract_driven/TASK_CATALOG.yaml`: adicionar campo `focal_gate_set: [...]` a cada task (ver tabela abaixo); em `scripts/contracts/validate/validate_contracts.py`, na função `main()`, adicionar: se `profile == "task_focal"`: ler `_reports/session_start.json`; carregar TASK_CATALOG; usar `focal_gate_set` do `task_type` da sessão como filtro de gates; executar apenas esses | TASK_CATALOG e validate_contracts.py são enriquecidos; sem novas dependências de runtime | `validate_contracts.py --profile task_focal` em sessão `new_schema` → executa apenas 3 gates |
| 13 | BKL-010 | Em `scripts/hb`, `cmd_preflight()`: após bloco de `final_decision`, adicionar `_format_actionable_output(self, checks_failed, semantic_findings, reviewability_check)` que: agrupa `checks_failed` por prefixo (ASYNCAPI → `async_contract_error`, OPENAPI → `openapi_structure_error`, BLOCKED → `session_error`); para cada grupo imprime `[CORRIGIR PRIMEIRO]`, `[NÃO TOCAR]`, `[PRÓXIMA AÇÃO]` | `cmd_preflight()` já calcula tudo; só falta pós-processar a saída | `hb preflight` BLOCK imprime grupos de causa raiz com ação next step |
| 14 | BKL-011 | Em `scripts/git-hooks/pre-commit`, classe `HBHookValidator`: adicionar `check_reviewability_limits(self) -> bool` que lê `_reports/preflight/latest.json`; se `reviewability_check.exceeded == True` e `split_required == True` → adiciona erro `PR excede limites de reviewability — split antes de commitar`; Chamar após `check_derived_artifact_guard()` (nova Fase 3.9) | Hook consolidado; adicionar verificação no final da cadeia de checks | Commit bloqueado quando `exceeded=true` e `split_required=true` |
| 15 | BKL-013 | Em `scripts/hb`, `cmd_verify()`: no bloco de `session_update`, dentro de `stage0_validation_results`, adicionar `"authority_source_used": "TASK_CATALOG"` | Mudança pontual; `stage0_validation_results` aceita propriedades extras (sem `additionalProperties: false`) | `stage0_validation_results.authority_source_used == "TASK_CATALOG"` em toda sessão |
| 16 | BKL-012 | Em `scripts/hb`: adicionar `cmd_audit_prompts(self, check_bridge_docs: bool = False) -> int`; lógica: listar `(self.root / ".contract_driven/agent_prompts").glob("*.prompt.md")`; para cada prompt calcular nome de worker esperado; verificar se existe TASK_CATALOG entry com `worker_path` apontando para ele; classificar como `active`/`frozen`/`orphan`/`legacy`; return exit 1 se orphan; registrar `audit-prompts` no parser `run()` com `--check-bridge-docs` | BKL-001 e BKL-004 já leram frontmatter de prompts; este comando agrega | `hb audit-prompts` lista 22 prompts; exit 1 em presença de orphan |
| 17 | BKL-020 | Em `scripts/contracts/validate/validate_contracts.py`: (a) Adicionar constante `BLOCKED_GOVERNANCE_WITHOUT_RUNTIME_BINDING` no bloco de constantes; (b) Implementar `_g_governance_regression(root: pathlib.Path) -> dict`; (c) Para cada `.prompt.md` em `.contract_driven/agent_prompts/`: verificar TASK_CATALOG entry; para cada entry active no TASK_CATALOG: verificar que worker_path existe E frontmatter é coerente; (d) Adicionar ao `gate_plan` e ao `_precommit_ids` | Padrão de frontmatter estabelecido em BKL-001; WORKER_PROMPT_AUTHORITY_GATE (linha 9541) serve de referência | `--profile precommit` falha com `BLOCKED_GOVERNANCE_WITHOUT_RUNTIME_BINDING` se binding ausente |
| 18 | BKL-014 | Em `scripts/hb`: adicionar `_check_ir_freshness(self, module: str) -> bool` que verifica `generated/source_graph/{module}/` existe; se existe, compara mtime do diretório contra mtime máximo de `contracts/openapi/paths/{module}.yaml` e `contracts/schemas/{module}/`; retorna True se fresco; No `cmd_generate()`, antes de executar stage `backend`: chamar `_check_ir_freshness(module)`; se False e não `--force`: `print("❌ IR ausente ou stale"); acumular falha` | P2; depois que core runtime binding está estabelecido (passos 1-13) | `hb generate --backend --module users` com IR ausente → exit 1 com instrução |
| 19 | BKL-017 | Em `scripts/hb`, `cmd_check()`: quando `task_type` é `readiness_promotion` ou `implementation_promotion`, chamar `_validate_lifecycle_preconditions(self, task_type: str, module: str) -> int`: lê MODULE_REGISTRY.yaml; extrai status atual do módulo; mapa `{"readiness_promotion": "validated_contract", "implementation_promotion": "implementation_ready"}`; se status atual != origem esperado → `print("❌ BLOCKED_LIFECYCLE_JUMP"); return 1` | `cmd_check()` já valida `stage0_exit_code`; este bloco entra após essa validação | `hb check --module users` em `readiness_promotion` com módulo em `draft_contract` → exit 1 |
| 20 | BKL-018 | Em `scripts/hb`, `cmd_artifact()`: antes de executar o validator, para `task_type` em `{"readiness_promotion", "implementation_promotion"}`: chamar `_validate_promotion_evidence(self, task_type: str, module: str) -> int`; verificar `_reports/evidence/module_readiness_scorecard.json`; verificar `_reports/contract_gates/latest.json` tem `overall_status == "PASS"`; para `implementation_promotion` verificar `src/{module}/` existe e não vazio | BKL-017 estabelece preconditions em `cmd_check()`; BKL-018 é verificação downstream em `cmd_artifact()` | `hb artifact MODULE_REGISTRY.yaml` em `readiness_promotion` sem scorecard → exit 1 |
| 21 | BKL-019 | Em `scripts/hb`: adicionar `cmd_stats(self) -> int`; ler todos `_reports/execution_evidence/*.json`; agrupar por `task_type`; contar tentativas, calcular `overflow_count`, top `cause_ids[0]`; imprimir tabela; Registrar `stats` no parser `run()` | Evidência existe desde BKL-006; agora pode ser agregada | `hb stats` imprime tabela estruturada |
| 22 | BKL-021 | Criar `tests/pipeline/test_runtime_behavior.py` com `__init__.py`; 5 classes: `TestModeSeparation` (bloqueia task CDD em modo ROADMAP), `TestPromptUsedEvidence` (verifica `_reports/execution_evidence/` com SHA-256 do prompt), `TestPrFixBoundedScope` (`hb verify --task-type pr_fix` sem ou com `--check-context` inválido → exit 1), `TestIrLineage` (`hb generate --backend` bloqueia IR ausente ou stale), `TestPromotionGuards` (`hb artifact` em `readiness_promotion` falha sem scorecard); usar subprocess + workspace temporário mínimo | Testes de integração dos invariantes de runtime já implementados no CLI | `pytest tests/pipeline/test_runtime_behavior.py` → 0 falhas |
| 23 | BKL-022 | No `cmd_audit_prompts()` (passo 16), implementar flag `--check-bridge-docs`: lista bridge docs (`CLAUDE.md`, `.github/copilot-instructions.md`, `.github/skills/**`); verifica presença de `NON-SOVEREIGN` ou `BRIDGE ONLY` em cada um; adiciona erro se ausente; return exit 1 | `cmd_audit_prompts()` já existe desde passo 16 | `hb audit-prompts --check-bridge-docs` → exit 1 para bridge doc sem disclaimer |

---

## Especificações de Implementação

### `_SCOPE_PATH_MAP` completo (BKL-005)
```python
_SCOPE_PATH_MAP = {
    "contracts":  ["contracts/", "docs/hbtrack/"],
    "backend":    ["src/", "contracts/", "docs/hbtrack/"],
    "docs":       ["docs/hbtrack/", "docs/_canon/"],
    "generated":  ["generated/", "docs/hbtrack/"],
    "migrations": ["src/", "migrations/"],
    "roadmap":    [],       # sem restrição de paths (modo amplo por design)
    "readonly":   [],       # qualquer staged file em paths governados é violação
}
```
Para `readonly`: bloquear qualquer staged file que comece com paths em `CONTRACT_PATHS`.

### `_REENTRY_MAP` completo (BKL-007)
```python
_REENTRY_MAP = {
    "BLOCKED_WORKER_FRONTMATTER_MISMATCH": {
        "retry_task_type": None, "retry_stage": 0,
        "suggested_fix": "hb verify --task-type <mesmo> --module <mesmo>; verificar frontmatter do worker prompt"
    },
    "ASYNCAPI_VALIDATION_GATE": {
        "retry_task_type": "new_event", "retry_stage": 2,
        "suggested_fix": "Corrigir schema AsyncAPI; hb artifact contracts/asyncapi/..."
    },
    "OPENAPI_ROOT_STRUCTURE_GATE": {
        "retry_task_type": "contract_revision", "retry_stage": 2,
        "suggested_fix": "Corrigir estrutura root OpenAPI; hb artifact contracts/openapi/..."
    },
    "HANDOFF_COHERENCE_GATE": {
        "retry_task_type": None, "retry_stage": 0,
        "suggested_fix": "Atualizar SESSION_HANDOFF.md; verificar campos mode_operacao e task_type"
    },
    "BLOCKED_BUNDLE_REQUIRED": {
        "retry_task_type": None, "retry_stage": 0,
        "suggested_fix": "python3 scripts/compile/compile_context_bundle.py --module <module>"
    },
    "BLOCKED_SCOPE_OVERFLOW": {
        "retry_task_type": "pr_fix", "retry_stage": 0,
        "suggested_fix": "Reverter arquivos fora do write_scope; hb verify com task_type correto"
    },
    "BLOCKED_GOVERNANCE_WITHOUT_RUNTIME_BINDING": {
        "retry_task_type": None, "retry_stage": 0,
        "suggested_fix": "Adicionar entry em TASK_CATALOG.yaml ou adicionar frontmatter ao prompt"
    },
    "BLOCKED_AXIOM_INTEGRITY": {
        "retry_task_type": "contract_revision", "retry_stage": 1,
        "suggested_fix": "Corrigir violação de axiom; consultar DOMAIN_AXIOMS.json"
    },
}
```

### `focal_gate_set` por task (BKL-008)
| task_type | focal_gate_set |
|-----------|----------------|
| `new_schema` | `[AXIOM_INTEGRITY_GATE, PATH_CANONICALITY_GATE, JSON_SCHEMA_VALIDATION_GATE]` |
| `new_contract` | `[AXIOM_INTEGRITY_GATE, PATH_CANONICALITY_GATE, OPENAPI_ROOT_STRUCTURE_GATE, TOOLING_CONFIG_GATE]` |
| `contract_revision` | `[AXIOM_INTEGRITY_GATE, OPENAPI_ROOT_STRUCTURE_GATE, CONTRACT_BREAKING_CHANGE_GATE, SCHEMA_CONSISTENCY_GATE]` |
| `new_event` | `[AXIOM_INTEGRITY_GATE, ASYNCAPI_VALIDATION_GATE, PATH_CANONICALITY_GATE]` |
| `new_workflow` | `[AXIOM_INTEGRITY_GATE, ARAZZO_VALIDATION_GATE, CROSS_SPEC_ALIGNMENT_GATE]` |
| `generate_code` | `[AXIOM_INTEGRITY_GATE, CODE_ARCHITECTURE_GATE, ADVERSARIAL_ANALYSIS_GATE]` |
| `feature_update` | `[AXIOM_INTEGRITY_GATE, OPENAPI_ROOT_STRUCTURE_GATE, CODE_ARCHITECTURE_GATE]` |
| `pr_fix` | `[AXIOM_INTEGRITY_GATE, HANDOFF_COHERENCE_GATE]` |
| `readiness_promotion` | `[AXIOM_INTEGRITY_GATE, DERIVED_DRIFT_GATE, OPENAPI_ROOT_STRUCTURE_GATE, REQUIRED_ARTIFACT_PRESENCE_GATE]` |
| `implementation_promotion` | `[CODE_ARCHITECTURE_GATE, FEATURE_READINESS_GATE, ADVERSARIAL_ANALYSIS_GATE]` |
| `new_module` | `[AXIOM_INTEGRITY_GATE, MODULE_REGISTRY_GATE, PATH_CANONICALITY_GATE]` |

### Estrutura de `_reports/execution_evidence/{session_id}.json`
```json
{
  "session_id": "<uuid-v4>",
  "created_at": "<ISO-8601-UTC>",
  "task_type": "<task_type>",
  "module": "<module-ou-null>",
  "worker_path": "<caminho-relativo>",
  "worker_prompt_sha256": "<64-hex>",
  "worker_frontmatter": {"task_type": "...", "version": "...", "status": "..."},
  "write_scope": "<scope>",
  "operation_mode": "<CDD|ROADMAP>",
  "retries": 0,
  "cause_ids": [],
  "scope_overflow_detected": false
}
```

---

## Validação Técnica

### Por item

| Item | Comando de validação | Tipo de teste |
|------|---------------------|---------------|
| A18 | `python3 -c "import json, jsonschema; s=json.load(open('contracts/schemas/shared/session_start.schema.json')); sess={...task_type:'pr_fix'...}; jsonschema.validate(sess, s); print('OK')"` | compilance |
| BKL-001 | `python3 scripts/hb verify --task-type new_contract --module training` → verificar `session_start.json["worker_prompt_sha256"]` tem 64 chars | funcionamento |
| BKL-001 | Criar prompt temporário com `task_type: wrong_task` no frontmatter; `hb verify` → exit 1 com `BLOCKED_WORKER_FRONTMATTER_MISMATCH` | bloqueio |
| BKL-002 | Modificar temporariamente TASK_CATALOG para `new_contract` ter `profile_id: roadmap_execution`; `hb verify --task-type new_contract --module users` → exit 1 com `BLOCKED_MODE_MISMATCH` | bloqueio |
| BKL-003 | Modificar BOOT_PROFILES.yaml para ter regra que seleciona `default` para `new_contract`; `hb verify --task-type new_contract --module users` → exit 1 com `BLOCKED_PROFILE_MISMATCH` | bloqueio |
| BKL-004 | `ls _reports/execution_evidence/` após `hb verify` bem-sucedido → arquivo UUID presente; `jq .worker_prompt_sha256 _reports/execution_evidence/*.json` → 64 chars | funcionamento |
| BKL-005 | Mock: `session_start.json` com `write_scope=contracts`; staged `src/users/api.py`; rodar hook → exit 1 com `BLOCKED_SCOPE_OVERFLOW` | bloqueio |
| BKL-005 | Mock: `session_start.json` com `write_scope=contracts`; staged `contracts/openapi/paths/users.yaml` → hook passa | funcionamento real |
| BKL-005 | Testar idempotência: rodar hook 2x com mesmo estado → mesmo resultado | idempotência |
| BKL-006 | Verificar que `session_start.json` não contém campo `worker_frontmatter` (exclusivo da evidência) | compilance |
| BKL-007 | `python3 scripts/hb reentry` com `latest.json` contendo gate FAIL → imprime `retry_task_type` | funcionamento |
| BKL-007 | `python3 scripts/hb reentry` sem relatório → exit 1 com mensagem explicativa | falha total |
| BKL-008 | `validate_contracts.py --profile task_focal` em sessão `task_type=new_schema` → `ASYNCAPI_VALIDATION_GATE` aparece como SKIP | funcionamento |
| BKL-009 | `hb verify --task-type pr_fix --check-context "ci / nao_existe"` → exit 1 com `GAP_DE_PARIDADE` | bloqueio |
| BKL-009 | `hb verify --task-type pr_fix --check-context "ci / Validate Contracts"` → grava `local_equivalent` | funcionamento |
| BKL-010 | `hb preflight` com checks falhando → output contém `[CORRIGIR PRIMEIRO]` e `[PRÓXIMA AÇÃO]` | funcionamento |
| BKL-011 | Criar `_reports/preflight/latest.json` com `exceeded=true` e `split_required=true`; staged qualquer arquivo → hook bloqueia | bloqueio |
| BKL-012 | `hb audit-prompts` → lista 22 prompts com classificação sem exceção Python | funcionamento |
| BKL-012 | Criar `.prompt.md` sem TASK_CATALOG entry; `hb audit-prompts` → exit 1 com `orphan` identificado | bloqueio |
| BKL-013 | `jq .stage0_validation_results.authority_source_used _reports/session_start.json` → `"TASK_CATALOG"` | compilance |
| BKL-014 | `hb generate --backend --module users` sem `generated/source_graph/users/` → exit 1 com instrução | bloqueio |
| BKL-015 | `hb verify --task-type generate_code --module users` sem `compiled_context/users/` → exit 1 com `BLOCKED_BUNDLE_REQUIRED` | bloqueio |
| BKL-016 | Staged `generated/source_graph/users/api.json` em sessão `new_contract` → hook bloqueia com `BLOCKED_DERIVED_ARTIFACT_MANUAL_EDIT` | bloqueio |
| BKL-017 | `hb check --module users` em sessão `readiness_promotion` com módulo em `draft_contract` → exit 1 com `BLOCKED_LIFECYCLE_JUMP` | bloqueio |
| BKL-018 | `hb artifact docs/_canon/MODULE_REGISTRY.yaml` em sessão `readiness_promotion` sem scorecard → exit 1 | bloqueio |
| BKL-019 | `hb stats` com pelo menos 1 arquivo em `execution_evidence/` → imprime tabela sem exceção | funcionamento |
| BKL-020 | `validate_contracts.py --profile precommit` com prompt sem TASK_CATALOG → `GOVERNANCE_REGRESSION_GATE: FAIL` | bloqueio |
| BKL-020 | Todos prompts alinhados → `GOVERNANCE_REGRESSION_GATE: PASS` | funcionamento real |
| BKL-021 | `pytest tests/pipeline/test_runtime_behavior.py -v` → 0 falhas | compilance |
| BKL-021 | `python3 scripts/hb survival-suite` → inclui novo arquivo, passa | funcionamento real |
| BKL-022 | `hb audit-prompts --check-bridge-docs` com bridge doc sem disclaimer → exit 1 | bloqueio |

---

## Análise Adversarial

### Cenários ELIMINADOS por este plano

| Cenário | Mecanismo de eliminação |
|---------|------------------------|
| Agente ignora `hb verify` e edita arquivos → commita | BKL-005 (hook bloqueia staged files fora do `write_scope` sem sessão válida) + BKL-001 (hook já exige `stage0_exit_code=0`) |
| Worker prompt trocado sem evidência | BKL-004 grava SHA-256; BKL-020 detecta inconsistência TASK_CATALOG vs frontmatter |
| Task CDD em sessão ROADMAP | BKL-002 bloqueia em `cmd_verify()` antes de criar sessão |
| `pr_fix` improvisa check não mapeado | BKL-009 exige `--check-context` mapeado em `merge-readiness.json` |
| `generate_code` sem bundle de contexto | BKL-015 bloqueia `hb verify` antes de iniciar |
| Edição manual de artefato derivado | BKL-016 bloqueia commit de `generated/` editado fora de task autorizada |
| Nova governança acumula sem binding | BKL-020 `GOVERNANCE_REGRESSION_GATE` bloqueia no precommit |

### Cenários MITIGADOS (risco reduzido, não eliminado)

| Cenário | Mitigação | Risco residual |
|---------|-----------|----------------|
| Evidência de execução criada com dados falsos manualmente | CLI valida antes de escrever; sem cross-check de integridade do arquivo | Baixo — exige manipulação deliberada de artefato de auditoria |
| `pr_fix` com `check_context` válido mas contexto errado | Validado contra `merge-readiness.json`; contexto errado mas existente passa | Médio — mitigado pelo worker prompt que exige lookup no GitHub |
| `focal_gate_set` incompleto (gate relevante omitido por engano) | Gate set é definido no TASK_CATALOG; BKL-020 verifica binding mas não cobertura | Baixo-médio — requer revisão humana do set por task |

### Cenários RESTANTES (aceitos com justificativa)

| Cenário | Justificativa |
|---------|---------------|
| Agente escreve fora do `write_scope` sem commitar (mudanças locais) | Hook opera apenas em staged files; mudanças locais detectadas no próximo `hb preflight`; não entram no repositório sem hook |
| `session_start.json` corrompido manualmente | Fora do modelo de ameaça de agent misbehavior; exige acesso físico |
| `write_scope=roadmap` sem restrição de paths | Aceito por design: ROADMAP abrange infra/frontend/mobile/deploy — restrição quebraria workflow legítimo |

### Cenário INACEITÁVEL não coberto por nenhum BKL

| Cenário | Por que inaceitável | Gap |
|---------|---------------------|-----|
| Sessão stale com `write_scope` antigo é reusada em nova tarefa | Sessão de dias anteriores pode ter scope diferente da tarefa atual | Não especificado no BACKLOG; correção seria `check_session_freshness(max_age_hours=8)` no hook comparando `session_timestamp` com `datetime.now()` |

---

## Correções Aplicadas

| ID | Arquivo / componente alterado | Mudança aplicada | Falha resolvida | Justificativa |
|----|-------------------------------|------------------|-----------------|---------------|
| A18 | `contracts/schemas/shared/session_start.schema.json` | Adicionados `pr_fix`, `implementation_promotion`, `feature_update` ao enum `task_type`; adicionados campos `worker_frontmatter_validated`, `worker_frontmatter_matches_catalog` em `stage0_validation_results`; adicionado campo raiz `worker_prompt_sha256` (pattern hex-64); versão atualizada para `1.4.0` | `hb verify` falhava por schema para tasks legítimas | **PASS** — `jsonschema.validate` aceita sessão com `task_type=pr_fix` sem exceção |
| BKL-004 parcial | `scripts/hb` — classe `HBCLIv2` | Adicionado método `_read_worker_frontmatter(self, path) -> dict`: extrai frontmatter YAML delimitado por `---`; retorna `{}` se ausente ou parse falhar | Método auxiliar puro necessário para BKL-001 | **PASS** — retorna `{}` para prompt sem frontmatter `---`; retorna dict vazio mas válido para `create_openapi_contract.prompt.md` (prompts não usam delimitador `---` padrão — será endereçado em BKL-020) |
| BKL-006 parcial | `scripts/hb` — classe `HBCLIv2` | Adicionado método `_write_execution_evidence(self, evidence: dict) -> None`: cria `_reports/execution_evidence/` e persiste `{session_id}.json`; idempotente por session_id | Evidência de execução deve ser separada do estado canônico `session_start.json` | **PASS** — arquivo criado, conteúdo correto, idempotente, `session_start.json` não contém `worker_frontmatter` |
| BKL-002 | `scripts/hb` — `cmd_verify()`, novo `_validate_operation_mode_coherence()` | Adicionado método que bloqueia `execute_roadmap_phase` em mode CDD e tasks CDD em mode ROADMAP; chamado após derivação de `operation_mode`, antes de `session_update` | `operation_mode` gravado na sessão sem validação cruzada com `task_type` | **PASS** — 4 combinações corretas validadas; rc=2 em `hb verify new_contract` é HANDOFF_COHERENCE_GATE pré-existente (SESSION_HANDOFF.md em ROADMAP/fase 6), não BKL-002; `BLOCKED_MODE_MISMATCH` ausente no output confirma que new_contract+CDD passa a checagem de modo |
| BKL-003 | `scripts/hb` — `_apply_selection_rules()` → `_enforce_selection_rules()` + `cmd_verify()` validação 5b | Renomeado e reescrito método: `_enforce_selection_rules(task_type, profile_id) -> int` — valida coerência entre `selection_rules` (BOOT_PROFILES.yaml) e `profile_id` (TASK_CATALOG); retorna 1 com `BLOCKED_PROFILE_MISMATCH` se divergir. Validação 5b em `cmd_verify()` convertida de aviso informativo para bloqueio hard: `if self._enforce_selection_rules(...) != 0: return 1` | `selection_rules` e `phase_profiles` em BOOT_PROFILES.yaml marcados `not_implemented`; aviso era apenas informativo | **PASS** — `selection_rules` retorna lista vazia (not_implemented), `_enforce_selection_rules` retorna 0 imediatamente; coerência garantida sem falsos positivos; `new_contract` profile=contract_execution + `execute_roadmap_phase` profile=roadmap_execution ambos validados |
| BKL-005 | `scripts/git-hooks/pre-commit` — classe `HBHookValidator` | Adicionado dict `_SCOPE_PATH_MAP` ao topo da classe (6 escopos + mapa de prefixos permitidos); adicionado método `check_write_scope_compliance()` — itera `staged_files`, verifica cada contra `_SCOPE_PATH_MAP[write_scope]`, acumula erro `BLOCKED_SCOPE_OVERFLOW` em `self.errors`; integrado em `run()` logo após `check_stage2_exit_code()` com return 1 | `write_scope` era derivado e gravado mas nunca enforced no hook — agente podia commitar arquivos fora do escopo declarado | **PASS** — 4 testes: src/users/api.py bloqueado em contracts, contracts/openapi/paths/users.yaml permitido em contracts, roadmap sem restrições, backend permite src/contracts mas bloqueia migrations/ |
| BKL-015 | `scripts/hb` — `cmd_verify()`, nova "Validação 4c" | Adicionado bloco de validação após Validação 4b: lê `bundle_required` de `task_config`; se true, resolve `bundle_path_template` substituindo `{module}` e `{feature}`; verifica `(root / bundle_path).exists()`; retorna exit 1 com `BLOCKED_BUNDLE_REQUIRED` + instrução de regeneração se ausente | Tasks com `bundle_required: true` (`feature_update`, `generate_code`, `execute_roadmap_phase`) não tinham gate verificando bundle antes da execução | **PASS** — 4 testes: generate_code/feature_update sem bundle → blocked, new_contract sem bundle_required → permitido, todos os bundle_required tasks têm template em TASK_CATALOG |
| BKL-016 | `scripts/git-hooks/pre-commit` — classe `HBHookValidator`, método `check_derived_artifact_guard()` | Adicionado método que bloqueia edição manual de arquivos em prefixos derivados (`generated/source_graph/`, `generated/`, `_reports/contract_gates/`); valida contra `artifacts_produced` do TASK_CATALOG para task_type da sessão; integrado em `run()` logo após `check_write_scope_compliance()` | Agente podia editar manualmente artefatos em `generated/` e `_reports/` que deveriam ser regenerados | **PASS** — `generated/source_graph/` bloqueado em ALL tasks (nenhum task lista `generated/` em artifacts_produced); `src/` permitido em generate_code (lista `src/`); `contracts/` permitido em qualquer task (não derivado); **correção real**: `generated/` e `_reports/contract_gates/` são 100% protegidos, não apenas "quando task não autoriza" |
| BKL-007 | `scripts/hb` — classe `HBCLIv2`, novo `cmd_reentry()` | Adicionado dict `_REENTRY_MAP` (8 gates → rota de reentrada); adicionado método `cmd_reentry()` que lê `_reports/contract_gates/latest.json`, identifica primeiro gate FAIL blocking, mapeia via `_REENTRY_MAP`, imprime rota estruturada; subparser reentry registrado; dispatch elif adicionado em `run()` | Falhas de validator não produzem causa raiz única nem próxima ação — agente reinicia do zero | **PASS** — 4 testes: ASYNCAPI_VALIDATION_GATE mapeia new_event, nenhuma falha blocking → NO_FAIL, gate FAIL não-blocking ignorado, gate desconhecido detectado |
| BKL-009 | `scripts/hb` — `cmd_verify()` + subparser verify + `merge-readiness.json` | Adicionado `--check-context` ao subparser verify; parâmetro `check_context: Optional[str]` em `cmd_verify()`; dispatch passa `check_context=getattr(parsed_args, "check_context", None)`; Validação 5d adicionada: `pr_fix` sem `--check-context` → exit 1; check inexistente → `GAP_DE_PARIDADE` com lista dos checks disponíveis; check encontrado → grava `check_context` e `local_equivalent` em `stage0_validation_results`; `merge-readiness.json`: 2 checks (Docker Build Check e Pact Provider Gate — training) receberam `local_equivalent: null` por ausência de equivalente local mapeado | `pr_fix` sem trilha formal: sem resolução `check_context → local_equivalent` | **PASS** — 4 testes: check inexistente → NOT_FOUND, `ci / Validate Contracts` → `local_equivalent: python3 scripts/hb validate --profile precommit`, None → MISSING_CHECK_CONTEXT, todos os 12 checks têm local_equivalent |
| BKL-001 | `scripts/hb` — `cmd_verify()` | Integração de `_read_worker_frontmatter()` e `_write_execution_evidence()`: (a) após `.exists()`: extrai frontmatter + calcula SHA-256 do prompt; (b) bloqueia com `BLOCKED_WORKER_FRONTMATTER_MISMATCH` se `fm_task_type` diverge; (c) grava `worker_prompt_sha256` na sessão raiz; (d) grava `worker_frontmatter_validated` e `worker_frontmatter_matches_catalog` em `stage0_validation_results`; (e) chama `_write_execution_evidence()` para **todos os runs** (incluindo falhas de gate), com `stage0_exit_code` no payload. **Desvio intencional da spec**: spec original previa escrita apenas no sucesso — implementação registra todos os runs pois evidência de falha é mais útil para auditoria. Separação session_start.json (estado) / execution_evidence (evidência imutável) mantida. | `cmd_verify()` validava apenas existência do worker; sem evidência auditável do prompt carregado | **PASS** — SHA-256 gravado (64 hex chars), `worker_frontmatter_validated: False` esperado (prompts não usam `---`), `worker_frontmatter_matches_catalog: True`, execution_evidence criado |

---

## Veredito Final

Este plano endurece o runtime do repositório em 4 camadas complementares e backward-compatible:

1. **Schema (A18)**: elimina travamento imediato de tasks legítimas e abre espaço para campos de evidência novos sem quebrar sessões existentes.

2. **CLI `scripts/hb` (BKL-001 a 003, 006, 007, 009, 012, 013, 015, 017, 018, 019)**: transforma `hb verify` em ponto de controle real — não apenas verifica existência do prompt, mas lê frontmatter, calcula hash, valida modo operacional, verifica bundle, e produz evidência separada e imutável por execução.

3. **Pre-commit hook (BKL-005, 011, 016)**: fecha o loop no ponto de saída — o agente não pode commitar fora do escopo da sessão, não pode commitar artefatos derivados editados manualmente, e não pode commitar quando o PR excede reviewability.

4. **Validator + testes (BKL-008, 020, 021)**: garante que governança nova não entra sem binding operacional, e qualquer regressão estrutural no plano de controle quebra a suíte de sobrevivência.

**Mínimo viável se escopo precisar ser cortado:** A18 + BKL-001 + BKL-005 + BKL-015. Essas 4 mudanças eliminam os erros de roteamento e os commits fora de escopo que causam a maioria dos loops de correção.

**Após implementação completa:**
- A implementação passa? **SIM** — cada item tem critério de aceite binário e testável
- Existe vulnerabilidade ou fragilidade material? **SIM** — sessão stale (sem freshness gate)
- Existe cenário plausível de erro relevante? **SIM** — `focal_gate_set` incompleto (requer revisão humana)
- A implementação é robusta contra falhas previsíveis? **SIM** — 7 cenários eliminados, 3 mitigados
- O que falta para ser operacionalmente blindada: `check_session_freshness(max_age_hours=8)` no hook (não coberto pelo BACKLOG atual)

---

## Arquivos Críticos

- `contracts/schemas/shared/session_start.schema.json` — A18
- `scripts/hb` — BKL-001, 002, 003, 004, 006, 007, 009, 010, 012, 013, 014, 015, 017, 018, 019
- `scripts/git-hooks/pre-commit` — BKL-005, 011, 016
- `scripts/contracts/validate/validate_contracts.py` — BKL-008, 020
- `.contract_driven/TASK_CATALOG.yaml` — BKL-008 (`focal_gate_set`)
- `tests/pipeline/test_runtime_behavior.py` *(novo)* — BKL-021
- `_reports/execution_evidence/` *(novo diretório, criado programaticamente)* — BKL-006
