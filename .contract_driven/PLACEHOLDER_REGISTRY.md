# PLACEHOLDER_REGISTRY.md

> Referência completa de placeholders para templates. Documento puro de referência, não normativo.
> Consultar quando preenchendo templates em `.contract_driven/templates/`.

---

## 0. Convenção de naming

**Todos os placeholders usam UPPER_SNAKE_CASE**: `{{PLACEHOLDER_NAME}}`

Exceções para identificadores técnicos específicos de módulo:
- `{{MODULE_NAME}}` — identificador técnico em lower_snake_case (ex: "training", "identity_access")
- Demais placeholders derivados do módulo usam variantes em uppercase ({{MODULE_NAME_UPPER}}, {{MODULE_NAME_PASCAL}})
- `{{HANDBALL_REFERENCE}}` — referência específica ao trecho/regra traduzida em `docs/_canon/HANDBALL_RULES_DOMAIN.md`

**Regra**: Todos os placeholders não resolvidos são proibidos em artefatos ready-for-implementation.

---

## 1. Placeholders core obrigatórios

| Placeholder | Descrição | Tipo |
|--|--|--|
| `{{PROJECT_NAME}}` | Nome do projeto/sistema | string |
| `{{MODULE_NAME}}` | Identificador técnico canônico lower_snake_case | string |
| `{{MODULE_NAME_UPPER}}` | Versão uppercase | string |
| `{{MODULE_NAME_PASCAL}}` | Versão PascalCase para código | string |
| `{{DOMAIN_ENTITY}}` | Entidade de domínio principal em linguagem natural | string |
| `{{DOMAIN_ENTITY_SNAKE}}` | Entidade em lower_snake_case técnico | string |
| `{{DOMAIN_ENTITY_PASCAL}}` | Entidade em PascalCase para código | string |

---

## 2. Placeholders de projeto e sistema

| Placeholder | Descrição |
|--|--|
| `{{CDD_MATURITY_LEVEL}}` | Nível de maturidade contract-driven |
| `{{LAST_REVIEW_DATE}}` | Data da última revisão |
| `{{SYSTEM_TYPE}}` | Tipo de sistema |
| `{{ORG_NAME}}` | Nome da organização |
| `{{TARGET_USERS}}` | Usuários-alvo |
| `{{PRIMARY_MARKET}}` | Mercado primário |
| `{{PROJECT_DOMAIN}}` | Domínio HTTP do projeto (ex: "hbtrack.com") |

---

## 3. Placeholders de arquitetura

| Placeholder | Descrição |
|--|--|
| `{{BACKEND_STYLE}}` | Estilo arquitetural backend |
| `{{FRONTEND_STYLE}}` | Estilo arquitetural frontend |
| `{{DATA_STYLE}}` | Estilo de persistência |
| `{{INTEGRATION_STYLE}}` | Estilo de integração |
| `{{BACKEND_STACK}}` | Stack tecnológica backend |
| `{{FRONTEND_STACK}}` | Stack tecnológica frontend |
| `{{DATABASE_STACK}}` | Stack de banco de dados |
| `{{EVENT_STACK}}` | Stack de mensageria |
| `{{TEST_STACK}}` | Stack de testes |

---

## 4. Placeholders de escopo e risco

| Placeholder | Descrição | Formato |
|--|--|--|
| `{{RESPONSIBILITIES_MD_LIST}}` | Lista Markdown de responsabilidades | `- item` |
| `{{OUT_OF_SCOPE_MD_LIST}}` | Lista Markdown de itens fora do escopo | `- item` |
| `{{EXTERNAL_DEPENDENCIES_MD_LIST}}` | Lista Markdown de dependências externas | `- item` |
| `{{KNOWN_RISKS_MD_LIST}}` | Lista Markdown de riscos conhecidos | `- item` |
| `{{OPEN_DECISIONS_MD_LIST}}` | Lista Markdown de decisões em aberto | `- item` |

---

## 5. Placeholders de convenções de API

| Placeholder | Descrição |
|--|--|
| `{{RESPONSE_ENVELOPE_POLICY}}` | Política de envelopes de resposta |
| `{{PAGINATION_POLICY}}` | Política de paginação |
| `{{SORT_POLICY}}` | Política de ordenação |
| `{{FILTER_POLICY}}` | Política de filtros |
| `{{AUTH_STRATEGY}}` | Estratégia de autenticação |
| `{{AUTHZ_STRATEGY}}` | Estratégia de autorização |
| `{{VERSIONING_STRATEGY}}` | Estratégia de versionamento |
| `{{DEPRECATION_POLICY}}` | Política de depreciação |

---

## 6. Placeholders de convenções de dados

| Placeholder | Descrição |
|--|--|
| `{{ID_STRATEGY}}` | Estratégia de IDs |
| `{{DATE_TIME_STANDARD}}` | Padrão de data/hora |
| `{{TIMEZONE_POLICY}}` | Política de fuso horário |
| `{{ENUM_POLICY}}` | Política de enums |
| `{{NULLABILITY_POLICY}}` | Política de nullability |
| `{{TABLE_NAMING}}` | Nomenclatura de tabelas |
| `{{FIELD_NAMING}}` | Nomenclatura de campos |

---

## 7. Placeholders de segurança

| Placeholder | Descrição |
|--|--|
| `{{SENSITIVE_DATA_POLICY}}` | Política de dados sensíveis |
| `{{RETENTION_POLICY}}` | Política de retenção |
| `{{MASKING_POLICY}}` | Política de mascaramento |
| `{{SECRETS_POLICY}}` | Origem de secrets |
| `{{ROTATION_POLICY}}` | Política de rotação de secrets |
| `{{LOGGING_POLICY}}` | Política de logs |

---

## 8. Placeholders de UI e acessibilidade

| Placeholder | Descrição |
|--|--|
| `{{BREAKPOINT_STRATEGY}}` | Estratégia de breakpoints |
| `{{TARGET_DEVICES}}` | Dispositivos-alvo |
| `{{A11Y_CONTRAST_RULE}}` | Regra de contraste de acessibilidade |
| `{{A11Y_LABEL_RULE}}` | Regra de labels de acessibilidade |

---

## 9. Placeholders de erro e trace

| Placeholder | Descrição |
|--|--|
| `{{RESOURCE_PATH}}` | Caminho do recurso HTTP |
| `{{TRACE_ID}}` | Identificador de rastreamento |
| `{{ERROR_MESSAGE}}` | Mensagem de erro |
| `{{ERROR_CODE}}` | Código de erro |
| `{{ERROR_CASE}}` | Caso de erro |
| `{{HTTP_STATUS}}` | Status HTTP |

---

## 10. Placeholders do domínio de handebol

| Placeholder | Descrição |
|--|--|
| `{{RULEBOOK_TITLE}}` | Título do regulamento oficial |
| `{{RULEBOOK_VERSION}}` | Versão do regulamento |
| `{{RULEBOOK_EFFECTIVE_DATE}}` | Data de vigência |
| `{{HANDBALL_TOPIC}}` | Tema do handebol |
| `{{HANDBALL_RULE}}` | Regra oficial do handebol |
| `{{PRODUCT_RULE}}` | Regra de produto derivada |
| `{{MODULES}}` | Módulos impactados |
| `{{RULE_REFERENCE}}` | Referência à regra |
| `{{HANDBALL_SEMANTIC_APPLICABILITY}}` | `true\|false` para campo no header YAML |

---

## 11. Placeholders de conteúdo de módulo

| Placeholder | Descrição |
|--|--|
| `{{MODULE_PURPOSE}}` | Propósito do módulo |
| `{{MODULE_MISSION}}` | Missão do módulo |
| `{{ACTORS_MD_LIST}}` | Lista Markdown de atores | 
| `{{DOMAIN_ENTITIES_MD_LIST}}` | Lista Markdown de entidades principais |
| `{{IN_SCOPE_MD_LIST}}` | Lista Markdown de itens dentro do escopo |
| `{{UPSTREAM_MODULES}}` | Módulos upstream (dependências) |
| `{{DOWNSTREAM_MODULES}}` | Módulos downstream (consumidores) |

---

## 12. Placeholders de regras de domínio

| Placeholder | Descrição | Formato |
|--|--|--|
| `{{BUSINESS_RULES_TABLE_ROWS}}` | Linhas para tabela de regras de negócio | Markdown `\| ... \|` |
| `{{HANDBALL_DERIVED_RULES_TABLE_ROWS}}` | Linhas para tabela de regras derivadas | Markdown `\| ... \|` |
| `{{SPORT_SCIENCE_RULES_TABLE_ROWS}}` | Linhas para tabela de métodos/protocolos/cálculos | Markdown `\| ... \|` |
| `{{SOURCE}}` | Fonte normativa |

---

## 13. Placeholders de state model

| Placeholder | Descrição |
|--|--|
| `{{STATE_NAME}}` | Nome de estado |
| `{{TRIGGER_ACTIVATE}}` | Gatilho de ativação |
| `{{TRIGGER_SUSPEND}}` | Gatilho de suspensão |
| `{{TRIGGER_RESUME}}` | Gatilho de retomada |
| `{{TRIGGER_CLOSE}}` | Gatilho de encerramento |
| `{{STATE_DESCRIPTION_DRAFT}}` | Descrição do estado Draft |
| `{{STATE_DESCRIPTION_ACTIVE}}` | Descrição do estado Active |
| `{{STATE_DESCRIPTION_SUSPENDED}}` | Descrição do estado Suspended |
| `{{STATE_DESCRIPTION_CLOSED}}` | Descrição do estado Closed |
| `{{RULE}}` | Regra associada à transição |

---

## 14. Placeholders de permissões, erros e UI

| Placeholder | Descrição |
|--|--|
| `{{ACTION}}` | Ação/operação |
| `{{ROLE}}` | Papel/perfil |
| `{{YES_NO}}` | Sim/não |
| `{{NOTE}}` | Nota/observação |
| `{{INPUT}}` | Entrada de UI |
| `{{OUTPUT}}` | Saída de UI |
| `{{SCREEN_A}}`, `{{SCREEN_B}}`, `{{SCREEN_C}}` | Telas em mapas de navegação |

---

## 15. Placeholders de teste e evidência

| Placeholder | Descrição |
|--|--|
| `{{STATE_TEST_TOOL}}` | Ferramenta de teste de transição de estado |
| `{{BUSINESS_RULE_TOOL}}` | Ferramenta de teste de regra de negócio |
| `{{INVARIANT_TEST_TOOL}}` | Ferramenta de teste de invariante |
| `{{CONTRACT_TEST_TOOL}}` | Ferramenta de teste contratual |
| `{{SCHEMA_TEST_TOOL}}` | Ferramenta de validação de schema |
| `{{UNIT_TEST_TOOL}}` | Ferramenta de teste unitário |
| `{{INTEGRATION_TEST_TOOL}}` | Ferramenta de teste de integração |
| `{{E2E_TEST_TOOL}}` | Ferramenta de teste E2E |
| `{{EVIDENCE}}` | Evidência de teste |
| `{{AREA}}` | Área de teste |
| `{{RISK_LEVEL}}` | Nível de risco |
| `{{TEST_TYPE}}` | Tipo de teste |

---

## 16. Placeholders de ADR

| Placeholder | Descrição |
|--|--|
| `{{ADR_NUMBER}}` | Número do ADR |
| `{{DECISION_TITLE}}` | Título da decisão |
| `{{DATE}}` | Data |
| `{{DECIDERS}}` | Tomadores de decisão |
| `{{TAGS}}` | Tags |
| `{{CONTEXT}}` | Contexto |
| `{{DECISION}}` | Decisão |
| `{{POSITIVE_CONSEQUENCES_MD_LIST}}` | Lista Markdown de consequências positivas | 
| `{{NEGATIVE_CONSEQUENCES_MD_LIST}}` | Lista Markdown de consequências negativas |
| `{{ALTERNATIVES_CONSIDERED_MD_LIST}}` | Lista Markdown de alternativas consideradas |
| `{{RELATED_DOCS}}` | Documentos relacionados |
| `{{RELATED_CONTRACTS}}` | Contratos relacionados |

---

## 17. Placeholders técnicos de OpenAPI e schema

| Placeholder | Descrição |
|--|--|
| `{{FIELD_NAME}}` | Nome de campo |
| `{{FIELD_TYPE}}` | Tipo de campo |
| `{{FIELD_DESCRIPTION}}` | Descrição de campo |
| `{{EXAMPLE_ID}}` | ID de exemplo |
| `{{EXAMPLE_CREATED_AT}}` | Exemplo de data de criação |
| `{{EXAMPLE_UPDATED_AT}}` | Exemplo de data de atualização |
| `{{FIELD_EXAMPLE_VALUE}}` | Valor de exemplo de campo |

---

## 18. Placeholders específicos de MODULE_MAP

| Placeholder | Descrição |
|--|--|
| `{{RESP_ATLETAS}}`, `{{DEP_ATLETAS}}` | Responsabilidade e dependências de Atletas |
| `{{RESP_EQUIPES}}`, `{{DEP_EQUIPES}}` | Responsabilidade e dependências de Equipes |
| `{{RESP_TREINOS}}`, `{{DEP_TREINOS}}` | Responsabilidade e dependências de Treinos |
| `{{RESP_JOGOS}}`, `{{DEP_JOGOS}}` | Responsabilidade e dependências de Jogos |
| `{{RESP_COMPETICOES}}`, `{{DEP_COMPETICOES}}` | Responsabilidade e dependências de Competições |
| `{{RESP_ANALYTICS}}`, `{{DEP_ANALYTICS}}` | Responsabilidade e dependências de Analytics |

---

## 19. Placeholders de gates e CI

| Placeholder | Descrição |
|--|--|
| `{{API_BASE_URL}}` | URL base da API para testes |

---

## 20. Placeholders de glossário

| Placeholder | Descrição |
|--|--|
| `{{TERM}}` | Termo |
| `{{DEFINITION}}` | Definição |
| `{{CONTEXT}}` | Contexto |

---

## 21. Placeholders de invariantes

| Placeholder | Descrição | Formato |
|--|--|--|
| `{{INVARIANT}}` | Invariante genérica | string |
| `{{INVARIANTS_TABLE_ROWS}}` | Linhas para tabela de invariantes | Markdown `\| ... \|` |
| `{{CHECK_METHOD}}` | Método de verificação |

---

## 22. Placeholders de propósito geral

| Placeholder | Descrição |
|--|--|
| `{{PURPOSE}}` | Propósito geral |
| `{{EVENT_NAME}}` | Nome de evento |

---

## Fonte e uso

Ao usar estes placeholders:
1. Consultar este registro antes de preencher templates
2. Garantir que todos os placeholders sejam preenchidos
3. Não criar novos placeholders — registrar aqui primeiro
4. Deletar placeholders não preenchidos antes de commitar

Referência de templates: [.contract_driven/templates/README.md](.contract_driven/templates/README.md)
