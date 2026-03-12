# CONTRACT_SYSTEM_LAYOUT.md

## 0. Índice cruzado

Este documento faz parte da trilogia **HB Track — Manual Contract-Driven**:

1. **.contract_driven/CONTRACT_SYSTEM_LAYOUT.md** (este arquivo)
   - **Responsabilidade**: Estrutura canônica de filesystem, taxonomia de módulos, convenções de nomenclatura, regras de localização de artefatos
   - **Use quando**: Definir onde criar artefatos, validar nomes de módulos, checar regras de naming

2. **.contract_driven/CONTRACT_SYSTEM_RULES.md**
   - **Responsabilidade**: Regras operacionais, hierarquia de precedência, boot protocol do agente, códigos de bloqueio, ferramentas de validação, procedimentos de evolução
   - **Use quando**: Entender como criar/modificar contratos, determinar precedência em conflitos, comportamento de bloqueio, passos de validação

3. **.contract_driven/GLOBAL_TEMPLATES.md**
   - **Responsabilidade**: Scaffolds e exemplos oficiais para documentação normativa e artefatos de contrato
   - **Use quando**: Criar novos docs de módulo, contratos, ou artefatos de governança

4. **.contract_driven/templates/api_rules/api_rules.yaml**
   - **Responsabilidade**: Regras, validações e templates canônicos para contratos de APIs (OpenAPI/HTTP)
   - **Use quando**: Definir convenções de API, segurança OWASP, semântica Google AIP e estilo Adidas

**Regra de navegação**: Estes arquivos devem ser lidos em conjunto. Referências cruzadas entre eles são explícitas e vinculantes.

---

## 1. Objetivo
Este documento define o layout canônico de filesystem, regras de localização de artefatos e regras de nomenclatura para artefatos de contrato e paths de documentação normativa no HB Track.

Ele governa:
- `contracts/openapi/`
- `contracts/schemas/`
- `contracts/workflows/`
- `contracts/asyncapi/`
- paths canônicos para documentação humana normativa relacionada ao sistema de contratos

Ele **não** substitui:
- a autoridade de conteúdo da documentação humana global (`docs/_canon/README.md` como canon; `README.md` como landing/entry; além de `SYSTEM_SCOPE.md`, `ARCHITECTURE.md`, `C4_CONTEXT.md`, `C4_CONTAINERS.md`, `UI_FOUNDATIONS.md`, `DESIGN_SYSTEM.md`, etc.)
- a autoridade de conteúdo da documentação humana por módulo (`docs/hbtrack/modulos/<module>/...`)
- regras operacionais (`.contract_driven/CONTRACT_SYSTEM_RULES.md`)
- templates/scaffolds (SSOT em `.contract_driven/templates/` — ver `globais/` e `modulos/`; índice em `.contract_driven/GLOBAL_TEMPLATES.md`)
- **convenções, regras de design HTTP e templates canônicos de API** — responsabilidade exclusiva de `.contract_driven/templates/api_rules/api_rules.yaml` (seção `contract_templates`)

---

## 1A. Tabela única de classificação de artefatos

| Classe | Soberano? | Path canônico | Template SSOT | Derivados (obrigatório) |
|---|---:|---|---|---|
| Governança do sistema de contratos | Sim | `.contract_driven/*` | N/A | `_reports/` (evidências), `generated/` (gerados) |
| Templates globais (canon humano) | Não (scaffold) | `.contract_driven/templates/globais/*` | `.contract_driven/templates/globais/*` | N/A |
| Templates de módulo (docs + schemas) | Não (scaffold) | `.contract_driven/templates/modulos/*` | `.contract_driven/templates/modulos/*` | N/A |
| SSOT de API HTTP (regras/validações/templates) | Sim | `.contract_driven/templates/api_rules/api_rules.yaml` | N/A | N/A |
| Canon global (docs) | Sim | `docs/_canon/*` | `.contract_driven/templates/globais/*` | `_reports/` (evidências) |
| Docs normativos de módulo | Sim | `docs/hbtrack/modulos/<module>/*` | `.contract_driven/templates/modulos/*` | `_reports/` (evidências) |
| Contrato OpenAPI | Sim | `contracts/openapi/*` | `.contract_driven/templates/api_rules/api_rules.yaml` (HTTP) | `generated/openapi/*` |
| Schemas de domínio (JSON Schema) | Sim | `contracts/schemas/*` | `.contract_driven/templates/modulos/schemas/*` | `generated/clients/*`, `generated/ui-types/*` |
| Workflows (Arazzo) | Sim | `contracts/workflows/*` | N/A | `generated/*` |
| Eventos (AsyncAPI) | Sim | `contracts/asyncapi/*` | N/A | `generated/asyncapi/*` |

Regras:
- `templates/*` são **SSOT de scaffold**: agentes DEVEM instanciar artefatos copiando destas fontes (não improvisar estrutura).
- Artefatos em `_reports/` e `generated/` são sempre derivados e nunca sobrepõem fontes soberanas.

---

## 2. Taxonomia canônica de módulos

Se um módulo não estiver listado aqui, ele não existe.

### 2.1 Módulos de domínio funcional
- `users`
- `seasons`
- `teams`
- `training`
- `wellness`
- `medical`
- `competitions`
- `matches`
- `scout`
- `exercises`
- `analytics`
- `reports`
- `ai_ingestion`

### 2.2 Módulos transversais formais
- `identity_access`
- `audit`
- `notifications`

### 2.3 Boundary crítico
- `users` = domínio de pessoa/profile
- `identity_access` = authentication, authorization, credentials, sessions, MFA, JWT, RBAC

### 2.4 Regras negativas de boundary
- nenhum artefato sob `users` pode definir política de autenticação ou autorização
- nenhum artefato sob `identity_access` pode redefinir profile, biography ou dados de identidade funcional pessoal
- se uma responsabilidade sobrepõe os dois módulos, o conflito deve ser resolvido por boundary explícito em contrato ou por ADR

---

## 3. Idioma canônico

### 3.1 Inglês obrigatório para identificadores técnicos
Os itens abaixo devem sempre estar em inglês:
- nomes de módulos
- nomes de pastas de contrato
- OpenAPI paths
- operationIds
- JSON property names
- schema filenames
- Arazzo filenames
- AsyncAPI filenames
- nomes de eventos
- nomes de tabelas/colunas de DB
- nomes de tipos gerados

### 3.2 Português obrigatório para conteúdo de documentação humana
O conteúdo de documentação humana em `docs/**/*.md` e `.contract_driven/**/*.md` deve ser escrito em português, exceto por:
- código (code blocks, exemplos, snippets)
- chaves e valores técnicos (keys)
- identificadores técnicos (ver seção 3.1)
- snippets normativos citados/colados quando necessários
- comandos de ferramenta/CLI
- exemplos gerados quando exigidos por tooling
- keywords MUST/SHOULD/MAY (devem permanecer exatamente como estão)

### 3.3 Proibição de identificador misto
Misturar idiomas dentro do mesmo identificador técnico é proibido.

Exemplos de identificadores proibidos:
- `treinosSession`
- `usuario_profile`
- `cadastroAuth`

---

## 4. Árvore canônica de contratos

```text
contracts/
  openapi/
    openapi.yaml
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
      parameters/
      responses/
      requestBodies/
      securitySchemes/
      examples/

  schemas/
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

  workflows/
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

  asyncapi/
    asyncapi.yaml
    channels/
    operations/
    messages/
    components/
      schemas/
      messageTraits/
      operationTraits/
```

### 4.1 Local canônico para artefatos derivados
Artefatos derivados devem viver fora das fontes soberanas de contrato.

Local canônico obrigatório:

```text
generated/
  openapi/
  asyncapi/
  clients/
  ui-types/
  docs/
  storybook/

_reports/
  contract_gates/
  test_runs/
  evidence/
```

Nenhum artefato gerado pode ser commitado como se fosse soberano.

---

## 4A. Paths canônicos para documentação humana normativa

O HB Track usa os seguintes paths canônicos para documentação humana normativa relacionada ao sistema de contratos e governança de contratos por módulo.

### 4A.1 Contract-system governance
Estes arquivos vivem em:

- `.contract_driven/`

Arquivos canônicos:
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/GLOBAL_TEMPLATES.md`

Templates SSOT (scaffolds) vivem em:
- `.contract_driven/templates/README.md`
- `.contract_driven/templates/globais/`
- `.contract_driven/templates/modulos/`
- `.contract_driven/templates/api_rules/` (SSOT de convenções/validações/templates de API HTTP)

### 4A.2 Global normative canon
Estes arquivos vivem em:

- `docs/_canon/`

Arquivos canônicos:
- `docs/_canon/README.md`
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/ARCHITECTURE.md`
- `docs/_canon/MODULE_MAP.md`
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/API_CONVENTIONS.md`
- `docs/_canon/DATA_CONVENTIONS.md`
- `docs/_canon/ERROR_MODEL.md`
- `docs/_canon/GLOBAL_INVARIANTS.md`
- `docs/_canon/DOMAIN_GLOSSARY.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/SECURITY_RULES.md`
- `docs/_canon/CI_CONTRACT_GATES.md`
- `docs/_canon/TEST_STRATEGY.md`
- `docs/_canon/C4_CONTEXT.md`
- `docs/_canon/C4_CONTAINERS.md`
- `docs/_canon/UI_FOUNDATIONS.md`
- `docs/_canon/DESIGN_SYSTEM.md`
- `docs/_canon/decisions/ADR-*.md`

### 4A.3 Documentação normativa de módulo
Estes arquivos vivem em:

- `docs/hbtrack/modulos/<module>/`

Arquivos canônicos:
- `docs/hbtrack/modulos/<module>/README.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MOD>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MOD>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MOD>.md`
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MOD>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MOD>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MOD>.md`
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MOD>.md`
- `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MOD>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MOD>.md`

### 4A.4 Contratos técnicos
Contratos técnicos vivem em:

- `contracts/`

Regra:
Um artefato normativo colocado fora do seu path canônico é estruturalmente não-compliant, a menos que um ADR explícito diga o contrário.

Artefatos canônicos ausentes:
- Se um artefato canônico necessário para a tarefa atual estiver ausente do seu path canônico, o agente deve bloquear com `BLOCKED_MISSING_CANON_ARTIFACT` (ver `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 9) em vez de inventar conteúdo.

---

## 5. Soberania por camada

### 5.1 Interface pública HTTP
Fonte primária da verdade:
- `contracts/openapi/openapi.yaml`

### 5.2 Shapes de dados reutilizáveis
Fonte primária da verdade:
- `contracts/schemas/<module>/*.schema.json`

### 5.3 Orquestração multi-step
Fonte primária da verdade:
- `contracts/workflows/**/*.arazzo.yaml`

### 5.4 Contratos de eventos
Fonte primária da verdade:
- `contracts/asyncapi/**/*.yaml`

### 5.5 Regra
Nenhuma superfície pode ter duas fontes primárias da verdade.

### 5.6 Regra de superfície derivada
Artefatos gerados/derivados podem existir para qualquer superfície, mas nunca substituem a fonte primária definida acima.

---

## 6. Regras de layout de OpenAPI
**Nota**: Este documento define apenas **layout/estrutura**. As convenções e regras de **design/validação** de APIs vivem em `.contract_driven/templates/api_rules/api_rules.yaml`.
- `contracts/openapi/openapi.yaml` é o entrypoint.
- `contracts/openapi/paths/<module>.yaml` contém path items de apenas um módulo.
- `contracts/openapi/components/schemas/shared/` contém schemas compartilhados HTTP-facing.
- `contracts/openapi/components/schemas/<module>/` contém schemas HTTP-facing específicos do módulo.
- OpenAPI pode usar `$ref` para schemas em `contracts/schemas/` quando o pipeline suportar isso sem ambiguidade.
- Nenhum arquivo de paths pode conter rotas de dois módulos.
- Um módulo não deve expor silenciosamente a superfície pública de outro módulo através do seu próprio arquivo de paths.
### 6.1 OpenAPI Schema Reference Policy

**Regra padrão**: OpenAPI paths devem referenciar schemas em `components/schemas/<module>/` para shapes HTTP-facing.

**Exceção permitida**: OpenAPI pode usar `$ref` direto para `contracts/schemas/` **somente quando**:
- a shape é semanticamente idêntica entre HTTP e domínio (zero adaptação/envelope)
- o pipeline suporta $ref externo sem transformação (validado por Redocly CLI)
- há justificativa documentada de que reuso direto não cria acoplamento indesejado

**Regra de conflito**: Se houver divergência entre shape HTTP e shape de domínio (envelopes, campos extras, adaptação), usar `components/schemas/` obrigatoriamente.

**Soberania preservada**: `contracts/schemas/` permanece SSOT de shapes de domínio; `components/schemas/` contém apenas adaptações HTTP quando necessárias.
---

## 7. Regras de layout de JSON Schema
- `contracts/schemas/<module>/` contém shapes de dados reutilizáveis, escopadas por módulo.
- `contracts/schemas/shared/` contém shapes reutilizadas entre módulos.
- Filenames devem terminar em `.schema.json`.
- JSON Schemas são shapes reutilizáveis de domínio/dados, não substitutos do contrato HTTP.
- Se o mesmo conceito existir em schema OpenAPI-facing e em schema reutilizável, a soberania de cada superfície deve permanecer explícita.

---

## 8. Regras de layout de Arazzo
- `contracts/workflows/_global/` é reservado para workflows cross-module.
- `contracts/workflows/<module>/` é reservado para workflows do módulo.
- Um workflow file é permitido apenas quando a orquestração multi-step for real e relevante.
- Um workflow file deve representar um use case nomeado.
- Filenames de workflows devem descrever o use case, não o detalhe de implementação.

---

## 9. Regras de layout de AsyncAPI
- `contracts/asyncapi/asyncapi.yaml` é o documento raiz.
- `channels/`, `operations/`, `messages/` e `components/` devem ser separados quando o documento crescer.
- AsyncAPI é permitido apenas quando há eventos reais.
- Arquivos AsyncAPI não devem existir como placeholders sem realidade de eventos.

---

## 10. Regras de naming

### 10.1 Module names
- `lower_snake_case`

### 10.2 OpenAPI path files
- `contracts/openapi/paths/<module>.yaml`

### 10.3 JSON Schema files
- `contracts/schemas/<module>/<entity>.schema.json`

### 10.4 Arazzo files
- `contracts/workflows/<module>/<use_case>.arazzo.yaml`

### 10.5 AsyncAPI files
- `contracts/asyncapi/<layer>/<name>.yaml`

### 10.6 Human documentation names
- docs globais podem usar nomes canônicos em uppercase (`SYSTEM_SCOPE.md`, `API_CONVENTIONS.md`)
- docs de módulo podem usar placeholders canônicos em uppercase (`DOMAIN_RULES_<MOD>.md`, etc.)
- dentro desses docs, identificadores técnicos referenciados permanecem em inglês

---

## 11. Links obrigatórios em documentação humana
Todo conjunto de documentação de módulo deve linkar explicitamente, quando aplicável, para:
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md`

Todo fluxo de criação de contrato deve preservar essa referência cruzada nos docs de módulo relacionados.

### 11.1 Conjunto mínimo de cross-references para docs de módulo
O footprint mínimo esperado de cross-references para documentação de módulo é:
- system scope
- regras de handebol quando o trigger aplicar
- OpenAPI path file
- pasta de schemas do módulo

---

## 12. Anti-patterns (proibidos)
- identificadores técnicos com idioma misto
- fonte primária da verdade duplicada
- path files misturando módulos
- workflow files sem orquestração real
- asyncapi files sem eventos reais
- contratos fora das pastas canônicas
- nomes de módulo fora da taxonomia canônica de 16 módulos
- artefatos gerados tratados como soberanos
- docs de módulo que não referenciam os docs globais obrigatórios quando aplicável

---

## 13. Fluxo de criação de contrato (estrutural)

**Este fluxo define ONDE criar artefatos (estrutura de filesystem e naming)**. Para o procedimento operacional completo (incluindo validação, boot sequence e critérios de readiness), veja `CONTRACT_SYSTEM_RULES.md` seção 15 (Contract Creation Procedure).

1. escolher o módulo canônico na taxonomia de 16 módulos
2. criar `contracts/openapi/paths/<module>.yaml`
3. criar `contracts/schemas/<module>/`
4. avaliar `contracts/workflows/<module>/`
5. avaliar `contracts/asyncapi/<module>.yaml`
6. linkar a documentação humana do módulo a `SYSTEM_SCOPE.md` e, quando aplicável, `HANDBALL_RULES_DOMAIN.md`

### 13.1 Structural Output Expectation
Um fluxo de criação de contrato é estruturalmente aceitável apenas quando o artefato:
- é criado sob a árvore canônica
- usa regras canônicas de idioma
- preserva soberania de superfície
- respeita boundary de módulo
- preserva cross-reference de módulo para documentação humana

---

## 14. Definition of Done estrutural
Uma estrutura de contrato é estruturalmente válida apenas quando:
- o artefato está na pasta canônica
- naming segue as regras canônicas
- o módulo pertence à lista de 16 módulos
- soberania de superfície é respeitada
- nenhum anti-pattern proibido está presente

---

## 15. Regras estruturais relevantes para o agente
O agente deve usar este arquivo apenas para determinar:
- onde um artefato pertence
- se um artefato pertence a um módulo válido
- qual pasta canônica e naming devem ser usados
- se o artefato viola soberania estrutural

Este arquivo não deve ser usado para inventar regras de negócio, estados, permissões ou semântica de eventos.
