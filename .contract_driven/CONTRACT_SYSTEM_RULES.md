# CONTRACT_SYSTEM_RULES.md

> Referência completa de regras operacionais. Carregar on-demand, não no boot.
> Para referência rápida operacional: `docs/_canon/OPERATIONS.md`

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

## 2A. Regra de canonização operacional

Toda mudança que altera comportamento esperado do agente **DEVE** existir em 3 níveis:

1. **regra normativa**
   - define o que é obrigatório;
   - vive em `RULES`, `LAYOUT` ou no canon global correto.

2. **registro operacional**
   - define quando a regra é lida, aplicada ou bloqueada;
   - vive em `docs/_canon/CONTRACT_PIPELINE.md`, `.contract_driven/BOOT_PROFILES.yaml` (boot profiles),
     `docs/_canon/gates/GATES_REGISTRY.yaml` e, quando aplicável, `docs/_canon/MODULE_REGISTRY.yaml`.

3. **enforcement técnico**
   - define como a regra é executada por generator, validator, gate, pipeline CI ou prompt operacional.

Regras:
- código executável sozinho **não** canoniza comportamento;
- relatório isolado **não** canoniza comportamento;
- prompt isolado **não** canoniza comportamento;
- se uma melhoria existir apenas em código ou apenas em `_reports/`, ela ainda **não** está resolvida para o agente.

### 2A.1 Regra prática de promoção

Ao introduzir uma melhoria:
- promover a substância da regra ao artefato canônico correto;
- decidir se ela entra em boot mínimo, boot condicional ou consulta apenas por gate;
- registrar o fluxo em pipeline / boot / gates;
- só então ajustar generator, validator, gate, CI ou prompt.

### 2A.2 Prompts são executores derivados, sujeitos a validação de gates

Prompts operacionais:
- são agentes de execução de regras já canonizadas em artefatos canônicos;
- não criam obrigação substantiva nova por conta própria;
- não podem ser a única fonte de uma regra que afeta comportamento do agente;
- estão sujeitos à validação de gates e NÃO sobrepõem o canon normativo.

**Hierarquia de SSOT de regras:** `CONTRACT_SYSTEM_RULES` > `ADRs` > `GATES_REGISTRY` > contratos de módulo > prompts.

Se um prompt contiver instrução sem respaldo explícito no canon, o agente deve bloquear em vez de assumir a regra como válida.

### 2A.3 Matriz obrigatória de promoção ao canon

| Tipo de mudança | Artefato canônico obrigatório |
| --- | --- |
| muda comportamento geral do agente | `.contract_driven/CONTRACT_SYSTEM_RULES.md` |
| muda path, classificação ou soberania de artefato | `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` |
| muda estágio do pipeline | `docs/_canon/CONTRACT_PIPELINE.md` |
| muda boot por tipo de tarefa | `.contract_driven/BOOT_PROFILES.yaml` |
| muda toolchain, timeout, degradação ou health-check | `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` |
| muda gate oficial | `docs/_canon/gates/GATES_REGISTRY.yaml` |
| muda worker ou roteamento operacional | `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` |
| muda DoD por superfície | `.contract_driven/CONTRACT_SYSTEM_RULES.md` |
| muda status ou maturidade de módulo | `docs/_canon/MODULE_REGISTRY.yaml` |
| muda classificação de docs não soberanas | `LAYOUT` + `RULES` + `README` local da pasta afetada |

### 2A.4 Regra de classificação de boot

Todo novo artefato de governança promovido ao canon **DEVE** ser classificado em
`boot_minimo`, `boot_condicional` ou `gate_only` em `.contract_driven/BOOT_PROFILES.yaml`.

Sem essa classificação:
- o agente não pode presumir que o artefato foi lido;
- o prompt não pode tratá-lo como contexto carregado;
- qualquer dependência operacional deve bloquear em vez de inferir.

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

Os 17 módulos canônicos são:

**Functional Domain Modules** (14):
- `users`, `seasons`, `teams`, `training`, `wellness`, `medical`, `competitions`, `matches`, `scout`, `exercises`, `analytics`, `reports`, `ai_ingestion`, `video`

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
- `.contract_driven/templates/api/api_rules.yaml`

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
- `docs/_canon/MODULE_REGISTRY.yaml`
- `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
- `docs/_canon/CHANGE_POLICY.md`
- `.contract_driven/templates/api/api_rules.yaml` (SSOT de convenções HTTP/OpenAPI)
- `docs/_canon/DATA_CONVENTIONS.md`
- `docs/_canon/GLOBAL_INVARIANTS.md`
- `docs/_canon/DOMAIN_GLOSSARY.md`
- `docs/_canon/HANDBALL_RULES_DOMAIN.md`
- `docs/_canon/SECURITY_RULES.md`
- `docs/_canon/UI_CONTRACT_GUIDE.md`
- `docs/_canon/CI_CONTRACT_GATES.md`
- `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md`
- `docs/_canon/CONTRACT_PIPELINE.md`
- `docs/_canon/TEST_STRATEGY.md`
- `docs/_canon/DECISION_POLICY.md`
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
- `docs/_canon/gates/README.md`
- `docs/_canon/gates/GATES_REGISTRY.yaml`

Landing/entry não-soberano:
- `README.md` na raiz do repositório é apenas navegação/entrada. Ele não deve introduzir novas regras normativas que conflitem com o canon.

### 3.2A Decision support sources (não-soberanos)

- `docs/hbtrack/decisoes/*.md`

Classificação formal:
- `explanation`
- `decision_support_source`
- `non-sovereign`

Regras:
- esses arquivos não podem atuar como SSOT;
- vocabulário soberano (`SSOT`, `canônico`, `fonte soberana`, `source of truth`) exige disclaimer explícito no topo;
- qualquer conflito entre DSS e fonte soberana é resolvido a favor do canon.

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
- `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md`
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

- `.contract_driven/templates/api/api_rules.yaml`

Regras:
- **SSOT**: agentes **DEVEM** usar `api_rules.yaml` como fonte primária para decisões de convenção de API.
- **Determinismo**: se uma convenção necessária não estiver explícita em `api_rules.yaml`, o agente **DEVE** bloquear com `BLOCKED_MISSING_API_CONVENTION`.
- **Registry legado**: a numeração estável `(#NNN)` do baseline externo foi migrada para `hbtrack_api_rules.legacy_rule_registry` dentro de `api_rules.yaml` (incluindo overrides por precedência).

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

Ordem de precedência (maior autoridade primeiro):
1. `DOMAIN_AXIOMS.json` — invariantes machine-readable, nunca sobrescritos
2. `.contract_driven/CONTRACT_SYSTEM_RULES.md` (este arquivo) — regras operacionais vinculantes
   2a. `.contract_driven/templates/api/api_rules.yaml` — convenções de API HTTP
3. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` — layout canônico de filesystem
4. contratos técnicos válidos (OpenAPI > JSON Schema > AsyncAPI > Arazzo)
   4a. `docs/_canon/HANDBALL_RULES_DOMAIN.md` — quando gatilho esportivo ativo
5. `.contract_driven/templates/api/api_rules.yaml`, `docs/_canon/DATA_CONVENTIONS.md`, `docs/_canon/SECURITY_RULES.md`, `docs/_canon/OPERATIONS.md`
6. `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
7. `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md`
8. `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
9. `docs/hbtrack/modulos/<module>/STATE_MODEL_<MODULE>.md`
10. `docs/hbtrack/modulos/<module>/PERMISSIONS_<MODULE>.md`
11. `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md`
12. implementação
13. `generated/` e `_reports/` — derivados, sem autoridade sobre 1–12

Conflito no mesmo nível → `BLOCKED_CONTRACT_CONFLICT`.
Conflito entre níveis → o nível mais alto (menor número) sempre vence.

**Detecção de conflito de precedência:** Ao criar ou atualizar um ADR, verificar se a regra introduzida contradiz uma regra de nível mais alto nesta hierarquia. Se contradição for identificada: emitir `BLOCKED_PRECEDENCE_CONFLICT` imediatamente e não prosseguir com a criação ou modificação do artefato. Precedência não pode ser contornada por instrução de agente ou prompt operacional. Se houver ambiguidade sobre a existência de conflito: elevar para decision discovery antes de prosseguir.

### 5A. Precedência por superfície (overrides determinísticos)
Para convenções de design de API HTTP: `api_rules.yaml` é SSOT e sobrepõe orientações em níveis inferiores (ver rank 2a acima).

---

## 6. Protocolo de boot do agente

### 6.1 Modo de boot
O agente deve usar:
- boot mínimo obrigatório
- loading condicional sob demanda
- bloquear em vez de inferir quando um artefato crítico estiver ausente

Para tarefas que resultam em validação, readiness ou handoff, o boot **DEVE** também carregar
`docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` antes do worker.

### 6.2 Condição de bloqueio no boot
Se o agente não conseguir carregar a sequência de boot necessária para a tarefa atual, ele deve se declarar bloqueado usando um código de bloqueio válido, em vez de continuar por inferência.

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

> MAPEAMENTO COM docs/_canon/AGENT_INSTRUCTIONS.md §4: BLOCKED_PRE_CONTRACT_SKIPPED, BLOCKED_MISSING_OPENAPI_PATH, BLOCKED_MISSING_HANDBALL_REFERENCE, BLOCKED_MISSING_API_CONVENTION → promovidos para docs/_canon/AGENT_INSTRUCTIONS.md §4.
> Demais códigos exclusivos desta seção = subcasos de BLOCKED_REQUIRED_ARTIFACT_MISSING.
> Em conflito com docs/_canon/AGENT_INSTRUCTIONS.md §4, docs/_canon/AGENT_INSTRUCTIONS.md §4 prevalece.

Saídas de bloqueio permitidas:
- `BLOCKED_MISSING_MODULE`
- `BLOCKED_MISSING_OPENAPI_PATH` [→ docs/_canon/AGENT_INSTRUCTIONS.md §4]
- `BLOCKED_MISSING_SCHEMA`
- `BLOCKED_MISSING_DOMAIN_RULE`
- `BLOCKED_MISSING_INVARIANT`
- `BLOCKED_MISSING_STATE_MODEL`
- `BLOCKED_MISSING_PERMISSION_MODEL`
- `BLOCKED_MISSING_SPORT_SCIENCE_RULES`
- `BLOCKED_MISSING_UI_CONTRACT`
- `BLOCKED_MISSING_HANDBALL_REFERENCE` [→ docs/_canon/AGENT_INSTRUCTIONS.md §4]
- `BLOCKED_MISSING_TEST_MATRIX`
- `BLOCKED_CONTRACT_CONFLICT`
- `BLOCKED_NONCANONICAL_NORMATIVE_PATH`
- `BLOCKED_MISSING_CANON_ARTIFACT`
- `BLOCKED_MISSING_API_CONVENTION` [→ docs/_canon/AGENT_INSTRUCTIONS.md §4]
- `BLOCKED_MISSING_ARCH_DECISION`
- `BLOCKED_REQUIRED_ARTIFACT_MISSING`
- `BLOCKED_MISSING_AGENT_PROMPT`
- `BLOCKED_PRE_CONTRACT_SKIPPED` [→ docs/_canon/AGENT_INSTRUCTIONS.md §4]
- `BLOCKED_SCOPE_OVERFLOW` [→ ADR-031]

Uso de `BLOCKED_MISSING_CANON_ARTIFACT`:
- emitir quando um artefato canônico listado (governança em `.contract_driven/` ou canon global em `docs/_canon/`) for necessário para a tarefa atual e estiver ausente no path canônico, e não existir um `BLOCKED_MISSING_*` mais específico aplicável.

Nenhum workaround especulativo em texto livre é permitido.

Uso de `BLOCKED_MISSING_ARCH_DECISION`:
- emitir quando existir uma decisão arquitetural classificada como `obrigatória` com `status: open` em `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` que afete o módulo ou seja global, e nenhuma ADR aceita a resolva.

Uso de `BLOCKED_REQUIRED_ARTIFACT_MISSING`:
- emitir quando um artefato de módulo obrigatório (conforme seção 10.1 deste documento) estiver ausente do seu path canônico e a fase pré-contrato o exigir para prosseguir.
- Este código é específico da fase pré-contrato; para ausências detectadas fora da fase pré-contrato, usar `BLOCKED_MISSING_CANON_ARTIFACT` ou o código específico mais adequado.

Uso de `BLOCKED_MISSING_AGENT_PROMPT`:
- emitir quando o `task_type` informado não possuir um worker prompt mapeado e disponível sob `.contract_driven/agent_prompts/`.
- O agente deve parar e registrar o bloqueio no backlog antes de qualquer tentativa de continuar.

Uso de `BLOCKED_PRE_CONTRACT_SKIPPED`:
- emitir quando um worker de contrato for acionado diretamente sem evidência de execução prévia da fase pré-contrato.
- Ver seção 22 (Fase Pré-Contrato Obrigatória) para a regra normativa completa.

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
- `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md`
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

### 11.8 docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md
Obrigatório quando o módulo depende de conteúdo técnico-científico aplicado, como:
- métodos/protocolos formais de treino e monitoramento
- cálculos (ex: sRPE, strain, TRIMP) e suas variáveis
- thresholds (zonas, ranges, cutoffs) e critérios de interpretação
- baterias de teste e critérios de prontidão/readiness
- prescrição de força/potência/HIIT/recuperação baseada em critério
- interpretação fisiológica/funcional que não é axioma estrutural nem regra oficial do handebol

Fontes permitidas e limites de inferência externa são governados por `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`.

### 11.9 Conditional artifact absence rule
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
- regras técnico-científicas do módulo => `docs/hbtrack/modulos/<module>/SPORT_SCIENCE_RULES_<MODULE>.md`
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

## 14A. Política de Domain Shapes (JSON Schema)

`contracts/schemas/<module>/*.schema.json` é a superfície soberana de shapes de dados reutilizáveis por módulo. Esta seção define as regras operacionais para criação, uso e promoção de domain shapes.

### 14A.1 Definições

| Conceito | Definição |
|----------|-----------|
| **domain shape** | Representação canônica de uma entidade ou conceito de domínio, agnóstica de protocolo. Vive em `contracts/schemas/<module>/`. |
| **HTTP DTO** | Adaptação da shape de domínio para transporte HTTP (envelopes, campos calculados, omissões de PII). Vive em `contracts/openapi/components/schemas/<module>/`. |

### 14A.2 Quando criar um domain shape

Criar um domain shape em `contracts/schemas/<module>/` quando:
- a entidade for persistida ou transmitida como dado de domínio estável
- a shape for reutilizada por mais de uma superfície (OpenAPI, AsyncAPI, Arazzo)
- a shape representar um conceito canônico definido em `DOMAIN_RULES_<MODULE>.md`
- a entidade tiver identidade própria (id) ou lifecycle mensurável

### 14A.3 Quando NÃO criar um domain shape separado

Não criar domain shape quando:
- o conceito existir exclusivamente como DTO de request/response sem reuso semântico
- a shape for um envelope técnico sem semântica de domínio (ex.: paginação genérica, error wrapper)
- a entidade for totalmente inferível a partir de outra shape canônica já existente

Nesses casos, a shape vive exclusivamente em `contracts/openapi/components/schemas/<module>/`.

### 14A.4 Quando promover para `shared/`

Usar `contracts/schemas/shared/` **somente** quando:
- a shape for usada por 2 ou mais módulos canônicos distintos
- não houver módulo dono claro da entidade
- a promoção for justificada por `DOMAIN_RULES` de mais de um módulo

Promoção para `shared/` requer que nenhum módulo específico reivindique ownership exclusivo. Em caso de dúvida, manter escopado ao módulo e aguardar segundo reuso real.

### 14A.5 Referência direta OpenAPI → contracts/schemas/

OpenAPI pode usar `` direto para `contracts/schemas/` **somente quando** todas as condições estiverem presentes:
1. a shape é semanticamente idêntica entre domínio e HTTP (zero adaptação/envelope)
2. o pipeline suporta $ref externo sem transformação (validado por Redocly CLI)
3. há documentação inline (`description` ou `x-schema-ref-justification`) justificando o reuso direto

Se qualquer condição falhar, usar `components/schemas/<module>/` obrigatoriamente.

**Regra de conflito**: se houver divergência entre shape HTTP e shape de domínio, `components/schemas/` vence para OpenAPI e `contracts/schemas/` preserva o domínio.

**Regra anti-amputação**: para entidades estáveis expostas em responses, `components/schemas/<module>/` não pode virar stub. Ele deve:
- reutilizar a shape soberana diretamente; ou
- documentar a adaptação HTTP com `x-schema-ref-justification` e explicitar o delta normativo.

Ausência de fields soberanos sem justificativa explícita = `BLOCKED_CONTRACT_CONFLICT`.

### 14A.6 Conformidade com DOMAIN_AXIOMS.json

Todo domain shape deve ser válido segundo `DOMAIN_AXIOMS.json` e deve:
- usar os tipos base canônicos definidos nos axiomas
- não redefinir idiomas/formatos já padronizados (ex.: `date-time` canônico)
- respeitar naming conventions de `CONTRACT_SYSTEM_LAYOUT.md` seção 10

### 14A.7 Lifecycle e audit fields são condicionais

Os fields `status`, `createdAt`, `updatedAt`, `deletedAt` e similares **não são boilerplate universal**. Incluí-los apenas quando:
- a entidade tiver lifecycle explícito governado por `STATE_MODEL_<MODULE>.md` (ver §11.1)
- a entidade tiver requisitos de auditoria documentados em `INVARIANTS_<MODULE>.md` ou em `docs/_canon/GLOBAL_INVARIANTS.md`

Não incluir por precaução sem evidência canônica. O template em `GLOBAL_TEMPLATES.md` §35 fornece o scaffold com esses fields comentados para ativação sob demanda.

### 14A.8 Bloqueios desta seção

| Código | Condição |
|--------|----------|
| `BLOCKED_MISSING_SCHEMA` | Schema de domínio obrigatório ausente no path canônico |
| `BLOCKED_MISSING_DOMAIN_RULE` | `DOMAIN_RULES_<MODULE>.md` ausente — sem base para criar domain shape |
| `BLOCKED_CONTRACT_CONFLICT` | Shape HTTP e shape de domínio divergem sem adaptação explícita documentada |
| `BLOCKED_MISSING_CANON_ARTIFACT` | `DOMAIN_AXIOMS.json` ausente quando necessário para validação |

Um módulo **não está pronto para implementação** enquanto seus JSON Schemas obrigatórios não existirem e não validarem como JSON Schema (ver §16 — Contrato pronto para implementação).


---

## 15. Procedimento de criação de contrato

**Este procedimento define a ordem operacional para criar contratos**. Para localizações canônicas de filesystem e convenções de naming de cada artefato, ver `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 13 (Fluxo de criação de contrato — estrutural).

1. selecionar módulo canônico
2. criar ou atualizar OpenAPI path file
   - **obrigatório (API execution contract)**: rodar o compiler determinístico para gerar policy resolvida + manifesto + cópias derivadas em `generated/`
     - `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface sync`
     - (quando aplicável) `python3 scripts/contracts/validate/api/compile_api_policy.py --module <module> --surface event`
     - se qualquer input global mudar (`.contract_driven/DOMAIN_AXIOMS.json` ou `.contract_driven/templates/api/*`), a execução parcial fica proibida e o agente **DEVE** usar `python3 scripts/contracts/validate/api/compile_api_policy.py --all`
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
- `generated/contracts/**` é consumível sem fallback manual para `contracts/**`
- zero `$ref` local quebrado em bundles gerados promovidos
- um único modelo público de erro HTTP (`shared/problem.yaml`)
- zero `bearerAuth` e zero `security: - {}` em contratos promovidos
- endpoints de query analítica não usam DSL textual solta nem rows abertas sem envelope soberano
- referência explícita a `docs/hbtrack/modulos/<module>/DOMAIN_RULES_<MODULE>.md`
- referência explícita a `docs/hbtrack/modulos/<module>/INVARIANTS_<MODULE>.md`
- referência explícita a `docs/hbtrack/modulos/<module>/TEST_MATRIX_<MODULE>.md`
- referência explícita a `docs/_canon/HANDBALL_RULES_DOMAIN.md` quando o gatilho de handebol aplicar
- naming e localização obedecem o layout
- regras de idioma obedecem o layout e regras de governança

### 16.1 DoD por superfície — HTTP/OpenAPI

Além da lista base:
- `TOOLING_CONFIG_GATE`, `OPENAPI_ROOT_STRUCTURE_GATE`, `OPENAPI_POLICY_RULESET_GATE` e `CONTRACT_BREAKING_CHANGE_GATE` não podem falhar;
- root OpenAPI deve estar sincronizado com os módulos;
- operations protegidas usam somente `HTTPBearer`;
- operations protegidas documentam `500` com `application/problem+json`;
- mutações contratuais documentam `409` quando não forem auth login/refresh/logout;
- operações com query analítica usam request/response soberanos com filtros estruturados e `additionalProperties: false` nas linhas de resultado;
- responses de entidades estáveis não amputam a shape soberana sem justificativa explícita;
- baseline e waiver machine-readable devem existir quando houver breaking change.

### 16.2 DoD por superfície — AsyncAPI

- channel/message/schema devem existir em path canônico;
- `ASYNCAPI_VALIDATION_GATE` deve passar;
- evento não pode contradizer invariantes do módulo;
- bundle gerado mantém root e filesystem em sincronia, sem canais ausentes.

### 16.3 DoD por superfície — Arazzo

- workflow deve referenciar apenas `operationId` soberano;
- `ARAZZO_VALIDATION_GATE` deve passar;
- handoff não ocorre com workflow órfão de contrato HTTP.

### 16.4 DoD por superfície — Schema-only

- schema valida em Draft 2020-12;
- naming, formatos e bindings semânticos obedecem `DATA_CONVENTIONS.md` e `DOMAIN_AXIOMS.json`;
- docs de módulo explicam o uso e a invariante do schema.

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

Regras adicionais:
- compatibilidade de tooling/config é validada por `TOOLING_CONFIG_GATE` antes dos gates semânticos;
- ausência de `oasdiff` ou `Schemathesis` em CI oficial resulta em `FAIL`;
- fora de CI, fallback só é permitido com estado explícito `DEGRADED`, conforme `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md`.

### Exemplos de uso
Para exemplos práticos de comandos de cada ferramenta, ver `.contract_driven/templates/globais/CI_CONTRACT_GATES.md` (referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 21).

---

## 20. Modos de operação do agente

O agente opera usando `task_type` canônicos definidos em `docs/_canon/AGENT_INSTRUCTIONS.md §4`:

- `new_contract` — criar novo artefato de contrato
- `contract_revision` — revisar ou alterar contrato existente
- `generate_code` — implementar software a partir de contratos
- `new_module`, `new_event`, `new_workflow`, `new_schema`, `new_state_model`, `new_ui_contract`, `architecture_review` — ver docs/_canon/AGENT_INSTRUCTIONS.md §4

Regra:
O `task_type` ativo determina qual worker é acionado e qual perfil de boot é carregado.
Os perfis formais de boot ficam em `.contract_driven/BOOT_PROFILES.yaml` (quando implementado).
O formato do relatório de boot está em `docs/_canon/OPERATIONS.md`.

---

---

## 22. Fase Pré-Contrato Obrigatória

### 22.1 Regra normativa
Nenhuma tarefa contract-driven pode acionar um worker diretamente sem ter completado com sucesso a fase pré-contrato definida em `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`.

O orquestrador pré-contrato é o **ponto de entrada obrigatório** para todas as tarefas de contrato.

### 22.2 Condição de bloqueio
Se um worker for acionado sem evidência de execução prévia da fase pré-contrato (Fases 0–3 de `pre_contract_orchestrator.prompt.md`), o agente deve:
1. Parar imediatamente.
2. Emitir `BLOCKED_PRE_CONTRACT_SKIPPED`.
3. Requerer que a execução reinicie pelo orquestrador pré-contrato.

Nenhuma exceção implícita é permitida.

### 22.3 Exceção explícita
A fase pré-contrato pode ser omitida apenas quando:
- A tarefa for estritamente de leitura/auditoria e não produzir artefato normativo algum, **e**
- O agente declarar explicitamente no output: `PRE_CONTRACT_SKIPPED: audit-only, no artifact produced`.

Qualquer outra omissão silenciosa é proibida.

### 22.4 Artefatos canônicos do orquestrador pré-contrato
Os seguintes arquivos compõem a infraestrutura operacional da fase pré-contrato e são normativos:
- `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` — ponto de entrada obrigatório
- `.contract_driven/agent_prompts/decision_discovery.prompt.md` — estágio Decision Discovery
- `docs/_canon/DECISION_POLICY.md` — SSOT de política de decisões arquiteturais
- `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` — registro de decisões em aberto

Esses artefatos têm o mesmo nível de soberania que os artefatos listados em §3.2 (Global governance docs) e aplicam-se à governança operacional de agentes.

---

## 23. Evolution Rule

Toda mudança deve seguir esta ordem:
1. atualizar artefato normativo
2. validar contrato
3. regenerar artefatos derivados
4. atualizar implementação
5. rodar testes
6. revisar impacto

Implementation-first seguido de documentação depois é proibido.

---

## 24. Validação de Scope Boundary — Cross-Module References

### Objetivo
Garantir que referências entre módulos (cross-module references) sejam explícitas e autorizadas,
prevenindo acoplamento silencioso e violações de isolamento de domínio.

### Contexto
O HB Track é um monólito modular com 17 módulos lógicos, cada um com responsabilidade de domínio clara.
Uma referência de módulo A para recurso de módulo B deve estar:
- Explicitamente permitida em política (`docs/_canon/SCOPE_BOUNDARY_POLICY.md`), **ou**
- Autorizada por ADR aprovada que autorize a exceção

Sem uma das duas → **BLOCKED_SCOPE_OVERFLOW**

### Regra Principal

Nenhuma referência cross-module é permitida sem justificativa explícita.

**Fail-safe**: quando há dúvida, rejeitar a referência.

### Tipos de Referências Detectadas

1. **JSON Schema `$ref`**: `#/components/schemas/users/User`, `identity_access/Identity.schema.json`
2. **OpenAPI `operationId`**: formato `module.operation` (ex: `training.publishSession`)
3. **AsyncAPI channels**: formato `module.event` (ex: `analytics.kpi_computed`)
4. **Arazzo `sourceDescription.$ref`**: referências de workflow entre operações

### Política de Autorização

A lista autoritativa de permissões está em `docs/_canon/SCOPE_BOUNDARY_POLICY.md` §2.

Cada módulo define:
- `allowed_references`: lista de módulos de destino permitidos + razão + exemplos
- `forbidden_references`: lista de módulos de destino explicitamente proibidos
- `exceptions`: ADRs específicas que autorizam violations excepcionais

### Validação Operacional

Gate: `SCOPE_BOUNDARY_GATE` (ordem 1.5 em GATES_REGISTRY.yaml)
- Fase: 1 (Fase de descoberta de artefatos pré-contrato)
- Script: `scripts/gates/check_scope_boundary.py`
- Failure code: `BLOCKED_SCOPE_OVERFLOW`

Pseudocódigo:
```
para cada reference em artifact:
  target_module = parse_module_from_reference(reference)
  
  se target_module == origem_module:
    continue  # intra-module OK
  
  se target_module in allowed_references[origin_module]:
    continue  # permitido
  
  se target_module tem ADR de exception em SCOPE_BOUNDARY_POLICY:
    validar ADR existe e é accepted
    se sim: continue | senão: BLOCKED_SCOPE_OVERFLOW
  
  # violação
  return BLOCKED_SCOPE_OVERFLOW
```

### Exemplos

**✓ PERMITIDO**:
- `users` → `seasons` (atleta vinculado a temporada)
- `training` → `exercises` (exercícios executados em sessão)
- `analytics` → qualquer módulo funcional (agregação de dados)

**✗ BLOQUEADO**:
- `users` → `identity_access` (users nunca define autenticação)
- `training` → `competitions` (training não orquestra competições)
- `identity_access` → `training` (cross-cutting nunca depende de funcional)

### Evolução

Quando precisar adicionar uma referência cross-module não permitida:

1. Avaliar: é realmente necessário ou pode ser refatorado?
2. Se necessário:
   - Criar ADR (ex: ADR-032: "Allow training → competitions for eligibility")
   - Descrever por que é necessário e quais proteções será implementadas
   - Submeter ADR para revisão
   - Após aceitar: atualizar `SCOPE_BOUNDARY_POLICY.md` com exceção + link à ADR

### Referências

- **Policy SSOT**: `docs/_canon/SCOPE_BOUNDARY_POLICY.md`
- **Gate metadata**: `docs/_canon/gates/GATES_REGISTRY.yaml` (SCOPE_BOUNDARY_GATE)
- **Validator script**: `scripts/gates/check_scope_boundary.py`
- **ADR de criação**: `docs/_canon/decisions/ADR-031-scope-boundary-validation.md`
- **Related rules**: §2C (Taxonomia de módulos), §9 (Códigos de bloqueio)
