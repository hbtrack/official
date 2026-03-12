# CONTRACT_SYSTEM_RULES.md

## 0. Índice cruzado

Este documento faz parte da trilogia **HB Track — Manual Contract-Driven**:

1. **.contract_driven/CONTRACT_SYSTEM_LAYOUT.md**
   - **Responsabilidade**: Estrutura canônica de filesystem, taxonomia de módulos, convenções de nomenclatura, regras de localização de artefatos
   - **Use quando**: Definir onde criar artefatos, validar nomes de módulos, checar regras de naming

2. **.contract_driven/CONTRACT_SYSTEM_RULES.md** (este arquivo)
   - **Responsabilidade**: Regras operacionais, hierarquia de precedência, boot protocol do agente, códigos de bloqueio, ferramentas de validação, procedimentos de evolução
   - **Use quando**: Entender como criar/modificar contratos, determinar precedência em conflitos, comportamento de bloqueio, passos de validação

3. **.contract_driven/GLOBAL_TEMPLATES.md**
   - **Responsabilidade**: Scaffolds e exemplos oficiais para documentação normativa e artefatos de contrato
   - **Use quando**: Criar novos docs de módulo, contratos, ou artefatos de governança

4. **.contract_driven/templates/api_rules/api_rules.yaml**
   - **Responsabilidade**: Regras, validações e templates canônicos para contratos de APIs (OpenAPI/HTTP)
   - **Use quando**: Resolver conflitos de convenção e definir/validar contratos de API

**Regra de navegação**: Estes arquivos devem ser lidos em conjunto. Referências cruzadas entre eles são explícitas e vinculantes.

---

## 1. Objetivo
Este documento define as regras operacionais para criar, validar, evoluir e consumir contratos no HB Track.

Ele é o manual operacional vinculante para desenvolvimento orientado a contrato (contract-driven).

---

## 2. Escopo
Estas regras governam:
- criação de contratos
- manutenção de contratos
- validação de contratos
- consumo de contratos por agentes de IA
- artefatos derivados de contrato
- definição de readiness para implementação

---

## 2B. Regras de idioma e naming

**Identificadores técnicos e convenções de naming são governados por `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`**:

- **Seção 3 (Idioma canônico)**: Define quais identificadores devem estar em inglês (nomes de módulos, OpenAPI paths, operationIds, JSON property names, schema filenames, event names, DB table/column names, generated type names) e quais conteúdos devem estar em português (conteúdo de documentação humana em arquivos `.md`).

- **Seção 10 (Regras de naming)**: Define padrões canônicos:
  - Module names: `lower_snake_case`
  - OpenAPI path files: `contracts/openapi/paths/<MODULE>.yaml`
  - JSON Schema files: `contracts/schemas/<MODULE>/<entity>.schema.json`
  - Arazzo files: `contracts/workflows/<MODULE>/<use_case>.arazzo.yaml`
  - AsyncAPI files: `contracts/asyncapi/<layer>/<name>.yaml`
  - Documentação humana: nomes canônicos em uppercase são permitidos

**Regra**: Ao validar ou criar artefatos, sempre consultar LAYOUT seções 3 e 10 para compliance de idioma e naming.

---

## 2C. Taxonomia de módulos

**A lista autoritativa de módulos válidos está definida em `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 2 (Taxonomia canônica de módulos)**.

Os 16 módulos canônicos são:

**Functional Domain Modules** (13):
- `users`, `seasons`, `teams`, `training`, `wellness`, `medical`, `competitions`, `matches`, `scout`, `exercises`, `analytics`, `reports`, `ai_ingestion`

**Cross-Cutting Modules** (3):
- `identity_access`, `audit`, `notifications`

**Critical boundary**:
- `users` = person/profile domain
- `identity_access` = authentication, authorization, credentials, sessions, MFA, JWT, RBAC

**Regra**: Se um módulo não estiver listado em LAYOUT seção 2.1, ele não existe. Qualquer artefato que referencie um módulo não-canônico deve emitir `BLOCKED_MISSING_MODULE`.

---

## 3. Artefatos normativos soberanos

Os artefatos abaixo são normativos e soberanos.

### 3.1 Contract-system governance
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `.contract_driven/GLOBAL_TEMPLATES.md`
- `.contract_driven/templates/api_rules/api_rules.yaml`

### 3.1A SSOT de templates (scaffolds)
Templates são scaffolds canônicos usados por agentes para criar artefatos normativos sem improviso de estrutura.

- Templates globais (canon humano): `.contract_driven/templates/globais/`
- Templates de módulo (docs + schemas + snippets): `.contract_driven/templates/modulos/`

Regras:
- Agents **DEVEM** instanciar artefatos copiando templates desta pasta para o path canônico definido em LAYOUT seção 4A.
- `.contract_driven/GLOBAL_TEMPLATES.md` é índice/regras; os corpos de template vivem em `templates/`.

### 3.2 Global governance docs
- `docs/_canon/README.md`
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/ARCHITECTURE.md`
- `docs/_canon/C4_CONTEXT.md`
- `docs/_canon/C4_CONTAINERS.md`
- `docs/_canon/MODULE_MAP.md` (mapeamento de macrodomínios para comunicação de negócio, não taxonomia técnica canônica)
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/API_CONVENTIONS.md`
- `docs/_canon/DATA_CONVENTIONS.md`
- `docs/_canon/ERROR_MODEL.md`
- `docs/_canon/GLOBAL_INVARIANTS.md`
- `docs/_canon/DOMAIN_GLOSSARY.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/SECURITY_RULES.md`
- `docs/_canon/UI_FOUNDATIONS.md`
- `docs/_canon/DESIGN_SYSTEM.md`
- `docs/_canon/CI_CONTRACT_GATES.md`
- `docs/_canon/TEST_STRATEGY.md`

Landing/entry não-soberano:
- `README.md` na raiz do repositório é apenas navegação/entrada. Ele não deve introduzir novas regras normativas que conflitem com o canon.

### 3.3 Technical contracts
- `contracts/openapi/openapi.yaml`
- `contracts/openapi/paths/*.yaml`
- `contracts/schemas/**/*.schema.json`
- `contracts/workflows/**/*.arazzo.yaml`
- `contracts/asyncapi/**/*.yaml`

### 3.4 Module minimum docs
- `docs/hbtrack/modulos/<module>/README.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`

### 3.5 Module docs when applicable
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md`

### 3.6 ADRs and explicit deviations
- `docs/_canon/decisions/ADR-*.md` quando o sistema desvia intencionalmente de uma regra normativa anterior ou de um comportamento oficial do domínio do handebol já traduzido para regras de produto

Regra:
Tudo fora das listas acima é não-soberano por padrão, a menos que seja explicitamente promovido pela governança.

---

## 3B. Convenções de API HTTP — SSOT canônico

As regras, validações e templates canônicos para **design de API HTTP** (OpenAPI/JSON/URLs/paginação/erros/compatibilidade/segurança) estão centralizados em:

- `.contract_driven/templates/api_rules/api_rules.yaml`

Regras:
- **SSOT**: agentes **DEVEM** usar `API_RULES.yaml` como fonte primária para decisões de convenção de API.
- **Determinismo**: se uma convenção necessária não estiver explícita em `API_RULES.yaml`, o agente **DEVE** bloquear com `BLOCKED_MISSING_API_CONVENTION`.
- **Registry legado**: a numeração estável `(#NNN)` do baseline externo foi migrada para `hbtrack_api_rules.legacy_rule_registry` dentro de `API_RULES.yaml` (incluindo overrides por precedência).

---

## 3A. Política de compliance de path canônico

Paths canônicos de filesystem são governados por `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 4A.

Esta seção não redefine paths canônicos. Ela define apenas as consequências de compliance para violações de path.

### 3A.1 Regra de compliance de path
Se um artefato normativo obrigatório existir com conteúdo correto, mas fora do seu path canônico:
- ele é não-compliant
- ele não satisfaz requisitos mínimos de presença
- o agente não deve tratá-lo como autoritativo por padrão

### 3A.2 Regra de exceção
Exceções de path exigem:
- ADR explícito
- cross-reference explícita
- nenhuma ambiguidade com a fonte canônica

---

## 4. Artefatos derivados / scaffolds

Os itens abaixo são derivados e nunca sobrepõem artefatos normativos:
- código de implementação (`.py`, `.ts`, `.tsx`, etc.)
- clients gerados
- UI types gerados
- bundles gerados
- documentação HTML gerada
- artefatos de Storybook gerados
- mocks
- exemplos de payload
- drafts
- boilerplates locais (rascunhos) fora da SSOT de templates

Regras:
- artefatos gerados nunca são normativos
- artefatos gerados não devem ser editados manualmente quando existe regeneração
- artefatos gerados devem viver sob `generated/`
- evidências e relatórios derivados devem viver sob `_reports/`
- artefatos gerados devem ser regeneráveis a partir de fontes soberanas
- drift entre artefato gerado e fonte normativa deve falhar o pipeline

---

## 5. Precedência em caso de conflito

Ordem de precedência:
1. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
2. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
3. `.contract_driven/templates/api_rules/api_rules.yaml` (apenas para convenções/validações/templates de API HTTP)
4. contratos técnicos válidos:
   - OpenAPI
   - JSON Schema
   - Arazzo
   - AsyncAPI
5. `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando uma regra derivada do esporte se aplica
6. `docs/_canon/API_CONVENTIONS.md`, `docs/_canon/DATA_CONVENTIONS.md`, `docs/_canon/ERROR_MODEL.md`, `docs/_canon/SECURITY_RULES.md`
7. `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
8. `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
9. `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
10. `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
11. `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
12. implementação
13. artefatos gerados

Conflito no mesmo nível:
- o agente deve emitir `BLOCKED_CONTRACT_CONFLICT`

Conflito entre níveis:
- o nível mais alto sempre vence

### 5A. Precedência por superfície (overrides determinísticos)
- Convenções de design de API HTTP (OpenAPI/JSON/URLs/pagination/errors/compatibility/security/events): aplicar `.contract_driven/templates/api_rules/api_rules.yaml` como baseline/SSOT antes de qualquer orientação de menor precedência.

Nota do baseline:
- O registry legado `(#NNN)` foi migrado para `API_RULES.yaml` para manter numeração estável e permitir overrides por precedência.
- Para convenções de design de API HTTP, `API_RULES.yaml` é a fonte canônica e sobrepõe orientações conflitantes em níveis de precedência inferiores.

---

## 6. Protocolo de boot do agente

### 6.1 Ordem obrigatória de boot
1. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
2. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
3. `.contract_driven/GLOBAL_TEMPLATES.md`
4. `.contract_driven/templates/README.md` (estrutura e contrato de uso de templates)
5. `.contract_driven/templates/api_rules/api_rules.yaml`
6. `docs/_canon/SYSTEM_SCOPE.md`
7. `docs/_canon/API_CONVENTIONS.md`
8. `docs/_canon/DATA_CONVENTIONS.md`
9. `docs/_canon/CHANGE_POLICY.md`
10. `docs/_canon/HANDBALL_RULES_DOMAIN.md`
11. `docs/_canon/DOMAIN_GLOSSARY.md`
12. `docs/_canon/MODULE_MAP.md`
13. `docs/_canon/ARCHITECTURE.md`
14. artefatos de contrato relevantes
15. docs de módulo relevantes

### 6.2 Modo de boot
O agente deve usar:
- boot mínimo obrigatório
- loading condicional sob demanda
- bloquear em vez de inferir quando um artefato crítico estiver ausente

### 6.3 Condição de bloqueio no boot
Se o agente não conseguir carregar a sequência de boot necessária para a tarefa atual, ele deve se declarar bloqueado usando um código de bloqueio válido, em vez de continuar por inferência.

### 6.4 Perfis de leitura por tarefa (contexto mínimo suficiente)
O boot mínimo continua obrigatório, mas o agente **DEVE** reduzir a leitura ao mínimo necessário para a tarefa (carregar sob demanda).

Perfis recomendados:

- **Gerar/alterar contrato de API (OpenAPI paths)**:
  - LAYOUT + RULES + `API_RULES.yaml`
  - `docs/_canon/SYSTEM_SCOPE.md`
  - docs do módulo (mínimo): README / MODULE_SCOPE / DOMAIN_RULES / INVARIANTS / TEST_MATRIX
  - contratos do módulo: `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<module>.yaml` + `contracts/openapi/components/`

- **Gerar docs mínimas de módulo**:
  - LAYOUT + RULES + `GLOBAL_TEMPLATES.md` (índice/regras)
  - templates: `.contract_driven/templates/modulos/*`
  - `docs/_canon/SYSTEM_SCOPE.md`
  - `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando o gatilho aplicar

- **Gerar schema de domínio (contracts/schemas)**:
  - LAYOUT + RULES + `.contract_driven/DOMAIN_AXIOMS.json`
  - template: `.contract_driven/templates/modulos/schemas/{{DOMAIN_ENTITY_SNAKE}}.schema.json`
  - docs do módulo (DOMAIN_RULES + INVARIANTS)

Prompts operacionais (checklists) vivem em `.contract_driven/agent_prompts/`.

---

## 7. Regra de arquitetura de documentação (Diátaxis)
A documentação do HB Track deve distinguir, no mínimo, estas funções:
- tutorial
- how-to
- reference
- explanation

Regras:
- contratos e specs técnicas são artefatos de referência
- regras operacionais são artefatos de referência
- ADRs e racional arquitetural são artefatos de explicação
- templates são scaffolds, não fontes de verdade de referência
- nenhum artefato deve misturar referência e explicação se isso prejudicar uso determinístico pelo agente

---

## 8. Modo estrito: inferência proibida

O agente de IA é proibido de inventar, sem contrato/documento explícito:
- módulos
- endpoints / paths
- fields estáveis
- enums estáveis
- eventos
- workflows
- transições de estado
- modelos de permissão
- erros domain-specific
- comportamento de UI
- regras de handebol
- integrações externas
- operações assíncronas

Artefato ausente => bloquear.

---

## 9. Códigos de bloqueio

Saídas de bloqueio permitidas:
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_SCHEMA`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_MISSING_TEST_MATRIX`
- `BLOCKED_CONTRACT_CONFLICT`
- `BLOCKED_NONCANONICAL_NORMATIVE_PATH`
- `BLOCKED_MISSING_CANON_ARTIFACT`
- `BLOCKED_MISSING_API_CONVENTION`

Uso de `BLOCKED_MISSING_CANON_ARTIFACT`:
- emitir quando um artefato canônico listado (governança em `.contract_driven/` ou canon global em `docs/_canon/`) for necessário para a tarefa atual e estiver ausente no path canônico, e não existir um `BLOCKED_MISSING_*` mais específico aplicável.

Nenhum workaround especulativo em texto livre é permitido.

---

## 10. Requisitos de documentação de módulo

### 10.1 Sempre obrigatório
- `docs/hbtrack/modulos/<module>/README.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`
- `contracts/openapi/paths/<MODULE>.yaml`
- `contracts/schemas/<MODULE>/*.schema.json`

**Nota**: Todos os arquivos de documentação de módulo listados acima devem incluir o header YAML obrigatório definido em `.contract_driven/GLOBAL_TEMPLATES.md` seção 3 (Required Header Template for Module Human Docs). Este header garante cross-references explícitas para `docs/_canon/SYSTEM_SCOPE.md`, `docs/_canon/HANDBALL_RULES_DOMAIN.md`, para os paths de contrato/schema do módulo, e para o flag semântico explícito `handball_semantic_applicability` governado pela seção 12 (Handball Trigger Rule).

### 10.2 Obrigatório quando aplicável
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
- `contracts/workflows/<MODULE>/*.arazzo.yaml`
- `contracts/asyncapi/<MODULE>.yaml`

---

## 11. Matriz de aplicabilidade

### 11.1 docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md
Obrigatório quando existe:
- status persistido
- transições de lifecycle
- aprovação/rejeição
- fechamento/reabertura
- progressão de fase

### 11.2 docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md
Obrigatório quando existe:
- RBAC local ao módulo
- ações sensíveis
- restrições de visibilidade
- regras de capability específicas por ator

### 11.3 docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md
Obrigatório quando existe:
- error codes domain-specific
- falhas de regra de negócio além de validação genérica
- semântica local de erro significativa

### 11.4 docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md
Obrigatório quando existe:
- tela de UI
- formulário de usuário
- ações disparadas pelo usuário
- estados loading/error/empty/success

### 11.5 docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md
Obrigatório quando existe:
- mais de uma tela user-facing
- fluxo de navegação entre telas
- ambiguidade de entry-point
- user journey com ramificações relevante para o comportamento

### 11.6 Arazzo workflow
Obrigatório quando:
- 2+ chamadas de API são encadeadas
- output de A é input obrigatório de B
- cronologia/ordem importa
- compensação/rollback é relevante

### 11.7 AsyncAPI
Obrigatório quando:
- o módulo publica ou consome eventos reais

### 11.8 Conditional artifact absence rule
Se um artefato aparentar ser aplicável por estas regras, mas estiver ausente, o agente não deve decidir sozinho. Ele deve emitir o código de bloqueio correspondente e parar o trabalho afetado.

---

## 12. Regra de gatilho do handebol

Um módulo deve linkar explicitamente para `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando tratar de:
- tempo de jogo
- timeout
- exclusão
- sanção
- gol
- tiro de 7m
- tiro livre
- substituição
- composição da equipe
- goleiro
- área de gol
- bola/categoria
- operações de mesa/scout
- fases da partida

Nenhuma regra esportiva inferida é permitida.

### 12.1 Product adaptation of official handball rule
O produto pode adaptar uma regra oficial derivada do handebol apenas quando essa adaptação estiver explicitamente registrada em:
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`, ou
- um `ADR` linkado

Se não existir adaptação explícita, a regra de domínio do handebol (traduzida) permanece vinculante.

---

## 13. Fonte da verdade por superfície

**Contratos técnicos**: Para estrutura canônica de filesystem e definição de soberania das superfícies técnicas de contrato (OpenAPI, JSON Schema, Arazzo, AsyncAPI), ver `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 5 (Soberania por camada).

**Esta seção estende LAYOUT adicionando superfícies de documentação de módulo**:

- interface pública HTTP => `contracts/openapi/openapi.yaml`
- shapes de dados reutilizáveis => `contracts/schemas/<MODULE>/*.schema.json`
- orquestração multi-step => `contracts/workflows/**/*.arazzo.yaml`
- contratos de eventos => `contracts/asyncapi/**/*.yaml`
- regras de negócio do módulo => `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- integridade do módulo => `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- estado do módulo => `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- permissões do módulo => `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- UI do módulo => `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
- navegação/telas do módulo => `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md`

Regra:
Nenhuma superfície pode ter duas fontes primárias.

---

## 14. Regras de derivação

- OpenAPI pode referenciar JSON Schemas quando a compatibilidade de pipeline for garantida (ver CONTRACT_SYSTEM_LAYOUT.md seção 6.1 para política de $ref)
- AsyncAPI pode referenciar JSON Schemas quando a compatibilidade de pipeline for garantida
- UI types são gerados a partir de OpenAPI
- API clients são gerados a partir de OpenAPI
- modelos internos podem ser gerados a partir de, ou alinhados a, contratos soberanos apenas

Regra:
Artefatos derivados nunca redefinem a fonte.

---

## 15. Procedimento de criação de contrato

**Este procedimento define a ordem operacional para criar contratos**. Para localizações canônicas de filesystem e convenções de naming de cada artefato, ver `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 13 (Fluxo de criação de contrato — estrutural).

1. selecionar módulo canônico
2. criar ou atualizar OpenAPI path file
   - **obrigatório (API execution contract)**: rodar o compiler determinístico para gerar policy resolvida + manifesto + cópias derivadas em `generated/`
     - `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface sync`
     - (quando aplicável) `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface event`
   - **fail-closed**: o compiler **DEVE** bloquear (não gera manifesto/hash) se detectar violação de style_veto, sufixo canônico ou binding `x-semantic-id` exigido
3. criar ou atualizar JSON Schemas do módulo
4. criar ou atualizar docs do módulo
5. avaliar estado, permissões, erros, UI, fluxo de telas, workflow e eventos
6. validar contratos técnicos
7. atualizar testes e artefatos de readiness
8. somente então a implementação pode começar

---

## 16. Contrato pronto para implementação (DoD binário)

Um contrato está pronto apenas quando todos forem verdadeiros:
- OpenAPI passa em Redocly CLI e Spectral
- JSON Schemas validam como JSON Schema
- Arazzo valida quando presente
- AsyncAPI valida quando presente
- zero `TODO`, `TBD`, `A definir` ou placeholders não-resolvidos
- referência explícita a `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- referência explícita a `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- referência explícita a `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`
- referência explícita a `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando o gatilho de handebol aplicar
- naming e localização obedecem o layout
- regras de idioma obedecem o layout e regras de governança

---

## 17. Módulo pronto para implementação (DoD binário)

Um módulo está pronto para implementação apenas quando:
- todos os docs sempre-obrigatórios existem
- todos os docs condicionalmente-obrigatórios existem
- todos os contratos relevantes validam
- a test matrix cobre API, schema, regra, invariante e estado quando aplicável
- mocks podem ser gerados do contrato sem ambiguidade
- nenhum artefato crítico ausente permanece

---

## 18. Módulo pronto para desenvolvimento guiado por IA

Além da seção 17:
- inputs são não-ambíguos
- outputs são não-ambíguos
- estados são não-ambíguos
- erros são não-ambíguos
- permissões são não-ambíguas
- invariantes são não-ambíguas
- nenhuma lacuna crítica força inferência livre
- todas as decisões em aberto estão explicitamente fora do escopo da tarefa atual

---

## 19. Tooling fixo de validação

- OpenAPI lint/validate: `Redocly CLI`
- OpenAPI rulesets: `Spectral`
- API policy compiler (determinístico): `python3 scripts/contracts/validate/api/compile_api_policy.py --all` (enforcement em `DERIVED_DRIFT_GATE`)
- HTTP breaking change detection: `oasdiff`
- HTTP contract/runtime tests: `Schemathesis`
- JSON Schema validation: `JSON Schema validator in pipeline`
- AsyncAPI validation: `AsyncAPI parser/validator`
- Arazzo validation: `Arazzo validator/linter defined in pipeline`
- UI docs validation when applicable: `Storybook build`

### Exemplos de uso
Para exemplos práticos de comandos de cada ferramenta, ver `.contract_driven/templates/globais/CI_CONTRACT_GATES.md` (referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 21).

---

## 20. Modos de operação do agente

O agente opera apenas nos seguintes modos formais:

### 20.1 `contract_creation_mode`
Usado ao criar um novo artefato de contrato.

### 20.2 `contract_revision_mode`
Usado ao revisar ou alterar um artefato de contrato existente.

### 20.3 `implementation_mode`
Usado ao implementar software a partir de contratos já definidos.

### 20.4 `audit_mode`
Usado ao auditar completude, consistência e readiness de contratos.

Regra:
O modo ativo determina o conjunto mínimo de boot e o output esperado.

---

## 21. Matriz mínima de boot por tipo de tarefa

### 21.1 Create new contract
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- template aplicável
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/_canon/API_CONVENTIONS.md`

**Boot condicional**
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se o gatilho de handebol aplicar
- `docs/_canon/DATA_CONVENTIONS.md` se um novo schema for criado
- `docs/_canon/MODULE_MAP.md` se o boundary do módulo estiver pouco claro
- `docs/_canon/DOMAIN_GLOSSARY.md` se a terminologia estiver ambígua
- contrato existente do módulo, se já existir

**Output esperado**
- contrato criado na localização canônica
- nenhum placeholder proibido
- linkagem explícita para documentos obrigatórios

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_SCHEMA`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.2 Review / change existing contract
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- contrato-alvo
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/API_CONVENTIONS.md`

**Boot condicional**
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se uma regra derivada do esporte for alterada
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md` se estado for alterado
- `docs/_canon/ERROR_MODEL.md` se comportamento de erro for alterado
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md` se comportamento de acesso for alterado
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` se comportamento de UI for alterado

**Output esperado**
- classificação explícita breaking/non-breaking
- contract diff claro
- update consistente dos artefatos afetados

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.3 Implement module guided by contract
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `docs/_canon/SYSTEM_SCOPE.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `contracts/openapi/paths/<MODULE>.yaml`
- `contracts/schemas/<MODULE>/*.schema.json`

**Boot condicional**
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` if handball trigger applies
- `contracts/workflows/<MODULE>/*.arazzo.yaml`
- `contracts/asyncapi/<MODULE>.yaml`

**Output esperado**
- implementação sem interface pública inventada
- código alinhado ao contrato
- nenhum field/state/event inferido fora da documentação

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_MISSING_TEST_MATRIX`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`

### 21.4 Audit module
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`
- `contracts/openapi/paths/<MODULE>.yaml`
- `contracts/schemas/<MODULE>/*.schema.json`

**Boot condicional**
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `contracts/workflows/<MODULE>/*.arazzo.yaml`
- `contracts/asyncapi/<MODULE>.yaml`
- `docs/_canon/CI_CONTRACT_GATES.md`

**Output esperado**
- `PASS`, `FAIL`, or `BLOCKED`
- lista exata de conflitos
- referência explícita ao artefato violado

**Possíveis códigos de bloqueio**
- qualquer código `BLOCKED_MISSING_*` que corresponda ao artefato obrigatório ausente
- `BLOCKED_CONTRACT_CONFLICT`

### 21.5 Create Arazzo workflow
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `contracts/openapi/openapi.yaml`
- `contracts/openapi/paths/<MODULE>.yaml`

**Boot condicional**
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se o fluxo depender de regra do esporte

**Output esperado**
- workflow apenas quando multi-step for real
- steps linkados a operações OpenAPI existentes

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_OPENAPI_PATH`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.6 Create AsyncAPI contract
**Boot obrigatório**
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- contexto do evento
- contrato do módulo afetado

**Boot condicional**
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se o evento carregar semântica esportiva

**Output esperado**
- evento apenas quando existir evento real
- payload estável e rastreável

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.7 Create UI contract
**Boot obrigatório**
- `docs/hbtrack/modulos/<module>/MODULE_SCOPE_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `contracts/openapi/paths/<MODULE>.yaml`
- `contracts/schemas/<MODULE>/*.schema.json`

**Boot condicional**
- `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se regra do esporte impactar comportamento de UI
- `docs/_canon/UI_FOUNDATIONS.md`
- `docs/_canon/DESIGN_SYSTEM.md`

**Output esperado**
- inputs
- outputs
- states
- actions
- errors
- permissions
- nenhum comportamento inventado

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.8 Create state model
**Boot obrigatório**
- `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`

**Boot condicional**
- `contracts/openapi/paths/<MODULE>.yaml`
- `docs/hbtrack/modulos/<module>/ERRORS_<MODULE>.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md` se o gatilho de handebol aplicar

**Output esperado**
- named states
- valid transitions
- triggers
- invalid-transition errors

**Possíveis códigos de bloqueio**
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_HANDBALL_REFERENCE`
- `BLOCKED_CONTRACT_CONFLICT`

### 21.9 Final operational rule
- não carregar tudo toda vez
- carregar o conjunto mínimo obrigatório
- carregar o restante apenas por aplicabilidade
- se um artefato crítico estiver ausente, bloquear em vez de inferir
- se um artefato normativo obrigatório existir fora do path canônico, tratá-lo como ausente até reconciliar ou cobrir via ADR

---

## 22. Evolution Rule

Toda mudança deve seguir esta ordem:
1. atualizar artefato normativo
2. validar contrato
3. regenerar artefatos derivados
4. atualizar implementação
5. rodar testes
6. revisar impacto

Implementation-first seguido de documentação depois é proibido.
