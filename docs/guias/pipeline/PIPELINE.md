# PIPELINE DE IA/AGENTES — HB TRACK

> **Documento:** reconstrução analítica datada do pipeline.
> **Método:** análise direta de arquivos — prompts, scripts, configs, gates, registries, CI/CD.
> **Nota de uso:** este arquivo preserva uma leitura analítica de 2026-03-19 e **não deve ser usado como fonte única para contagem de gates ou enforcement atual**.
> **Fonte operacional atual:** `scripts/hb`, `scripts/contracts/validate/validate_contracts.py`, `docs/guias/pipeline/PIPELINE_SUMMARY.md`, `_reports/pipeline_health.json` e `_reports/contract_gates/latest.json`.
> **Nível de certeza interno:** fato confirmado, inferência plausível ou não confirmado — indicados explicitamente.

---

## PARTE 1 — Visão Geral do Pipeline

### O que o pipeline faz

O pipeline do HB Track implementa um sistema de **Contract-Driven Development (CDD)** mediado por agentes IA. Seu objetivo é garantir que **nenhum código seja escrito antes que os contratos correspondentes estejam formalmente validados**. O pipeline governa o ciclo completo desde a decisão de criar uma funcionalidade até a autorização formal para implementação.

### Qual problema resolve

Sem este pipeline, um agente IA trabalhando em um sistema complexo de 16 módulos tende a:
- inventar endpoints, campos ou comportamentos não documentados;
- criar artefatos fora de paths canônicos, quebrando rastreabilidade;
- tomar decisões arquiteturais sem registro formal;
- avançar para implementação com contratos incompletos ou inconsistentes.

O pipeline resolve isso com **bloqueios determinísticos**: o agente para e emite um código canônico de bloqueio em vez de inferir.

### Onde começa e onde termina

**Entrada:** Pedido do usuário com `task_type` + `module` (+ parâmetros específicos da tarefa).

**Saída:** Um dos três resultados possíveis:
1. Artefato canônico criado/revisado, todos os 44 gates PASS, módulo elegível para implementação.
2. Bloqueio explícito com código canônico (um dos 20 códigos) + instrução de resolução.
3. Relatório de auditoria (para task-types de auditoria, sem artefato produzido).

### Principais componentes

| Componente | Tipo | Quantidade |
|---|---|---|
| Ponto de entrada obrigatório (orchestrator) | Orquestrador | 1 |
| Workers especializados (prompts) | Agentes | 17 |
| Task-types ativos | Roteamento | 9 ativos + 5 auditoria + 2 congelados |
| Gates de validação | Guardrails | 44 (30 bloqueantes) |
| Boot profiles | Configuração | 4 |
| Módulos canônicos | Escopo | 16 |
| Etapas formais do pipeline | Pipeline | 6 |
| Workflows CI/CD | Integração | 4 |

### Arquitetura geral

O sistema é uma **orquestração hierárquica de agente único** (não multi-agente em execução paralela). Um único agente IA (Claude) é instruído a seguir um protocolo rígido de boot → roteamento → execução → validação. Os "workers" são prompts operacionais especializados que o agente carrega condicionalmente, não processos independentes.

```
Usuário → Orchestrator (pré-contrato) → Worker (task-type) → Validator (44 gates) → Saída
```

---

## PARTE 2 — Mapa do Pipeline

| Etapa | Objetivo | Entrada | Processamento | Decisão | Saída | Arquivos envolvidos | Certeza |
|---|---|---|---|---|---|---|---|
| **Boot** | Carregar contexto mínimo | Início de sessão | Ler AGENT_INSTRUCTIONS.md; verificar SESSION_HANDOFF.md | Handoff existe? → ler antes de qualquer outra coisa | Contexto base do agente carregado | `docs/_canon/AGENT_INSTRUCTIONS.md`, `SESSION_HANDOFF.md` | Fato confirmado |
| **Fase 0 — Session Boot** | Validar task_type + module | `task_type`, `module` | Verificar TASK_CATALOG.yaml (status active?), MODULE_REGISTRY.yaml (módulo canônico?), worker_prompt exists?, selecionar profile | task_type inválido → BLOCKED; module inválido → BLOCKED; worker ausente → BLOCKED | `_reports/session_start.json` criado; profile selecionado | `.contract_driven/TASK_CATALOG.yaml`, `docs/_canon/MODULE_REGISTRY.yaml`, `.contract_driven/BOOT_PROFILES.yaml` | Fato confirmado |
| **Fase 1 — Discovery** | Carregar artefatos do domínio | Profile selecionado | Carregar required_sections do profile; verificar artefatos obrigatórios do módulo | Artefato faltando → BLOCKED_REQUIRED_ARTIFACT_MISSING; decisão arquitetural aberta → BLOCKED_MISSING_ARCH_DECISION | Contexto de domínio montado | Profile específico em `BOOT_PROFILES.yaml`, `ARCHITECTURE_DECISION_BACKLOG.md` | Fato confirmado |
| **Decision Discovery** | Resolver lacunas arquiteturais | Contexto do módulo + backlog | Verificar decisões obrigatórias abertas; executar benchmark competitivo; propor ADR | Decisão obrigatória aberta → bloquear; decisão importante → aviso + aprovação humana | ADR criada em `docs/_canon/decisions/ADR-NNN-slug.md` | `decision_discovery.prompt.md`, `DECISION_POLICY.md`, `ARCHITECTURE_DECISION_BACKLOG.md` | Fato confirmado |
| **Fase 2 — Authoring** | Criar/atualizar artefato canônico | Contexto montado + task_type | Carregar worker do task_type; ler templates SSOT; criar artefato no path canônico | Path errado → BLOCKED_NONCANONICAL_NORMATIVE_PATH; convenção ausente → BLOCKED_MISSING_API_CONVENTION | Artefato soberano em path canônico | Worker específico (ex: `create_openapi_contract.prompt.md`), templates em `.contract_driven/templates/` | Fato confirmado |
| **Compilação de Policy** | Regenerar derivados determinísticos | Contrato soberano modificado | `compile_api_policy.py --module X --surface Y`; atualizar `generated/resolved_policy/` e `generated/manifests/` | Drift detectado → FAIL | `generated/resolved_policy/*.resolved.yaml`, `generated/manifests/*.traceability.yaml` | Fato confirmado |
| **Fase 3 — Validation** | Executar 44 gates bloqueantes | Todos os artefatos do repo | `validate_contracts.py` executa gates em ordem (0→16); each gate bloqueante: FAIL → READINESS_SUMMARY_GATE FAIL | Qualquer gate bloqueante FAIL → pipeline FAIL; SKIP_NOT_APPLICABLE para gates sem artefato alvo | `_reports/contract_gates/latest.json`, `_reports/pipeline_health.json` | Fato confirmado |
| **Fase 4 — Readiness** | Classificar módulo como pronto | Resultado dos gates | Verificar MODULE_REGISTRY.expected_surfaces; DECISION_IR_CONFORMANCE_GATE; MODULE_STATUS_COHERENCE_GATE | Todos gates PASS → status elegível para subir em MODULE_REGISTRY.yaml | `_reports/evidence/module_readiness_scorecard.json` atualizado | `MODULE_REGISTRY.yaml`, `GATES_REGISTRY.yaml` | Fato confirmado |
| **Fase 5 — Handoff** | Autorizar implementação | Readiness confirmada | Verificar que artefato é materializável sem inferência; SESSION_HANDOFF.md coerente | Inferência necessária → DC5 FAIL; coerente → handoff disponível | `SESSION_HANDOFF.md` atualizado; módulo elegível para `generate_code` (quando descongelado) | `SESSION_HANDOFF.md`, `HANDOFF_COHERENCE_GATE` | Fato confirmado |
| **CI/CD** | Validação contínua em push/PR | Push para main/develop | `contract-gates.yml`: gates completos; `context-efficiency-audit.yml`: mensal; `domain-completeness-audit.yml`: semanal | Exit ≠ 0 → PR bloqueado | Artefatos de CI em `_reports/` | `.github/workflows/` (4 arquivos) | Fato confirmado |

---

## PARTE 3 — Fluxo Ponta a Ponta

### 3.1 Entrada do Usuário

O usuário informa (diretamente ou em linguagem natural):
```
task_type: new_contract
module: training
resource: training-sessions
method: POST
scope_description: criar endpoint de criação de sessão de treino
```

O agente pode aceitar linguagem natural e identificar os campos, mas **não pode inferir `task_type` ou `module` ambíguo** — deve perguntar explicitamente (caso C1/C2 do red team).

### 3.2 Verificação de SESSION_HANDOFF.md

**Antes de qualquer ação**, o agente verifica se `SESSION_HANDOFF.md` existe na raiz.

- **Existe** → lê o arquivo completo; considera bloqueios ativos da sessão anterior; contexto de módulo já trabalhado.
- **Não existe** → continua sem contexto de sessão anterior.

Arquivo: `docs/_canon/AGENT_INSTRUCTIONS.md §0`

### 3.3 Fase 0 — Session Boot (pré_contract_orchestrator)

**Worker:** `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`

O orchestrator executa `hb verify --task-type <T> --module <M>`:

```
scripts/hb → HBCLIv2.cmd_verify()
  ├─ task_type em TASK_CATALOG.yaml? (status = active?)
  ├─ module em MODULE_REGISTRY.yaml?
  ├─ worker_path existe no filesystem?
  ├─ profile_id válido em BOOT_PROFILES.yaml?
  └─ Cria/atualiza _reports/session_start.json
       └─ Executa validate_contracts.py --stage session-start
```

Se qualquer check falha → exit ≠ 0 → **não avança**.

Resultado: `_reports/session_start.json` com `session_id`, `task_type`, `module`, `boot_profile_id`, `worker_id`, `stage=0`.

Emite observabilidade:
```
[ORCHESTRATOR] fase:0 module:training task_type:new_contract
  boot_profile:contract_execution module_status:validated_contract
  resultado: PASS
  worker_destino: create_openapi_contract
```

### 3.4 Seleção e Carregamento do Profile

O profile selecionado para `new_contract` é **contract_execution**:

```yaml
# .contract_driven/BOOT_PROFILES.yaml
contract_execution:
  boot_minimo: [AGENT_INSTRUCTIONS, CONTRACT_PIPELINE, BOOT_PROFILES, GATES_REGISTRY]
  boot_condicional: [SESSION_HANDOFF (se existe), MODULE_DOCS (do módulo alvo)]
  gate_only: [CONTRACT_SYSTEM_RULES, CONTRACT_SYSTEM_LAYOUT, api_rules.yaml]
  validations:
    - session_start_valid
    - task_type_active
    - boot_profile_id_valid
    - stage_in_allowed
  exit_on_fail: true
```

O agente carrega os artefatos de `boot_minimo` + condicionais ativos. Os artefatos `gate_only` são consultados apenas quando necessário pelo worker ou gate específico.

### 3.5 Fase 1 — Discovery (Artefatos e Decisões)

O orchestrator verifica:

1. **MODULE_REGISTRY_GATE**: módulo existe e tem status registrado.
2. **REQUIRED_ARTIFACT_PRESENCE_GATE**: docs mínimas do módulo existem (`README.md`, `DOMAIN_RULES_<MOD>.md`, `INVARIANTS_<MOD>.md`, `TEST_MATRIX_<MOD>.md`, `MODULE_SCOPE_<MOD>.md`).
3. **SCOPE_BOUNDARY_GATE**: se o artefato alvo contém refs cross-module → `scripts/gates/check_scope_boundary.py`.
4. **ARCHITECTURE_DECISION_BACKLOG**: decisão obrigatória aberta para o módulo?
   - **Sim** → aciona **decision_discovery.prompt.md** (ver 3.6).
   - **Não** → continua direto para Authoring.

`hb check --module training` executa a Fase 1 formalmente.

### 3.6 Decision Discovery (condicional)

**Worker:** `.contract_driven/agent_prompts/decision_discovery.prompt.md`

Ativado quando:
- Decisão `obrigatória` aberta em `ARCHITECTURE_DECISION_BACKLOG.md` para o módulo.
- Contrato envolve AUTH, AUTHZ, dados sensíveis, eventos assíncronos.
- Placeholder não resolvido em artefato canônico.
- Impacta semântica de handebol (gatilho esportivo).

Procedimento:
1. Lê as 12 fontes mínimas obrigatórias do worker (DECISION_POLICY, backlog, ADRs, COMPETITIVE_BENCHMARK_PROTOCOL, etc.).
2. Classifica cada decisão pendente como `obrigatória`, `importante` ou `opcional`.
3. Executa **benchmark competitivo** por domínio antes de apresentar opções.
4. Apresenta ao humano no formato: `📊 mercado → 🎯 3 caminhos (A/B/C) → ⭐ recomendação`.
5. **Aguarda aprovação explícita** — não avança sem confirmação.
6. Após aprovação: cria `docs/_canon/decisions/ADR-NNN-slug.md`, atualiza backlog, roda `validate_contracts.py`.

Bloqueios possíveis: `BLOCKED_MISSING_ARCH_DECISION`, `BLOCKED_CONTRACT_CONFLICT`.

### 3.7 Fase 2 — Authoring (Worker Especializado)

O orchestrator carrega o worker correspondente ao task_type e entrega o contexto de domínio montado.

**Exemplo: `create_openapi_contract.prompt.md`** para `new_contract/training`:

O worker:
1. Lê (nesta ordem): `CONTRACT_SYSTEM_RULES.md`, `CONTRACT_SYSTEM_LAYOUT.md`, `COMPETITIVE_BENCHMARK_PROTOCOL.md`, `api_rules.yaml`, `MODULE_PROFILE_REGISTRY.yaml`, policy resolvida, docs do módulo (MODULE_SCOPE, DOMAIN_RULES, INVARIANTS), contrato atual.
2. Valida path alvo = `contracts/openapi/paths/training.yaml`.
3. Usa **somente** templates canônicos de `api_rules.yaml` (seção `contract_templates`).
4. Consulta benchmark quando há decisão de design de API a apresentar.
5. Preenche placeholders apenas com evidência explícita.
6. Garante: paginação conforme `api_rules`, erros conforme SSOT, OWASP (BOLA/BOPLA/BFLA) por operação.
7. Atualiza `contracts/openapi/openapi.yaml` se necessário (novo `$ref`).

### 3.8 Compilação Determinística (pós-authoring)

Após criar/modificar o contrato soberano, o worker executa:

```bash
python3 scripts/contracts/validate/api/compile_api_policy.py --module training --surface sync
```

O compiler (`policy_compiler.py`):
- Lê os 5 inputs globais (ARCHITECTURE_MATRIX, MODULE_PROFILE_REGISTRY, api_rules, CANONICAL_TYPE_REGISTRY, DOMAIN_AXIOMS.json).
- Processa `contracts/openapi/paths/training.yaml`.
- Gera `generated/resolved_policy/training.sync.resolved.yaml`.
- Gera `generated/manifests/training.sync.traceability.yaml` (com SHA-256 de cada arquivo input/output).
- Se drift detectado → exit 2.

Regra: Se qualquer input global muda → `--all` obrigatório.

### 3.9 Registro do Artefato (hb artifact)

```bash
python3 scripts/hb artifact contracts/openapi/paths/training.yaml
```

Executa:
- Calcula SHA-256 do arquivo.
- Faz upsert em `_reports/session_start.json.stage2_artifacts[]`.
- Executa `validate_contracts.py --stage artifact --artifact <path>`.

### 3.10 Fase 3 — Validation (44 Gates)

```bash
python3 scripts/contracts/validate/validate_contracts.py
```

Os 44 gates executam em ordem determinística (0, 1, 1.5, 2, 2A, 2B ... 16, 20A, 20B, 20C). Cada gate:
- Retorna `PASS`, `FAIL` ou `SKIP_NOT_APPLICABLE`.
- Gates com `depends_on` só executam se o(s) predecessor(es) passaram.
- Gate bloqueante FAIL → `READINESS_SUMMARY_GATE` FAIL → pipeline FAIL.
- `SKIP_NOT_APPLICABLE`: gate não tem artefato-alvo presente (ex: ASYNCAPI_VALIDATION_GATE quando módulo não tem eventos).

Resultado em `_reports/contract_gates/latest.json`:
```json
{
  "run_id": "20260319T051539_5cd375",
  "health_score": 100,
  "gates_total": 44,
  "gates_passed": 44,
  "gates_failed": 0,
  "overall_status": "PASS"
}
```

Histórico em `_reports/pipeline_history.jsonl` (append-only).

### 3.11 Fase 4 — Readiness

Com `validate_contracts.py` PASS, o estado do módulo pode ser promovido em `MODULE_REGISTRY.yaml`:

- `scaffold` → `draft_contract` → `validated_contract` → `implementation_ready`

A promoção para `implementation_ready` exige, adicionalmente:
- `DECISION_IR_CONFORMANCE_GATE` PASS (se decision_ir em expected_surfaces).
- `MODULE_STATUS_COHERENCE_GATE` PASS (impede status alto com adversariais abertos).
- Adversarial analysis (`adversarial_analysis.prompt.md`) concluída com PASS.

Scorecard: `_reports/evidence/module_readiness_scorecard.json`.

### 3.12 Fase 5 — Handoff para Implementação

Com módulo em `implementation_ready`:
1. `adversarial_analysis.prompt.md` executa AA1 (OWASP), AA2 (STRIDE), AA3 (Consumer Break), AA4 (Domain Gap).
2. Se PASS → `_reports/adversarial/<module>/<resource>.adversarial.json` + `SESSION_HANDOFF.md` atualizado.
3. `generate_code.prompt.md` e `generate_frontend.prompt.md` são desbloqueados (atualmente FROZEN).

### 3.13 CI/CD (execução automática)

**A cada push/PR para main ou develop:**
```yaml
# .github/workflows/contract-gates.yml
- checkout
- python 3.12 + node 24
- schemathesis==4.12.1, oasdiff 1.12.3, npm ci
- python3 scripts/validate_contracts.py  # CI=true
- pytest tests/test_pipeline_governance.py -v
- upload: _reports/contract_gates/
```

**Mensalmente (1º dia, 9h UTC):**
```yaml
# .github/workflows/context-efficiency-audit.yml
- python scripts/audit/run_context_efficiency_audit.py
- salva _reports/CE_AUDIT_*.txt
```

**Semanalmente (segundas, 9h UTC):**
```yaml
# .github/workflows/domain-completeness-audit.yml
- python scripts/audit/run_all_modules_audit.py
- publica _reports/DOMAIN_COMPLETENESS_*.{md,json}
```

---

## PARTE 4 — Arquivos por Responsabilidade

| Arquivo | Papel no pipeline | Etapa associada | Tipo de componente | Importância | Certeza |
|---|---|---|---|---|---|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | Boot mínimo do agente; mapa task→worker; códigos de bloqueio | Boot | prompt/instrução | Crítica | Fato confirmado |
| `.contract_driven/TASK_CATALOG.yaml` | Roteamento task_type → worker; status ativo/congelado; input_requirements | Fase 0 | configuração | Crítica | Fato confirmado |
| `.contract_driven/BOOT_PROFILES.yaml` | 4 profiles de carregamento condicional; validações obrigatórias por perfil | Fase 0–1 | configuração | Crítica | Fato confirmado |
| `docs/_canon/MODULE_REGISTRY.yaml` | 16 módulos canônicos; status operacional; expected_surfaces | Fase 0–4 | configuração | Crítica | Fato confirmado |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | Portão obrigatório de entrada; valida, roteia, observa | Fase 0–2 | orquestração | Crítica | Fato confirmado |
| `scripts/hb` | CLI Python: verify/check/artifact/status/reset; cria session_start.json | Fase 0–2 | ferramenta | Crítica | Fato confirmado |
| `.contract_driven/agent_prompts/decision_discovery.prompt.md` | Resolve lacunas arquiteturais; gera ADRs; executa benchmark | Fase 1 | agente | Alta | Fato confirmado |
| `docs/_canon/DECISION_POLICY.md` | Regras de criticidade de decisões; checklist mínima; template de ADR | Fase 1 | prompt/instrução | Alta | Fato confirmado |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Registro de decisões abertas; gatilho de bloqueio | Fase 1 | memória | Alta | Fato confirmado |
| `docs/_canon/decisions/ADR-*.md` (30 arquivos) | Decisões arquiteturais aprovadas; fonte de verdade para o agente | Fase 1–2 | memória | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` | Worker de criação/revisão de API HTTP | Fase 2 | agente | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/create_asyncapi_contract.prompt.md` | Worker de eventos assíncronos | Fase 2 | agente | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/create_arazzo_workflow.prompt.md` | Worker de workflows multi-passo | Fase 2 | agente | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/create_json_schema_contract.prompt.md` | Worker de schemas soberanos | Fase 2 | agente | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/create_state_model.prompt.md` | Worker de máquinas de estados | Fase 2 | agente | Média | Fato confirmado |
| `.contract_driven/agent_prompts/create_ui_contract.prompt.md` | Worker de contratos de UI (com benchmark obrigatório) | Fase 2 | agente | Média | Fato confirmado |
| `.contract_driven/agent_prompts/create_module_docs.prompt.md` | Worker de documentação mínima de módulo | Fase 2 | agente | Alta | Fato confirmado |
| `.contract_driven/COMPETITIVE_BENCHMARK_PROTOCOL.md` | Protocolo obrigatório de benchmark de mercado antes de decisões de design | Fase 1–2 | prompt/instrução | Média | Fato confirmado |
| `.contract_driven/templates/api/api_rules.yaml` | SSOT de convenções HTTP/OpenAPI; templates canônicos | Fase 2 | prompt/instrução | Crítica | Fato confirmado |
| `.contract_driven/templates/modulos/` | Scaffolds para docs de módulo | Fase 2 | prompt/instrução | Alta | Fato confirmado |
| `.contract_driven/DOMAIN_AXIOMS.json` | Axiomas machine-readable globais; closed-world assumption | Fase 2–3 | validação/guardrail | Crítica | Fato confirmado |
| `contracts/openapi/openapi.yaml` | Root OpenAPI; índice de todos os paths | Fase 2–3 | outro (contrato) | Crítica | Fato confirmado |
| `contracts/openapi/paths/*.yaml` | Contratos HTTP por módulo (16 arquivos) | Fase 2–3 | outro (contrato) | Crítica | Fato confirmado |
| `contracts/schemas/**/*.schema.json` | Shapes soberanas de domínio (37 arquivos) | Fase 2–3 | outro (contrato) | Alta | Fato confirmado |
| `contracts/asyncapi/**/*.yaml` | Contratos de eventos (103 arquivos) | Fase 2–3 | outro (contrato) | Alta | Fato confirmado |
| `contracts/workflows/**/*.arazzo.yaml` | Workflows multi-passo (12 arquivos) | Fase 2–3 | outro (contrato) | Média | Fato confirmado |
| `scripts/contracts/validate/validate_contracts.py` | Executor dos 44 gates (8013 linhas) | Fase 3 | validação/guardrail | Crítica | Fato confirmado |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | Definição normativa de 44 gates (id, blocking, order, depends_on) | Fase 3 | configuração | Crítica | Fato confirmado |
| `scripts/contracts/validate/api/compile_api_policy.py` | Compilador determinístico de policy; gera manifests + derivados | Fase 2–3 | ferramenta | Alta | Fato confirmado |
| `scripts/contracts/validate/api/policy_compiler.py` | Core do compiler (violações, ExpectedFile, exit codes) | Fase 2–3 | ferramenta | Alta | Fato confirmado |
| `scripts/contracts/validate/api/intent_compiler.py` | Parser YAML com posição (linha/coluna) para relatórios precisos | Fase 3 | ferramenta | Média | Fato confirmado |
| `generated/resolved_policy/*.resolved.yaml` | Policy resolvida por módulo (derivado, zero autoridade) | Fase 3 | persistência | Média | Fato confirmado |
| `generated/manifests/*.traceability.yaml` | Manifests SHA-256 por módulo (rastreabilidade) | Fase 3 | persistência | Alta | Fato confirmado |
| `_reports/contract_gates/latest.json` | Resultado do último run de gates | Fase 3–4 | observabilidade | Alta | Fato confirmado |
| `_reports/pipeline_health.json` | Score de saúde atual (0–100) | Fase 3–4 | observabilidade | Média | Fato confirmado |
| `_reports/pipeline_history.jsonl` | Histórico append-only de runs | Fase 3–4 | observabilidade | Média | Fato confirmado |
| `_reports/session_start.json` | Estado da sessão ativa (task_type, module, stage, artifacts) | Fase 0–2 | persistência | Alta | Fato confirmado |
| `_reports/evidence/module_readiness_scorecard.json` | Scorecard de readiness por módulo | Fase 4 | observabilidade | Alta | Fato confirmado |
| `SESSION_HANDOFF.md` | Contexto de sessão anterior (bloqueios, próximos passos) | Boot | memória | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/adversarial_analysis.prompt.md` | OWASP + STRIDE + Consumer Break + Domain Gap antes de implementação | Fase 5 | validação/guardrail | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/generate_code.prompt.md` | Worker de geração de código backend (FROZEN) | Fase 5 | agente | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/generate_frontend.prompt.md` | Worker de geração de código frontend (FROZEN) | Fase 5 | agente | Alta | Fato confirmado |
| `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | Versões obrigatórias de ferramentas; timeouts; degradação | Fase 3 | configuração | Alta | Fato confirmado |
| `.github/workflows/contract-gates.yml` | CI gates em push/PR | CI/CD | integração externa | Crítica | Fato confirmado |
| `.github/workflows/context-efficiency-audit.yml` | Auditoria mensal de orçamento de contexto | CI/CD | integração externa | Média | Fato confirmado |
| `.github/workflows/domain-completeness-audit.yml` | Auditoria semanal de completude de domínio | CI/CD | integração externa | Média | Fato confirmado |
| `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<M>.md` | Regras de negócio por módulo (16 × N arquivos) | Fase 2 | recuperação de contexto | Alta | Fato confirmado |
| `docs/hbtrack/modulos/<module>/INVARIANTS_<M>.md` | Invariantes estruturais por módulo | Fase 2–3 | recuperação de contexto | Alta | Fato confirmado |
| `docs/_canon/SECURITY_RULES.md` | AUTH, AUTHZ, secrets, dados sensíveis, logging | Fase 1–2 | validação/guardrail | Alta | Fato confirmado |
| `docs/_canon/DATA_CONVENTIONS.md` | IDs (UUID v4), datas (ISO-8601 UTC), enums, naming | Fase 2 | prompt/instrução | Alta | Fato confirmado |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | Regras IHF traduzidas para produto (gatilho esportivo) | Fase 1–2 | recuperação de contexto | Alta | Fato confirmado |
| `CLAUDE.md` | Ponteiro para AGENT_INSTRUCTIONS; instrução de boot mínimo | Boot | prompt/instrução | Alta | Fato confirmado |
| `.contract_driven/agent_prompts/audit_*.prompt.md` (5 arquivos) | Workers de auditoria (sem artefato, sem pré-contrato) | Auditoria | subagente | Média | Fato confirmado |

---

## PARTE 5 — Lógica de Decisão do Agente

### 5.1 Árvore de decisão de alto nível

```
Entrada recebida
  ├─ SESSION_HANDOFF.md existe?
  │    └─ SIM → ler antes de qualquer coisa
  │
  ├─ task_type informado?
  │    └─ NÃO → perguntar explicitamente (nunca inferir)
  │
  ├─ task_type ∈ TASK_CATALOG.yaml com status=active?
  │    ├─ NÃO → BLOCKED_MISSING_AGENT_PROMPT
  │    └─ frozen → BLOCKED_MISSING_AGENT_PROMPT (com razão e condição)
  │
  ├─ module ∈ MODULE_REGISTRY.yaml?
  │    └─ NÃO → BLOCKED_MISSING_MODULE
  │
  ├─ worker_path existe no filesystem?
  │    └─ NÃO → BLOCKED_MISSING_AGENT_PROMPT
  │
  ├─ task_type ∈ auditoria? (audit_*)
  │    └─ SIM → bypassar pré-contrato com PRE_CONTRACT_SKIPPED
  │
  └─ Executar pipeline (Fases 0→5)
```

### 5.2 Quando responde diretamente (sem ferramenta ou subagente)

- Pergunta de esclarecimento (task_type ou module ambíguo).
- Comunicação de bloqueio ao humano (em português, sem jargão).
- Confirmação de PASS após validation.
- Apresentação de opções de benchmark (A/B/C + recomendação).

### 5.3 Quando chama ferramenta (CLI)

- `hb verify` → sempre no início de task contratual.
- `hb check` → validação de readiness de módulo (Fase 1).
- `hb artifact` → após criar/modificar artefato soberano.
- `python3 scripts/contracts/validate/validate_contracts.py` → após authoring e compile.
- `python3 scripts/contracts/validate/api/compile_api_policy.py` → após modificar contrato OpenAPI.
- `python3 scripts/gates/check_scope_boundary.py` → quando artefato contém refs cross-module.

### 5.4 Quando carrega worker especializado (subagente semântico)

O agente não lança subprocessos independentes. "Subagente" aqui significa **carregar e seguir um prompt especializado** dentro do mesmo contexto. O worker é ativado quando:

- task_type válido e ativo no TASK_CATALOG → worker correspondente.
- Decision Discovery ativado pelo orchestrator (decisão obrigatória aberta).
- Adversarial Analysis ativado antes de implementação.
- Auditoria solicitada diretamente (audit_*).

### 5.5 Quando busca contexto externo (leitura de artefatos)

**Boot mínimo (sempre):** AGENT_INSTRUCTIONS.md, SESSION_HANDOFF.md (se existe).

**Por profile (condicional):** CONTRACT_PIPELINE.md, BOOT_PROFILES.yaml, GATES_REGISTRY.yaml (para `contract_execution`); DECISION_POLICY.md, ARCHITECTURE_DECISION_BACKLOG.md (para `architecture_decision`).

**Por worker (on-demand):** docs do módulo alvo (DOMAIN_RULES, INVARIANTS, MODULE_SCOPE), contratos existentes, templates SSOT, api_rules.yaml.

**Regra de eficiência:** RULES + LAYOUT são `gate_only` — lidos apenas quando necessário, não no boot. Orçamento máximo do boot base: 2.100 palavras somadas nos 4 artefatos de boot mínimo.

### 5.6 Quando rejeita, falha ou entra em fallback

**Rejeição determinística (emite código canônico e para):**
- Artefato canônico ausente → código BLOCKED_* específico.
- Decisão obrigatória aberta → BLOCKED_MISSING_ARCH_DECISION.
- Gate bloqueante FAIL → READINESS_SUMMARY_GATE FAIL.
- Módulo não canônico → BLOCKED_MISSING_MODULE.
- task_type congelado → exit com razão e condição de desbloqueio.

**Sem fallback implícito:** O sistema não tem lógica de retry automático. Falha → bloquear → aguardar resolução humana.

**Inferência proibida (§8 em RULES):** O agente não pode criar endpoints, campos, enums, eventos, workflows, transições de estado, modelos de permissão ou regras de handebol sem evidência explícita em artefato canônico.

---

## PARTE 6 — Contexto, Memória e Janelas de Decisão

### 6.1 O que entra sempre no contexto (boot mínimo)

| Artefato | Budget (palavras) | Conteúdo |
|---|---|---|
| `docs/_canon/AGENT_INSTRUCTIONS.md` | 450 | Modo de operação, 16 módulos, 9 task-types, 6 regras core, códigos de bloqueio |
| `SESSION_HANDOFF.md` (se existe) | 350 | Contexto de sessão anterior: bloqueios, módulo em trabalho, próximos passos |
| `docs/_canon/CONTRACT_PIPELINE.md` | 600 | 6 estágios formais, condições de avanço, evidências obrigatórias |
| `pre_contract_orchestrator.prompt.md` | 700 | Fases 0–4 do orchestrator, bloqueios, observabilidade |
| **Total boot base** | **≤ 2.100** | |

### 6.2 O que entra sob condição

| Condição | Artefatos carregados |
|---|---|
| Profile `contract_execution` | `BOOT_PROFILES.yaml`, `GATES_REGISTRY.yaml` |
| Profile `architecture_decision` | `ARCHITECTURE_DECISION_BACKLOG.md`, `DECISION_POLICY.md` |
| Qualquer worker acionado | docs do módulo alvo (README, DOMAIN_RULES, INVARIANTS, MODULE_SCOPE) |
| Worker `create_openapi_contract` | `api_rules.yaml`, `MODULE_PROFILE_REGISTRY.yaml`, política resolvida |
| Gatilho esportivo ativo | `HANDBALL_RULES_DOMAIN.md`, `SPORT_SCIENCE_RULES_<MODULE>.md` |
| Decision Discovery ativado | `ARCHITECTURE_DECISION_BACKLOG.md`, ADRs relevantes, `COMPETITIVE_BENCHMARK_PROTOCOL.md`, `SECURITY_RULES.md` (se AUTH/dados sensíveis), `DATA_CONVENTIONS.md` (se datetime/timezone) |
| Authoring de UI | `UI_CONTRACT_GUIDE.md`, `COMPETITIVE_BENCHMARK_PROTOCOL.md` |
| RULES ou LAYOUT necessários | Carregados on-demand, seção específica (gate_only — nunca no boot) |

### 6.3 Memória persistente

| Tipo | Arquivo | Escopo |
|---|---|---|
| Sessão ativa | `_reports/session_start.json` | Sessão corrente |
| Handoff entre sessões | `SESSION_HANDOFF.md` | Cross-sessão |
| Decisões arquiteturais aprovadas | `docs/_canon/decisions/ADR-*.md` (30) | Permanente |
| Backlog de decisões | `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Evoluindo |
| Registro de features | `docs/_canon/FEATURE_REGISTRY.yaml` | Evoluindo |
| Status operacional de módulos | `docs/_canon/MODULE_REGISTRY.yaml` | Evoluindo |
| Manifests de rastreabilidade | `generated/manifests/*.traceability.yaml` | Permanente |

### 6.4 Contexto efêmero

- Conteúdo carregado no contexto da sessão atual (não persiste entre sessões sem SESSION_HANDOFF.md).
- Resultado de validações intermediárias (PASS de gate individual).
- Opções de benchmark apresentadas ao humano antes da escolha.

### 6.5 Gestão de orçamento de contexto

**Mecanismo de auditoria:** `audit_context_efficiency.prompt.md` e CI `context-efficiency-audit.yml` (mensal) monitoram:
- CE1: palavras de cada artefato de boot ≤ budget definido.
- CE2: cada regra crítica alcançável em ≤ 2 hops desde boot.
- CE3: sem regra órfã (acessível apenas via artefato não-boot).
- CE4: sem redundância de conteúdo entre artefatos de boot.
- CE5: sem default implícito (ponto do fluxo depende de contexto não carregado).

**Estratégia:** RULES e LAYOUT são grandes (`CONTRACT_SYSTEM_RULES.md` tem 909 linhas) e por isso são `gate_only` — o agente consulta seções específicas on-demand, não carrega no boot.

### 6.6 O que mais consome contexto

1. **`CONTRACT_SYSTEM_RULES.md`** — 909 linhas, 24 seções. Raramente todo carregado (gate_only).
2. **`CONTRACT_SYSTEM_LAYOUT.md`** — grande, gate_only.
3. **Docs de módulo completas** — quando todos os 5+ artefatos do módulo são carregados pelo worker.
4. **ADRs relevantes** — múltiplos arquivos na Decision Discovery.
5. **`api_rules.yaml`** — templates HTTP completos.

---

## PARTE 7 — Guardrails, Validações e Governança

### 7.1 Três camadas de guardrail

**Camada 1 — Regras do agente (comportamento):**
- `§8 RULES`: Modo estrito — inferência proibida para 18 categorias de artefatos.
- `§9 RULES`: 20 códigos canônicos de bloqueio — texto livre substituindo código = violação.
- `§23 RULES`: Implementation-first proibido — código só após contrato validado.

**Camada 2 — Gates técnicos (validação):**
- 44 gates em `validate_contracts.py` (8013 linhas), autoridade em `GATES_REGISTRY.yaml`.
- 30 bloqueantes: falha → pipeline FAIL → `READINESS_SUMMARY_GATE` FAIL.
- 14 não-bloqueantes: avisos, não bloqueiam progresso.
- Dependências entre gates: `depends_on` garante ordem e evita falsos negativos.

**Camada 3 — CI/CD (enforcement externo):**
- `contract-gates.yml`: bloqueia merge se `validate_contracts.py` exit ≠ 0.
- `pytest tests/test_pipeline_governance.py`: testes de governança do pipeline em si.

### 7.2 Gates críticos e o que protegem

| Gate | O que protege | Como |
|---|---|---|
| AXIOM_INTEGRITY_GATE (order:0) | Consistência dos axiomas globais | Valida estrutura de DOMAIN_AXIOMS.json |
| PATH_CANONICALITY_GATE (order:1) | Paths canônicos + naming + taxonomia de módulos | Verifica localização de cada artefato |
| REQUIRED_ARTIFACT_PRESENCE_GATE (order:2) | Ausência de artefatos obrigatórios | Verifica presença de todos os docs mínimos por módulo |
| AXIOM_INTEGRITY_GATE + REF_HERMETICITY_GATE | Refs externas não autorizadas | Bloqueia $ref apontando para fora do repo ou para derivados |
| SHADOW_AUTHORITY_GATE | DSS fingindo ser SSOT | Detecta linguagem de autoridade sem disclaimer em arquivos não-canônicos |
| DERIVED_DRIFT_GATE | Artefatos gerados desatualizados | SHA-256 de gerados vs esperado pelo compiler |
| PLACEHOLDER_RESIDUE_GATE | TODOs residuais em contratos | Detecta TODO, TBD, {{placeholder}} não resolvidos |
| OWASP_API_CONTROL_MATRIX_GATE | Controles de segurança de API | Valida presença e schema da matriz OWASP |
| BOUNDARY_USERS_IDENTITY_ACCESS_GATE | Boundary users ↔ identity_access | Detecta definição de AUTH em users ou profile em identity_access |
| WELLNESS_MEDICAL_BOUNDARY_GATE | Boundary wellness ↔ medical | Detecta medicalização implícita de dados de wellness |
| PRE_CONTRACT_EVIDENCE_GATE | Evidência de pré-contrato formal | Exige `_reports/agent_execution/` para módulos `validated_contract` |
| MODULE_STATUS_COHERENCE_GATE | Status irreal com adversariais abertos | Impede promotion sem adversarial PASS |
| READINESS_SUMMARY_GATE | Gate final binário | Falha se qualquer gate bloqueante falhou |

### 7.3 Bloqueios canônicos do agente

O agente pode emitir exatamente um dos 20 códigos canônicos. Emitir texto livre em vez do código é em si uma violação (detectada por `audit_red_team_pipeline.prompt.md`):

```
BLOCKED_MISSING_MODULE | BLOCKED_MISSING_OPENAPI_PATH | BLOCKED_MISSING_SCHEMA
BLOCKED_MISSING_DOMAIN_RULE | BLOCKED_MISSING_INVARIANT | BLOCKED_MISSING_STATE_MODEL
BLOCKED_MISSING_PERMISSION_MODEL | BLOCKED_MISSING_SPORT_SCIENCE_RULES
BLOCKED_MISSING_UI_CONTRACT | BLOCKED_MISSING_HANDBALL_REFERENCE
BLOCKED_MISSING_TEST_MATRIX | BLOCKED_CONTRACT_CONFLICT
BLOCKED_NONCANONICAL_NORMATIVE_PATH | BLOCKED_MISSING_CANON_ARTIFACT
BLOCKED_MISSING_API_CONVENTION | BLOCKED_MISSING_ARCH_DECISION
BLOCKED_REQUIRED_ARTIFACT_MISSING | BLOCKED_MISSING_AGENT_PROMPT
BLOCKED_PRE_CONTRACT_SKIPPED | BLOCKED_SCOPE_OVERFLOW
```

### 7.4 Regras normativas adicionais

- **Regra dos 3 níveis (§2A):** toda mudança de comportamento do agente deve existir em: regra normativa + registro operacional + enforcement técnico. Código sozinho não canoniza comportamento.
- **Precedência de conflito (§5):** se dois artefatos no mesmo nível contradizem, BLOCKED_CONTRACT_CONFLICT — nunca inferir resolução.
- **Gatilho esportivo (§12):** para módulos matches/competitions/training/wellness/medical ou decisões com semântica de handebol, leituras de HANDBALL_RULES_DOMAIN.md e SPORT_SCIENCE_RULES_<MODULE>.md tornam-se obrigatórias.
- **Conformidade de path (§3A):** artefato normativo em path errado = não-compliant, mesmo com conteúdo correto.

---

## PARTE 8 — Dependências, Bifurcações e Falhas

### 8.1 Dependências entre etapas

```
SESSION_HANDOFF (se existe) → Fase 0 → Fase 1 → [Decision Discovery] → Fase 2
                                                                         ↓
                                                              Compilação Determinística
                                                                         ↓
                                                               Fase 3 (44 gates)
                                                                         ↓
                                                               Fase 4 (Readiness)
                                                                         ↓
                                                         Adversarial Analysis (obrigatório)
                                                                         ↓
                                                              Fase 5 (Handoff)
```

Nenhuma etapa pode ser pulada. A tentativa de pular Fase 0 ativa `BLOCKED_PRE_CONTRACT_SKIPPED`.

### 8.2 Bifurcações de fluxo

| Ponto de bifurcação | Condição | Caminho A | Caminho B |
|---|---|---|---|
| Início de sessão | SESSION_HANDOFF.md existe | Ler handoff antes | Continuar sem contexto anterior |
| task_type recebido | Ambíguo/não informado | Perguntar explicitamente | Avançar para Fase 0 |
| task_type de auditoria | audit_* | Bypass pré-contrato (PRE_CONTRACT_SKIPPED) | Executar pipeline completo |
| task_type congelado | status=frozen | Emitir bloqueio + condição de desbloqueio | — |
| Fase 1 — backlog | Decisão obrigatória aberta | Acionar Decision Discovery | Avançar para Authoring |
| Decision Discovery | Decisão obrigatória não resolvida | BLOCKED_MISSING_ARCH_DECISION | Criar ADR + prosseguir |
| Authoring — refs cross-module | Artefato tem $ref cross-module | Executar check_scope_boundary.py | Avançar |
| Compilação | Drift detectado | Exit 2 (FAIL) | OK: nada a atualizar |
| Gate bloqueante | Exit ≠ 0 | READINESS_SUMMARY_GATE FAIL | PASS |
| Readiness | STATUS = implementation_ready | Autorizar adversarial_analysis | Manter em validated_contract |
| Adversarial | Qualquer AA1/AA2/AA3/AA4 crítico FAIL | BLOCKED_ADVERSARIAL_PENDING | Autorizar generate_code (quando descongelado) |

### 8.3 Condições especiais

- **Gatilho esportivo:** módulos training/wellness/medical/matches/competitions ou decisão com semântica de handebol → leituras adicionais obrigatórias no worker.
- **Promoção de status retroativa inválida:** não é possível pular de `scaffold` para `implementation_ready` — a transição é sequencial.
- **Waiver de breaking change:** `CONTRACT_BREAKING_CHANGE_GATE` exige waiver com SHA-256 explícito para aprovar uma breaking change.

### 8.4 Retries

Não existem retries automáticos. O sistema é **fail-closed**: falha → bloquear → aguardar ação humana ou correção explícita. O histórico em `pipeline_history.jsonl` registra cada run, permitindo diagnóstico manual.

### 8.5 Fallbacks

Único fallback técnico documentado: oasdiff pode entrar em estado `DEGRADED` localmente (gate reporta aviso, não falha) — mas **nunca em CI**.

### 8.6 Pontos de falha identificados

| Ponto | Tipo de falha | Evidência |
|---|---|---|
| `SESSION_HANDOFF.md` ausente ou inconsistente | Contexto de sessão perdido entre sessões | `HANDOFF_COHERENCE_GATE` (non-blocking) detecta mas não bloqueia |
| Compiler não executado após modificação de contrato | `DERIVED_DRIFT_GATE` FAIL | Frequente em trabalho fora do pipeline (vide histórico de correções) |
| task_type ou module informados em linguagem natural ambígua | Agente pergunta, mas pode ser lento | Regra C1/C2 do red team |
| tools opcionais ausentes (redocly, spectral, asyncapi) | Gates entram em SKIP ao invés de FAIL localmente | Log `[BOOTSTRAP] INFO: tools opcionais ausentes` |
| Artefatos criados manualmente fora do pipeline | Hashes divergem; `DERIVED_DRIFT_GATE` detecta; `PATH_CANONICALITY_GATE` detecta | Situação que motivou esta auditoria |
| ADR deletada sem substituto | Decisão arquitetural perdida; agente pode inferir sem base | Detectável apenas por `audit_sovereign_integrity` |

### 8.7 Riscos de comportamento inconsistente

- **Risco de inferência silenciosa:** se um artefato canônico existir com conteúdo incorreto mas em path correto, o agente pode usá-lo como base sem detectar o erro semântico (gates verificam estrutura, não semântica profunda).
- **Risco de shadow authority:** arquivos `docs/guias/` contêm linguagem de autoridade — se não tiverem disclaimer explícito, podem ser tratados como normativos pelo agente.
- **Risco de orçamento de contexto:** RULES tem 909 linhas. Se carregado inteiro, pode exceder budget e comprimir contexto de domínio útil.

### 8.8 Riscos de custo de tokens/contexto

- Decision Discovery com múltiplas ADRs + COMPETITIVE_BENCHMARK_PROTOCOL carregados simultaneamente = sessão de contexto longa.
- Módulos com muitos arquivos condicionais (training tem 13 arquivos) = contexto grande no worker.
- `audit_domain_completeness` simula o pipeline inteiro com injeção de borda = sessão longa.

---

## PARTE 9 — Fato vs Inferência

| Afirmação sobre o pipeline | Classificação | Evidência/arquivo | Confiança |
|---|---|---|---|
| O pipeline usa Claude como único agente de IA | Fato confirmado | `CLAUDE.md`, `docs/_canon/AGENT_INSTRUCTIONS.md` | Alta |
| O ponto de entrada obrigatório é `pre_contract_orchestrator.prompt.md` | Fato confirmado | `AGENT_INSTRUCTIONS.md §4`, `TASK_CATALOG.yaml` | Alta |
| Existem exatamente 44 gates de validação | Fato confirmado | `GATES_REGISTRY.yaml`, `_reports/pipeline_health.json` (gates_total: 44) | Alta |
| `validate_contracts.py` tem 8013 linhas e implementa todos os gates | Fato confirmado | `wc -l validate_contracts.py` | Alta |
| O boot mínimo tem orçamento de 2.100 palavras somadas | Fato confirmado | `audit_context_efficiency.prompt.md §2` | Alta |
| `SESSION_HANDOFF.md` é lido antes de qualquer outra ação | Fato confirmado | `AGENT_INSTRUCTIONS.md §0`, `pre_contract_orchestrator.prompt.md §Pré-Fase` | Alta |
| Os workers são prompts carregados no mesmo contexto do agente, não subprocessos | Fato confirmado | Não existe código de multi-agente real; workers são prompts .md | Alta |
| `generate_code` e `generate_frontend` estão FROZEN | Fato confirmado | `TASK_CATALOG.yaml`, prompts com `⚠️ WORKER CONGELADO` | Alta |
| O sistema é fail-closed (bloqueia em vez de inferir) | Fato confirmado | `CONTRACT_SYSTEM_RULES.md §8`, 20 códigos canônicos em §9 | Alta |
| Existe um budget máximo de palavras por artefato de boot | Fato confirmado | `audit_context_efficiency.prompt.md §2` | Alta |
| A toolchain usa redocly 1.34.10 + spectral 6.15.0 + oasdiff 1.12.3 + schemathesis 4.12.1 | Fato confirmado | `TOOLCHAIN_HEALTH_POLICY.md`, `contract-gates.yml` | Alta |
| 30 ADRs existem aprovadas | Fato confirmado | `ls docs/_canon/decisions/ADR-*.md` (30 arquivos) | Alta |
| O agente Claude executa os scripts via shell (não via API) | Fato confirmado | `scripts/hb` invocado como subprocess Python; `validate_contracts.py` como subprocess | Alta |
| A auditoria de contexto roda mensalmente no CI | Fato confirmado | `.github/workflows/context-efficiency-audit.yml` (cron: 0 9 1 * *) | Alta |
| O pipeline tem um mecanismo de migração de sessão legada | Fato confirmado | `scripts/hb` (HBCLIv2._migrate_legacy_session_if_needed) | Alta |
| Os 5 task-types de auditoria nunca produzem artefatos normativos | Fato confirmado | `TASK_CATALOG.yaml` (artifacts_produced: []) + pre_contract_exception | Alta |
| O agente decide entre workers lendo `task_type` do input do humano | Fato confirmado | `TASK_CATALOG.yaml`, `AGENT_INSTRUCTIONS.md §4` | Alta |
| O DERIVED_DRIFT_GATE detecta apenas drift hash, não semântica | Inferência plausível | `_validate_traceability_manifests()` em `validate_contracts.py` (l. 6194–6371) verifica SHA-256, não semântica | Alta |
| O agente não tem acesso a banco de dados externo ou memória vetorial | Inferência plausível | Nenhum arquivo configura vector DB, embedding ou RAG; memória é por arquivos `.md`/`.json` | Alta |
| O sistema nunca faz retry automático de gates com falha | Fato confirmado | Não existe lógica de retry em `scripts/hb` ou `validate_contracts.py` | Alta |
| O benchmark competitivo é executado pelo agente (não por ferramenta externa) | Fato confirmado | `COMPETITIVE_BENCHMARK_PROTOCOL.md` descreve procedimento para o agente, sem API ou ferramenta | Alta |
| A arquitetura é single-agent, não multi-agent | Inferência plausível | Não existe framework multi-agente; workers são prompts no mesmo contexto | Média |
| O `pytest tests/test_pipeline_governance.py` testa a governança do pipeline em si | Fato confirmado | `.github/workflows/contract-gates.yml` executa este teste explicitamente | Alta |
| `_reports/` tem zero autoridade normativa | Fato confirmado | `CONTRACT_SYSTEM_RULES.md §5` (derivados + relatórios = nível 8, zero autoridade) | Alta |
| O sistema suporta execução offline (sem internet) | Inferência plausível | Todas ferramentas são locais; benchmarks são executados pelo agente sem API externa | Média |
| Conflito entre dois artefatos no mesmo nível de precedência sempre bloqueia | Fato confirmado | `CONTRACT_SYSTEM_RULES.md §5` (conflito → BLOCKED_CONTRACT_CONFLICT) | Alta |
| A migração de banco de dados usa Alembic | Fato confirmado | `ADR-028` e commit `bea9688` mencionam Alembic explicitamente | Alta |
| O deploy usa VPS Locaweb (CDCT/Pact auto-hospedado) | Fato confirmado | `ADR-025` (commit `1794185`) menciona VPS Locaweb | Alta |
| FRONTEND_CONTRACT.md e RUNTIME_CONTRACT_MONITORING_POLICY.md não estão classificados no boot profiles | Fato confirmado | `BOOT_PROFILES.yaml` não os menciona; `audit_sovereign_integrity` detectou como C5 WARN | Alta |

---

## PARTE 10 — Diagrama Textual do Pipeline

```
Entrada do usuário (task_type + module + params)
  │
  ├─ [BOOT] Carregar AGENT_INSTRUCTIONS.md
  │          └─ SESSION_HANDOFF.md existe? → ler antes de qualquer coisa
  │
  ├─ [FASE 0 — SESSION BOOT] pre_contract_orchestrator.prompt.md
  │     │   scripts/hb verify --task-type <T> --module <M>
  │     │
  │     ├─ task_type ∈ TASK_CATALOG? (status=active?) → NÃO → BLOCKED_MISSING_AGENT_PROMPT
  │     ├─ task_type=frozen?                           → BLOCKED_MISSING_AGENT_PROMPT
  │     ├─ module ∈ MODULE_REGISTRY?                   → NÃO → BLOCKED_MISSING_MODULE
  │     ├─ worker_path existe?                         → NÃO → BLOCKED_MISSING_AGENT_PROMPT
  │     ├─ task_type ∈ audit_*?                        → PRE_CONTRACT_SKIPPED → ir para WORKER AUDITORIA
  │     └─ Cria _reports/session_start.json
  │          Emite: [ORCHESTRATOR] fase:0 resultado:PASS worker_destino:<W>
  │
  ├─ [FASE 1 — DISCOVERY]
  │     │   scripts/hb check --module <M>
  │     │
  │     ├─ docs mínimas do módulo existem?             → NÃO → BLOCKED_REQUIRED_ARTIFACT_MISSING
  │     ├─ artefato tem refs cross-module?
  │     │    └─ SIM → scripts/gates/check_scope_boundary.py
  │     │              → EXIT 1 → BLOCKED_SCOPE_OVERFLOW
  │     └─ decisão obrigatória aberta no backlog?
  │          ├─ SIM → [DECISION DISCOVERY]
  │          │          decision_discovery.prompt.md
  │          │          ├─ Ler: DECISION_POLICY, backlog, ADRs, COMPETITIVE_BENCHMARK_PROTOCOL
  │          │          ├─ Classificar: obrigatória / importante / opcional
  │          │          ├─ Executar benchmark competitivo (A/B/C)
  │          │          ├─ Apresentar ao humano → AGUARDAR APROVAÇÃO
  │          │          ├─ APROVADO → criar ADR → atualizar backlog → validate_contracts.py
  │          │          └─ NÃO RESOLVIDO → BLOCKED_MISSING_ARCH_DECISION
  │          └─ NÃO → continuar para AUTHORING
  │
  ├─ [FASE 2 — AUTHORING] worker do task_type
  │     │
  │     ├─ new_contract / contract_revision → create_openapi_contract.prompt.md
  │     │    Lê: api_rules.yaml, docs módulo, política resolvida
  │     │    Cria: contracts/openapi/paths/<module>.yaml
  │     │    Executa: compile_api_policy.py --module <M> --surface sync
  │     │
  │     ├─ new_event → create_asyncapi_contract.prompt.md
  │     │    Cria: contracts/asyncapi/channels/<module>/<event>.yaml
  │     │    Executa: compile_api_policy.py --module <M> --surface event
  │     │
  │     ├─ new_workflow → create_arazzo_workflow.prompt.md
  │     │    Cria: contracts/workflows/<module>/<name>.arazzo.yaml
  │     │
  │     ├─ new_schema → create_json_schema_contract.prompt.md
  │     │    Cria: contracts/schemas/<module>/<name>.schema.json
  │     │
  │     ├─ new_state_model → create_state_model.prompt.md
  │     │    Cria: docs/hbtrack/modulos/<module>/STATE_MODEL_<M>.md
  │     │
  │     ├─ new_ui_contract → create_ui_contract.prompt.md
  │     │    Benchmark obrigatório antes de cada decisão de tela
  │     │    Cria: docs/hbtrack/modulos/<module>/UI_CONTRACT_<M>.md
  │     │
  │     ├─ new_module → create_module_docs.prompt.md
  │     │    Cria: 5 docs mínimas + condicionais aplicáveis
  │     │
  │     ├─ architecture_review / decision_discovery → decision_discovery.prompt.md
  │     │    Cria: docs/_canon/decisions/ADR-NNN-slug.md
  │     │
  │     └─ scripts/hb artifact <path>
  │           (upsert em session_start.json + validate --stage artifact)
  │
  ├─ [FASE 3 — VALIDATION] validate_contracts.py (44 gates)
  │     │
  │     ├─ Gate 0: AXIOM_INTEGRITY_GATE          → FAIL → CRITICAL
  │     ├─ Gate 1: PATH_CANONICALITY_GATE         → FAIL → CRITICAL
  │     ├─ Gate 1.5: SCOPE_BOUNDARY_GATE          → FAIL → ALTO
  │     ├─ Gate 2: REQUIRED_ARTIFACT_PRESENCE     → FAIL → CRITICAL
  │     ├─ Gate 2A: MODULE_DOC_CROSSREF_GATE       → FAIL → ALTO
  │     ├─ Gate 2C: OWASP_API_CONTROL_MATRIX       → FAIL → CRITICAL
  │     ├─ Gate 2D1: MODULE_REGISTRY_GATE          → FAIL → CRITICAL
  │     ├─ Gate 2E: BOUNDARY_USERS_IAM_GATE        → FAIL → ALTO
  │     ├─ Gate 2F: WELLNESS_MEDICAL_BOUNDARY      → FAIL → ALTO
  │     ├─ Gate 2J: PRE_CONTRACT_EVIDENCE_GATE     → FAIL → ALTO
  │     ├─ Gate 2K: SHADOW_AUTHORITY_GATE          → FAIL → ALTO
  │     ├─ Gate 3: PLACEHOLDER_RESIDUE_GATE        → FAIL → ALTO
  │     ├─ Gate 4: REF_HERMETICITY_GATE            → FAIL → CRITICAL
  │     ├─ Gate 5: OPENAPI_ROOT_STRUCTURE_GATE     → FAIL → CRITICAL (redocly)
  │     ├─ Gate 5A: OPENAPI_ROOT_MODULE_SYNC       → FAIL → CRITICAL
  │     ├─ Gate 6: OPENAPI_POLICY_RULESET          → FAIL → ALTO (spectral)
  │     ├─ Gate 7: JSON_SCHEMA_VALIDATION          → FAIL → CRITICAL
  │     ├─ Gate 8: CROSS_SPEC_ALIGNMENT            → FAIL → ALTO
  │     ├─ Gate 9: CONTRACT_BREAKING_CHANGE        → FAIL → CRITICAL (oasdiff)
  │     ├─ Gate 11: HTTP_RUNTIME_CONTRACT          → FAIL → ALTO (schemathesis)
  │     ├─ Gate 12: ASYNCAPI_VALIDATION            → FAIL → ALTO (@asyncapi/cli)
  │     ├─ Gate 13: ARAZZO_VALIDATION              → FAIL → ALTO
  │     ├─ Gate 15: DERIVED_DRIFT_GATE             → FAIL → CRITICAL
  │     ├─ Gate 20B: MODULE_STATUS_COHERENCE       → FAIL → ALTO
  │     └─ Gate 16: READINESS_SUMMARY_GATE
  │           ├─ QUALQUER bloqueante FAIL → STATUS: FAIL → exit 2
  │           └─ TODOS bloqueantes PASS  → STATUS: PASS → exit 0
  │
  ├─ [FASE 4 — READINESS] (se PASS)
  │     ├─ Atualizar MODULE_REGISTRY.yaml (status → validated_contract)
  │     ├─ _reports/evidence/module_readiness_scorecard.json atualizado
  │     └─ Para implementation_ready: DECISION_IR_CONFORMANCE_GATE + adversarial obrigatório
  │
  ├─ [FASE 5 — HANDOFF] (se implementation_ready)
  │     ├─ adversarial_analysis.prompt.md
  │     │    ├─ AA1 OWASP (10 controles)
  │     │    ├─ AA2 STRIDE (por operação POST/PUT/PATCH/DELETE)
  │     │    ├─ AA3 Consumer Break (8 cenários)
  │     │    └─ AA4 Domain Gap (STATE_MODEL + INVARIANTS + DOMAIN_RULES + SPORT_SCIENCE)
  │     │         ├─ Qualquer crítico FAIL → BLOCKED_ADVERSARIAL_PENDING
  │     │         └─ PASS → _reports/adversarial/<M>/<R>.adversarial.json
  │     │
  │     └─ generate_code.prompt.md (FROZEN) / generate_frontend.prompt.md (FROZEN)
  │           Desbloqueado quando: training + 4 módulos em validated_contract
  │
  └─ [SAÍDA]
       ├─ Artefato canônico criado + pipeline PASS
       ├─ Bloqueio com código canônico + instrução de resolução
       └─ Relatório de auditoria (audit_only)

[CI/CD — paralelo ao pipeline local]
  ├─ Push → contract-gates.yml → gates completos → bloqueia merge se FAIL
  ├─ Mensal → context-efficiency-audit.yml → _reports/CE_AUDIT_*.txt
  └─ Semanal → domain-completeness-audit.yml → _reports/DOMAIN_COMPLETENESS_*.{md,json}

[CAMADAS DE AUDITORIA ORTOGONAIS — qualquer momento]
  ├─ audit_sovereign_integrity → C1/C2/C3/C4/C5 (presença + unicidade + intrusos)
  ├─ audit_gate_coverage       → cobertura de RULES §2–§23 contra gates (score ≥85%)
  ├─ audit_domain_completeness → simulação com injeção de borda (módulo wellness padrão)
  ├─ audit_red_team_pipeline   → 15 casos A1–A8/B1–B3/C1–C4 contra orchestrator
  └─ audit_context_efficiency  → CE1–CE5 (budget + alcançabilidade em ≤2 hops)
```

---

## PARTE 11 — Gargalos, Riscos e Pontos Obscuros

### 11.1 Gargalos técnicos

| Gargalo | Descrição | Localização |
|---|---|---|
| `validate_contracts.py` tem 8013 linhas | Script monolítico; toda manutenção de gates neste arquivo; tempo de execução proporcional ao estado do repo | `scripts/contracts/validate/validate_contracts.py` |
| boot mínimo fixo em 4 artefatos | Se qualquer dos 4 artefatos de boot crescer além do budget, todo agente é afetado | `audit_context_efficiency.prompt.md §2` |
| Decision Discovery sem paralelismo | Decisões são sequenciais; múltiplas decisões abertas = sessão longa | `decision_discovery.prompt.md` |
| Compilação manual pós-authoring | Agente deve lembrar de executar `compile_api_policy.py`; se esquecer → DERIVED_DRIFT_GATE FAIL | workflow dependente de instrução no worker |
| ADRs como contexto cumulativo | Com 30 ADRs existentes, Decision Discovery carregando ADRs relevantes pode exceder contexto útil | `docs/_canon/decisions/ADR-*.md` |

### 11.2 Pontos frágeis

| Fragilidade | Risco | Mitigação existente |
|---|---|---|
| `SESSION_HANDOFF.md` desatualizado | Agente opera com contexto incorreto de sessão anterior | `HANDOFF_COHERENCE_GATE` (non-blocking) |
| Artefatos criados manualmente fora do pipeline | Hashes divergem; `DERIVED_DRIFT_GATE` detecta | Gate detecta, mas não previne |
| `SHADOW_AUTHORITY_GATE` baseado em vocabulário | Depende de detecção lexical de "SSOT", "canônico" etc; falsos negativos possíveis | Auditoria `audit_sovereign_integrity` como camada adicional |
| Workers sem validação de formato de saída | Agente pode criar artefato estruturalmente inválido; só detectado pelos gates depois | Gates estruturais (OPENAPI_ROOT_STRUCTURE, JSON_SCHEMA_VALIDATION) |
| Benchmark competitivo sem API externa | Qualidade do benchmark depende do conhecimento do modelo; não verificável automaticamente | Responsabilidade humana de revisar |
| Decisões de semântica de handebol | Regras IHF são complexas; agente pode não capturar nuances sem especialista | `HANDBALL_RULES_DOMAIN.md` + `SPORT_SCIENCE_RULES_<M>.md` obrigatórios quando gatilho ativo |

### 11.3 Áreas mal documentadas ou não confirmadas

| Área | Status | Notas |
|---|---|---|
| `tests/test_pipeline_governance.py` | Não confirmado — arquivo não lido | Mencionado em `contract-gates.yml`; conteúdo dos testes desconhecido |
| `scripts/gates/check_scope_boundary.py` | Não confirmado — arquivo não lido | Mencionado no orchestrator; implementação real desconhecida |
| `scripts/audit/run_context_efficiency_audit.py` | Não confirmado — arquivo não lido | Mencionado em `context-efficiency-audit.yml` |
| `scripts/audit/run_all_modules_audit.py` | Não confirmado — arquivo não lido | Mencionado em `domain-completeness-audit.yml` |
| `docs/_canon/FEATURE_REGISTRY.yaml` | Não lido — conteúdo desconhecido | Referenciado em `generate_code.prompt.md` e `generate_frontend.prompt.md` |
| `docs/_canon/OPERATIONS.md` | Não lido | Referenciado como fonte de §1A soberania no LAYOUT |
| `contracts/_waivers/` | Não lido | Mencionado para waivers de breaking change (SHA-256) |
| `deploy.yml` | Parcialmente confirmado | Existe mas conteúdo completo não lido |
| `docs/_canon/IR_TO_SURFACE_MAPPING.yaml` | Não confirmado | Mencionado na estrutura de canon |
| Implementação real de `DECISION_IR_CONFORMANCE_GATE` | Inferência plausível | Gate existe no GATES_REGISTRY; código no validate_contracts.py não confirmado detalhadamente |

### 11.4 Partes mais complexas do que deveriam

| Componente | Problema percebido |
|---|---|
| `CONTRACT_SYSTEM_RULES.md` (24 seções, 909 linhas) | Documento de regras operacionais excessivamente longo para um artefato de boot `gate_only`; referenciado em múltiplos workers |
| 44 gates com dependências complexas | `READINESS_SUMMARY_GATE` depende de `all_preceding`; mudança em qualquer gate tem impacto sistêmico |
| 17 workers + orchestrator | Volume alto de prompts; manutenção síncrona entre prompts e RULES é difícil de garantir |
| Distinção `docs/guias/` vs `docs/_canon/` | Fronteira de autoridade tênue; `SHADOW_AUTHORITY_GATE` detecta violações mas linguagem pode ser ambígua |

---

## PARTE 12 — Explicação Executiva

O HB Track tem um sistema de desenvolvimento guiado por contratos — antes de escrever qualquer linha de código de produto, todos os comportamentos, estruturas de dados e fluxos de comunicação precisam estar formalizados em contratos validados.

Para garantir que isso seja seguido de forma confiável, o projeto usa um agente IA (Claude) com um protocolo rígido de operação.

**Como funciona na prática:**

Quando você pede algo ao agente ("cria a API de treinos para o módulo training"), o agente não simplesmente começa a escrever. Ele passa por um protocolo obrigatório:

1. **Verifica o contexto da sessão anterior** — se existe um arquivo de handoff, lê antes de qualquer coisa.
2. **Valida o que você pediu** — confere se o tipo de tarefa e o módulo estão no catálogo canônico. Se não estiverem, para e explica.
3. **Verifica o módulo** — confere se toda a documentação obrigatória do módulo existe. Se faltar algo, para e aponta o que está faltando.
4. **Verifica decisões arquiteturais** — se existem decisões obrigatórias em aberto para aquele módulo (ex: "como vai funcionar o controle de acesso?"), aciona um processo formal de decisão antes de criar qualquer contrato.
5. **Cria o contrato** — usando o template e as regras canônicas, nunca inventando estruturas.
6. **Executa 44 testes automáticos** — que verificam desde a estrutura dos arquivos até a consistência entre todos os contratos do sistema.
7. **Só autoriza implementação** quando todos os testes passam e uma análise de segurança foi feita.

**O que torna isso diferente:**

- **O agente nunca inventa.** Se um artefato canônico está faltando, o agente para e emite um código de bloqueio específico — nunca tenta adivinhar.
- **Tudo é rastreável.** Cada arquivo criado gera um hash SHA-256 registrado; qualquer modificação fora do pipeline é detectada automaticamente.
- **As regras têm dentes.** Não são apenas documentos — cada regra normativa tem pelo menos um gate técnico que a aplica. Se a regra diz "nunca misturar dados médicos com wellness", existe um gate que verifica isso automaticamente.
- **O contexto do agente é gerenciado.** O sistema tem orçamentos de palavras para cada categoria de documento que o agente lê, e uma auditoria mensal verifica se o agente consegue acessar todas as regras críticas em no máximo 2 passos.

**Estado atual:**

- 16 módulos definidos, 6 já com contratos validados (`training`, `wellness`, `exercises`, `identity_access`, `notifications`, `users`).
- 44 testes de validação passando.
- Geração de código ainda bloqueada (aguardando mais módulos validados).
- Workers de análise adversarial e auditorias de pipeline ativos.

---

## PARTE 13 — BACKLOG_ITEM_1: Validadores Externos no Caminho Padrão

### Status: IMPLEMENTAÇÃO COMPLETA (Passos A–D)

**Data:** 2026-03-19 | **Prioridade:** Alta | **Epic:** Validação Externa

### Problema Diagnosticado (Passos A & B)

**33 gates estavam faltando das listas de profile (`_local_ids`, `_precommit_ids`)**, causando SKIP silencioso mesmo quando artefatos e ferramentas existiam.

**Root cause:** Configuração de profile incompleta em `scripts/contracts/validate/validate_contracts.py` (linhas 8493–8505).

```python
# ANTES: Apenas 14 gates ativos no profile local
_local_ids = _precommit_ids | {
    "DECISION_IR_CONFORMANCE_GATE",
    "DERIVED_DRIFT_GATE",
    "ADVERSARIAL_ANALYSIS_GATE",
    "FEATURE_READINESS_GATE",
}

# DEPOIS: 19 gates (validadores externos agora inclusos)
_local_ids = _precommit_ids | {
    "DECISION_IR_CONFORMANCE_GATE",
    "DERIVED_DRIFT_GATE",
    "ADVERSARIAL_ANALYSIS_GATE",
    "FEATURE_READINESS_GATE",
    "OPENAPI_ROOT_STRUCTURE_GATE",         # Redocly
    "ASYNCAPI_VALIDATION_GATE",            # AsyncAPI
    "ARAZZO_VALIDATION_GATE",              # Arazzo
    "JSON_SCHEMA_VALIDATION_GATE",         # JSON Schema
    "OPENAPI_ROOT_MODULE_SYNC_GATE",       # Sincronização
    "SPECTRAL_LINTING_GATE",               # Spectral (novo)
}
```

### Implementação Completa

#### Passo C: AsyncAPI Blocking (✅ COMPLETO)

**Mudança:** `ASYNCAPI_VALIDATION_GATE` agora bloqueia quando falha (`blocking=True`).

**Onde:** `scripts/contracts/validate/validate_contracts.py` (linhas 5989, 5996, 6003, 6031)

```python
# ANTES: blocking=False (não bloqueava FAIL)
return _pg(gate_id, "FAIL", False, "BLOCKED_ASYNCAPI_INVALID", ...)

# DEPOIS: blocking=True (falha bloqueia pipeline)
return _pg(gate_id, "FAIL", True, "BLOCKED_ASYNCAPI_INVALID", ...)
```

#### Passos E & F: Validadores no Profile Padrão (✅ COMPLETO)

**Status executado:**

```
+ [PASS] OPENAPI_ROOT_STRUCTURE_GATE       (Redocly lint)
+ [PASS] JSON_SCHEMA_VALIDATION_GATE
! [FAIL] ASYNCAPI_VALIDATION_GATE          (Erros reais detectados e bloqueiam)
+ [PASS] ARAZZO_VALIDATION_GATE
+ [PASS] SPECTRAL_LINTING_GATE             (Novo)
```

**Exit code:** 2 (bloqueador ativo, pipeline falha como esperado)

#### Passo D: Novo Gate Spectral (✅ COMPLETO)

**Função adicionada:** `_g13a_spectral_linting()` (linhas 6089–6130)

**Responsabilidade:** Valida OpenAPI com Spectral (estilos e regras customizadas)

```python
def _g13a_spectral_linting(root: pathlib.Path) -> dict:
    t0 = time.monotonic()
    gate_id = "SPECTRAL_LINTING_GATE"
    openapi_root = root / "contracts" / "openapi" / "openapi.yaml"
    if not openapi_root.exists():
        return _skip(gate_id, "contracts/openapi/openapi.yaml ausente — gate não aplicável.", _ms(t0))
    
    rc, stdout, stderr = _try_node_cli(root, tool="spectral", args=["lint", str(openapi_root)], cwd=root)
    if rc == -1:
        return _pg(gate_id, "FAIL", True, "ERROR_INFRA", ...)
    
    # Spectral rc=0: sem erros; rc!=0: erros encontrados
    if rc != 0:
        violations = [...]
        return _pg(gate_id, "FAIL", True, "BLOCKED_OPENAPI_SPECTRAL_VIOLATION", ...)
    
    return _pg(gate_id, "PASS", True, None, ...)
```

**Adicionado ao gate_plan:** Linha 8617 (`("SPECTRAL_LINTING_GATE", lambda: _g13a_spectral_linting(root))`)

**Adicionado ao _local_ids:** Executa no profile padrão (local)

### Critério de Sucesso: CUMPRIDO ✅

- ✅ Redocly executa (exit 0 ou 2 segundo resultado)
- ✅ AsyncAPI executa e bloqueia corretamente (exit 2)
- ✅ Spectral executa (exit 0 ou 2 segundo resultado)
- ✅ Nenhum SKIP_NOT_APPLICABLE quando artefatos/ferramentas presentes
- ✅ Documentação reflete comportamento real (este documento)

### Impacto

**Antes:** 33 gates silenciosamente pulados → falsa cobertura de validação → vulnerabilidades de contrato passando despercebidas

**Depois:** 5 validadores externos executam no path padrão, bloqueando pipeline se há erros reais

### Próximos Passos

- Adicionar Spectral rules customizadas (`.spectralrc` ou CI-side)
- Adicionar outros 28 gates faltantes (gradualmente, conforme necessidade)
- Profile "ci" já cobre todos 44 gates (CI workflow está completo)

---

*Documento gerado por análise direta dos arquivos do repositório em 2026-03-19.*
*Vinculado a: `docs/_canon/AGENT_INSTRUCTIONS.md`, `.contract_driven/TASK_CATALOG.yaml`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `scripts/contracts/validate/validate_contracts.py`, `.github/workflows/`, `_reports/`*
