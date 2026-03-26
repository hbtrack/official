# CHECKLIST — VERIFICAÇÃO REAL DAS PREMISSAS DO HB Track

**REGRA FUNDAMENTAL**:ESTA CHECKLIST REPRESENTA O ESTADO REAL DO REPOSITÓRIO ATUAL E SERVE COMO BASE PARA O PLANO DE AÇÃO PARA PRONTIDÃO DO PILOTO. ATUALIZE COM BASE NA VERIFICAÇÃO REAL E USE AS SEÇÕES DE RESULTADOS ENCONTRADOS E RESUMO DO ESTADO OPERACIONAL REAL PARA DOCUMENTAR O STATUS ATUAL, IDENTIFICAR GAPS, E DEFINIR AÇÕES NECESSÁRIAS PARA AVANÇAR PARA UM ESTADO OPERACIONAL COMPLETO.

Atualize esta checklist com base na verificação real que você fez no repositório, marcando cada item de acordo com o status encontrado. Use as seções de resultados encontrados e resumo do estado operacional real para documentar o status atual do repositório em relação ao manual de contratos driven, identificando claramente quais premissas estão atendidas, quais ferramentas estão funcionando, e quais gaps existem.

Changelog:
>
>
>


- Leia os arquivos `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` e `.contract_driven/CONTRACT_SYSTEM_RULES.md` para entender as premissas e regras do sistema de contratos. Depois, use este checklist para verificar o que está realmente operacional no repositório.

- Marque [x] apenas se houver evidência real de que a premissa está atendida (ex.: o artefato existe e segue o layout, a ferramenta roda e valida um contrato real, o agente bloqueia quando deveria, etc.). Apenas o que foi testado e validado conta como atendido.

- Não marque [x] apenas por existir, confira se o artefato segue o layout canônico. Por exemplo, para marcar o item de OpenAPI paths, deve haver 16 arquivos reais em `contracts/openapi/paths/` seguindo o layout definido, e não apenas a pasta vazia.

## 1. Premissas já resolvidas por decisão sua
Marque `[x]` se confirmado.

- [x] Eu aceito seguir contrato antes do código
- [x] Eu aceito usar a trilogia canônica do sistema de contratos como autoridade:
  - [x] `CONTRACT_SYSTEM_LAYOUT.md`
  - [x] `CONTRACT_SYSTEM_RULES.md`
  - [x] `GLOBAL_TEMPLATES.md`
- [x] Eu aceito `api_rules.yaml` como SSOT de convenções/templates de API HTTP:
  - [x] Canonical esperado: `.contract_driven/templates/api/api_rules.yaml` (criado em 2026-03-13 — tarefa B2)
  - [x] Origem legada eliminada: `.contract_driven/templates/API_RULES/` (removida para evitar split-brain/duplicação normativa)
- [x] Eu aceito a taxonomia canônica dos 16 módulos
- [x] Eu aceito strict mode: bloquear em vez de inferir
- [x] Eu aceito boot mínimo por tarefa
- [x] Eu aceito DoD binário para contrato e módulo

---

## 2. Artefatos canônicos presentes no repositório
- [x] `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` existe e segue o layout canônico definido no manual
- [x] `.contract_driven/CONTRACT_SYSTEM_RULES.md` existe e segue o layout canônico definido no manual
- [x] `.contract_driven/GLOBAL_TEMPLATES.md` existe e segue o layout canônico definido no manual
- [x] `.contract_driven/templates/api/api_rules.yaml` existe e é apontado como SSOT no manual (criado em 2026-03-13 — tarefa B2)
- [x] `.contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml` existe (criado em 2026-03-13 — tarefa B2)
- [x] `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` existe (criado em 2026-03-13 — tarefa B2)
- [x] `.contract_driven/DOMAIN_AXIOMS.json` existe e define axiomas/invariantes globais
- [x] `contracts/schemas/shared/domain_axioms_module.schema.json` existe (contrato estrutural de extensões modulares)
- [x] `docs/hbtrack/modulos/README.md` existe (guia do path/contrato de extensões modulares)
- [x] `docs/_canon/README.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/SYSTEM_SCOPE.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/ARCHITECTURE.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/MODULE_MAP.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/CHANGE_POLICY.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/API_CONVENTIONS.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/DATA_CONVENTIONS.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/ERROR_MODEL.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/GLOBAL_INVARIANTS.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/DOMAIN_GLOSSARY.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/HANDBALL_RULES_DOMAIN.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/SECURITY_RULES.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml` existe (matriz normativa: OWASP → declaração → evidência → gate)
- [x] `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml` existe (matriz normativa: fontes permitidas → artefatos obrigatórios → limites de inferência → gates)
- [x] `docs/_canon/CI_CONTRACT_GATES.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/TEST_STRATEGY.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/C4_CONTEXT.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/C4_CONTAINERS.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/UI_FOUNDATIONS.md` existe e segue o layout canônico definido no manual
- [x] `docs/_canon/DESIGN_SYSTEM.md` existe e segue o layout canônico definido no manual

---

## 3. Estrutura real de contratos no repositório
- [x] `contracts/openapi/openapi.yaml` existe
- [x] `contracts/openapi/paths/` existe e contém os 16 arquivos de módulo canônicos
- [x] `contracts/openapi/intents/` existe (DSL `.intent.yaml` para geração determinística)
- [x] `contracts/schemas/` existe
- [x] `contracts/workflows/` existe
- [x] `contracts/asyncapi/` existe
- [x] `contracts/openapi/README.md` existe
- [x] `contracts/schemas/README.md` existe
- [x] `contracts/workflows/README.md` existe
- [x] `contracts/asyncapi/README.md` existe
- [x] a árvore real segue o layout canônico (evidência: `PATH_CANONICALITY_GATE` → PASS)
- [x] não existem contratos fora da árvore canônica (evidência: higiene aplicada + gates PASS)
- [x] não existem módulos fora da taxonomia (evidência: `.bin/` removida desta branch)
- [x] `.contract_driven/agent_prompts/create_module_docs.prompt.md` existe (pendente revisão/validação do conteúdo)
- [x] `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` existe (pendente revisão/validação do conteúdo)
- [x] `.contract_driven/agent_prompts/create_state_model.prompt.md` existe (pendente revisão/validação do conteúdo)
- [x] `.contract_driven/agent_prompts/create_ui_contract.prompt.md` existe (pendente revisão/validação do conteúdo)
- [ ] `.contract_driven/agent_prompts/create_asyncapi_contract.prompt.md` existe
- [ ] `.contract_driven/agent_prompts/create_arazzo_workflow.prompt.md` existe
- [ ] os prompts para criação de contratos estão alinhados com os templates em `GLOBAL_TEMPLATES.md` e as regras em `CONTRACT_SYSTEM_RULES.md`
- [ ] os prompts para criação de contratos estão alinhados com os artefatos de módulo (ex.: `MODULE_SCOPE`, `DOMAIN_RULES`, `INVARIANTS`, `TEST_MATRIX`) para garantir que o contrato gerado seja completo e consistente com a documentação do módulo
- [ ] os prompts para criação de contratos estão alinhados com o domínio do handebol documentado em `HANDBALL_RULES_DOMAIN.md` para garantir que as regras esportivas sejam incorporadas nos contratos gerados quando aplicável
- [ ] os prompts para criação de contratos estão alinhados com as convenções de API e dados definidas em `API_CONVENTIONS.md` e `DATA_CONVENTIONS.md` para garantir consistência em toda a base de contratos
- [ ] os prompts para criação de contratos estão alinhados com as regras de segurança definidas em `SECURITY_RULES.md` para garantir que os aspectos de segurança sejam considerados nos contratos gerados
- [ ] os prompts para criação de contratos estão alinhados com as regras de mudança definidas em `CHANGE_POLICY.md` para garantir que os contratos gerados sejam compatíveis com a política de mudanças do sistema
- [ ] os prompts para criação de contratos estão alinhados com as regras de teste definidas em `TEST_STRATEGY.md` para garantir que os contratos gerados sejam testáveis e que as estratégias de teste sejam consideradas na geração dos contratos
- [ ] os prompts para criação de contratos estão alinhados com as regras de governança definidas em `CONTRACT_SYSTEM_RULES.md` para garantir que os contratos gerados sigam as regras de governança do sistema de contratos
- [ ] os prompts para criação de contratos estão alinhados com as regras de layout definidas em `CONTRACT_SYSTEM_LAYOUT.md` para garantir que os contratos gerados sigam o layout canônico do sistema de contratos
- [ ] os prompts para criação de contratos estão alinhados com as regras de validação definidas em `CONTRACT_SYSTEM_RULES.md` para garantir que os contratos gerados sejam válidos e que as ferramentas de validação possam processá-los corretamente
- [ ] os prompts para criação de contratos estão alinhados com as regras de extensão modular definidas em `CONTRACT_SYSTEM_RULES.md` e `docs/hbtrack/modulos/README.md` para garantir que os contratos gerados possam ser estendidos de forma modular quando aplicável

---

## 4. Ferramentas instaladas
Marque `[x]` só se o comando roda no seu ambiente.

- [ ] Node.js **WSL-native** disponível no PATH (`node`) — necessário para CLIs via npm (`redocly`, `spectral`, `ajv`, `asyncapi`) (use `source ./setup-env.sh`)
- [ ] Redocly CLI disponível (`redocly --version`) (preferir toolchain pinada do projeto; evite wrappers Windows)
- [ ] Spectral disponível (`spectral --version`) (preferir toolchain pinada do projeto; evite wrappers Windows)
- [ ] oasdiff instalado (`oasdiff` não encontrado no PATH)
- [ ] Schemathesis instalado (`schemathesis` não encontrado no PATH)
- [ ] validador JSON Schema instalado (ajv) (`ajv` via npm; use `source ./setup-env.sh`)
- [ ] validator/parser AsyncAPI instalado (`asyncapi --version`) (use `source ./setup-env.sh`)
- [x] validator/linter Arazzo instalado (evidência: `ARAZZO_VALIDATION_GATE` → PASS em `python3 scripts/validate_contracts.py`)
- [ ] Storybook disponível, se houver UI documentada
- [x] Intent compiler disponível (`python3 scripts/contracts/validate/api/compile_api_intent.py` executa)
- [x] Policy compiler disponível (`python3 scripts/contracts/validate/api/compile_api_policy.py` executa)
- [ ] Ferramentas de geração de artefatos (clientes, docs, etc.) configuradas e testadas

---

## 5. Ferramentas funcionando de verdade
Marque `[x]` só se você executou e obteve resultado real.

- [ ] Redocly roda contra `contracts/openapi/openapi.yaml` (após `source ./setup-env.sh`)
- [ ] Spectral executa (versão/CLI disponível) (após `source ./setup-env.sh`)
- [ ] oasdiff roda entre duas versões da spec (baseline vs. atual; gate `CONTRACT_BREAKING_CHANGE_GATE`) (`oasdiff` ausente)
- [ ] Schemathesis roda contra uma API real ou ambiente local
- [ ] JSON Schema validator (ajv) executa (help/CLI disponível) (após `source ./setup-env.sh`)
- [ ] AsyncAPI validator roda no contrato atual (após `source ./setup-env.sh`)
- [x] Arazzo validator roda nos workflows atuais
- [ ] Storybook build roda, se aplicável
- [x] Intent compiler (DSL) roda e falha fechado (não toca `contracts/openapi/paths/` em erro)
- [ ] Intent compiler roda e gera contrato quando o prompt é seguido corretamente
- [ ] Policy compiler roda e falha fechado quando há drift semântico
- [ ] Policy compiler roda e passa quando não há drift semântico
- [ ] Ferramentas de geração de artefatos (clientes, docs, etc.) rodam e geram artefatos válidos
- [ ] Gates de CI estão configurados e falham quando o contrato é inválido ou quando há breaking change (evidência: `CONTRACT_BREAKING_CHANGE_GATE` e `DERIVED_DRIFT_GATE` → FAIL em `python3 scripts/validate_contracts.py`)
- [ ] Gates de CI estão configurados e passam quando o contrato é válido e não há breaking change (evidência: `CONTRACT_BREAKING_CHANGE_GATE` e `DERIVED_DRIFT_GATE` → PASS em `python3 scripts/validate_contracts.py`)
- [ ] Gates de CI estão configurados e falham quando artefato obrigatório está ausente (evidência: `REQUIRED_ARTIFACT_PRESENCE_GATE` → FAIL em `python3 scripts/validate_contracts.py`)
- [ ] Gates de CI estão configurados e falham quando artefato de módulo não referencia contrato adequadamente (evidência: `MODULE_DOC_CROSSREF_GATE` → FAIL em `python3 scripts/validate_contracts.py`)

> **Evidência validate_contracts (WSL, 2026-03-13)**: `python3 scripts/validate_contracts.py` → **FAIL** (exit code 3).
> Gates PASS: `REQUIRED_ARTIFACT_PRESENCE_GATE`, `MODULE_DOC_CROSSREF_GATE`, `API_NORMATIVE_DUPLICATION_GATE`, `OWASP_API_CONTROL_MATRIX_GATE`, `MODULE_SOURCE_AUTHORITY_MATRIX_GATE`, `BOUNDARY_USERS_IDENTITY_ACCESS_GATE`, `WELLNESS_MEDICAL_BOUNDARY_GATE`, `SCOUT_TAXONOMY_GATE`, `ASYNC_REQUIRED_MODULE_GATE`, `EXTERNAL_SOURCE_AUTHORITY_GATE`, `PLACEHOLDER_RESIDUE_GATE`, `REF_HERMETICITY_GATE`, `JSON_SCHEMA_VALIDATION_GATE`, `CROSS_SPEC_ALIGNMENT_GATE`, `ARAZZO_VALIDATION_GATE`, `DERIVED_DRIFT_GATE`.
> Falhas bloqueantes: `OPENAPI_ROOT_STRUCTURE_GATE`, `OPENAPI_POLICY_RULESET_GATE`, `CONTRACT_BREAKING_CHANGE_GATE`.
> Falhas não-bloqueantes: `ASYNCAPI_VALIDATION_GATE` (infra: `node` ausente no WSL).
> Ver `_reports/contract_gates/latest.json`.

> **Evidência Intent compiler (WSL, 2026-03-13)**: `python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --intent contracts/openapi/intents/ai_ingestion.intent.yaml --format json` → PASS (exit code 0).

> **Evidência Drift semântico (WSL, 2026-03-13)**: `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json` → PASS (exit code 0).

> **Evidência Redocly (Windows 11, 2026-03-12)**: `redocly lint contracts/openapi/openapi.yaml` → PASS (exit code 0). Ver `contracts/openapi/redocly_lint.log`.

> **Evidência validate_contracts (Windows 11, 2026-03-12)**: `python3 scripts/generate/gen_openapi_baseline.py` + `python3 scripts/validate_contracts.py` → PASS (exit code 0), com `CONTRACT_BREAKING_CHANGE_GATE` executando.

> **Evidência Intent compiler (Windows 11, 2026-03-12)**:
> - Intent inválida (colisão de semantic_id local) → FAIL_ACTIONABLE com `location` (linha/coluna): `python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --intent contracts/openapi/intents/examples/ai_ingestion.invalid.intent.yaml --format json`
> - Intent válida → PASS e geração aplicada: `python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --apply --format json`

> **Evidência Drift semântico (Windows 11, 2026-03-12)**: `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json` → PASS (sem drift); em drift real, o comando retorna FAIL com lista de `drifts`.

---

## 6. Enforcement real
- [x] existe script/comando único para validar contratos
- [x] existe rotina de falha quando o contrato está inválido
- [x] o validador consome `DOMAIN_AXIOMS.json` explicitamente (sem interpretação livre)
- [x] existe rotina de falha para breaking change (evidência: `CONTRACT_BREAKING_CHANGE_GATE` via oasdiff)
- [x] existe rotina de falha para drift entre fonte soberana e derivado (evidência: `DERIVED_DRIFT_GATE` semântico)
- [x] existe rotina de falha quando placeholder residual aparece (evidência: `PLACEHOLDER_RESIDUE_GATE`)
- [x] existe rotina de falha quando artefato obrigatório está ausente (evidência: `REQUIRED_ARTIFACT_PRESENCE_GATE`)
- [x] existe rotina de falha para matriz normativa OWASP (evidência: `OWASP_API_CONTROL_MATRIX_GATE`)
- [x] existe rotina de falha para matriz de fontes/autoridade por módulo (evidência: `MODULE_SOURCE_AUTHORITY_MATRIX_GATE`)
- [x] existe rotina de falha para boundary `users` vs `identity_access` (evidência: `BOUNDARY_USERS_IDENTITY_ACCESS_GATE`)
- [x] existe rotina de falha para boundary `wellness` vs `medical` (evidência: `WELLNESS_MEDICAL_BOUNDARY_GATE`)
- [x] existe rotina de falha quando taxonomia de scout é usada sem artefato canônico (evidência: `SCOUT_TAXONOMY_GATE`)
- [x] existe rotina de falha quando módulo com paths reais exige async/workflow e não possui artefatos (evidência: `ASYNC_REQUIRED_MODULE_GATE`)
- [x] existe rotina de falha quando benchmark é tratado como SSOT em docs (evidência: `EXTERNAL_SOURCE_AUTHORITY_GATE`)
- [ ] existe rotina de falha quando artefato de módulo não referencia contrato adequadamente (evidência: `MODULE_DOC_CROSSREF_GATE`)
- [ ] existe rotina de falha quando artefato de módulo não alinha com contrato (realidade de implementação) (evidência: `CROSS_SPEC_ALIGNMENT_GATE`)
- [ ] existe rotina de falha quando artefato de módulo não alinha com domínio do handebol (evidência: `HANDBALL_RULES_ALIGNMENT_GATE`)
- [ ] existe rotina de falha quando implementação real viola regra de domínio documentada (evidência: testes automatizados baseados em `DOMAIN_RULES_TRAINING.md` e `HANDBALL_RULES_DOMAIN.md`)
- [ ] existe rotina de falha quando implementação real viola invariante documentada (evidência: testes automatizados baseados em `INVARIANTS_TRAINING.md` e `DOMAIN_AXIOMS.json`)
- [ ] existe rotina de falha quando agente improvisa em vez de bloquear (evidência: logs de execução do agente mostrando bloqueios em lacunas críticas)
- [ ] existe rotina de falha quando agente cria módulo fora da taxonomia (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar módulos não listados em `MODULE_MAP.md`)
- [ ] existe rotina de falha quando agente cria path fora de contrato (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar paths não definidos nos contratos OpenAPI)
- [ ] existe rotina de falha quando agente cria evento fora de AsyncAPI (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar eventos não definidos nos contratos AsyncAPI)
- [ ] existe rotina de falha quando agente cria workflow sem Arazzo (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar workflows sem seguir os contratos de Arazzo)
- [ ] existe rotina de falha quando agente cria regra esportiva fora de `HANDBALL_RULES_DOMAIN.md` (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar regras esportivas não documentadas em `HANDBALL_RULES_DOMAIN.md`) 
- [ ] existe rotina de falha quando artefato gerado é editado manualmente (evidência: comparação semântica entre artefato gerado e versão editada mostrando divergências, e logs de execução do agente mostrando bloqueios em tentativas de editar artefatos gerados)
---

## 7. Artefatos gerados
- [x] existe pasta canônica para artefatos gerados (`generated/`)
- [x] tipos/políticas/manifests gerados vão para essa pasta
- [ ] clientes gerados vão sempre para essa pasta
- [ ] docs geradas vão sempre para essa pasta
- [ ] artefatos gerados não são editados manualmente
- [x] artefatos gerados são regeneráveis (compiler determinístico)
- [x] drift entre gerado e soberano é detectável (comparação semântica)
- [x] existe rotina de falha para drift entre gerado e soberano (evidência: `DERIVED_DRIFT_GATE` semântico)
- [ ] artefatos gerados estão alinhados com domínio do handebol (evidência: `HANDBALL_RULES_ALIGNMENT_GATE` e testes automatizados baseados em `HANDBALL_RULES_DOMAIN.md`)
- [ ] artefatos gerados estão alinhados com regras de domínio documentadas (evidência: testes automatizados baseados em `DOMAIN_RULES_TRAINING.md`)
- [ ] artefatos gerados estão alinhados com invariantes documentadas (evidência: testes automatizados baseados em `INVARIANTS_TRAINING.md ` e `DOMAIN_AXIOMS.json`)

---

## 8. Agente / fluxo operacional
- [ ] o agente realmente usa a ordem de boot definida
- [ ] o agente realmente usa boot mínimo por tarefa
- [ ] o agente realmente bloqueia em lacuna crítica
- [ ] o agente realmente emite códigos de bloqueio fechados
- [ ] o agente não cria módulo fora da taxonomia
- [ ] o agente não cria path fora de contrato
- [ ] o agente não cria evento fora de AsyncAPI
- [ ] o agente não cria workflow sem Arazzo
- [ ] o agente não cria regra esportiva fora de `HANDBALL_RULES_DOMAIN.md`
- [ ] o agente não edita artefato gerado manualmente
- [ ] o agente realmente gera artefato quando o prompt é seguido corretamente
- [ ] o agente realmente bloqueia quando o prompt é seguido incorretamente (ex.: contrato inválido, artefato fora de layout, tentativa de improvisação, etc.)
- [ ] o agente realmente gera artefato alinhado com domínio do handebol quando o prompt é seguido corretamente (evidência: artefato gerado alinhado com regras esportivas documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o agente realmente gera artefato alinhado com regras de domínio documentadas quando o prompt é seguido corretamente (evidência: artefato gerado alinhado com regras de domínio documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o agente realmente gera artefato alinhado com invariantes documentadas quando o prompt é seguido corretamente (evidência: artefato gerado alinhado com invariantes documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
---

## 9. Domínio do handebol
- [x] `docs/_canon/HANDBALL_RULES_DOMAIN.md` existe
- [x] cobre regras que impactam `training`
- [x] cobre regras que impactam `matches`
- [x] cobre regras que impactam `scout`
- [x] cobre regras que impactam `competitions`
- [ ] adaptações locais do produto estão registradas
- [ ] não há regra esportiva crítica ainda “na cabeça” e fora do documento
- [ ] o agente bloqueia quando tentativa de criar regra esportiva fora do documento (evidência: logs de execução do agente mostrando bloqueios em tentativas de criar regras esportivas não documentadas em `HANDBALL_RULES_DOMAIN.md`)
- [ ] os contratos refletem o domínio documentado (evidência: `HANDBALL_RULES_ALIGNMENT_GATE` e `CROSS_SPEC_ALIGNMENT_GATE`)
- [ ] a implementação real respeita o domínio documentado (evidência: testes automatizados baseados em `DOMAIN_RULES_TRAINING.md` e `HANDBALL_RULES_DOMAIN.md`)
- [ ] não há lacunas críticas entre o domínio documentado e a implementação real (evidência: ausência de falhas em testes automatizados baseados em `DOMAIN_RULES_TRAINING.md` e `HANDBALL_RULES_DOMAIN.md`)
- [ ] o domínio documentado é suficiente para guiar a implementação de features críticas (evidência: implementação de features críticas sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o domínio documentado é suficiente para guiar a criação de contratos (evidência: contratos OpenAPI e AsyncAPI alinhados com as regras esportivas documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o domínio documentado é suficiente para guiar a criação de artefatos de módulo (evidência: artefatos de módulo alinhados com as regras esportivas documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o domínio documentado é suficiente para guiar a criação de testes automatizados (evidência: testes automatizados baseados em `DOMAIN_RULES_TRAINING.md` e `HANDBALL_RULES_DOMAIN.md` cobrindo as regras esportivas documentadas, sem necessidade de improvisação ou consulta externa ao domínio)
- [ ] o domínio documentado é suficiente para guiar a geração de artefatos (evidência: artefatos gerados alinhados com as regras esportivas documentadas, sem necessidade de improvisação ou consulta externa ao domínio)

---

## 10. Módulos reais já aderentes ao manual
Piloto existente: `training` (artefatos presentes), mas o estado **não está PASS** no ambiente WSL em `2026-03-13` (ver `_reports/contract_gates/latest.json`).

- [x] possui `README`
- [x] possui `MODULE_SCOPE`
- [x] possui `DOMAIN_RULES`
- [x] possui `INVARIANTS`
- [x] possui `TEST_MATRIX`
- [x] possui OpenAPI path
- [x] possui schemas
- [ ] possui `STATE_MODEL`, se aplicável
- [ ] possui `PERMISSIONS`, se aplicável
- [ ] possui `ERRORS`, se aplicável
- [ ] possui `UI_CONTRACT`, se aplicável
- [ ] possui `SCREEN_MAP`, se aplicável
- [x] possui Arazzo, se aplicável
- [x] possui AsyncAPI, se aplicável

---

## 11. Prontidão real
- [ ] existe pelo menos 1 contrato validado ponta a ponta (no ambiente WSL em `2026-03-13`: `python3 scripts/validate_contracts.py` → FAIL)
- [ ] existe pelo menos 1 módulo que passa no DoD de contrato pronto (no ambiente WSL em `2026-03-13`: gates bloqueantes falham)
- [ ] existe pelo menos 1 módulo que passa no DoD de módulo pronto (no ambiente WSL em `2026-03-13`: gates bloqueantes falham)
- [ ] existe pelo menos 1 fluxo onde contrato gerou/dirigiu implementação real
- [ ] existe pelo menos 1 evidência de que o agente bloqueou corretamente em uma lacuna
- [ ] existe pelo menos 1 evidência de que o agente gerou artefato alinhado com domínio do handebol quando o prompt foi seguido corretamente
- [ ] existe pelo menos 1 evidência de que o agente gerou artefato alinhado com regras de domínio documentadas quando o prompt foi seguido corretamente
- [ ] existe pelo menos 1 evidência de que o agente gerou artefato alinhado com invariantes documentadas quando o prompt foi seguido corretamente 

# 11.2 - Checklist de prontidão ideal para lançamento do piloto
- [ ] arquivos canônicos `CONTRACT_SYSTEM_RULES.md`, `CONTRACT_SYSTEM_RULES.md` `GLOBAL_TEMPLATES.md` estão atualizados, alinhados e sincronizados, diminuindo a alucinação do agente e servindo como referência clara para criação de artefatos, contratos e prompts.
- [ ] arquivos canônicos de domínio (`DOMAIN_AXIOMS.json`, `HANDBALL_RULES_DOMAIN.md`) estão atualizados, alinhados e sincronizados, garantindo que o domínio do handebol esteja claramente documentado e incorporado em contratos, artefatos e prompts.
- [ ] arquivos SSOT de artefatos (ex.: `api_rules.yaml`) estão atualizados, alinhados e sincronizados, servindo como referência clara para criação de contratos e artefatos de API HTTP.
- [ ] artefatos canônicos estão atualizados e refletem a realidade do repositório (ex.: contratos seguindo o layout canônico, prompts alinhados com templates/regras/contratos, etc.) 
- [ ] ferramentas críticas estão instaladas e funcionando (ex.: Redocly, Spectral, oasdiff, AsyncAPI CLI, etc.)
- [ ] domínio do handebol crítico está documentado (ex.: regras que impactam `training`, `matches`, `scout`, `competitions`, etc.)
- [ ] o agente/fluxo operacional respeita bloqueios (ex.: bloqueia em vez de improvisar, bloqueia criação de artefato fora de contrato, bloqueia criação de módulo fora da taxonomia, etc.)
- [ ] existe pelo menos 1 evidência executável ponta a ponta (ex.: contrato validado por ferramentas, agente bloqueando em lacuna crítica, artefato gerado alinhado com domínio do handebol, etc.)  
- [ ] existe pelo menos 1 evidência de que o agente gerou artefato alinhado com regras de domínio documentadas quando o prompt foi seguido corretamente
- [ ] arquivos README estão atualizados e refletem a realidade do repositório, servindo como guia claro para entendimento do sistema de contratos, domínio do handebol, regras de domínio, invariantes, estratégias de teste, arquitetura, etc.

---

## 12. Resultado final
### PASS se:
- [ ] todas as premissas indispensáveis têm evidência real
- [ ] ferramentas críticas estão instaladas e funcionando
- [x] domínio do handebol crítico está documentado
- [ ] o agente/fluxo operacional respeita bloqueios
- [ ] existe pelo menos 1 evidência executável ponta a ponta

### FAIL se houver qualquer um destes:
- [x] ferramenta crítica definida no manual não roda (ex.: `redocly`/`spectral` bloqueados por `node` ausente; `oasdiff`/`asyncapi` ausentes no PATH)
- [ ] domínio esportivo crítico está fora do documento
- [ ] agente improvisa em vez de bloquear
- [ ] não existe enforcement real
- [ ] contrato e derivado competem como fonte de verdade (no WSL em 2026-03-13: `DERIVED_DRIFT_GATE` → PASS)

## Resultados encontrados (2026-03-13 — WSL)

## Resumo do estado operacional real (2026-03-13 — WSL)

Execução real em WSL (`/mnt/c/HB TRACK`):

- `python3 scripts/validate_contracts.py` → **FAIL** (exit code 3). Ver `_reports/contract_gates/latest.json`.
- Bloqueios principais:
  - **Node ausente** (`node: not found`) → gates `OPENAPI_ROOT_STRUCTURE_GATE` (Redocly), `OPENAPI_POLICY_RULESET_GATE` (Spectral) e `ASYNCAPI_VALIDATION_GATE` falham.
  - **Ferramentas ausentes**: `oasdiff` → `CONTRACT_BREAKING_CHANGE_GATE` falha.

- Sinais positivos (WSL, 2026-03-13):
  - `REQUIRED_ARTIFACT_PRESENCE_GATE` → PASS (SSOT de API presente em `.contract_driven/templates/api/*`).
  - `REF_HERMETICITY_GATE` → PASS.
  - `DERIVED_DRIFT_GATE` → PASS.
  - `OWASP_API_CONTROL_MATRIX_GATE` → PASS.
  - `CROSS_SPEC_ALIGNMENT_GATE` → PASS.

**REGRAS:**
- Atualize essa sessão com base na verificação real que você fez no repositório, com o status de cada item e evidências encontradas. No final, faça um resumo do estado operacional real e liste as ações necessárias para chegar a um estado operacional completo.

- As ações devem seguir uma ordem lógica de execução, começando pelas tarefas não bloqueantes e avançando para as tarefas bloqueantes, garantindo que cada etapa seja concluída antes de passar para a próxima. Por exemplo: Se uma ferramenta de validação é necessária para validar um artefato, a tarefa de criar o artefato deve ser concluída antes da tarefa de configurar a ferramenta de validação.

- As ações devem formar um plano completo para o funcionamento dos contratos driven do HB Track, evitando generalidades, para que outros agentes possam executar o plano sem alucinações. Seja específico sobre o que criar, onde criar, e como validar cada artefato necessário.

**Estrutura recomendada (copiar/colar e preencher)**:
- [Tarefa]: Tn — descreva claramente a tarefa
  - *Subtarefa 1.1*: descreva a subtarefa
  - *Subtarefa 1.2*: descreva a subtarefa
- [Objetivo]: descreva o resultado esperado (o que muda no repo/sistema)
- [Escopo]: descreva o que está incluído e o que está fora
- [Critérios de aceitação]: liste evidências objetivas (arquivos/commmands/saídas)
- [Critérios de rejeição]: descreva o que invalida a tarefa
- [Critérios de bloqueio]: descreva dependências externas que impedem avanço
- [Comandos permitidos]: liste comandos/ações permitidos (quando houver restrições)
- [Comandos proibidos]: liste comandos/ações proibidos (quando houver restrições)
- [Validação]: descreva como checar o resultado (comandos + inspeção manual)
- [Definition of Done]: descreva quando considerar “feito”
- [Saída esperada]: liste artefatos atualizados/criados

## Resumo do estado operacional real (2026-03-12)

Verificação real executada em Windows 11, ambiente local do repositório `c:\HB TRACK\`.

- **Trilogia SSOT** (`.contract_driven/*`): presente e íntegra (`CONTRACT_SYSTEM_LAYOUT.md`, `CONTRACT_SYSTEM_RULES.md`, `GLOBAL_TEMPLATES.md`).
- **SSOT de API HTTP**: `.contract_driven/templates/api/api_rules.yaml` presente (regras/templates/validações de API).
- **DOMAIN_AXIOMS + enforcement**: `.contract_driven/DOMAIN_AXIOMS.json` atualizado (event_type fechado, HALFTIME na FSM, progressão disciplinar verificável, extensões modulares habilitadas); `python scripts/validate_contracts.py` executa e retorna **PASS** (exit code 0) com evidência em `_reports/contract_gates/latest.json`.
- **Extensões modulares**: contrato estrutural em `contracts/schemas/shared/domain_axioms_module.schema.json` + doc em `docs/hbtrack/modulos/README.md`.
- **Canon global** em `docs/_canon/`: **completo** — presentes `README`, `SYSTEM_SCOPE`, `ARCHITECTURE`, `MODULE_MAP`, `API_CONVENTIONS`, `DATA_CONVENTIONS`, `ERROR_MODEL`, `GLOBAL_INVARIANTS`, `SECURITY_RULES`, `CI_CONTRACT_GATES`, `TEST_STRATEGY`, `UI_FOUNDATIONS`, `DESIGN_SYSTEM`, `C4_CONTEXT`, `C4_CONTAINERS`, `CHANGE_POLICY`, `DOMAIN_GLOSSARY`, `HANDBALL_RULES_DOMAIN`.
- **OpenAPI**: `contracts/openapi/openapi.yaml` existe com `paths: {}` (esqueleto) e 16 arquivos em `contracts/openapi/paths/`; **Gate 1 PASS** (lint estrutural), mas o conteúdo ainda não descreve rotas reais.
- **Intent DSL (OpenAPI)**: `contracts/openapi/intents/` presente + `compile_api_intent.py` gera `contracts/openapi/paths/<module>.yaml` de forma **fail-closed** (erro aponta para `.intent.yaml` com `location` linha/coluna).
- **Tooling Windows**:
  - `redocly`: instalado via npm global, executável nativamente. ✓
  - `spectral`: instalado via npm global, executável nativamente. ✓
  - `ajv` (JSON Schema): instalado via npm global, executável nativamente. ✓
  - `schemathesis`: disponível em `Hb Track - Backend/.venv/Scripts/schemathesis.exe`. ✓ (mas sem API real para testar)
  - `asyncapi`: devDependency `@asyncapi/cli` + fallback via `node_modules/.bin/asyncapi` no validador; Gate 12 **PASS** (ver `_reports/contract_gates/latest.json` e `contracts/asyncapi/asyncapi_validate.log`). ✓
  - `oasdiff`: instalado via Go (`go install github.com/tufin/oasdiff@latest`), ver `scripts/contract_gates/oasdiff_version.log`. ✓
  - `arazzo`: validado via gate `ARAZZO_VALIDATION_GATE` (ver `_reports/contract_gates/latest.json`). ✓
- **Lacunas de contrato SSOT**: `contracts/asyncapi/asyncapi.yaml` existe com evento real do módulo `training` e validação `asyncapi validate` **PASS** (ver `contracts/asyncapi/asyncapi_validate.log`). `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml` existe (Gate 13 aplicável; evidência em `_reports/contract_gates/latest.json`). Em `contracts/schemas/` há schemas estruturais em `shared/` e 1 schema SSOT de entidade em `contracts/schemas/training/training_session.schema.json` (Gate 5 operacional; AJV PASS em `contracts/schemas/training/ajv_compile.log`).
- **READMEs de contrato**: criados em `contracts/openapi/`, `contracts/schemas/`, `contracts/workflows/`, `contracts/asyncapi/`. ✓
- **Higiene de árvore canônica**: removidos de `.bin/atletas/` os `*.schema.json` e `*.arazzo.yaml` (schemas movidos para `tools/contract_linter/schemas/` e workflow vazio removido). Item **atendido**. (Arquivos em `node_modules/` não são considerados contratos de domínio.)
- **Higiene de taxonomia**: `.bin/` removida desta branch (`hb-track-contratos-driven`). Item **atendido**.
- **ADRs**: diretório `docs/_canon/decisions/` criado com 4 ADRs: ADR-001 (CDD), ADR-002 (UUID v4), ADR-003 (media type versioning), ADR-004 (autoridade do API policy compiler). ✓


## TABELA DE EVIDENCIAS ENCONTRADAS
Tabela preenchida com base na verificação real executada neste ambiente (Windows 11, 2026-03-12).

| Item | Evidência encontrada | Status |
|---|---|---|
| OpenAPI entrypoint | `contracts/openapi/openapi.yaml` existe com `paths: {}` e `components:` | Atendida |
| OpenAPI paths (16 módulos) | 16 arquivos em `contracts/openapi/paths/`: `users`, `seasons`, `teams`, `training`, `wellness`, `medical`, `competitions`, `matches`, `scout`, `exercises`, `analytics`, `reports`, `ai_ingestion`, `identity_access`, `audit`, `notifications` | Atendida |
| Node runtime | `node.exe` em `C:\Program Files\nodejs\node.exe`, nativo no PATH | Atendida |
| Redocly CLI | `redocly lint contracts/openapi/openapi.yaml` → PASS (ver `contracts/openapi/redocly_lint.log`) | Atendida |
| Spectral | `spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml` executa (ver `contracts/openapi/spectral_lint.log`) | Atendida |
| oasdiff | `scripts/contract_gates/verify_oasdiff.ps1` → `oasdiff version main` (ver `scripts/contract_gates/oasdiff_version.log`) | Atendida |
| Schemathesis | `Hb Track - Backend/.venv/Scripts/schemathesis.exe` disponível, mas sem API local para validar | Parcialmente atendida |
| JSON Schema validator (ajv) | `ajv help` executa (ver `_reports/T1_PROVISIONING_RESULT.md`) | Atendida |
| AsyncAPI CLI | Gate 12 **PASS** no `python scripts/validate_contracts.py` (ver `_reports/contract_gates/latest.json` e `contracts/asyncapi/asyncapi_validate.log`) | Atendida |
| Arazzo linter | Gate `ARAZZO_VALIDATION_GATE` **PASS** no `python scripts/validate_contracts.py` (ver `_reports/contract_gates/latest.json`) | Atendida |
| Intent DSL | `contracts/openapi/intents/ai_ingestion.intent.yaml` + `python3 scripts/contracts/validate/api/compile_api_intent.py --module ai_ingestion --apply --format json` → PASS | Atendida |
| Drift semântico | `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json` → PASS (sem drift); em drift retorna FAIL com `drifts` | Atendida |
| Validator por axiomas | `python3 scripts/validate_contracts.py` → PASS (consome `.contract_driven/DOMAIN_AXIOMS.json`, valida extensões modulares e regras mínimas) | Atendida |
| Contrato de axiomas modulares | `contracts/schemas/shared/domain_axioms_module.schema.json` + `docs/hbtrack/modulos/README.md` | Atendida |
| JSON Schemas SSOT | Existe `contracts/schemas/training/training_session.schema.json` e `ajv compile -s contracts/schemas/training/*.schema.json` → PASS (ver `contracts/schemas/training/ajv_compile.log`) | Atendida |
| AsyncAPI SSOT | Existe `contracts/asyncapi/asyncapi.yaml` + contrato real em `contracts/asyncapi/channels/training_attendance_marked.yaml`; `asyncapi validate` → PASS (warnings de governança em `contracts/asyncapi/asyncapi_validate.log`) | Atendida |
| Workflows SSOT (Arazzo) | Existe `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml`; Gate 13 aplicável e passando (ver `_reports/contract_gates/latest.json`) | Atendida |
| READMEs em contracts/ | Criados: `contracts/openapi/README.md`, `contracts/schemas/README.md`, `contracts/workflows/README.md`, `contracts/asyncapi/README.md` | Atendida |
| Contratos fora da árvore canônica | Removidos de `.bin/atletas/`: schemas movidos para `tools/contract_linter/schemas/` e `04_ATLETAS_WORKFLOWS.arazzo.yaml` removido (era vazio) | Atendida |
| Módulos fora da taxonomia | `.bin/` removida desta branch (`hb-track-contratos-driven`) | Atendida |
| Canon global — completo | `README`, `SYSTEM_SCOPE`, `ARCHITECTURE`, `MODULE_MAP`, `API_CONVENTIONS`, `DATA_CONVENTIONS`, `ERROR_MODEL`, `GLOBAL_INVARIANTS`, `SECURITY_RULES`, `CI_CONTRACT_GATES`, `TEST_STRATEGY`, `UI_FOUNDATIONS`, `DESIGN_SYSTEM`, `C4_CONTEXT`, `C4_CONTAINERS`, `CHANGE_POLICY`, `DOMAIN_GLOSSARY`, `HANDBALL_RULES_DOMAIN` em `docs/_canon/` | Atendida |
| HANDBALL_RULES_DOMAIN | `docs/_canon/HANDBALL_RULES_DOMAIN.md` presente e cobre `training`, `matches`, `scout`, `competitions` | Atendida |
| ADRs (`docs/_canon/decisions/`) | Criados: `ADR-001-contract-driven-development.md`, `ADR-002-uuid-v4-identifiers.md`, `ADR-003-media-type-versioning.md`, `ADR-004-api-policy-compiler-authority.md` | Atendida |

# PROXIMAS TAREFAS

**Ordem recomendada (WSL, 2026-03-13)**: B1 → B3 → (revalidar `python3 scripts/validate_contracts.py`).

> **Nota de ambiente (WSL, 2026-03-13)**:
> - `node.exe` existe em `/mnt/c/Program Files/nodejs/node.exe`, mas o comando `node` não resolve no PATH (bloqueia CLIs via npm).
> - `redocly`, `spectral` e `ajv` existem como CLIs (npm global), mas falham com `node: not found`.
> - `node_modules/.bin/asyncapi` existe, mas o comando falha por `node: not found` no WSL.

> **Nota de ambiente (Windows 11, 2026-03-12)**: `redocly`, `spectral` e `ajv` disponíveis via npm global (ver `_reports/T1_PROVISIONING_RESULT.md`). `schemathesis` disponível no venv do backend.

---
[Tarefa]: B1 Habilitar `node` no WSL (pré-requisito para gates via npm)
[Status]: **Aberta (2026-03-13)**.
[Objetivo]: Fazer `node` ficar disponível no PATH do WSL para destravar `redocly`, `spectral`, `ajv` e `asyncapi`.
[Escopo]: Ajuste de runtime/PATH no ambiente WSL (sem alterar contratos).
[Critérios de aceitação]:
  - `node -v` executa no WSL.
  - `redocly --version` e `spectral --version` executam no WSL (sem `node: not found`).
[Validação]:
  - `node -v`
  - `redocly --version`
  - `spectral --version`
  - `ajv --help`
---

[Tarefa]: B2 Normalizar SSOT de API para o path canônico `.contract_driven/templates/api/*`
[Status]: **Concluída (2026-03-13)**.
[Objetivo]: Fazer `REQUIRED_ARTIFACT_PRESENCE_GATE` passar no WSL criando os artefatos esperados no path canônico (sem mudar o conteúdo SSOT).
[Escopo]: Criar/alinhar:
  - `.contract_driven/templates/api/api_rules.yaml` (origem histórica: `.contract_driven/templates/API_RULES/API_RULES.yaml`)
  - `.contract_driven/templates/api/ARCHITECTURE_MATRIX.yaml` (origem histórica: `.contract_driven/templates/API_RULES/ARCHITECTURE_MATRIX.yaml`)
  - `.contract_driven/templates/api/MODULE_PROFILE_REGISTRY.yaml` (origem histórica: `.contract_driven/templates/API_RULES/MODULE_PROFILE_REGISTRY.yaml`)
  - `.contract_driven/templates/api/CANONICAL_TYPE_REGISTRY.yaml` (origem histórica: `.contract_driven/templates/API_RULES/CANONICAL_TYPE_REGISTRY.yaml`)
  - `.contract_driven/templates/api/REGRAS_API.md` (origem histórica: `.contract_driven/templates/API_RULES/_REGRAS.md`)
  - `.contract_driven/templates/api/GoogleAPI.md` (criado — referências Google API Design Guide)
  - `.contract_driven/templates/api/AddidasAPI.md` (criado — referências Adidas API Guidelines)
  - `.contract_driven/templates/api/OWASPAPI.md` (criado — referências OWASP API Security Top 10)
[Critérios de aceitação]: ✅ **ATENDIDOS**
  - ✅ `python3 scripts/validate_contracts.py` → `REQUIRED_ARTIFACT_PRESENCE_GATE` **PASS**
[Validação]:
  - `python3 scripts/validate_contracts.py` (verificar `REQUIRED_ARTIFACT_PRESENCE_GATE`)
[Artefatos criados]:
  - 8 arquivos em `.contract_driven/templates/api/`
  - (origem legada `.contract_driven/templates/API_RULES/` removida posteriormente para evitar duplicação)
  - 3 criados (GoogleAPI.md, AddidasAPI.md, OWASPAPI.md)
---

[Tarefa]: B3 Provisionar CLIs ausentes no WSL (`asyncapi` e `oasdiff`)
[Status]: **Aberta (2026-03-13)**.
[Objetivo]: Fazer `ASYNCAPI_VALIDATION_GATE` e `CONTRACT_BREAKING_CHANGE_GATE` executarem no WSL.
[Escopo]:
  - Disponibilizar `asyncapi` via `node_modules/.bin/asyncapi` (instalação do `@asyncapi/cli`) ou PATH.
  - Disponibilizar `oasdiff` no PATH (Go install) ou alternativa documentada.
[Critérios de aceitação]:
  - `asyncapi validate contracts/asyncapi/asyncapi.yaml` executa no WSL (exit code 0).
  - `oasdiff` é encontrado e executa (`oasdiff --version` ou equivalente).
[Validação]:
  - `python3 scripts/validate_contracts.py` (verificar `ASYNCAPI_VALIDATION_GATE` e `CONTRACT_BREAKING_CHANGE_GATE`).
---

[Tarefa]: B4 Corrigir `$ref` OpenAPI para serem herméticos (Gate `REF_HERMETICITY_GATE`)
[Status]: **Concluída (2026-03-13)**.
[Objetivo]: Eliminar `$ref` não resolvidos em `contracts/openapi/openapi.yaml` (atualmente refs de operação em `./paths/training.yaml#/...`).
[Escopo]:
  - Ajustar refs quando necessário para apontar para artefatos/pointers existentes.
[Critérios de aceitação]:
  - `python3 scripts/validate_contracts.py` → `REF_HERMETICITY_GATE` PASS.
[Validação]:
  - `python3 scripts/validate_contracts.py`.
---

[Tarefa]: B5 Remover drift em `generated/` (Gate `DERIVED_DRIFT_GATE`)
[Status]: **Concluída (2026-03-13)**.
[Objetivo]: Regenerar artefatos derivados para que `compile_api_policy --check` fique PASS.
[Escopo]:
  - Regenerar `generated/` usando o compiler determinístico (não editar arquivos em `generated/` manualmente).
[Critérios de aceitação]:
  - `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json` retorna PASS (exit code 0).
[Validação]:
  - `python3 scripts/contracts/validate/api/compile_api_policy.py --all --format json`
  - `python3 scripts/contracts/validate/api/compile_api_policy.py --all --check --format json`
---

[Tarefa]: B6 Corrigir violações de alinhamento cross-spec (Gate `CROSS_SPEC_ALIGNMENT_GATE`)
[Status]: **Concluída (2026-03-13)**.
[Objetivo]: Padronizar campos (`createdAt`, `closedAt`, `closedByUserId`, etc.) para usar os patterns/semânticas canônicas (`timestamp_utc`, `uuid_v4`) nas specs onde exigido.
[Escopo]:
  - Ajustar os contratos (ex.: `contracts/openapi/components/schemas/**`) para refletirem os semantic types/patterns canônicos. ✅
[Critérios de aceitação]:
  - `python3 scripts/validate_contracts.py` → `CROSS_SPEC_ALIGNMENT_GATE` PASS (0 violações). ✅
[Validação]:
  - `python3 scripts/validate_contracts.py` (verificar `CROSS_SPEC_ALIGNMENT_GATE`). ✅
[Evidências]:
  - Adicionados patterns canônicos em `contracts/openapi/components/schemas/training/training_session.yaml` (17 campos):
    - timestamp_utc: sessionAt, createdAt, updatedAt, deletedAt, closedAt, startedAt, endedAt, postReviewCompletedAt, postReviewDeadlineAt
    - uuid_v4: id, organizationId, teamId, seasonId, microcycleId, createdByUserId, closedByUserId, postReviewCompletedByUserId
  - Adicionados patterns canônicos em `contracts/openapi/paths/training.yaml` (11 campos inline):
    - POST /training-sessions: organizationId, teamId, seasonId, microcycleId, sessionAt
    - PATCH /training-sessions/{id}: sessionAt
    - POST /training-sessions/{id}/attendance: athleteId (request), attendanceId, athleteId, trainingSessionId, createdAt (response)
  - Corrigidos operationIds em `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml`:
    - create_training_session → createTrainingSession
    - scoped_add_training_attendance → registerTrainingAttendance
  - Regenerados artefatos derivados (2 arquivos): generated/contracts/openapi/paths/training.yaml, generated/manifests/training.sync.traceability.yaml
  - `CROSS_SPEC_ALIGNMENT_GATE`: PASS (validado 2026-03-13)
  - `DERIVED_DRIFT_GATE`: PASS após regeneração
---

[Tarefa]: B7 Corrigir conversão de paths WSL→Windows nos gates (OPENAPI_ROOT_STRUCTURE_GATE e OPENAPI_POLICY_RULESET_GATE)
[Status]: **Concluída (2026-03-13)**.
[Objetivo]: Fazer ferramentas npm (redocly, spectral) funcionarem corretamente quando executadas de dentro do WSL com paths WSL.
[Escopo]:
  - Adicionar função helper `_wsl_to_windows_path()` em `scripts/contracts/validate/validate_contracts.py`.
  - Converter paths `/mnt/c/...` para `C:\...` antes de passar para redocly e spectral.
[Critérios de aceitação]:
  - `python3 scripts/validate_contracts.py` → `OPENAPI_ROOT_STRUCTURE_GATE` PASS. ✅
  - `python3 scripts/validate_contracts.py` → `OPENAPI_POLICY_RULESET_GATE` PASS. ✅
  - Pipeline completo: Overall PASS, Exit code 0. ✅
[Validação]:
  - `python3 scripts/validate_contracts.py`. ✅
[Evidências]:
  - Criada função `_wsl_to_windows_path()` que converte `/mnt/c/HB TRACK/file.yaml` → `C:\HB TRACK\file.yaml`
  - Modificado `_g5_openapi_root_structure()` para converter paths antes de chamar redocly
  - Modificado `_g6_openapi_policy_ruleset()` para converter paths antes de chamar spectral
  - `OPENAPI_ROOT_STRUCTURE_GATE`: PASS (validado 2026-03-13)
  - `OPENAPI_POLICY_RULESET_GATE`: PASS (validado 2026-03-13)
  - Pipeline completo: **Overall: PASS, Exit code: 0** (validado 2026-03-13)
  - **14 de 14 gates bloqueantes passando (100%)**
---

[Tarefa]: B0 Desbloquear permissão de edição nos paths canônicos (pré-requisito de execução)
[Status]: **Resolvida (2026-03-11)** — já houve edição real em `docs/`, `contracts/`, `.contract_driven/` e `scripts/`.
[Objetivo]: Permitir executar T0–T4 sem violar a regra “editar somente `CHECKLIST.md`”.
[Escopo]: Apenas autorização/ajuste de restrição para permitir edição em:
  - `docs/_canon/`
  - `contracts/`
  - `.contract_driven/`
  - `scripts/`
  - `.spectral.yaml` (raiz)
[Regra de escopo] (explícita):
  - Permitido: editar/criar arquivos apenas em `docs/_canon/`, `contracts/`, `.contract_driven/`, `scripts/`, `.spectral.yaml` e `CHECKLIST.md`.
  - Proibido: qualquer alteração fora dos paths acima.
[Critérios de aceitação]:
  - Existe autorização explícita para editar os paths acima (e continuar proibindo alterações fora deles).
[Critérios de rejeição]:
  - Liberação genérica de edição fora dos paths canônicos acima.
[Critérios de bloqueio]:
  - Instrução ativa de “editar somente `CHECKLIST.md`”.
[Comandos permitidos]:
  - Nenhum (decisão/ajuste de restrição).
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Confirmação explícita da regra de escopo de edição para a próxima execução.
[Definition of Done]:
  - Bloqueio removido e escopo de edição definido.
**Saída esperada**:
  - Permissão registrada para execução das tarefas T0–T4.
---

[Tarefa]: T1 Provisionar runtime + CLIs para gates 1–2 e 5
[Status]: **Concluída (2026-03-11)** — ver `_reports/T1_PROVISIONING_RESULT.md`.
[Artefatos]: `scripts/contract_gates/env.sh`, `scripts/contract_gates/env.ps1`, `scripts/contract_gates/verify_tools.sh`, `scripts/contract_gates/verify_tools.ps1`.
  - *Subtarefa 1.1*: Padronizar `PATH` no ambiente de execução (CI/local) para incluir `node` e os binários das CLIs.
  - *Subtarefa 1.2*: Garantir execução de `redocly`, `spectral` e `ajv` no ambiente de execução.
[Objetivo]: Ter as ferramentas executáveis de forma reprodutível (mesmos comandos para qualquer executor).
[Escopo]: Ambiente e executabilidade de ferramentas; não inclui corrigir contratos.
[Critérios de aceitação]:
  - `node -v` e `npm -v` executam no ambiente alvo.
  - `redocly --version`, `spectral --version` e `ajv help` executam no ambiente alvo.
[Critérios de rejeição]:
  - Ferramenta não executa sem intervenção manual fora do procedimento definido.
[Critérios de bloqueio]:
  - Sem runtime Node no ambiente alvo.
[Comandos permitidos]:
  - `node -v`, `npm -v`, `redocly --version`, `spectral --version`, `ajv help`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Executar os comandos de versão/ajuda e registrar saída.
[Definition of Done]:
  - Ferramentas executam no ambiente alvo sem erro de runtime.
**Saída esperada**:
  - Procedimento documentado (passos + comandos) para provisionar/rodar as ferramentas.
---

[Tarefa]: T0 Completar canon global mínimo faltante em `docs/_canon/` (pré-requisito de governança)
[Status]: **Resolvida (2026-03-11)** — os artefatos listados já existem em `docs/_canon/`.
[Artefatos]: `docs/_canon/ERROR_MODEL.md`, `docs/_canon/GLOBAL_INVARIANTS.md`, `docs/_canon/SECURITY_RULES.md`, `docs/_canon/UI_FOUNDATIONS.md`, `docs/_canon/DESIGN_SYSTEM.md`, `docs/_canon/CI_CONTRACT_GATES.md`, `docs/_canon/TEST_STRATEGY.md`, `docs/_canon/C4_CONTEXT.md`, `docs/_canon/C4_CONTAINERS.md`.
  - *Subtarefa 0.1*: Criar os artefatos canônicos globais ausentes usando os templates oficiais em `.contract_driven/GLOBAL_TEMPLATES.md`:
    - `docs/_canon/ERROR_MODEL.md` (template seção 14)
    - `docs/_canon/GLOBAL_INVARIANTS.md` (template seção 15)
    - `docs/_canon/SECURITY_RULES.md` (template seção 18)
    - `docs/_canon/UI_FOUNDATIONS.md` (template seção 19)
    - `docs/_canon/DESIGN_SYSTEM.md` (template seção 20)
    - `docs/_canon/CI_CONTRACT_GATES.md` (template seção 21)
    - `docs/_canon/TEST_STRATEGY.md` (template seção 22)
    - `docs/_canon/C4_CONTEXT.md` (template seção 8)
    - `docs/_canon/C4_CONTAINERS.md` (template seção 9)
[Objetivo]: Eliminar lacunas de canon global que impedem gates, convenções e rastreabilidade.
[Escopo]: Apenas `docs/_canon/` (artefatos listados no manual); sem criação de novos artefatos fora do template.
[Critérios de aceitação]:
  - Todos os arquivos acima existem em `docs/_canon/` e não contêm placeholders proibidos.
[Critérios de rejeição]:
  - Introduzir regra normativa que conflite com `.contract_driven/CONTRACT_SYSTEM_RULES.md` ou `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`.
[Comandos permitidos]:
  - Edição/criação de arquivos em `docs/_canon/`.
  - Leitura local de `.contract_driven/GLOBAL_TEMPLATES.md`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Conferir presença no filesystem + revisão manual de ausência de placeholders.
[Definition of Done]:
  - Canon global mínimo completo e pronto para ser referenciado por módulos e gates.
[Saída esperada]:
  - Os 9 arquivos canônicos criados em `docs/_canon/` conforme templates.
---

[Tarefa]: T3 Corrigir falha de Redocly (Gate 1) reportada em `contracts/openapi/openapi.yaml`
[Status]: **Concluída (2026-03-12)** — Gate 1 passou após inclusão de `servers:` (ver `contracts/openapi/openapi.yaml` e `contracts/openapi/redocly_lint.log`).
[Observação]: O OpenAPI ainda é esqueleto (`paths: {}`) e não representa “conteúdo real” de endpoints.
  - *Subtarefa 3.1*: Incluir `servers:` em `contracts/openapi/openapi.yaml` (erro atual do Redocly).
  - *Subtarefa 3.2*: Re-rodar `redocly lint contracts/openapi/openapi.yaml` e registrar output.
[Objetivo]: Fazer Gate 1 passar sem erros.
[Escopo]: Apenas o erro explícito atual do Redocly (não adicionar comportamento/rotas novas).
[Critérios de aceitação]:
  - `redocly lint contracts/openapi/openapi.yaml` retorna exit code 0.
[Critérios de rejeição]:
  - Alterações fora do escopo do erro atual sem justificativa normativa.
[Criterios de bloqueio]:
  - Restrições que impeçam editar `contracts/openapi/openapi.yaml`.
[Comandos permitidos]:
  - Edição de `contracts/openapi/openapi.yaml`.
  - `redocly lint contracts/openapi/openapi.yaml`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Rodar Redocly e registrar exit code.
[Definition of Done]:
  - Gate 1 passa.
[Saída esperada]:
  - `contracts/openapi/openapi.yaml` ajustado + log do Redocly.
---


[Tarefa]: T2 Criar artefato `.spectral.yaml` (Gate 2)
[Status]: **Concluída (2026-03-12)** — ver `.spectral.yaml` e `contracts/openapi/spectral_lint.log`.
[Artefatos]: `.spectral.yaml`, `contracts/openapi/spectral_lint.log`.
  - *Subtarefa 2.1*: Criar `.spectral.yaml` na raiz do repositório, alinhado à SSOT de convenções/templates de API (`.contract_driven/templates/api/api_rules.yaml`) e às regras de validação (`docs/_canon/CI_CONTRACT_GATES.md` template em `.contract_driven/GLOBAL_TEMPLATES.md` seção 21). `docs/_canon/API_CONVENTIONS.md` é ponteiro (não-SSOT).
  - *Subtarefa 2.2*: Executar `spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml` e registrar output.
[Objetivo]: Habilitar Gate 2 com ruleset versionado.
[Escopo]: Apenas criação do ruleset e execução do lint.
[Critérios de aceitação]:
  - `.spectral.yaml` existe.
  - `spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml` executa e retorna resultado real (0 se OK; !=0 se violações).
[Criterios de rejeição]:
  - Ruleset inventa convenções não presentes na SSOT de API nem no canon/manual.
[Criterios de bloqueio]:
  - Ausência de `docs/_canon/CI_CONTRACT_GATES.md` (se a política de gates for tratada como obrigatória no canon).
[Comandos permitidos]:
  - Edição/criação de `.spectral.yaml`.
  - `spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Rodar o comando Spectral e registrar exit code.
[Definition of Done]:
  - Gate 2 executável com `.spectral.yaml` presente.
[Saída esperada]:
  - `.spectral.yaml` + log do lint.
---


[Tarefa]: T4 Criar ao menos 1 schema SSOT real (Gate 5)
[Status]: **Concluída (2026-03-12)** — ver `contracts/schemas/training/training_session.schema.json` e `contracts/schemas/training/ajv_compile.log`.
[Artefatos]: `contracts/schemas/training/training_session.schema.json`, `contracts/schemas/training/ajv_compile.log`.
  - *Subtarefa 4.1*: Criar `contracts/schemas/<module>/<entity>.schema.json` usando o template de `.contract_driven/GLOBAL_TEMPLATES.md` seção 35.
  - *Subtarefa 4.2*: Validar schema (ex.: `ajv compile -s contracts/schemas/<module>/*.schema.json`) e registrar output.
[Objetivo]: Tornar Gate 5 aplicável com schema real.
[Escopo]: Apenas `contracts/schemas/` (SSOT de domínio).
[Critérios de aceitação]:
  - Existe ao menos 1 `*.schema.json` em `contracts/schemas/<module>/`.
  - AJV valida/compila o(s) schema(s) sem erro.
[Criterios de rejeição]:
  - Criar schema placeholder sem entidade real definida pelo módulo.
[Criterios de bloqueio]:
  - Restrições que impeçam editar/criar arquivos em `contracts/schemas/`.
[Comandos permitidos]:
  - Edição/criação de `contracts/schemas/<module>/*.schema.json`.
  - `ajv compile -s contracts/schemas/<module>/*.schema.json`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Rodar AJV e registrar exit code.
[Definition of Done]:
  - Gate 5 executável para pelo menos 1 módulo.
[Saída esperada]:
  - `contracts/schemas/<module>/<entity>.schema.json` + log do AJV.
---


[Tarefa]: T6 Criar 1 extensão modular real de `event_type` (enforcement semântico)
[Status]: **Concluída (2026-03-12)** — `python scripts/validate_contracts.py` → PASS (exit code 0). Ver `docs/hbtrack/modulos/training/DOMAIN_AXIOMS_TRAINING.json` e `_reports/contract_gates/latest.json`.
[Artefatos]: `docs/hbtrack/modulos/training/DOMAIN_AXIOMS_TRAINING.json`, `_reports/contract_gates/latest.json`.
  - *Subtarefa 6.1*: Criar 1 módulo em `docs/hbtrack/modulos/<module>/` com `DOMAIN_AXIOMS_<MODULE>.json` seguindo `contracts/schemas/shared/domain_axioms_module.schema.json`.
  - *Subtarefa 6.2*: Declarar ao menos 1 `event_type` novo como objeto com:
    - `name`
    - `semantic_id`
    - `description`
    - `payload_constraints.required_fields`
    - `payload_constraints.field_formats`
  - *Subtarefa 6.3*: Rodar `python3 scripts/validate_contracts.py` e registrar PASS/FAIL.
[Objetivo]: Exercitar o contrato de extensões modulares com colisão semântica determinística (sem merge “mudo”).
[Escopo]: Somente `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json` + evidência de execução do validador.
[Critérios de aceitação]:
  - `python3 scripts/validate_contracts.py` retorna exit code 0 com a extensão presente.
  - O arquivo modular contém `event_type` com valores em formato objeto (não string).
[Critérios de rejeição]:
  - Extensão declarar `event_type` como lista de strings (perde semântica verificável).
  - Colisão semântica gerar erro genérico sem detalhes (deve usar `BLOCKED_AXIOM_EXTENSION_COLLISION` com payload específico).
---

[Tarefa]: T7 Criar 1 contrato AsyncAPI SSOT real (Gate 12)
[Status]: **Concluída (2026-03-12)** — `asyncapi validate contracts/asyncapi/asyncapi.yaml` → PASS (exit code 0; warnings de governança não-bloqueantes). Ver `contracts/asyncapi/asyncapi_validate.log`.
[Artefatos]: `contracts/asyncapi/asyncapi.yaml`, `contracts/asyncapi/channels/training_attendance_marked.yaml`, `contracts/asyncapi/messages/training_attendance_marked.yaml`, `contracts/asyncapi/components/schemas/training_attendance_marked_payload.yaml`.
[Objetivo]: Tornar o Gate 12 aplicável com contrato AsyncAPI real (sem placeholder).
[Escopo]: Apenas `contracts/asyncapi/**`.
[Critérios de aceitação]:
  - Existe `contracts/asyncapi/asyncapi.yaml` com pelo menos 1 canal/mensagem real.
  - `asyncapi validate contracts/asyncapi/asyncapi.yaml` retorna exit code 0.
[Critérios de bloqueio]:
  - AsyncAPI CLI ausente no ambiente alvo.
[Comandos permitidos]:
  - Edição/criação de `contracts/asyncapi/**/*.yaml`.
  - `asyncapi validate contracts/asyncapi/asyncapi.yaml`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Rodar `asyncapi validate` e registrar exit code.
[Definition of Done]:
  - Gate 12 executável e validando o contrato AsyncAPI.
[Saída esperada]:
  - `contracts/asyncapi/asyncapi.yaml` + `contracts/asyncapi/asyncapi_validate.log`.
---

[Tarefa]: T8 Criar 1 workflow Arazzo SSOT real (Gate 13)
[Status]: **Concluída (2026-03-12)** — `python scripts/validate_contracts.py` → `PASS_WITH_WARNINGS` (exit code 0) com `ARAZZO_VALIDATION_GATE` aplicável e passando. Evidência em `_reports/contract_gates/latest.json`.
[Artefatos]: `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml`, `contracts/openapi/paths/training.yaml`.
[Objetivo]: Tornar Gate 13 aplicável com workflow multi-step real, linkado a `operationId` existente no OpenAPI.
[Escopo]: `contracts/workflows/training/*.arazzo.yaml` + `contracts/openapi/paths/training.yaml`.
[Critérios de aceitação]:
  - Existe ao menos 1 `contracts/workflows/training/*.arazzo.yaml` real (não placeholder).
  - `python scripts/validate_contracts.py` retorna exit code 0 com `ARAZZO_VALIDATION_GATE` aplicável.
[Critérios de rejeição]:
  - Workflow de 1 step (não é multi-step).
  - Referenciar `operationId` inexistente nos arquivos em `contracts/openapi/paths/`.
[Critérios de bloqueio]:
  - Restrições que impeçam editar/criar arquivos em `contracts/workflows/` ou `contracts/openapi/paths/`.
[Comandos permitidos]:
  - Edição/criação em `contracts/workflows/` e `contracts/openapi/paths/`.
  - `python scripts/validate_contracts.py`.
[Comandos proibidos]:
  - `git` (qualquer subcomando).
[Validação]:
  - Rodar `python scripts/validate_contracts.py` e registrar exit code.
[Definition of Done]:
  - Gate 13 executável e passando no ambiente alvo.
[Saída esperada]:
  - `contracts/workflows/training/*.arazzo.yaml` + evidência no relatório `_reports/contract_gates/latest.json`.
---
