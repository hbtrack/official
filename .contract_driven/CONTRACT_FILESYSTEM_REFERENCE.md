# CONTRACT_FILESYSTEM_REFERENCE.md

> Referência técnica de estrutura de filesystem. Documento informativo apenas.
> Fonte normativa: [CONTRACT_SYSTEM_LAYOUT.md](CONTRACT_SYSTEM_LAYOUT.md) seção 4.

---

## 0. Estrutura completa de contracts/

```text
contracts/
  openapi/
    openapi.yaml                  # Raiz do OpenAPI
    paths/
      users.yaml
      seasons.yaml
      teams.yaml
      training.yaml
      wellness.yaml
      medical.yaml
      competitions.yaml
      matches.yaml
      scout.yaml
      exercises.yaml
      analytics.yaml
      reports.yaml
      ai_ingestion.yaml
      identity_access.yaml
      audit.yaml
      notifications.yaml
    components/
      schemas/
        shared/                   # Schemas compartilhados
        users/
        seasons/
        teams/
        training/
        wellness/
        medical/
        competitions/
        matches/
        scout/
        exercises/
        analytics/
        reports/
        ai_ingestion/
        identity_access/
        audit/
        notifications/
      parameters/
      responses/
      requestBodies/
      securitySchemes/
      examples/

  schemas/                        # Domain shapes canônicos
    shared/
    users/
    seasons/
    teams/
    training/
    wellness/
    medical/
    competitions/
    matches/
    scout/
    exercises/
    analytics/
    reports/
    ai_ingestion/
    identity_access/
    audit/
    notifications/

  workflows/                      # Arazzo (workflow orchestration)
    _global/
    users/
    seasons/
    teams/
    training/
    wellness/
    medical/
    competitions/
    matches/
    scout/
    exercises/
    analytics/
    reports/
    ai_ingestion/
    identity_access/
    audit/
    notifications/

  asyncapi/                       # AsyncAPI (event contracts)
    asyncapi.yaml               # Raiz do AsyncAPI
    channels/
    operations/
    messages/
    components/
      schemas/
      messageTraits/
      operationTraits/

  _waivers/                       # Waivers (exceções documentadas)
    README.md
    <waiver_files>
```

---

## 1. Gerado (artefatos derivados)

```text
generated/
  contracts/
    openapi/                   # OpenAPI gerado/resolvido
    asyncapi/                  # AsyncAPI gerado/resolvido
  manifests/                   # Manifestos de rastreabilidade
  resolved_policy/             # Policy resolvida por módulo/surface
```

---

## 2. Relatórios (_reports)

```text
_reports/
  contract_gates/              # Resultados de gates de contrato
    latest.json
    CONFORMIDADE_EMPIRICA.md
    SPECTRAL_AUDIT_*.md
  agent_execution/             # Logs de execução do agente
  dispatch/                    # Dispatch de tarefas
  evidence/                    # Evidência de readiness
    module_readiness_scorecard.json
    boot_resolution_report.json
  runs/                        # Histórico de execuções
    20260317T205708_5e6898/
    20260317T205844_e1a6c4/
    ...
```

---

## 3. Documentação humana normativa

```text
.contract_driven/
  CONTRACT_SYSTEM_LAYOUT.md          # Layout canônico (normativo)
  CONTRACT_SYSTEM_RULES.md           # Regras operacionais (normativo)
  GLOBAL_TEMPLATES.md                # Índice de templates (normativo)
  PLACEHOLDER_REGISTRY.md            # Registro de placeholders (referência)
  BOOT_PROFILES.yaml                 # Boot profiles (normativo)
  TASK_CATALOG.yaml                  # Task routing (normativo)
  OPERATIONS.md                      # Operações rápidas (referência)
  agent_prompts/
    pre_contract_orchestrator.prompt.md
    decision_discovery.prompt.md
  templates/
    README.md
    globais/                         # Globais (scaffolds)
    modulos/                         # Por módulo (scaffolds)
    api/
      api_rules.yaml                 # Regras de API (normativo)

docs/_canon/
  README.md
  OPERATIONS.md                      # Referência operacional rápida
  SYSTEM_SCOPE.md
  ARCHITECTURE.md
  C4_CONTEXT.md
  C4_CONTAINERS.md
  MODULE_REGISTRY.yaml               # 17 módulos canônicos (normativo SSOT)
  MODULE_MAP.md
  CHANGE_POLICY.md
  DATA_CONVENTIONS.md
  GLOBAL_INVARIANTS.md
  DOMAIN_GLOSSARY.md
  HANDBALL_RULES_DOMAIN.md
  SECURITY_RULES.md
  CI_CONTRACT_GATES.md
  TEST_STRATEGY.md
  TOOLCHAIN_HEALTH_POLICY.md
  gates/
    GATES_REGISTRY.yaml              # Gates de contrato (normativo SSOT)
  decisions/
    ADR-0001-template.md
    ADR-XXXX-*.md

docs/hbtrack/modulos/
  <MODULE>/
    README.md
    MODULE_SCOPE_<MODULE_UPPER>.md
    DOMAIN_RULES_<MODULE_UPPER>.md
    INVARIANTS_<MODULE_UPPER>.md
    STATE_MODEL_<MODULE_UPPER>.md
    PERMISSIONS_<MODULE_UPPER>.md
    ERRORS_<MODULE_UPPER>.md
    UI_CONTRACT_<MODULE_UPPER>.md
    SCREEN_MAP_<MODULE_UPPER>.md
    TEST_MATRIX_<MODULE_UPPER>.md
    SPORT_SCIENCE_RULES_<MODULE_UPPER>.md
```

---

## 4. Referência cruzada

| Path | Tipo | Escopo | Referência |
|--|--|--|--|
| `.contract_driven/` | system | Especificação CDD | CONTRACT_SYSTEM_LAYOUT.md §4A.1 |
| `contracts/` | technical | Artefatos de contrato | CONTRACT_SYSTEM_LAYOUT.md §4 |
| `generated/` | derived | Derivados de contratos | CONTRACT_SYSTEM_LAYOUT.md §4.1 |
| `_reports/` | derived | Evidência e gates | CONTRACT_SYSTEM_LAYOUT.md §4.1 |
| `docs/_canon/` | system | Canon normativo global | CONTRACT_SYSTEM_LAYOUT.md §4A.2 |
| `docs/hbtrack/modulos/<MODULE>/` | system | Module documentation | CONTRACT_SYSTEM_LAYOUT.md §4A.3 |
