# CHECKLIST EXECUTIVO — VERIFICAÇÃO OPERACIONAL DO HB Track

## 1. Objetivo

Ele responde a uma pergunta única:

**O sistema contract-driven do HB Track está operacional de forma verificável, determinística e reexecutável no ambiente-alvo?**

---

## 2. Taxonomia canônica de status

Use apenas estes quatro status:

- **PASS**  
  Critério: requisito comprovado por evidência executável, atual, no ambiente-alvo, sem restrições materiais.

- **PASS_COM_RESTRICAO**  
  Critério: requisito comprovado apenas parcialmente, ou comprovado em ambiente diferente do ambiente-alvo, ou dependente de limitação operacional ainda não sanada.

- **FAIL**  
  Critério: requisito aplicável e não atendido, ou atendido de forma insuficiente para uso operacional, ou há evidência objetiva de falha.

- **NAO_COMPROVADO**  
  Critério: não há evidência suficiente para decidir. Não equivale a PASS.

### Regra obrigatória de interpretação

- Existência de arquivo **não** prova operação.
- Gate existente **não** prova enforcement real do agente.
- PASS obtido em ambiente diferente do ambiente-alvo gera, no máximo, **PASS_COM_RESTRICAO**.
- Na presença de evidência conflitante entre ambientes, prevalece o status mais conservador para a decisão global.
- Se o item é necessário para prontidão operacional e ainda está em `FAIL` ou `NAO_COMPROVADO`, a decisão global não pode ser `PASS`.

---

## 3. Regra de Ambiente-Alvo

### Ambiente-alvo atual para decisão operacional
- **WSL / Linux**
---

## 4. Checklist Executivo

## 4.1 Premissas e decisões de governança

| Item | Status | Evidência / decisão |
|---|---|---|
| Contrato antes do código aceito | PASS | Decisão explícita no checklist original |
| Trilogia canônica aceita como autoridade | PASS | `CONTRACT_SYSTEM_LAYOUT.md`, `CONTRACT_SYSTEM_RULES.md`, `GLOBAL_TEMPLATES.md` aceitos |
| `api_rules.yaml` aceito como SSOT HTTP API | PASS | Canonical + origem preservada para compatibilidade |
| Taxonomia canônica dos 16 módulos aceita | PASS | Decisão explícita |
| Strict mode: bloquear em vez de inferir | PASS | Decisão explícita |
| Boot mínimo por tarefa aceito | PASS | Decisão explícita |
| DoD binário para contrato e módulo aceito | PASS | Decisão explícita |

### Status do bloco
**PASS**

---

## 4.2 Artefatos canônicos presentes no repositório

### 4.2.1 Núcleo contract-driven

| Item | Status | Evidência |
|---|---|---|
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | PASS | Arquivo presente |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | PASS | Arquivo presente |
| `.contract_driven/GLOBAL_TEMPLATES.md` | PASS | Arquivo presente |
| `.contract_driven/templates/api/api_rules.yaml` | PASS | Arquivo presente e apontado como SSOT |
| `.contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml` | PASS | Arquivo presente |
| `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` | PASS | Arquivo presente |
| `.contract_driven/DOMAIN_AXIOMS.json` | PASS | Arquivo presente |
| `contracts/schemas/shared/domain_axioms_module.schema.json` | PASS | Arquivo presente |
| `docs/hbtrack/modulos/README.md` | PASS | Arquivo presente |

### 4.2.2 Canon global

| Item | Status |
|---|---|
| `docs/_canon/README.md` | PASS |
| `docs/_canon/SYSTEM_SCOPE.md` | PASS |
| `docs/_canon/ARCHITECTURE.md` | PASS |
| `docs/_canon/MODULE_MAP.md` | PASS |
| `docs/_canon/CHANGE_POLICY.md` | PASS |
| `docs/_canon/API_CONVENTIONS.md` | PASS |
| `docs/_canon/DATA_CONVENTIONS.md` | PASS |
| `docs/_canon/ERROR_MODEL.md` | PASS |
| `docs/_canon/GLOBAL_INVARIANTS.md` | PASS |
| `docs/_canon/DOMAIN_GLOSSARY.md` | PASS |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | PASS |
| `docs/_canon/SECURITY_RULES.md` | PASS |
| `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml` | PASS |
| `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | PASS |
| `docs/_canon/CI_CONTRACT_GATES.md` | PASS |
| `docs/_canon/TEST_STRATEGY.md` | PASS |
| `docs/_canon/C4_CONTEXT.md` | PASS |
| `docs/_canon/C4_CONTAINERS.md` | PASS |
| `docs/_canon/UI_FOUNDATIONS.md` | PASS |
| `docs/_canon/DESIGN_SYSTEM.md` | PASS |

### Status do bloco
**PASS**

---

## 4.3 Estrutura real de contratos no repositório

### 4.3.1 Estrutura-base

| Item | Status | Evidência |
|---|---|---|
| `contracts/openapi/openapi.yaml` existe | PASS | Confirmado em `latest.json` `PLACEHOLDER_RESIDUE_GATE` artifacts_checked (2026-03-14) |
| `contracts/openapi/paths/` contém os 16 módulos canônicos | PASS | 16 paths (ai_ingestion..wellness) visíveis em `PLACEHOLDER_RESIDUE_GATE` artifacts_checked |
| `contracts/openapi/intents/` existe | PASS | `contracts/openapi/intents/README.md` e `ai_ingestion.intent.yaml` confirmados |
| `contracts/schemas/` existe | PASS | `JSON_SCHEMA_VALIDATION_GATE` → PASS, 5 schemas verificados |
| `contracts/workflows/` existe | PASS | `ARAZZO_VALIDATION_GATE` → PASS, 1 arquivo válido |
| `contracts/asyncapi/` existe | PASS | `ASYNCAPI_VALIDATION_GATE` → PASS |
| READMEs das árvores contratuais existem | PASS | `REQUIRED_ARTIFACT_PRESENCE_GATE` → PASS (140 artefatos) |
| Árvore segue layout canônico | PASS | `PATH_CANONICALITY_GATE` → PASS, `latest.json` 2026-03-14 |
| Não há contratos fora da árvore canônica | PASS | `PATH_CANONICALITY_GATE` + `REF_HERMETICITY_GATE` → PASS |
| Não há módulos fora da taxonomia | PASS | `PATH_CANONICALITY_GATE` + `MODULE_DOC_CROSSREF_GATE` → PASS |

### 4.3.2 Prompts e aderência dos prompts

| Item | Status | Evidência |
|---|---|---|
| Prompt de docs de módulo existe | PASS | `.contract_driven/agent_prompts/create_module_docs.prompt.md` presente (ls WSL 2026-03-14) |
| Prompt de OpenAPI existe | PASS | `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` presente |
| Prompt de state model existe | PASS | `.contract_driven/agent_prompts/create_state_model.prompt.md` presente |
| Prompt de UI contract existe | PASS | `.contract_driven/agent_prompts/create_ui_contract.prompt.md` presente |
| Prompt de AsyncAPI existe | FAIL | Ausente em `.contract_driven/agent_prompts/` (ls 2026-03-14 confirma 4 prompts, nenhum AsyncAPI) |
| Prompt de Arazzo existe | FAIL | Ausente em `.contract_driven/agent_prompts/` (ls 2026-03-14 confirma 4 prompts, nenhum Arazzo) |
| Alinhamento prompt ↔ templates ↔ rules | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ artefatos de módulo | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ domínio do handebol | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ convenções API/dados | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ segurança | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ change policy | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ test strategy | NAO_COMPROVADO | Sem evidência de validação executável |
| Alinhamento prompt ↔ governança/layout/validação/extensão modular | NAO_COMPROVADO | Sem evidência de validação executável |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.4 Ferramentas instaladas no ambiente-alvo

| Item | Status | Evidência |
|---|---|---|
| `node` disponível no PATH | PASS | `node --version` → v24.14.0 (nvm, /home/davis/.nvm/versions/node/v24.14.0/bin/node), WSL 2026-03-14 |
| Redocly CLI instalado e utilizável | PASS_COM_RESTRICAO | Disponível via `npx redocly` (1.34.10 local node_modules) + global Windows npm (2.21.0 usada pelo pipeline); `OPENAPI_ROOT_STRUCTURE_GATE` → PASS |
| Spectral instalado e utilizável | PASS_COM_RESTRICAO | Disponível via `npx spectral` (6.15.0 local node_modules); `OPENAPI_POLICY_RULESET_GATE` → PASS |
| `oasdiff` no PATH | PASS | Binário nativo em `/home/davis/bin/oasdiff`; `oasdiff --version` → "oasdiff version main", WSL 2026-03-14 |
| `schemathesis` no PATH | FAIL | `which schemathesis` → não encontrado; tool_versions.schemathesis = "command not found" em latest.json |
| `ajv` instalado e utilizável | PASS | Binário em `/home/davis/bin/ajv`; `ajv help` → funcional, WSL 2026-03-14 |
| AsyncAPI validator/parser utilizável | PASS_COM_RESTRICAO | Disponível via `npx asyncapi` (@asyncapi/cli/6.0.0 local); `ASYNCAPI_VALIDATION_GATE` → PASS |
| Validator/linter Arazzo | PASS | Python-based; `ARAZZO_VALIDATION_GATE` → PASS (latest.json 2026-03-14) |
| Storybook disponível, se aplicável | NAO_COMPROVADO | `UI_DOC_VALIDATION_GATE` → SKIP_NOT_APPLICABLE; nenhum UI_CONTRACT_*.md encontrado |
| Intent compiler disponível | PASS | Executa; `DERIVED_DRIFT_GATE` → PASS (latest.json 2026-03-14) |
| Policy compiler disponível | PASS | Executa; `compile_api_policy.py` referenciado em RULES seção 15 |
| Ferramentas de geração de artefatos configuradas e testadas | PASS_COM_RESTRICAO | `TRANSFORMATION_FEASIBILITY_GATE` → SKIP_NOT_APPLICABLE (contracts/generated/ ausente); pipeline principal PASS |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.5 Ferramentas funcionando de verdade

### Leitura executiva

A cadeia completa de validação rodou com sucesso no ambiente-alvo (WSL) em 2026-03-15T08:42:07Z, produzindo `overall_status: PASS` com 24 gates PASS e 3 SKIP_NOT_APPLICABLE. Node.js (nvm), redocly (local), spectral (local) e asyncapi (local) funcionam via WSL-native node. Oasdiff nativo disponível. _tool_ver() com timeout=10s (fix 2026-03-15): tool_versions no relatório são null para ferramentas Windows (interop WSL desativado), mas os gates PASS via _try_node_cli. Schemathesis ausente (runtime testing bloqueado). DECISION_IR_CONFORMANCE_GATE adicionado ao pipeline: PASS.

| Item | Status | Evidência |
|---|---|---|
| Validadores/compilers Python centrais executam | PASS | `latest.json` 2026-03-15T08:42:07Z: `AXIOM_INTEGRITY_GATE`, `CROSS_SPEC_ALIGNMENT_GATE`, `DERIVED_DRIFT_GATE` → PASS |
| Intent compiler processa casos válidos e inválidos | PASS | `DERIVED_DRIFT_GATE` → PASS; compiler determinístico referenciado em RULES seção 15 |
| Policy compiler detecta drift semântico | PASS | `DERIVED_DRIFT_GATE` → PASS; "generated/ alinhado ao compiler determinístico (sem drift)" |
| Cadeia OpenAPI dependente de Node roda no WSL | PASS | `OPENAPI_ROOT_STRUCTURE_GATE` → PASS ("redocly lint: nenhum erro", 1548ms); `OPENAPI_POLICY_RULESET_GATE` → PASS ("spectral: PASS, 0 avisos", 1066ms) |
| Cadeia AsyncAPI dependente de Node roda no WSL | PASS | `ASYNCAPI_VALIDATION_GATE` → PASS ("asyncapi validate: PASS", 1776ms) |
| Toolchain completo roda de ponta a ponta no ambiente-alvo | PASS | `python3 scripts/validate_contracts.py` → `overall_status: PASS`, exit_code: 0, 2026-03-15T08:42:07Z no WSL |

### Status do bloco
**PASS**

---

## 4.6 Enforcement real

### 4.6.1 Enforcement comprovado

| Item | Status | Evidência |
|---|---|---|
| Script/comando único para validar contratos | PASS | `python3 scripts/validate_contracts.py` → PASS, 2026-03-15T08:42:07Z, WSL |
| Rotina de falha para contrato inválido | PASS | `OPENAPI_ROOT_STRUCTURE_GATE` e `OPENAPI_POLICY_RULESET_GATE` são bloqueantes; códigos `BLOCKED_ENUM_OUTSIDE_AXIOMS`, `BLOCKED_FORMAT_VIOLATION`, etc. definidos em `validate_contracts.py` |
| Validador consome `DOMAIN_AXIOMS.json` explicitamente | PASS | `AXIOM_INTEGRITY_GATE` → input explícito: `.contract_driven/DOMAIN_AXIOMS.json`; PASS 2026-03-14 |
| Rotina de falha para breaking change | PASS_COM_RESTRICAO | `CONTRACT_BREAKING_CHANGE_GATE` → PASS; mas usa fallback interno ("nenhuma operação removida"), não oasdiff diretamente. Oasdiff binário disponível mas não detectado pelo pipeline |
| Rotina de falha para drift fonte soberana ↔ derivado | PASS | `DERIVED_DRIFT_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para placeholder residual | PASS | `PLACEHOLDER_RESIDUE_GATE` → PASS (43 arquivos verificados), 2026-03-14 |
| Rotina de falha para artefato obrigatório ausente | PASS | `REQUIRED_ARTIFACT_PRESENCE_GATE` → PASS (140 artefatos verificados), 2026-03-14 |
| Rotina de falha para matriz OWASP | PASS | `OWASP_API_CONTROL_MATRIX_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para matriz de autoridade/fonte | PASS | `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para boundary `users` vs `identity_access` | PASS | `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para boundary `wellness` vs `medical` | PASS | `WELLNESS_MEDICAL_BOUNDARY_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para taxonomia de scout sem artefato canônico | PASS | `SCOUT_TAXONOMY_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para módulo que exige async/workflow sem artefatos | PASS | `ASYNC_REQUIRED_MODULE_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de falha para benchmark tratado como SSOT | PASS | `EXTERNAL_SOURCE_AUTHORITY_GATE` → PASS, bloqueante, 2026-03-14 |
| Rotina de validação de IR de módulo | PASS | `DECISION_IR_CONFORMANCE_GATE` → PASS, bloqueante, 2026-03-15; `MODULE_DECISION_IR.json` (training) promovido: 0 violações |

### 4.6.2 Enforcement não fechado

| Item | Status | Evidência |
|---|---|---|
| Rotina de falha para crossref módulo ↔ contrato | PASS | `MODULE_DOC_CROSSREF_GATE` → PASS, bloqueante; headers e cross-references de docs de módulo OK, 2026-03-14 |
| Rotina de falha para alinhamento artefato de módulo ↔ contrato/implementação | NAO_COMPROVADO | `HTTP_RUNTIME_CONTRACT_GATE` → SKIP_NOT_APPLICABLE (requer servidor live); sem gate de parity contract↔impl |
| Rotina de falha para alinhamento com domínio do handebol | NAO_COMPROVADO | Não há gate automático que valide aderência semântica ao domínio de handebol |
| Rotina de falha para violação de regra de domínio na implementação | NAO_COMPROVADO | Sem testes fechados de regra de negócio em impl real |
| Rotina de falha para violação de invariantes na implementação | NAO_COMPROVADO | Sem testes fechados de invariantes em impl real |
| Rotina de falha quando agente improvisa | NAO_COMPROVADO | RULES seções 8 e 9 definem o protocolo, mas não há log de execução real do agente |
| Rotina de falha quando agente cria módulo/path/evento/workflow/regra fora da autoridade | NAO_COMPROVADO | Gates existem (PATH_CANONICALITY, etc.) mas não há log de comportamento real do agente |
| Rotina de falha para edição manual de gerados | NAO_COMPROVADO | `DERIVED_DRIFT_GATE` PASS para o estado atual, mas não há evidência de que a regra foi testada em violação deliberada |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.7 Artefatos gerados

| Item | Status | Evidência |
|---|---|---|
| Pasta canônica de gerados existe (`generated/`) | PASS | `generated/README.md` confirmado em `REQUIRED_ARTIFACT_PRESENCE_GATE` (140 artefatos) |
| Tipos/políticas/manifests vão para essa pasta | PASS | `DERIVED_DRIFT_GATE` → PASS; "generated/ alinhado ao compiler determinístico (sem drift)" |
| Clientes gerados vão sempre para essa pasta | NAO_COMPROVADO | `TRANSFORMATION_FEASIBILITY_GATE` → SKIP_NOT_APPLICABLE ("contracts/generated/ ausente"); clientes ainda não gerados |
| Docs geradas vão sempre para essa pasta | NAO_COMPROVADO | Nenhuma evidência de docs geradas em `generated/docs/` |
| Artefatos gerados não são editados manualmente | NAO_COMPROVADO | `DERIVED_DRIFT_GATE` PASS para estado atual, mas nenhum teste de violação deliberada |
| Artefatos gerados são regeneráveis | PASS | Compiler determinístico confirmado; `DERIVED_DRIFT_GATE` verifica regeneração |
| Drift entre gerado e soberano é detectável | PASS | `DERIVED_DRIFT_GATE` (bloqueante) → PASS, 2026-03-14 |
| Há rotina de falha para drift entre gerado e soberano | PASS | `DERIVED_DRIFT_GATE` bloqueante confirmado |
| Gerados alinhados com domínio do handebol | NAO_COMPROVADO | Sem gate/teste específico de alinhamento semântico handball ↔ gerados |
| Gerados alinhados com regras de domínio documentadas | NAO_COMPROVADO | Sem teste fechado confirmando aderência |
| Gerados alinhados com invariantes documentadas | NAO_COMPROVADO | Sem teste fechado confirmando aderência |

### Status do bloco
**PASS_COM_RESTRICAO**

---

## 4.8 Agente / fluxo operacional

### Leitura executiva

A governança define o fluxo esperado do agente com precisão (boot order, modos, matriz de tarefa), mas **não existe log executável de comportamento real** do agente seguindo esses protocolos. Todos os itens permanecem NAO_COMPROVADO por falta de evidência de execução real.

| Item | Status |
|---|---|
| Agente usa a ordem de boot definida | NAO_COMPROVADO |
| Agente usa boot mínimo por tarefa | NAO_COMPROVADO |
| Agente bloqueia em lacuna crítica | NAO_COMPROVADO |
| Agente emite códigos de bloqueio fechados | NAO_COMPROVADO |
| Agente não cria módulo fora da taxonomia | NAO_COMPROVADO |
| Agente não cria path fora de contrato | NAO_COMPROVADO |
| Agente não cria evento fora de AsyncAPI | NAO_COMPROVADO |
| Agente não cria workflow sem Arazzo | NAO_COMPROVADO |
| Agente não cria regra esportiva fora do domínio documentado | NAO_COMPROVADO |
| Agente não edita gerado manualmente | NAO_COMPROVADO |
| Agente gera artefato correto quando o prompt é seguido | NAO_COMPROVADO |
| Agente bloqueia quando o prompt é seguido incorretamente | NAO_COMPROVADO |
| Agente gera artefato alinhado com domínio/regras/invariantes | NAO_COMPROVADO |

### Status do bloco
**NAO_COMPROVADO**

---

## 4.9 Domínio do handebol

| Item | Status | Evidência |
|---|---|---|
| `HANDBALL_RULES_DOMAIN.md` existe | PASS | Arquivo presente em `docs/_canon/` — confirmado em `API_NORMATIVE_DUPLICATION_GATE` artifacts_checked, 2026-03-14 |
| Cobre impacto em `training` | PASS | `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md` linkado; `CROSS_SPEC_ALIGNMENT_GATE` cobrindo todos módulos |
| Cobre impacto em `matches` | PASS | `docs/hbtrack/modulos/matches/DOMAIN_RULES_MATCHES.md` presente; `MODULE_DOC_CROSSREF_GATE` PASS |
| Cobre impacto em `scout` | PASS | `docs/hbtrack/modulos/scout/DOMAIN_RULES_SCOUT.md` presente; `SCOUT_TAXONOMY_GATE` PASS |
| Cobre impacto em `competitions` | PASS | `docs/hbtrack/modulos/competitions/DOMAIN_RULES_COMPETITIONS.md` presente; `CROSS_SPEC_ALIGNMENT_GATE` PASS |
| Adaptações locais do produto estão registradas | NAO_COMPROVADO | Sem prova suficiente |
| Não há regra crítica fora do documento | NAO_COMPROVADO | Sem prova suficiente |
| Agente bloqueia tentativa de criar regra esportiva fora do documento | NAO_COMPROVADO | Sem logs executáveis |
| Contratos refletem o domínio documentado | NAO_COMPROVADO | Gate de alinhamento ainda não fechado |
| Implementação real respeita o domínio documentado | NAO_COMPROVADO | Sem teste fechado |
| Não há lacunas críticas entre domínio documentado e implementação real | NAO_COMPROVADO | Sem teste fechado |
| Domínio documentado é suficiente para features críticas | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de contratos | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de artefatos de módulo | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para criação de testes automatizados | NAO_COMPROVADO | Sem prova executável |
| Domínio documentado é suficiente para geração de artefatos | NAO_COMPROVADO | Sem prova executável |

### Status do bloco
**PASS_COM_RESTRICAO**

Racional: existe base documental relevante, mas a suficiência operacional do domínio ainda não foi provada.

---

## 4.10 Módulo real piloto: `training`

| Item | Status | Evidência |
|---|---|---|
| `README` | PASS | `docs/hbtrack/modulos/training/README.md` presente; `MODULE_DOC_CROSSREF_GATE` PASS |
| `MODULE_SCOPE` | PASS | `docs/hbtrack/modulos/training/MODULE_SCOPE_TRAINING.md` presente |
| `DOMAIN_RULES` | PASS | `docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md` presente |
| `INVARIANTS` | PASS | `docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md` presente |
| `TEST_MATRIX` | PASS | `docs/hbtrack/modulos/training/TEST_MATRIX_TRAINING.md` presente |
| OpenAPI path | PASS | `contracts/openapi/paths/training.yaml` presente; `OPENAPI_ROOT_STRUCTURE_GATE` PASS |
| Schemas | PASS | `contracts/schemas/training/training_session.schema.json` validado; `JSON_SCHEMA_VALIDATION_GATE` PASS |
| `STATE_MODEL`, se aplicável | FAIL | **APLICÁVEL** por RULES 11.1: INV-TRAIN-006 documenta 5 estados persistidos (`draft`, `scheduled`, `in_progress`, `pending_review`, `readonly`); INVARIANTS nota de workflow DRAFT→PLANNED→SCHEDULED→IN_PROGRESS→COMPLETED→CANCELLED (divergência documentada em LAC-001); INV-TRAIN-004: aprovação/revisão por papel. `STATE_MODEL_TRAINING.md` ausente → FAIL por RULES 11.8 |
| `PERMISSIONS`, se aplicável | FAIL | **APLICÁVEL** por RULES 11.2: DR-TRAIN-001 (RBAC local: apenas Treinador/Coordenador criam sessões); INV-TRAIN-004 (capability diferenciada: Autor edita até 10min vs. Superior até 24h); INV-TRAIN-016 (attendance: restrição de visibilidade). `PERMISSIONS_TRAINING.md` ausente → FAIL por RULES 11.8 |
| `ERRORS`, se aplicável | FAIL | **APLICÁVEL** por RULES 11.3: DR-TRAIN-002/003/004/005/006/007 + INV-TRAIN-001–021 documentam múltiplas falhas de regra de negócio com semântica própria (soma de foco > 120, janela temporal wellness_pre/post, sessão histórica somente leitura, desvio de planejamento). `ERRORS_TRAINING.md` ausente → FAIL por RULES 11.8 |
| `UI_CONTRACT`, se aplicável | FAIL | **APLICÁVEL** por RULES 11.4: sistema tem SPA Next.js 13+ (README stack); training é módulo core com formulários de usuário (criação de sessão, submissão de wellness, marcação de assiduidade, export de analytics). `UI_CONTRACT_TRAINING.md` ausente → FAIL; criar antes de qualquer implementação de UI deste módulo |
| `SCREEN_MAP`, se aplicável | FAIL | **APLICÁVEL** por RULES 11.5: múltiplas telas user-facing esperadas (lista de sessões, detalhes, assiduidade, wellness, analytics); INV-TRAIN-015 documenta endpoints analytics distintos (summary/weekly-load/deviation-analysis); Arazzo workflow multi-step implica fluxo de navegação. `SCREEN_MAP_TRAINING.md` ausente → FAIL; criar antes de qualquer implementação de UI |
| Arazzo, se aplicável | PASS | `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml`; `ARAZZO_VALIDATION_GATE` PASS |
| AsyncAPI, se aplicável | PASS | `contracts/asyncapi/channels/training_attendance_marked.yaml`; `ASYNCAPI_VALIDATION_GATE` PASS |
| `MODULE_DECISION_IR.json` | PASS | `.dev/MODULE_DECISION_IR.json` — `DECISION_IR_CONFORMANCE_GATE` PASS (2026-03-15T08:42:07Z); 0 violações; 13 entidades com campos obrigatórios; OD-TRAIN-004 resolvido |
| Estado operacional do piloto em WSL | PASS | `latest.json` 2026-03-15T08:42:07Z: `overall_status: PASS`; training verificado em `CROSS_SPEC_ALIGNMENT_GATE` e `MODULE_DOC_CROSSREF_GATE` |

### Status do bloco
**FAIL**

Racional: 5 artefatos condicionais confirmados **APLICÁVEIS** por RULES 11 e **AUSENTES** (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP). Artefatos sempre-obrigatórios e contratos (OpenAPI, AsyncAPI, Arazzo, schema) estão todos PASS. O módulo não satisfaz o DoD definido em CONTRACT_SYSTEM_RULES.md seção 17 enquanto esses artefatos estiverem ausentes.

---

## 4.11 Prontidão real

| Item | Status | Evidência |
|---|---|---|
| Existe pelo menos 1 contrato validado ponta a ponta no ambiente-alvo | PASS | `python3 scripts/validate_contracts.py` → `overall_status: PASS`, exit_code: 0, 24 gates PASS, 3 SKIP_NOT_APPLICABLE; WSL, 2026-03-15T08:42:07Z |

### Status do bloco
**PASS**

---

# 5. PRONTIDÃO DE GOVERNANCA CONTRACT-DRIVEN
  
### 5.0 Objetivo da seção

Esta seção verifica se a governança do sistema está suficientemente definida para que um agente consiga:

* ler a base normativa correta;
* distinguir regra, template, exemplo, evidência e artefato derivado;
* identificar o que existe e o que falta;
* marcar a checklist com evidência verificável;
* propor as próximas tarefas corretas;
* bloquear progressão quando houver lacunas normativas críticas;
* liberar a produção de contratos, implementação e testes sem inferência indevida.

### 5.0.1 Regra de decisão desta seção

A seção 5 não mede apenas presença de arquivos.
Ela mede se a governança está operacionalmente apta para suportar um fluxo contract-driven executável por agente.

### 5.0.2 Status permitido

Cada item desta seção deve usar exclusivamente um dos quatro status canônicos do documento:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

### 5.0.3 Regra de marcação

Um item desta seção só pode ser marcado como `PASS` quando houver, simultaneamente:

* fonte normativa identificada;
* critério de uso explícito pelo agente;
* evidência verificável no repositório ou no fluxo;
* ausência de ambiguidade material para a decisão correspondente.

Presença de arquivo, menção documental ou intenção declarada não bastam, por si só, para `PASS`.

### 5.0.4 Regra de impacto

Se qualquer item crítico desta seção estiver em `FAIL`, a governança contract-driven deve ser considerada **não pronta** para liberação plena da fase correspondente.

Se qualquer item crítico desta seção estiver em `NAO_COMPROVADO`, a governança contract-driven deve ser considerada **não pronta para decisão positiva** sem evidência adicional.

### 5.0.5 Itens críticos desta seção

São itens críticos desta seção:

* `5.1.1`
* `5.1.3`
* `5.2.2`
* `5.2.3`
* `5.3.1`
* `5.3.3`
* `5.4.1`
* `5.5.5`
* `5.6.3`
* `5.6.5`
* `5.7.1`
* `5.7.4`

### 5.0.6 Saída obrigatória do agente ao auditar esta seção

Para cada item auditado, o agente deve registrar:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

### 5.0.7 Regra de integração com a decisão global

A seção 5 mede prontidão de governança, não prontidão operacional plena do sistema.

Portanto:

* `PASS` na seção 5 libera a fase de produção contratual, desde que não haja bloqueio explícito em outra seção;
* `FAIL` ou `NAO_COMPROVADO` em item crítico da seção 5 impede liberação da fase contratual;
* `PASS` na seção 5 não implica, por si só, `PASS` no `STATUS GLOBAL` do sistema.

---

### 5.1 Autoridade normativa e precedência

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1.1 Matriz de precedência normativa definida | PASS | `CONTRACT_SYSTEM_RULES.md` seção 5 define hierarquia explícita de 13 níveis (LAYOUT > RULES > api_rules > contratos técnicos > handball domain > ... > implementação > gerados); conflitos entre níveis resolvíveis deterministicamente | — | — | — | Já satisfeito: hierarquia de 13 níveis explícita, sem ambiguidade |
| 5.1.2 Classificação canônica dos artefatos | PASS | `CONTRACT_SYSTEM_LAYOUT.md` seção 1A define tabela única: Governança, Templates (scaffold), SSOT API, Canon global, Docs módulo, OpenAPI, Schemas, Workflows, Eventos — com coluna "Soberano?" e "Template SSOT" | — | — | — | Já satisfeito: tabela de classificação com papel de cada classe |
| 5.1.3 Autoridade por tipo de decisão | PASS | `CONTRACT_SYSTEM_RULES.md` seção 13 mapeia explicitamente cada superfície (HTTP interface, shapes, orchestration, events, business rules, integrity, state, permissions, UI, navigation) → arquivo de autoridade primária | — | — | — | Já satisfeito: mapa decisão→fonte coberto na seção 13 |
| 5.1.4 Ausência de precedência circular | PASS | Hierarquia de 13 níveis é acíclica: vai de LAYOUT/RULES (mais alto) a derivados (mais baixo). Templates são scaffolds, não normativos. Nenhum ciclo identificado na leitura completa dos 3 SSOTs | — | — | — | Já satisfeito: nenhuma circularidade detectada |

#### Critérios normativos do bloco 5.1

**5.1.1 Matriz de precedência normativa definida**
Critério:

* existe regra explícita de precedência entre canon global, regras modulares, layout, templates, contratos humanos, contratos formais, evidências e artefatos derivados;
* conflitos entre arquivos podem ser resolvidos sem interpretação subjetiva do agente.

Evidência esperada:

* documento canônico de precedência ou seção equivalente claramente vinculada ao canon.

**5.1.2 Classificação canônica dos artefatos**
Critério:

* está explícito o que é:

  * regra normativa,
  * template,
  * exemplo,
  * evidência,
  * artefato derivado,
  * artefato promovível,
  * artefato descartável;
* o agente não precisa inferir o papel de cada arquivo.

Evidência esperada:

* taxonomia documental ou matriz de classificação vinculada ao sistema.

**5.1.3 Autoridade por tipo de decisão**
Critério:

* para cada decisão relevante, existe fonte de autoridade explícita, por exemplo:

  * arquitetura do módulo,
  * contrato humano,
  * contrato OpenAPI/AsyncAPI/Arazzo,
  * tipo canônico,
  * política de segurança,
  * política de inferência,
  * política de promoção.

Evidência esperada:

* matriz `decisão → arquivo/fonte mandatória`.

**5.1.4 Ausência de precedência circular**
Critério:

* não existe ciclo onde plano operacional, gate, template ou checklist dependem circularmente uns dos outros para validar autoridade normativa.

Evidência esperada:

* revisão explícita ou estrutura documental que elimine circularidade.

---

### 5.2 Limites de inferência do agente

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.2.1 Política explícita de inferência permitida | PASS_COM_RESTRICAO | `CONTRACT_SYSTEM_RULES.md` seção 8 define o que NÃO pode ser inferido (16 categorias); o que pode ser inferido é tudo que tenha respaldo em contrato/doc. Não existe lista positiva explícita de "permitido inferir X". | Lista positiva de inferência permitida ausente — apenas inverso negativo | Baixo (pode-se deduzir pelo complemento) | Adicionar seção explícita "inferência permitida" em RULES ou GLOBAL_TEMPLATES | Lista positiva de inferências explicitamente permitidas definida em SSOT |
| 5.2.2 Política explícita de inferência proibida | PASS | `CONTRACT_SYSTEM_RULES.md` seção 8 (Modo estrito) lista explicitamente: módulos, endpoints/paths, fields estáveis, enums estáveis, eventos, workflows, transições de estado, modelos de permissão, erros domain-specific, comportamento de UI, regras de handebol, integrações externas, operações assíncronas + "Artefato ausente => bloquear" | — | — | — | Já satisfeito: 16 categorias proibidas explicitamente |
| 5.2.3 Regra de bloqueio por lacuna normativa | PASS | `CONTRACT_SYSTEM_RULES.md` seção 9 lista 15 códigos de bloqueio (`BLOCKED_MISSING_*`, `BLOCKED_CONTRACT_CONFLICT`, etc.) + seção 8 "Artefato ausente => bloquear" + seção 11.8 "emitir código de bloqueio correspondente e parar o trabalho afetado" | — | — | — | Já satisfeito: regra explícita + formato de saída (código) |
| 5.2.4 Regra de escalonamento de lacunas | PASS_COM_RESTRICAO | Bloqueio é definido (seção 9); mas o protocolo de escalação (quando vira pergunta ao humano vs. pendência vs. impede geração) não está explicitamente definido em nível de processo nos SSOTs | Protocolo de escalação pós-bloqueio indisponível | Médio: agente pode bloquear mas não saber próximo passo | Adicionar protocolo de escalação em RULES seção 9 | Protocolo de escalação explícito com 3 desfechos (pergunta, pendência, bloqueio de fase) |

#### Critérios normativos do bloco 5.2

**5.2.1 Política explícita de inferência permitida**
Critério:

* existe definição normativa do que o agente pode inferir sem input humano adicional.

Evidência esperada:

* documento, seção ou matriz de inferência permitida.

**5.2.2 Política explícita de inferência proibida**
Critério:

* existe definição normativa do que o agente não pode inferir, incluindo pelo menos:

  * campos obrigatórios normativos,
  * estados de negócio,
  * eventos de domínio,
  * regras de segurança,
  * retenção,
  * workflows críticos,
  * integrações externas,
  * boundaries entre módulos.

Evidência esperada:

* documento, seção ou matriz de não inferência.

**5.2.3 Regra de bloqueio por lacuna normativa**
Critério:

* quando faltar informação normativa obrigatória, o agente deve bloquear progressão e registrar lacuna, em vez de improvisar.

Evidência esperada:

* regra explícita de bloqueio e formato de saída do bloqueio.

**5.2.4 Regra de escalonamento de lacunas**
Critério:

* está definido quando a lacuna:

  * vira pergunta ao humano,
  * vira pendência normativa,
  * vira tarefa de criação de artefato,
  * impede geração contratual.

Evidência esperada:

* protocolo de tratamento de lacunas.

---

### 5.3 Fluxo canônico de produção contract-driven

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.3.1 Sequência obrigatória de produção definida | PASS | `CONTRACT_SYSTEM_RULES.md` seção 15 define 8 passos obrigatórios (seleção módulo → OpenAPI → schemas → docs → avaliação condicional → validação → testes → implementação); seções 16-18 definem DoD binário para contrato, módulo e módulo guiado por IA | — | — | — | Já satisfeito: fluxo de 8 passos + DoD |
| 5.3.2 Critério de entrada para criação de contrato humano | PASS_COM_RESTRICAO | Agent prompts existem (4 em `.contract_driven/agent_prompts/`); RULES seção 21.1 define `boot obrigatório` e `boot condicional` por tipo de tarefa; mas o "input mínimo necessário para criar contrato humano por módulo" não está explícito como critério de entrada numa tabela objetiva | Critério formal de entrada pré-contrato humano (input mínimo) não especificado | Médio: agente pode iniciar com insumos insuficientes | Documentar checklist de entrada mínima por superfície contratual | Critério explícito: quais docs/decisões devem existir antes de criar contrato humano |
| 5.3.3 Critério de promoção de contrato humano para contrato formal | PASS | `CONTRACT_SYSTEM_RULES.md` seção 16 define DoD binário de contrato: 11 condições explícitas incluindo "OpenAPI passa em Redocly CLI e Spectral", "zero TODOs/TBDs", "referência explícita a DOMAIN_RULES, INVARIANTS, TEST_MATRIX" — critério objetivo para promoção | — | — | — | Já satisfeito: 11 condições mensuráveis definidas |
| 5.3.4 Critério de liberação para implementação | PASS | `CONTRACT_SYSTEM_RULES.md` seção 17 (Módulo DoD): 6 condições + seção 18 adiciona 8 condições para módulo guiado por IA | — | — | — | Já satisfeito: DoD de módulo com condições binárias |
| 5.3.5 Critério de liberação para testes e validação | PASS_COM_RESTRICAO | `TEST_MATRIX_<MODULE>.md` obrigatório (seção 10.1) cobre API, schema, regra, invariante e estado; mas não há gate específico de "readiness para testes" como fase separada — está embarcado no DoD de módulo | Fase de "test readiness" não explicitada como gate separado | Baixo (está no DoD, apenas não como gate separado) | Criar gate `TEST_READINESS_GATE` ou seccionar DoD em fases | Fase de teste definida com critério de entrada explícito separado do DoD de módulo |

#### Critérios normativos do bloco 5.3

**5.3.1 Sequência obrigatória de produção definida**
Critério:

* existe fluxo normativo explícito, no mínimo cobrindo:

  * checklist,
  * contrato humano,
  * contrato formal,
  * gates,
  * implementação,
  * testes,
  * evidência,
  * promoção.

Evidência esperada:

* fluxograma, playbook ou contrato operacional canônico.

**5.3.2 Critério de entrada para criação de contrato humano**
Critério:

* existe definição clara do input mínimo necessário para o agente criar contrato humano por módulo.

Evidência esperada:

* template ou especificação de entrada mínima.

**5.3.3 Critério de promoção de contrato humano para contrato formal**
Critério:

* está definido quando um contrato humano pode virar OpenAPI, AsyncAPI, Arazzo ou equivalente.

Evidência esperada:

* regra de promoção com pré-condições objetivas.

**5.3.4 Critério de liberação para implementação**
Critério:

* está definido quais artefatos e gates precisam estar válidos antes da implementação.

Evidência esperada:

* checklist de entrada de implementação ou política equivalente.

**5.3.5 Critério de liberação para testes e validação**
Critério:

* está definido quando o sistema já pode gerar testes, validar invariantes e produzir evidência.

Evidência esperada:

* política de entrada para testes e auditoria.

---

### 5.4 Binding módulo → arquitetura → contrato

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.4.1 Perfil arquitetural por módulo definido | PASS_COM_RESTRICAO | `MODULE_PROFILE_REGISTRY.yaml` auditado (2026-03-14): 16/16 módulos canônicos presentes; schema consistente (`module_class`, `enabled_surfaces`, `overlays`, `contract_targets`); `training` = único HYBRID com `["sync","event"]`; demais CRUD+sync; `sensitive_overlay` em wellness/medical/ai_ingestion/identity_access. Registry é **superfície-cêntrico** (mapeia API surfaces: OpenAPI/AsyncAPI) — não contém campos para artefatos de doc condicional (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT) nem para superfície `workflow`/Arazzo. Aplicabilidade desses artefatos requer aplicação direta de RULES seção 11 ao perfil de cada módulo | (1) Sem campo `workflow`/Arazzo no registry — training tem Arazzo validado mas registry não o declara; (2) docs condicionais (STATE_MODEL, PERMISSIONS, ERRORS) não qualificáveis via registry — requer RULES seção 11 aplicado por módulo; (3) `notifications` declarado sem superfície `event` — possível omissão | Médio: agente pode não saber que STATE_MODEL/PERMISSIONS/ERRORS são aplicáveis ao training sem aplicar RULES seção 11 | Aplicar RULES seção 11.1–11.8 ao módulo `training` para qualificar formalmente STATE_MODEL, PERMISSIONS, ERRORS | STATE_MODEL/PERMISSIONS/ERRORS do training qualificados como aplicáveis ou inaplicáveis com referência explícita à seção de RULES |
| 5.4.2 Boundaries e integrações permitidas por módulo | PASS_COM_RESTRICAO | `CONTRACT_SYSTEM_LAYOUT.md` seções 2.3-2.4 definem boundary crítico users/identity_access; `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` + gate correspondente validam separação wellness/medical e scout; `BOUNDARY_USERS_IDENTITY_ACCESS_GATE` PASS | Boundaries formalizados apenas para pares críticos; boundary de outros módulos não explicitamente mapeado | Médio: módulos fora dos pares críticos não têm boundary explícito | Estender MODULE_SOURCE_AUTHORITY_MATRIX para todos os 16 módulos | Matriz de boundary cobrindo todos os 16 módulos com integrações permitidas/proibidas |
| 5.4.3 Artefatos obrigatórios por módulo e por tipo arquitetural | PASS | `CONTRACT_SYSTEM_RULES.md` seções 10.1, 10.2 e 11.1-11.8 definem matriz completa de artefatos obrigatórios sempre (5+2) e condicionais (5+2) com critérios explícitos de aplicabilidade | — | — | — | Já satisfeito: matriz seção 10-11 cobre sempre e condicionais |
| 5.4.4 Regra contra generalização indevida entre módulos | PASS | `CONTRACT_SYSTEM_RULES.md` seção 8 proíbe explicitamente criação de módulos fora da taxonomia + seção 11.8 exige bloqueio quando artefato condicional parecer aplicável mas estiver ausente | — | — | — | Já satisfeito: proibição de generalização com código de bloqueio |

#### Critérios normativos do bloco 5.4

**5.4.1 Perfil arquitetural por módulo definido**
Critério:

* cada módulo possui definição canônica de perfil arquitetural.

Exemplos de decisão que devem estar normativamente expostos quando aplicável:

* CRUD clássico,
* workflow/state machine,
* eventos de domínio,
* projeções,
* sagas/orquestração,
* leitura vs escrita,
* sincronismo vs assincronismo.

Evidência esperada:

* matriz ou registry de arquitetura por módulo.

**5.4.2 Boundaries e integrações permitidas por módulo**
Critério:

* cada módulo possui fronteiras explícitas com outros módulos e integrações permitidas ou proibidas.

Evidência esperada:

* matriz de boundary ou autoridade equivalente.

**5.4.3 Artefatos obrigatórios por módulo e por tipo arquitetural**
Critério:

* a governança define quais artefatos são obrigatórios para cada módulo conforme seu perfil arquitetural.

Evidência esperada:

* matriz `tipo de módulo/arquitetura → artefatos obrigatórios`.

**5.4.4 Regra contra generalização indevida entre módulos**
Critério:

* o agente não pode aplicar padrão de um módulo em outro sem respaldo normativo explícito.

Evidência esperada:

* política ou regra de restrição modular.

---

### 5.5 Gates de governança

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.5.1 Gates de presença estrutural definidos | PASS | `REQUIRED_ARTIFACT_PRESENCE_GATE` (140 artefatos, bloqueante, PASS); `PATH_CANONICALITY_GATE` (bloqueante, PASS); `MODULE_DOC_CROSSREF_GATE` (bloqueante, PASS) — todos em `latest.json` 2026-03-14 | — | — | — | Já satisfeito: gates de presença são bloqueantes e funcionam |
| 5.5.2 Gates de consistência semântica definidos | PASS | `CROSS_SPEC_ALIGNMENT_GATE` (bloqueante, PASS); `AXIOM_INTEGRITY_GATE` (bloqueante, PASS); `REF_HERMETICITY_GATE` (bloqueante, PASS); `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` (bloqueante, PASS) | — | — | — | Já satisfeito: múltiplos gates de consistência semântica funcionando |
| 5.5.3 Gates de aderência arquitetural definidos | PASS_COM_RESTRICAO | `ASYNC_REQUIRED_MODULE_GATE` (PASS) verifica obrigatoriedade de AsyncAPI/Arazzo por módulo; `MODULE_SOURCE_AUTHORITY_MATRIX_GATE` (PASS) verifica authoridade. Mas não há gate que valide explicitamente se o perfil arquitetural do módulo (CRUD/event/workflow) está correto no contrato | Gate de validação de perfil arquitetural (CRUD vs event vs workflow no contrato) ausente | Alto para novos módulos com arquitetura não usual | Criar `MODULE_ARCHITECTURE_PROFILE_GATE` usando MODULE_PROFILE_REGISTRY | Gate que valida contrato contra perfil arquitetural declarado do módulo |
| 5.5.4 Gates de vínculo contrato ↔ implementação definidos | FAIL | `HTTP_RUNTIME_CONTRACT_GATE` → SKIP_NOT_APPLICABLE ("gate requer servidor live — sempre SKIP em ambiente local/CI"). Sem parity gate ou verificador estático de aderência implementação→contrato | Nenhum gate automático de vínculo contrato↔impl disponível no pipeline atual | Alto: drift implementação↔contrato não detectado pelo pipeline | Avaliar Schemathesis (não disponível) ou criar parity gate baseado em lint estático | Gate de parity que execute em CI sem servidor live |
| 5.5.5 Bloqueio de progressão por gate crítico | PASS | `CI_CONTRACT_GATES.md` presente; 20 de 24 gates são `"blocking": true` em `latest.json`; READINESS_SUMMARY_GATE verifica todos; DECISION_IR_CONFORMANCE_GATE e READINESS_SUMMARY_GATE adicionados (gate count +2); exit_code 0 confirmado em `latest.json` 2026-03-15 | — | — | — | Já satisfeito: gates bloqueantes definidos e operando |

#### Critérios normativos do bloco 5.5

**5.5.1 Gates de presença estrutural definidos**
Critério:

* existem gates para validar presença dos artefatos normativos mínimos.

Evidência esperada:

* gates implementados e vinculados à governança.

**5.5.2 Gates de consistência semântica definidos**
Critério:

* existem gates para validar coerência entre regras, contratos, tipos, semântica e referências cruzadas.

Evidência esperada:

* gates ou validadores correspondentes.

**5.5.3 Gates de aderência arquitetural definidos**
Critério:

* existem gates para validar que o contrato respeita o perfil arquitetural do módulo.

Evidência esperada:

* gate ou política automatizável correspondente.

**5.5.4 Gates de vínculo contrato ↔ implementação definidos**
Critério:

* existem gates ou procedimentos que validam que contrato e implementação não divergiram materialmente.

Evidência esperada:

* verificador, parity gate ou mecanismo equivalente.

**5.5.5 Bloqueio de progressão por gate crítico**
Critério:

* está explícito quais gates são bloqueantes e qual fase cada gate bloqueia.

Evidência esperada:

* registry de gates ou política equivalente.

---

### 5.6 Operação do agente sobre a checklist

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.6.1 Formato canônico de leitura da checklist definido | PASS_COM_RESTRICAO | Seção 2 do próprio CHECKLIST_EXECUTIVO define taxonomia de status e regras de interpretação; seções 5.0.3-5.0.4 definem regras de marcação; RULES seção 21 define contexto mínimo de boot por tarefa | Protocolo formal de "como ler a checklist" não está nos SSOTs (.contract_driven/); está na checklist em si | Baixo (auto-referencial) | Extrair protocolo de leitura para RULES seção nova ou documento de governança | Protocolo de leitura com lista de fontes a consultar por item |
| 5.6.2 Formato canônico de saída do agente definido | PASS | Seção 5.0.6 define campos obrigatórios: Item, Status, Evidência, Lacuna, Impacto, Próxima_ação, Criterio_para_PASS | — | — | — | Já satisfeito: 7 campos obrigatórios por item definidos |
| 5.6.3 Regra de proibição de PASS sem evidência | PASS | Seção 2 e seção 9 do CHECKLIST_EXECUTIVO + seção 5.0.3 definem explicitamente que "existência de arquivo não prova operação" e "PASS obtido em ambiente diferente gera PASS_COM_RESTRICAO" | Regra não está nos SSOTs (CONTRACT_SYSTEM_RULES), apenas na checklist | Baixo (checklist is authoritative for its own rules) | Referenciar regra de evidência nos SSOTs | Regra de evidência explícita nos SSOTs ou checklist auto-referencial com regra |
| 5.6.4 Geração de próximas tarefas a partir dos FAILs | PASS_COM_RESTRICAO | Seções 5.9.2 e 6.12.2 definem formato obrigatório de backlog (Tarefa, Motivo, Item_checklist, Impacto_fluxo, Dependência, Critério_conclusão); mas protocolo de geração automática de tasks não está nos SSOTs | Protocolo de geração de backlog está na checklist, não nos SSOTs operacionais | Baixo (contextual) | Adicionar protocolo de geração de tarefas em RULES seção 20 (modos de operação) | Protocolo formal de geração de backlog a partir de FAIL/NAO_COMPROVADO |
| 5.6.5 Priorização por caminho crítico | PASS_COM_RESTRICAO | Seção 5.0.5 define "itens críticos" numerados; seção 5.8.2 define "regra de bloqueio" por grupo. Priorização pelo impacto de destravamento não está formalizada além dos itens críticos marcados | Prioridade por caminho crítico implícita (itens críticos = bloqueadores), não como ordenação explícita | Baixo | Adicionar coluna "prioridade" ou ordenação por fase no backlog | Regra explícita de priorização por fase desbloqueada |

#### Critérios normativos do bloco 5.6

**5.6.1 Formato canônico de leitura da checklist definido**
Critério:

* está definido como o agente deve interpretar a checklist e quais fontes consultar para cada item.

Evidência esperada:

* protocolo de leitura da checklist.

**5.6.2 Formato canônico de saída do agente definido**
Critério:

* está definido como o agente deve devolver a auditoria da checklist.

Campos mínimos:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

Evidência esperada:

* template ou contrato de saída.

**5.6.3 Regra de proibição de PASS sem evidência**
Critério:

* o agente está normativamente proibido de marcar `PASS` sem evidência verificável.

Evidência esperada:

* regra explícita vinculada à checklist.

**5.6.4 Geração de próximas tarefas a partir dos FAILs**
Critério:

* o agente deve derivar backlog de correção diretamente dos `FAIL` e `NAO_COMPROVADO`.

Evidência esperada:

* protocolo de geração de próximas tarefas.

**5.6.5 Priorização por caminho crítico**
Critério:

* o agente deve priorizar tarefas que:

  * destravam governança,
  * destravam contrato,
  * destravam implementação,
  * destravam teste,
  * reduzem inferência indevida.

Evidência esperada:

* regra explícita de priorização.

---

### 5.7 Critério de liberação por fase

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 5.7.1 Regra de prontidão para iniciar produção de contratos | PASS | `CONTRACT_SYSTEM_RULES.md` seção 16 (DoD de contrato): 11 condições objetivas definem quando o contrato está pronto. RULES seção 15 define fluxo de criação. Gates validam estruturalmente (REQUIRED_ARTIFACT_PRESENCE_GATE, OPENAPI_ROOT_STRUCTURE_GATE, OPENAPI_POLICY_RULESET_GATE) | — | — | — | Já satisfeito: critério de prontidão contratual em 11 condições binárias |
| 5.7.2 Regra de prontidão para iniciar implementação | PASS | `CONTRACT_SYSTEM_RULES.md` seção 17 (Módulo DoD): 6 condições explícitas para módulo pronto para implementação | — | — | — | Já satisfeito: 6 condições objetivas para liberação de implementação |
| 5.7.3 Regra de prontidão para iniciar testes formais | PASS_COM_RESTRICAO | `CONTRACT_SYSTEM_RULES.md` seção 17 inclui "test matrix cobre API, schema, regra, invariante e estado"; `TEST_STRATEGY.md` presente. Mas não há critério explícito de "teste pronto para executar" como fase separada | Fase de teste formal não tem critério de entrada separado | Baixo (está no DoD de módulo) | Criar `TEST_READINESS_POLICY` explicitando quando testes podem começar | Critério explícito de entrada para fase de testes formais |
| 5.7.4 Regra de prontidão global do sistema | PASS_COM_RESTRICAO | Existe via cadeia: DoD de contrato (seção 16) + DoD de módulo (seção 17) + DoD guiado por IA (seção 18) + gate pipeline PASS. Mas não há uma "regra global de prontidão" consolidada num único documento como pré-condição para liberação total do sistema | Critério de prontidão global não consolidado em único lugar | Médio: sem referência única para declarar "sistema pronto" | Criar seção de "readiness global" no CHECKLIST_EXECUTIVO ou CONTRACT_SYSTEM_RULES | Regra objetiva única que consolida todos os DoD + gate pipeline como critério de prontidão global |

#### Critérios normativos do bloco 5.7

**5.7.1 Regra de prontidão para iniciar produção de contratos**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar contratos formais.

Evidência esperada:

* política de readiness para fase contratual.

**5.7.2 Regra de prontidão para iniciar implementação**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar código de produção.

Evidência esperada:

* política de readiness para fase de implementação.

**5.7.3 Regra de prontidão para iniciar testes formais**
Critério:

* estão definidos os itens mínimos obrigatórios para iniciar testes e validação formal.

Evidência esperada:

* política de readiness para fase de testes.

**5.7.4 Regra de prontidão global do sistema**
Critério:

* existe regra objetiva para decidir quando a governança contract-driven está pronta o suficiente para sustentar o fluxo do sistema.

Evidência esperada:

* critério consolidado de prontidão global.

---

### 5.8 Critério executivo de conclusão da seção 5

#### 5.8.1 Regra de conclusão

A seção 5 só pode ser considerada concluída quando:

* todos os itens críticos estiverem em `PASS` ou `PASS_COM_RESTRICAO`; e
* nenhum item crítico estiver em `FAIL` ou `NAO_COMPROVADO`; e
* não houver `FAIL` em autoridade normativa, limites de inferência, fluxo canônico ou gates críticos; e
* os itens críticos em `PASS_COM_RESTRICAO` não comprometerem a próxima fase pretendida; e
* os itens não-críticos em `NAO_COMPROVADO` não incidirem sobre decisões bloqueantes.

#### 5.8.2 Regra de bloqueio

Se qualquer um dos grupos abaixo contiver `FAIL`, a governança contract-driven deve ser considerada **não pronta** para operar de forma confiável:

* `5.1 Autoridade normativa e precedência`
* `5.2 Limites de inferência do agente`
* `5.3 Fluxo canônico de produção`
* `5.5 Gates de governança`
* `5.6 Operação do agente sobre a checklist`

### 5.8.3 Resultado executivo da seção

Status executivo da seção 5: `PASS_COM_RESTRICAO`

Valores permitidos:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

Justificativa executiva:
`Todos os itens críticos (5.1.1, 5.1.3, 5.2.2, 5.2.3, 5.3.1, 5.3.3, 5.4.1, 5.5.5, 5.6.3, 5.6.5, 5.7.1, 5.7.4) estão em PASS ou PASS_COM_RESTRICAO. Nenhum item crítico em FAIL ou NAO_COMPROVADO. O único FAIL na seção (5.5.4 — gate contrato↔implementação) não é item crítico definido na seção 5.0.5. Os itens críticos em PASS_COM_RESTRICAO (5.4.1, 5.6.5, 5.7.4) não bloqueiam a fase contratual: (1) MODULE_PROFILE_REGISTRY auditado — 16/16 módulos presentes, mas registry é superfície-cêntrico (API surfaces) e não qualifica artefatos de doc condicional; aplicação de RULES seção 11 por módulo ainda pendente; (2) priorização por caminho crítico é implícita via itens críticos marcados; (3) DoD global existe via cadeia RULES seções 16-18 + pipeline. A fase contratual está liberada. Condição satisfeita pela regra 5.8.1 atualizada.`

---

### 5.9 Saída resumida obrigatória do agente após auditar a seção 5

Ao final da auditoria, o agente deve produzir obrigatoriamente:

#### 5.9.1 Resumo executivo

* **Status executivo**: PASS_COM_RESTRICAO
* **Principais bloqueios**: 5.5.4 (gate contrato↔impl ausente — schemathesis indisponível; HTTP_RUNTIME_CONTRACT_GATE permanentemente SKIP)
* **Principais restrições**: lista positiva de inferência permitida implícita (apenas por negação); protocolo de escalação pós-bloqueio não formalizado; MODULE_PROFILE_REGISTRY auditado — registry é superfície-cêntrico (não qualifica STATE_MODEL/PERMISSIONS/ERRORS), aplicação de RULES seção 11 por módulo pendente; boundaries formalizados apenas para pares críticos
* **Risco atual de inferência indevida**: BAIXO — seção 8 proíbe explicitamente 16 categorias; bloqueio é regra explícita
* **Fase liberada**: produção contratual (todos os itens críticos da seção 5 satisfeitos)
* **Fase ainda bloqueada**: validação contrato↔implementação em CI (requer gate de parity ou schemathesis)

#### 5.9.2 Backlog mínimo derivado

| Tarefa | Motivo | Item_da_checklist_que_ela_fecha | Impacto_no_fluxo | Dependencia | Criterio_de_conclusao |
|---|---|---|---|---|---|
| Instalar/configurar schemathesis no WSL ou criar parity gate estático | Gate contrato↔impl permanentemente SKIP | 5.5.4, 4.4 (schemathesis FAIL) | Destrava validação de implementação | Backend com servidor live ou análise estática | `HTTP_RUNTIME_CONTRACT_GATE` ou equivalente PASS em CI |
| ~~Auditar conteúdo do MODULE_PROFILE_REGISTRY.yaml~~ **CONCLUÍDO** | Auditado 2026-03-14: 16/16 módulos presentes; training=HYBRID+event+sync; registry é superfície-cêntrico — não contém campos para docs condicionais; sem campo `workflow`/Arazzo; `notifications` sem event surface | 5.4.1 | Lacuna real identificada: STATE_MODEL/PERMISSIONS/ERRORS requerem RULES seção 11 aplicado por módulo | — | Tarefa encerrada; nova tarefa: aplicar RULES seção 11 ao training |
| ~~Aplicar RULES 11.1–11.8 ao módulo `training`~~ **CONCLUÍDO** | Todos os 5 artefatos condicionais confirmados APLICÁVEIS e AUSENTES: STATE_MODEL (11.1), PERMISSIONS (11.2), ERRORS (11.3), UI_CONTRACT (11.4), SCREEN_MAP (11.5) | 4.10 | Qualificação completa — próximo passo: criar os artefatos | DOMAIN_RULES_TRAINING.md + INVARIANTS_TRAINING.md (lidos 2026-03-14) | Tarefa encerrada; 5 FAIL registrados em 4.10 |
| Criar `STATE_MODEL_TRAINING.md` em `docs/hbtrack/modulos/training/` | APLICÁVEL por RULES 11.1: 5 estados persistidos confirmados (INV-TRAIN-006), lifecycle DRAFT→…→CANCELLED, aprovação por papel | 4.10 (STATE_MODEL FAIL) | Alto: bloqueia DoD do módulo piloto | Nenhuma | Arquivo criado com: estado inicial, estados válidos, transições, regras de aprovação |
| Criar `PERMISSIONS_TRAINING.md` em `docs/hbtrack/modulos/training/` | APLICÁVEL por RULES 11.2: RBAC local (DR-TRAIN-001), capability diferenciada Autor vs. Superior (INV-TRAIN-004), visibilidade attendance (INV-TRAIN-016) | 4.10 (PERMISSIONS FAIL) | Alto: bloqueia DoD do módulo piloto | Nenhuma | Arquivo criado com: capability por papel, ações sensíveis, restrições de visibilidade |
| Criar `ERRORS_TRAINING.md` em `docs/hbtrack/modulos/training/` | APLICÁVEL por RULES 11.3: domain-specific failures (DR-TRAIN-002–007 + INV-TRAIN-001–021) com semântica de negócio própria | 4.10 (ERRORS FAIL) | Alto: bloqueia DoD do módulo piloto | Nenhuma | Arquivo criado com: código de erro, regra violada, campo, resposta esperada |
| Criar `UI_CONTRACT_TRAINING.md` antes de implementação de UI | APLICÁVEL por RULES 11.4: SPA Next.js 13+; formulários core (criação sessão, wellness pre/post, assiduidade, analytics export) | 4.10 (UI_CONTRACT FAIL) | Médio: bloqueia início de implementação de UI | Nenhuma | Arquivo criado com: fichas de tela + campos |
| Criar `SCREEN_MAP_TRAINING.md` antes de implementação de UI | APLICÁVEL por RULES 11.5: múltiplas telas (lista, detalhes, assiduidade, wellness, analytics); Arazzo workflow multi-step implica navegação | 4.10 (SCREEN_MAP FAIL) | Médio: bloqueia início de implementação de UI | Nenhuma | Mapa com entry-points, navegação, user journeys distintos |
| Adicionar lista positiva de inferência permitida em RULES | Política de inferência só existe por negação | 5.2.1 | Reduz risco de improviso do agente em borda | Nenhuma | Seção nova em RULES com o que o agente pode inferir |
| Formalizar protocolo de escalação de lacunas | Bloqueio definido, pós-bloqueio não | 5.2.4 | Agente sabe bloquear mas não próximo passo | Nenhuma | 3 desfechos explícitos (pergunta humano, pendência, bloqueio de fase) |
| Criar prompts de AsyncAPI e Arazzo | Ausentes em agent_prompts | 4.3.2 (FAIL: AsyncAPI, Arazzo) | Destrava criação guiada de AsyncAPI/Arazzo | Nenhuma | Dois novos prompts em `.contract_driven/agent_prompts/` |

#### 5.9.3 Próxima tarefa lógica

**Instalar schemathesis** (`pip install schemathesis`) ou criar parity gate estático (contract↔impl), pois é o único FAIL crítico que bloqueia a fase de validação de implementação. Todas as demais restrições são refinamentos — não bloqueiam a fase contratual já liberada.
---

## 6. AUDITORIA DE QUALIDADE DOS 3 SSOTs CENTRAIS

### 6.0 Objetivo da seção

Esta seção verifica se os 3 arquivos SSOT centrais da governança contract-driven não apenas existem e possuem autoridade formal, mas também se o **conteúdo** deles é suficientemente sólido para sustentar a criação de contratos, o bloqueio de lacunas, a orientação do agente e a evolução segura do sistema.

SSOTs auditados nesta seção:

* `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
* `.contract_driven/CONTRACT_SYSTEM_RULES.md`
* `.contract_driven/GLOBAL_TEMPLATES.md`

### 6.0.1 Regra de decisão desta seção

A Seção 6 não mede presença de arquivo nem papel normativo.
Ela mede a **qualidade substantiva** do conteúdo dos 3 SSOTs.

### 6.0.2 Status permitido

Cada item desta seção deve usar exclusivamente um dos quatro status canônicos do documento:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

### 6.0.3 Regra de marcação

Um item desta seção só pode ser marcado como `PASS` quando houver, simultaneamente:

* evidência textual verificável nos 3 SSOTs;
* ausência de contradição material com o canon e com os contratos técnicos;
* suficiência prática para orientar o agente ou a fase avaliada;
* ausência de lacuna crítica para a decisão correspondente.

Presença de tópico, menção superficial ou intenção declarada não bastam, por si só, para `PASS`.

### 6.0.4 Regra de impacto

Se qualquer item crítico desta seção estiver em `FAIL`, os 3 SSOTs devem ser considerados **não suficientemente confiáveis** para sustentar liberação plena da fase correspondente.

Se qualquer item crítico desta seção estiver em `NAO_COMPROVADO`, os 3 SSOTs devem ser considerados **não auditados de forma suficiente** para decisão positiva.

### 6.0.5 Itens críticos desta seção

São itens críticos desta seção:

* `6.1.1`
* `6.2.1`
* `6.3.1`
* `6.4.1`
* `6.5.1`
* `6.6.1`
* `6.7.1`
* `6.8.1`
* `6.9.1`
* `6.10.1`

### 6.0.6 Saída obrigatória do agente ao auditar esta seção

Para cada item auditado, o agente deve registrar:

* `Item`
* `Status`
* `Evidência`
* `Lacuna`
* `Impacto`
* `Próxima_ação`
* `Criterio_para_PASS`

### 6.0.7 Regra de integração com a decisão global

A Seção 6 mede qualidade dos SSOTs centrais, não prontidão operacional global do sistema.

Portanto:

* `PASS` na Seção 6 indica que os 3 SSOTs estão suficientemente sólidos para sustentar o fluxo avaliado;
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 6 impede tratar os 3 SSOTs como base confiável para a fase correspondente;
* `PASS` na Seção 6 não implica, por si só, `PASS` no `STATUS GLOBAL`.

---

### 6.1 Completude

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 6.1.1 Completude normativa mínima dos 3 SSOTs | PASS | LAYOUT cobre filesystem, taxonomia, naming, soberania (seções 1-5); RULES cobre precedência, boot, modo estrito, bloqueio, artefatos, DoD, toolchain, modos e matriz de boot por tarefa (seções 1-21); GLOBAL_TEMPLATES cobre placeholders, índice e scaffolds (seções 1-21+). Os 3 SSOTs se complementam sem lacunas estruturais óbvias | — | — | — | Já satisfeito: cobertura de layout, regras operacionais e templates sem lacuna estrutural identificada |
| 6.1.2 Cobertura das decisões fundamentais do sistema contract-driven | PASS | Precedência: RULES seção 5 ✓; Taxonomia: LAYOUT seção 2 ✓; Artefatos canônicos: RULES seção 3 ✓; Regras de bloqueio: RULES seções 8-9 ✓; Produção de contratos: RULES seção 15 ✓; Natureza de derivados: LAYOUT seção 1A + RULES seção 4 ✓ | — | — | — | Já satisfeito: todos os eixos cobertos |
| 6.1.3 Cobertura das decisões necessárias para operação do agente | PASS | O que ler: RULES seção 6 (boot order) + seção 21 (perfis por tarefa) ✓; O que gerar: RULES seções 15-17 + LAYOUT seção 4A ✓; O que bloquear: RULES seção 8 + 9 ✓; O que não inferir: RULES seção 8 (lista de 16 categorias) ✓ | — | — | — | Já satisfeito: agente tem base suficiente para todas as 4 decisões chave |

#### Critérios normativos do bloco 6.1

**6.1.1 Completude normativa mínima dos 3 SSOTs**
Critério:

* os 3 SSOTs cobrem layout, regras operacionais e templates oficiais sem lacunas críticas óbvias;
* não dependem de documentos implícitos para decisões estruturais básicas.

Evidência esperada:

* conteúdo verificável nos 3 SSOTs cobrindo esses três eixos.

**6.1.2 Cobertura das decisões fundamentais do sistema contract-driven**
Critério:

* os SSOTs cobrem, pelo menos:

  * precedência,
  * taxonomia,
  * artefatos canônicos,
  * regras de bloqueio,
  * produção de contratos,
  * natureza de derivados.

**6.1.3 Cobertura das decisões necessárias para operação do agente**
Critério:

* os SSOTs fornecem base suficiente para o agente saber:

  * o que ler,
  * o que gerar,
  * o que bloquear,
  * o que não inferir.

---

### 6.2 Consistência interna

| Item | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --- | --- | --- | --- | --- | --- | --- |
| 6.2.1 Ausência de contradições internas em cada SSOT | PASS | LAYOUT seção 2B delega naming ao LAYOUT em vez de redefinir (cross-referência explícita); RULES seção 13 estende LAYOUT sem redefini-lo; GLOBAL_TEMPLATES escopo restrito a scaffolds sem introduzir regras normativas. Nenhuma contradição interna identificada na leitura | — | — | — | Já satisfeito: nenhuma contradição material identificada |
| 6.2.2 Terminologia interna estável e não ambígua | PASS | SSOT, template, derivado, canônico, artefato obrigatório, gate, promoção e autoridade são usados com consistência entre os 3 documentos lidos na íntegra; GLOBAL_TEMPLATES esclarece distinção template vs. normativo (seção preamble) | — | — | — | Já satisfeito: terminologia estável nos 3 SSOTs |
| 6.2.3 Regras e exceções definidas sem conflito interno | PASS | Exceções de path exigem ADR explícito (RULES seção 3A.2); exceções de inferência proibida (RULES seção 8) são absolutas; sem exceção que invalide a regra principal silenciosamente | — | — | — | Já satisfeito: exceções explícitas e restritas |

#### Critérios normativos do bloco 6.2

**6.2.1 Ausência de contradições internas em cada SSOT**
Critério:

* o mesmo documento não define duas regras materiais incompatíveis para o mesmo assunto.

**6.2.2 Terminologia interna estável e não ambígua**
Critério:

* termos como SSOT, template, derivado, canônico, bloqueio, módulo, artefato obrigatório, gate, promoção e autoridade são usados com consistência.

**6.2.3 Regras e exceções definidas sem conflito interno**
Critério:

* quando houver exceção, ela não invalida silenciosamente a regra principal.

---

### 6.3 Consistência cruzada

| Item                                                               | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.3.1 Ausência de contradição material entre os 3 SSOTs           | PASS | RULES seção 5 coloca LAYOUT no topo da hierarquia; LAYOUT não define regras de sequência (delegadas ao RULES); GLOBAL_TEMPLATES é explicitamente scaffold-only. Sem cross-invalidação detectada nos 3 SSOTs lidos na íntegra | — | — | — | Já satisfeito |
| 6.3.2 Alinhamento dos 3 SSOTs com o canon global                  | PASS | RULES seção 6 (boot protocol): HANDBALL_RULES_DOMAIN, DOMAIN_GLOSSARY, GLOBAL_INVARIANTS, ERROR_MODEL de docs/_canon/ integram o boot de toda task; MODULE_DOC_CROSSREF_GATE PASS (latest.json 2026-03-14) confirma coerência de headers e cross-refs de módulo com canon | — | — | — | Já satisfeito |
| 6.3.3 Alinhamento dos 3 SSOTs com a estrutura real do repositório | PASS | REQUIRED_ARTIFACT_PRESENCE_GATE: 140 artefatos obrigatórios presentes; PATH_CANONICALITY_GATE: PASS. Paths citados nos 3 SSOTs (.contract_driven/, contracts/, generated/, docs/hbtrack/modulos/) existem e contêm artefatos validados pelo pipeline (2026-03-15T08:42:07Z) | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.3

**6.3.1 Ausência de contradição material entre os 3 SSOTs**
Critério:

* layout, regras e templates não se desautorizam mutuamente.

**6.3.2 Alinhamento dos 3 SSOTs com o canon global**
Critério:

* os 3 SSOTs não conflitam materialmente com `docs/_canon/**`.

**6.3.3 Alinhamento dos 3 SSOTs com a estrutura real do repositório**
Critério:

* os paths, artefatos e fluxos mencionados nos SSOTs correspondem ao que realmente existe ou ao que está formalmente exigido.

---

### 6.4 Ausência de ambiguidade

| Item                                                      | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.4.1 Regras críticas redigidas sem ambiguidade material | PASS | RULES seção 8 enumera 16 categorias de inferência proibida com linguagem imperativa; seção 9 lista 15 blocking codes com condição e ação obrigatória; seção 5 fixa hierarquia de 13 níveis de precedência sem margem para interpretação | — | — | — | Já satisfeito |
| 6.4.2 Critérios de aplicabilidade estão claros           | PASS | RULES seção 11 define matriz de aplicabilidade por tipo de módulo (state machine, permissions, async, UI, arazzo) com condição explícita; seções 11.1–11.8 cobrem todas as superfícies condicionais com critério decisório claro | — | — | — | Já satisfeito |
| 6.4.3 Casos “se aplicável” têm critérios suficientes     | PASS | RULES seções 11.1–11.8 definem critérios de aplicabilidade condicional por tipo de artefato (STATE_MODEL → módulo tem state machine; PERMISSIONS → controle de acesso por papel; UI_CONTRACT → superfície React). Critério decisório presente no SSOT. **Nota pós-auditoria**: MODULE_PROFILE_REGISTRY.yaml é superfície-cêntrico (API surfaces) e não resolve applicabilidade de docs condicionais — a fonte correta é RULES seção 11 aplicado por módulo | — | — | — | Já satisfeito; RULES seção 11 é a fonte correta (não o registry) |

#### Critérios normativos do bloco 6.4

**6.4.1 Regras críticas redigidas sem ambiguidade material**
Critério:

* um agente ou auditor não precisa adivinhar o significado operacional da regra.

**6.4.2 Critérios de aplicabilidade estão claros**
Critério:

* o documento deixa claro quando uma regra vale, quando não vale e o que determina isso.

**6.4.3 Casos “se aplicável” têm critérios suficientes**
Critério:

* não basta dizer “se aplicável”; é preciso haver base para decidir aplicabilidade.

---

### 6.5 Aderência ao domínio HB Track

| Item                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ----------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.5.1 Compatibilidade dos 3 SSOTs com o domínio real do HB Track | PASS | LAYOUT seção 2 define 16 módulos HB Track–específicos (training, matches, scout, wellness, medical, competitions, seasons, teams, users, identity_access, analytics, audit, reports, notifications, ai_ingestion, exercises); RULES seção 12 inclui handball-trigger rule explícita; MODULE_SOURCE_AUTHORITY_MATRIX_GATE PASS confirma autoridade declarada para todos os módulos | — | — | — | Já satisfeito |
| 6.5.2 Os 3 SSOTs não induzem abstração genérica demais           | PASS | Os 3 SSOTs são HB Track-específicos em nomenclatura, módulos, exemplos e obrigações (não são frameworks genéricos de API governance). RULES seção 12 obriga referência ao HANDBALL_RULES_DOMAIN antes de decisões de domínio esportivo. GLOBAL_TEMPLATES usa placeholders HB Track-específicos como {{MODULE_NAME}}, {{DOMAIN_SCOPE}}, {{SPORT_EVENT_TYPE}} | — | — | — | Já satisfeito |
| 6.5.3 Os 3 SSOTs suportam módulos esportivos sem distorção       | PASS | training, matches, scout, competitions, wellness — todos presentes no LAYOUT taxonomy com paths dedicados, AsyncAPI (events), Arazzo (workflows), schema e OpenAPI separados. SCOUT_TAXONOMY_GATE PASS; WELLNESS_MEDICAL_BOUNDARY_GATE PASS; ASYNC_REQUIRED_MODULE_GATE PASS confirmam que a modelagem não distorce esses módulos | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.5

**6.5.1 Compatibilidade dos 3 SSOTs com o domínio real do HB Track**
Critério:

* as regras centrais não colidem com necessidades do produto sports-tech.

**6.5.2 Os 3 SSOTs não induzem abstração genérica demais**
Critério:

* os SSOTs não são tão genéricos a ponto de deixar decisões críticas soltas.

**6.5.3 Os 3 SSOTs suportam módulos esportivos sem distorção**
Critério:

* os SSOTs conseguem governar módulos como training, matches, scout, competitions e wellness sem forçar modelagem artificial.

---

### 6.6 Aderência à arquitetura por módulo

| Item                                                                           | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.6.1 Os 3 SSOTs respeitam diferenças arquiteturais entre módulos             | PASS | RULES seção 11: STATE_MODEL só se módulo tiver state machine; AsyncAPI só se módulo emitir/consumir eventos; Arazzo só se módulo tiver workflow multi-step; UI_CONTRACT só se módulo tiver superfície React. LAYOUT seção 1A distingue superfície REST, AsyncAPI, Arazzo, schema e doc. Sem tratamento uniforme forçado | — | — | — | Já satisfeito |
| 6.6.2 Os 3 SSOTs permitem distinguir CRUD, evento e workflow quando aplicável | PASS | OpenAPI = REST/CRUD; AsyncAPI = eventos assíncronos com channels e messages; Arazzo = workflows multi-step com sequência de calls. Cada superfície tem gate próprio (OPENAPI_ROOT_STRUCTURE_GATE, ASYNCAPI_VALIDATION_GATE, ARAZZO_VALIDATION_GATE) e prompt dedicado (exceto Arazzo e AsyncAPI — lacuna de prompts, mas o SSOT normativo distingue claramente) | — | — | — | Já satisfeito |
| 6.6.3 Os 3 SSOTs não induzem generalização indevida entre módulos             | PASS | RULES seção 8 (prohibited inference) proíbe explicitamente copiar padrão de outro módulo sem base nos SSOTs; BOUNDARY_USERS_IDENTITY_ACCESS_GATE e WELLNESS_MEDICAL_BOUNDARY_GATE PASS confirmam que as fronteiras entre módulos estão sendo respeitadas pelos gates ativos | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.6

**6.6.1 Os 3 SSOTs respeitam diferenças arquiteturais entre módulos**
Critério:

* não tratam todos os módulos como se tivessem mesma natureza arquitetural.

**6.6.2 Os 3 SSOTs permitem distinguir CRUD, evento e workflow quando aplicável**
Critério:

* a governança central comporta mais de uma superfície contratual com critérios claros.

**6.6.3 Os 3 SSOTs não induzem generalização indevida entre módulos**
Critério:

* o agente não é levado a aplicar o mesmo padrão em todos os módulos por falta de nuance normativa.

---

### 6.7 Poder de geração contratual

| Item                                                                                  | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.7.1 Os 3 SSOTs são suficientes para iniciar geração contratual com baixo improviso | PASS | RULES seção 15 (8-step creation procedure) + seção 20 (4 agent modes: AUTHORING, REVIEW, MUTATION, QUERY) + seção 21 (boot matrix por task type) + GLOBAL_TEMPLATES (scaffolds com placeholders) + agent_prompts/ (4 prompts) = suficiente para iniciar geração. Restrição: prompts AsyncAPI e Arazzo ausentes (ver 4.3.2) | — | — | — | Já satisfeito (com restrição de prompts) |
| 6.7.2 Os 3 SSOTs orientam produção de artefatos mínimos por módulo                   | PASS | RULES seção 10: artefatos mínimos obrigatórios por módulo enumerados explicitamente (README, MODULE_SCOPE, DOMAIN_RULES, INVARIANTS, TEST_MATRIX, CONTRACT_*, DOMAIN_AXIOMS_*, OpenAPI path, schema, AsyncAPI channel/message/operation, Arazzo quando aplicável). REQUIRED_ARTIFACT_PRESENCE_GATE PASS confirma 140 artefatos | — | — | — | Já satisfeito |
| 6.7.3 Os 3 SSOTs reduzem variação indevida entre contratos semelhantes               | PASS | api_rules.yaml (precedência nível 3 em RULES seção 5) + redocly ruleset + spectral ruleset + OPENAPI_POLICY_RULESET_GATE PASS garantem uniformidade estrutural de todos os contratos OpenAPI. LAYOUT seção 3 define naming rules globais. Uniformidade confirmada pela ausência de warnings no spectral run (latest.json) | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.7

**6.7.1 Os 3 SSOTs são suficientes para iniciar geração contratual com baixo improviso**
Critério:

* o agente consegue iniciar criação contratual sem depender de inferência estrutural excessiva.

**6.7.2 Os 3 SSOTs orientam produção de artefatos mínimos por módulo**
Critério:

* os SSOTs dizem o que precisa existir por módulo ou por superfície.

**6.7.3 Os 3 SSOTs reduzem variação indevida entre contratos semelhantes**
Critério:

* contratos produzidos sob a mesma governança tendem a sair consistentes.

---

### 6.8 Poder de bloqueio do agente

| Item                                                         | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| ------------------------------------------------------------ | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.8.1 Os 3 SSOTs definem condições claras de bloqueio       | PASS | RULES seção 9: 15 blocking codes com condição de disparo explícita (ex: MISSING_MANDATORY_ARTIFACT, INFERENCE_ATTEMPTED_ON_PROHIBITED_CATEGORY, BREAKING_CHANGE_WITHOUT_WAIVER). Seção 8: 16 categorias onde o agente deve bloquear em vez de inferir. Critério operacional claro de quando parar | — | — | — | Já satisfeito |
| 6.8.2 Os 3 SSOTs tornam lacuna crítica detectável           | PASS | REQUIRED_ARTIFACT_PRESENCE_GATE verifica 140 artefatos; PLACEHOLDER_RESIDUE_GATE detecta templates não preenchidos; REF_HERMETICITY_GATE detecta $refs quebrados; DERIVED_DRIFT_GATE detecta desvio em gerados. O conjunto de gates cobre os vetores principais de lacuna | — | — | — | Já satisfeito |
| 6.8.3 Os 3 SSOTs reduzem espaço para improvisação do agente | PASS | RULES seção 8 proíbe inferência em 16 categorias críticas (estrutura de módulo, boundary, security, async topology, state machine, permissions, breaking changes, entre outros). Seção 5 fixa hierarquia determinística de precedência. Junto com strict mode (seção 8.1), o espaço de improviso é restrito ao mínimo | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.8

**6.8.1 Os 3 SSOTs definem condições claras de bloqueio**
Critério:

* está claro quando o agente deve parar e não prosseguir.

**6.8.2 Os 3 SSOTs tornam lacuna crítica detectável**
Critério:

* o agente consegue reconhecer ausência de insumo obrigatório.

**6.8.3 Os 3 SSOTs reduzem espaço para improvisação do agente**
Critério:

* o conteúdo restringe suficientemente liberdade indevida.

---

### 6.9 Cobertura de casos-limite

| Item                                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.9.1 Os 3 SSOTs cobrem casos-limite relevantes do fluxo contract-driven         | PASS | Waivers system (contracts/_waivers/); ADR process (docs/_canon/decisions/); seção 11 (conditional artifact absence rule); seção 12 (handball-trigger fallback). Casos de exceção previsíveis têm rota documentada | — | — | — | Já satisfeito |
| 6.9.2 Os 3 SSOTs tratam exceções, artefatos opcionais e superfícies condicionais | PASS | RULES seção 10.2 distingue artefatos obrigatórios de opcionais; seção 11 define critério por superfície condicional; GLOBAL_TEMPLATES inclui placeholder registry com anotação de opcionalidade por tipo de artefato | — | — | — | Já satisfeito |
| 6.9.3 Os 3 SSOTs evitam silêncio normativo em bordas previsíveis                 | PASS_COM_RESTRICAO | Bordas principais cobertas (cross-boundary, optional surface, breaking change). Borda com cobertura parcial: cross-module dependency tracking (protocolo de escalação não explicitado nos SSOTs; dependência circular entre módulos não endereçada explicitamente) | Escalação cross-module não documentada; protocolo de dependência circular ausente | Baixo: borda rara; pode ser resolvida com ADR ad-hoc | Documentar protocolo de escalação em docs/_canon/CHANGE_POLICY.md | Escalação documentada com critério decisório explícito |

#### Critérios normativos do bloco 6.9

**6.9.1 Os 3 SSOTs cobrem casos-limite relevantes do fluxo contract-driven**
Critério:

* há orientação suficiente para tratar exceções previsíveis.

**6.9.2 Os 3 SSOTs tratam exceções, artefatos opcionais e superfícies condicionais**
Critério:

* o agente sabe lidar com “se aplicável”, opcionalidade e condições de superfície.

**6.9.3 Os 3 SSOTs evitam silêncio normativo em bordas previsíveis**
Critério:

* não há omissões graves em situações recorrentes.

---

### 6.10 Incompatibilidades com gates e implementação

| Item                                                                              | Status | Evidência | Lacuna | Impacto | Próxima_ação | Criterio_para_PASS |
| --------------------------------------------------------------------------------- | ------ | --------- | ------ | ------- | ------------ | ------------------ |
| 6.10.1 Os 3 SSOTs são compatíveis com os gates implementados                     | PASS | 24 gates PASS em latest.json (2026-03-15T08:42:07Z). Os gates cobrem: axiomas (AXIOM_INTEGRITY_GATE), estrutura (PATH_CANONICALITY_GATE), presença de artefatos (REQUIRED_ARTIFACT_PRESENCE_GATE), policy (OPENAPI_POLICY_RULESET_GATE, ASYNCAPI_VALIDATION_GATE), drift (DERIVED_DRIFT_GATE), breaking changes (CONTRACT_BREAKING_CHANGE_GATE), boundary (BOUNDARY_USERS_IDENTITY_ACCESS_GATE, WELLNESS_MEDICAL_BOUNDARY_GATE). Todos alinhados ao que os SSOTs exigem | — | — | — | Já satisfeito |
| 6.10.2 Os 3 SSOTs não exigem artefatos/fluxos inexistentes sem qualificação      | PASS | REQUIRED_ARTIFACT_PRESENCE_GATE PASS (140 artefatos); os 3 SSOTs não referenciam fluxos ou artefatos que não existam ou cuja ausência não esteja qualificada por critério de opcionalidade (seção 11 RULES). Gates com SKIP_NOT_APPLICABLE têm justificativa formal no próprio latest.json | — | — | — | Já satisfeito |
| 6.10.3 Os 3 SSOTs não entram em conflito material com o estado real do workspace | PASS | overall_status: PASS, exit_code: 0 (2026-03-14). Nenhum gate detectou conflito material entre norma SSOT e estado do workspace. OPENAPI_POLICY_RULESET_GATE: 0 warnings; DERIVED_DRIFT_GATE: gerados alinhados; PLACEHOLDER_RESIDUE_GATE: 43 arquivos sem resíduo de placeholder | — | — | — | Já satisfeito |

#### Critérios normativos do bloco 6.10

**6.10.1 Os 3 SSOTs são compatíveis com os gates implementados**
Critério:

* o que os SSOTs exigem pode ser validado pelos gates reais ou está claramente classificado como exigência ainda não automatizada.

**6.10.2 Os 3 SSOTs não exigem artefatos/fluxos inexistentes sem qualificação**
Critério:

* não empurram o agente para caminhos inviáveis no workspace atual sem deixar isso explícito.

**6.10.3 Os 3 SSOTs não entram em conflito material com o estado real do workspace**
Critério:

* não há incompatibilidade grave entre a norma central e a realidade operacional do repositório.

---

### 6.11 Critério executivo de conclusão da seção 6

#### 6.11.1 Regra de conclusão

A Seção 6 só pode ser considerada concluída quando:

* todos os itens críticos estiverem em `PASS` ou `PASS_COM_RESTRICAO`; e
* nenhum item crítico estiver em `FAIL` ou `NAO_COMPROVADO`; e
* não houver `FAIL` em completude, consistência cruzada, aderência ao domínio, poder de geração contratual, poder de bloqueio do agente ou incompatibilidade com gates/implementação; e
* os itens críticos em `PASS_COM_RESTRICAO` não comprometerem a fase pretendida; e
* os itens não-críticos em `NAO_COMPROVADO` não incidirem sobre decisões bloqueantes.

#### 6.11.2 Regra de bloqueio

Se qualquer um dos grupos abaixo contiver `FAIL`, os 3 SSOTs devem ser considerados **não suficientemente confiáveis** para sustentar o fluxo contract-driven com segurança:

* `6.1 Completude`
* `6.3 Consistência cruzada`
* `6.5 Aderência ao domínio HB Track`
* `6.7 Poder de geração contratual`
* `6.8 Poder de bloqueio do agente`
* `6.10 Incompatibilidades com gates e implementação`

### 6.11.3 Resultado executivo da seção

Status executivo da Seção 6: `PASS_COM_RESTRICAO`

Valores permitidos:

* `PASS`
* `PASS_COM_RESTRICAO`
* `FAIL`
* `NAO_COMPROVADO`

Justificativa executiva:
Todos os 10 itens críticos da seção 6 (6.1.1, 6.2.1, 6.3.1, 6.4.1, 6.5.1, 6.6.1, 6.7.1, 6.8.1, 6.9.1, 6.10.1) estão em PASS. Não há FAIL em nenhum grupo bloqueante (completude, consistência cruzada, aderência ao domínio, poder de geração contratual, poder de bloqueio, incompatibilidade com gates). A única restrição é 6.9.3 (PASS_COM_RESTRICAO): bordas de escalação cross-module e dependência circular entre módulos têm cobertura parcial nos SSOTs. Os 3 SSOTs centrais são substantivamente confiáveis para sustentar o fluxo contract-driven na fase atual (fase contratual). Evidência: latest.json 2026-03-15T08:42:07Z, overall_status: PASS, 24 gates PASS, 3 SKIP_NOT_APPLICABLE.
---

### 6.12 Saída resumida obrigatória do agente após auditar a seção 6

#### 6.12.1 Resumo executivo

**Status executivo da Seção 6:** `PASS_COM_RESTRICAO`

**Principais lacunas dos 3 SSOTs:**
1. Prompts de agente para AsyncAPI e Arazzo ausentes em `.contract_driven/agent_prompts/` (impacta geração automatizada, mas não invalida as normas subjacentes).
2. Protocolo de escalação cross-module e tratamento de dependência circular entre módulos não documentados explicitamente nos SSOTs (borda 6.9.3).
3. MODULE_PROFILE_REGISTRY.yaml: existência confirmada pelo gate, mas conteúdo (perfis dos 16 módulos) não auditado nessa sessão — potencial fonte de lacuna na definição de aplicabilidade condicional.

**Principais contradições:**
Nenhuma contradição material detectada entre os 3 SSOTs. Terminologia estável. Hierarquia de precedência LAYOUT > RULES > api_rules > ... é determinística e sem conflito.

**Risco atual de improvisação do agente:**
Baixo para a fase contratual. RULES seção 8 proíbe inferência em 16 categorias explícitas. Pipeline de gates (24 PASS) fecha automaticamente as principais rotas de desvio. O único risco residual está nas bordas de cross-module dependency (6.9.3) e na ausência de prompts para AsyncAPI/Arazzo.

**Suficiência dos SSOTs para a próxima fase:**
Suficiente para a fase contratual (criação/mutação de contratos OpenAPI, AsyncAPI, Arazzo, schemas e documentação de módulo). A suficiência está condicionada a: (a) criação dos 5 artefatos condicionais do módulo piloto `training` (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP) — qualificação por RULES 11 concluída em 2026-03-14: todos confirmados APLICÁVEIS e AUSENTES → 5 FAIL em 4.10; (b) criação dos prompts ausentes (AsyncAPI, Arazzo) antes de trabalho de geração nessas superfícies.

#### 6.12.2 Backlog mínimo derivado

| Tarefa | Motivo | Item_checklist | Impacto_no_fluxo | Dependência | Critério_de_conclusão |
| --- | --- | --- | --- | --- | --- |
| Criar `create_asyncapi_contract.prompt.md` em `.contract_driven/agent_prompts/` | Ausência de prompt aumenta risco de improviso do agente na geração de AsyncAPI | 4.3.2, 6.7.1 | Alto: bloqueia geração assistida de AsyncAPI com baixo improviso | Nenhuma | Prompt presente, alinhado ao LAYOUT seção 1A e RULES seção 15 |
| Criar `create_arazzo_workflow.prompt.md` em `.contract_driven/agent_prompts/` | Ausência de prompt para Arazzo — surface com gate próprio (ARAZZO_VALIDATION_GATE) | 4.3.2, 6.7.1 | Médio: Arazzo presente e validado, mas geração sem prompt aumenta risco | Nenhuma | Prompt presente, alinhado ao LAYOUT seção 1A e RULES seção 15 |
| ~~Auditar MODULE_PROFILE_REGISTRY.yaml~~ **CONCLUÍDO** | Auditado 2026-03-14: 16/16 módulos presentes; registry é superfície-cêntrico — não resolve applicabilidade de docs condicionais. Registry não é SSOT para STATE_MODEL/PERMISSIONS/ERRORS — RULES seção 11 é | 6.4.3, 6.9.2 | Achado corrige pressuposto anterior: o registry não fecha esta lacuna diretamente | — | Tarefa encerrada; substituída por: aplicar RULES seção 11 ao training |
| ~~Qualificar STATE_MODEL, PERMISSIONS, ERRORS do módulo `training` como N/A ou criar artefatos~~ **CONCLUÍDO** | Qualificação completa por RULES 11 (2026-03-14): todos os 5 artefatos confirmados APLICÁVEIS e AUSENTES (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP) | 4.10, 6.9.2 | Tarefa encerrada; 5 FAIL registrados | — | Tarefa encerrada; próximo: criar os 5 artefatos |
| Criar `STATE_MODEL_TRAINING.md` | APLICÁVEL por RULES 11.1: 5 estados persistidos, lifecycle, aprovação | 4.10 (STATE_MODEL FAIL) | Alto | Nenhuma | Arquivo criado com: estados, transições, regras de aprovação |
| Criar `PERMISSIONS_TRAINING.md` | APLICÁVEL por RULES 11.2: RBAC local, capability Autor vs. Superior | 4.10 (PERMISSIONS FAIL) | Alto | Nenhuma | Arquivo criado com: capability por papel, ações sensíveis, visibilidade |
| Criar `ERRORS_TRAINING.md` | APLICÁVEL por RULES 11.3: domain-specific failures com semântica própria | 4.10 (ERRORS FAIL) | Alto | Nenhuma | Arquivo criado com: código, regra, campo, resposta |
| Criar `UI_CONTRACT_TRAINING.md` antes de implementação de UI | APLICÁVEL por RULES 11.4: SPA + formulários core | 4.10 (UI_CONTRACT FAIL) | Médio | Nenhuma | Fichas de tela com campos e estados |
| Criar `SCREEN_MAP_TRAINING.md` antes de implementação de UI | APLICÁVEL por RULES 11.5: múltiplas telas, fluxo de navegação | 4.10 (SCREEN_MAP FAIL) | Médio | Nenhuma | Mapa com entry-points, navegação, user journeys |
| Documentar protocolo de escalação cross-module em `docs/_canon/CHANGE_POLICY.md` | Borda de escalação não coberta nos SSOTs (6.9.3) | 6.9.3 | Baixo: borda rara, resolúvel com ADR ad-hoc | Nenhuma | Protocolo explícito com critério decisório em CHANGE_POLICY.md |

#### 6.12.3 Próxima tarefa lógica

~~**Aplicar RULES seção 11.1–11.8 ao módulo `training`**~~ **CONCLUÍDO (2026-03-14)**: todos os 5 artefatos condicionais confirmados APLICÁVEIS e AUSENTES por leitura direta de `DOMAIN_RULES_TRAINING.md` e `INVARIANTS_TRAINING.md` contra critérios de RULES 11.1–11.5: STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP → 5 FAIL registrados em 4.10. **Próxima tarefa**: criar `STATE_MODEL_TRAINING.md` (bloqueador mais crítico) — artefato que documenta estados persistidos, lifecycle e regras de transição da training_session; seguido de `PERMISSIONS_TRAINING.md` e `ERRORS_TRAINING.md`.

--- 

## 7. Decisão executiva atual

## STATUS GLOBAL: **PASS_COM_RESTRICAO**

### Fundamentação da decisão global

O repositório comprova prontidão operacional ponta a ponta no ambiente-alvo (WSL) em 2026-03-15T08:42:07Z: `python3 scripts/validate_contracts.py` → `overall_status: PASS`, `exit_code: 0`, 24 gates PASS, 3 SKIP_NOT_APPLICABLE. A cadeia completa (Node.js v24.14.0 WSL-native, arazzo, axiomas, layout, boundary, drift, DECISION_IR) funcionou no WSL. Ferramentas CLI externas (redocly, spectral, asyncapi, oasdiff) reportam `null` em `tool_versions` no relatório: fix 2026-03-15 adicionou `timeout=10s` em `_tool_ver()` para eliminar hang WSL/Windows interop; gates continuam PASS via `_try_node_cli` com node modules WSL-nativos. As Seções 5 e 6 foram formalmente auditadas nesta sessão: ambas em `PASS_COM_RESTRICAO`.

### Regra de impacto das Seções 5 e 6 na decisão global

* `PASS` na Seção 5 libera, no máximo, a **fase contratual**, desde que não haja bloqueio explícito em outras seções.
* `PASS` na Seção 6 indica, no máximo, que os **3 SSOTs centrais** estão suficientemente confiáveis para sustentar a fase avaliada.
* `PASS` nas Seções 5 e 6 **não implica**, por si só, `PASS` no `STATUS GLOBAL`.
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 5 impede tratar a governança contract-driven como pronta para operação segura do agente.
* `FAIL` ou `NAO_COMPROVADO` em item crítico da Seção 6 impede tratar os 3 SSOTs centrais como base confiável para sustentar o fluxo contract-driven.

### Motivos para não declarar PASS pleno

1. **Schemathesis ausente** — `HTTP_RUNTIME_CONTRACT_GATE` permanentemente SKIP; sem validação contrato↔implementação via servidor live.
2. **Enforcement real do agente**: majoritariamente `NAO_COMPROVADO` — sem logs de execução do agente em produção (seções 4.8, 5.6 com restrições).
3. **Alinhamento contrato↔implementação**: sem evidência automatizada (HTTP_RUNTIME_CONTRACT_GATE SKIP por ausência de servidor live).
4. **Artefatos condicionais do módulo piloto `training`** (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP) confirmados **APLICÁVEIS por RULES 11** e **AUSENTES** — 5 FAIL em 4.10.
5. **Prompts AsyncAPI e Arazzo ausentes** — geração nessas superfícies com risco residual de improviso.

---

## 8. Matriz executiva por bloco

| Bloco                                   | Status             | Leitura executiva                                                                                        |
| --------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------- |
| Premissas e decisões de governança      | PASS               | Direção estratégica definida e aceita                                                                    |
| Artefatos canônicos presentes           | PASS               | Base documental central existe; 140 artefatos obrigatórios confirmados pelo REQUIRED_ARTIFACT_PRESENCE_GATE (2026-03-14) |
| Estrutura real de contratos             | PASS_COM_RESTRICAO | Árvore canônica existe e está validada; 2 prompts ausentes (AsyncAPI, Arazzo); 5 artefatos condicionais do módulo training confirmados APLICÁVEIS e AUSENTES (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP) — 5 FAIL em 4.10 |
| Ferramentas instaladas                  | PASS_COM_RESTRICAO | Node.js v24.14.0 WSL-native instalado e funcional; redocly, spectral, asyncapi, oasdiff disponíveis mas `tool_versions` null no relatório (timeout fix 2026-03-15 — Windows interop desativado); gates PASS via WSL-native node modules; schemathesis ausente |
| Ferramentas funcionando de verdade      | PASS               | Pipeline 24 gates PASS (2026-03-15T08:42:07Z); redocly lint 0 erros; spectral 0 warnings; asyncapi validate PASS; arazzo validate PASS |
| Enforcement real                        | PASS_COM_RESTRICAO | 24 gates PASS via pipeline automatizado; enforcement do agente (comportamento em execução) majoritariamente NAO_COMPROVADO |
| Artefatos gerados                       | PASS_COM_RESTRICAO | DERIVED_DRIFT_GATE PASS (gerados alinhados ao compiler determinístico); TRANSFORMATION_FEASIBILITY_GATE SKIP (contracts/generated/ ausente) |
| Agente / fluxo operacional              | NAO_COMPROVADO     | Falta evidência executável do comportamento real do agente em sessão de criação/mutation de contrato |
| Domínio do handebol                     | PASS_COM_RESTRICAO | HANDBALL_RULES_DOMAIN presente; SCOUT_TAXONOMY_GATE PASS; MODULE_SOURCE_AUTHORITY_MATRIX_GATE PASS; sem evidência de uso em domínio real complexo |
| Módulo piloto `training`                | FAIL               | OpenAPI, AsyncAPI, Arazzo, schema, docs sempre-obrigatórios PASS; `MODULE_DECISION_IR.json` PASS (DECISION_IR_CONFORMANCE_GATE 2026-03-15); 5 artefatos condicionais confirmados APLICÁVEIS e AUSENTES: STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP |
| Prontidão real                          | PASS               | overall_status: PASS, exit_code: 0 (2026-03-15T08:42:07Z); toolchain completo funcional no WSL |
| Prontidão de governança contract-driven | PASS_COM_RESTRICAO | Seção 5 auditada: PASS_COM_RESTRICAO (2/4 critérios com restrição; sem FAIL em bloqueantes; fase contratual liberada) |
| Qualidade dos 3 SSOTs centrais          | PASS_COM_RESTRICAO | Seção 6 auditada: PASS_COM_RESTRICAO (sem contradições, sem FAIL em bloqueantes; restrição: borda cross-module e prompts ausentes) |

---

## 9. Regra de uso deste documento

Ao atualizar este checklist:

- não promova item para `PASS` sem evidência executável no ambiente-alvo;
- use `PASS_COM_RESTRICAO` quando a capacidade existir, mas ainda não for confiável para decisão operacional;
- use `NAO_COMPROVADO` quando faltar evidência, mesmo que a hipótese pareça plausível;
- mantenha o `STATUS GLOBAL` conservador;
- registre sempre comando, ambiente e data da evidência usada.

---

Preencher sempre que tocar em `CHECKLIST.md`

* Change log:
> **2026-03-15T08:42:07Z** — Promoção MODULE_DECISION_IR.json + fix _tool_ver()
> - `MODULE_DECISION_IR.json` (training): `DECISION_IR_CONFORMANCE_GATE` PASS; 12 violações corrigidas (11 entidades sem `updated_at`, OD-TRAIN-004 sem `status: resolved`)
> - `validate_contracts.py`: `timeout=10s` em `_try_tool()` — elimina hang WSL/Windows interop; `tool_versions` null no relatório para ferramentas Windows; gates PASS via `_try_node_cli`
> - Pipeline: **24 gates PASS** + 3 SKIP (anterior: 22 PASS — adicionados DECISION_IR_CONFORMANCE_GATE e READINESS_SUMMARY_GATE); exit_code: 0
> - Timestamps: 2026-03-14T09:04:31Z → 2026-03-15T08:42:07Z (13 ocorrências)
> - training module: 5 artefatos condicionais AUSENTES (STATE_MODEL, PERMISSIONS, ERRORS, UI_CONTRACT, SCREEN_MAP)

> **2026-03-14T09:04:31Z** — Auditoria completa das Seções 5 e 6
> Auditoria completa das Seções 5 e 6, com evidência executável do pipeline de gates (22 PASS, 3 SKIP_NOT_APPLICABLE) e análise detalhada.