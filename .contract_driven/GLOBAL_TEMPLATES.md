# GLOBAL_TEMPLATES.md

## 0. Índice cruzado

Este documento faz parte da trilogia **HB Track — Manual Contract-Driven**:

1. **.contract_driven/CONTRACT_SYSTEM_LAYOUT.md**
   - **Responsabilidade**: Estrutura canônica de filesystem, taxonomia de módulos, convenções de nomenclatura, regras de localização de artefatos
   - **Use quando**: Definir onde criar artefatos, validar nomes de módulos, checar regras de naming

2. **.contract_driven/CONTRACT_SYSTEM_RULES.md**
   - **Responsabilidade**: Regras operacionais, hierarquia de precedência, boot protocol do agente, códigos de bloqueio, ferramentas de validação, procedimentos de evolução
   - **Use quando**: Entender como criar/modificar contratos, determinar precedência em conflitos, comportamento de bloqueio, passos de validação

3. **.contract_driven/GLOBAL_TEMPLATES.md** (este arquivo)
   - **Responsabilidade**: Scaffolds e exemplos oficiais para documentação normativa e artefatos de contrato
   - **Use quando**: Criar novos docs de módulo, contratos, ou artefatos de governança

4. **.contract_driven/templates/api/api_rules.yaml**
   - **Responsabilidade**: Regras, validações e templates canônicos para contratos de APIs (OpenAPI/HTTP)
   - **Use quando**: Criar/validar contratos de APIs com determinismo máximo

**Regra de navegação**: Estes arquivos devem ser lidos em conjunto. Referências cruzadas entre eles são explícitas e vinculantes.

---

> **Escopo deste arquivo**: scaffolds para documentação humana normativa (`docs/_canon/`,
> `docs/hbtrack/modulos/`, `contracts/README`, ADRs e artefatos de governança).
>
> **Não** contém nem deve conter templates de artefatos técnicos de API (root OpenAPI,
> path modules, schemas de request/response, parâmetros de paginação, shapes de erro).
> Esses templates vivem exclusivamente em `.contract_driven/templates/api/api_rules.yaml`
> (seção `contract_templates`). Este arquivo deve apenas **referenciar** — nunca duplicar.

---

## Objetivo

> **Nota**: os corpos completos das templates deste documento foram migrados para `.contract_driven/templates/` (subpastas `globais/` e `modulos/`).
> Este arquivo mantém apenas o índice, regras e referências. Para instanciar, copie o arquivo de template para o path canônico e preencha os placeholders.

Este arquivo fornece scaffolds oficiais para documentação normativa e artefatos de contrato.

Templates **não são normativos por si só**.
Os arquivos instanciados tornam-se normativos apenas quando criados na localização canônica e governados pelas regras.

---

## 1. Referência de placeholders

**Referência completa de placeholders:** consultar [PLACEHOLDER_REGISTRY.md](PLACEHOLDER_REGISTRY.md)

Regra:
- Placeholders não resolvidos são proibidos em artefatos ready-for-implementation
- Ao criar novos placeholders, registrar em PLACEHOLDER_REGISTRY.md

---

## 2. Regra de soberania de templates

Templates são apenas scaffolds.

Eles tornam-se normativos apenas quando:
- instanciados na localização canônica
- preenchidos sem placeholders proibidos
- alinhados a `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- alinhados a `.contract_driven/CONTRACT_SYSTEM_RULES.md`

Se um template conflitar com uma regra normativa, a regra normativa vence.

---

## 2A. Paths canônicos de instanciação

Templates devem ser instanciados apenas nos paths canônicos abaixo.

### 2A.1 Contract-system governance
- `.contract_driven/`

### 2A.2 Global normative canon
- `docs/_canon/`

### 2A.3 Module normative documentation
- `docs/hbtrack/modulos/<module>/`

### 2A.4 Technical contracts
- `contracts/`

Regra:
Um template corretamente preenchido, mas instanciado fora do path canônico, não é considerado compliant por padrão.

---

## 3. Required Header Template for Module Human Docs


Template movido para: `.contract_driven/templates/modulos/snippets/module_human_docs_header.yaml`


Use este header em:
- `docs/hbtrack/modulos/{{MODULE_NAME}}/README.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/INVARIANTS_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/STATE_MODEL_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/PERMISSIONS_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/ERRORS_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`
- `docs/hbtrack/modulos/{{MODULE_NAME}}/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md`

### 3.1 Header rules
- module deve usar o identificador técnico canônico do módulo em inglês (`lower_snake_case` de `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` seção 2)
- `system_scope_ref` é sempre obrigatório
- `handball_rules_ref` é sempre presente no header para navegabilidade
- `handball_semantic_applicability` deve ser true apenas quando o gatilho definido em `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 12 se aplica
- `handball_semantic_applicability` deve ser false quando o módulo não for semanticamente governado por regras derivadas do handebol
- `contract_path_ref` deve apontar para o OpenAPI path file canônico
- `schemas_ref` deve apontar para a pasta canônica de schemas

Nota: MODULE_NAME placeholder deve usar identificador técnico canônico lower_snake_case da taxonomia (ex: 'training', 'identity_access', 'competitions').

## 4. Regra de arquitetura de documentação (Diátaxis)

**Para a regra completa de arquitetura de documentação usando o framework Diátaxis, ver `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 7.**

Os templates neste arquivo miram apenas artefatos de referência e explicação.

---

## 5. Global Template — docs/_canon/README.md

Template movido para: `.contract_driven/templates/globais/README.md`


---

## 6. Global Template — docs/_canon/SYSTEM_SCOPE.md


Template movido para: `.contract_driven/templates/globais/SYSTEM_SCOPE.md`


---

## 7. Global Template — docs/_canon/ARCHITECTURE.md


Template movido para: `.contract_driven/templates/globais/ARCHITECTURE.md`


---

## 8. Global Template — docs/_canon/C4_CONTEXT.md


Template movido para: `.contract_driven/templates/globais/C4_CONTEXT.md`


---

## 9. Global Template — docs/_canon/C4_CONTAINERS.md


Template movido para: `.contract_driven/templates/globais/C4_CONTAINERS.md`


---

## 10. Global Template — docs/_canon/MODULE_MAP.md


Template movido para: `.contract_driven/templates/globais/MODULE_MAP.md`


---

## 11. Global Template — docs/_canon/CHANGE_POLICY.md


Template movido para: `.contract_driven/templates/globais/CHANGE_POLICY.md`


---

## 13. Global Template — docs/_canon/DATA_CONVENTIONS.md


Template movido para: `.contract_driven/templates/globais/DATA_CONVENTIONS.md`


---

## 14. Global Template — docs/_canon/GLOBAL_INVARIANTS.md


Template movido para: `.contract_driven/templates/globais/GLOBAL_INVARIANTS.md`


---

## 16. Global Template — docs/_canon/DOMAIN_GLOSSARY.md


Template movido para: `.contract_driven/templates/globais/DOMAIN_GLOSSARY.md`


---

## 17. Global Template — docs/_canon/HANDBALL_RULES_DOMAIN.md


Template movido para: `.contract_driven/templates/globais/HANDBALL_RULES_DOMAIN.md`


---

## 18. Global Template — docs/_canon/SECURITY_RULES.md


Template movido para: `.contract_driven/templates/globais/SECURITY_RULES.md`


---

## 18. Global Template — docs/_canon/CI_CONTRACT_GATES.md


Template movido para: `.contract_driven/templates/globais/CI_CONTRACT_GATES.md`


---

## 22. Global Template — docs/_canon/TEST_STRATEGY.md


Template movido para: `.contract_driven/templates/globais/TEST_STRATEGY.md`


---

## 23. Global Template — docs/_canon/decisions/ADR-0001-template.md


Template movido para: `.contract_driven/templates/globais/decisions/ADR-0001-template.md`


---

## 24. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/README.md


Template movido para: `.contract_driven/templates/modulos/README.md`


---

## 25. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/MODULE_SCOPE_{{MODULE_NAME_UPPER}}.md`


---

## 26. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md`


---

## 27. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/INVARIANTS_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/INVARIANTS_{{MODULE_NAME_UPPER}}.md`


---

## 28. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/STATE_MODEL_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md`


---

## 29. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/PERMISSIONS_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/PERMISSIONS_{{MODULE_NAME_UPPER}}.md`


---

## 30. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/ERRORS_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/ERRORS_{{MODULE_NAME_UPPER}}.md`


---

## 31. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md`


---

## 32. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md`


---

## 33. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`

---

## 33A. Module Template — docs/hbtrack/modulos/{{MODULE_NAME}}/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md


Template movido para: `.contract_driven/templates/modulos/SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md`


---

## 34. Module Template — contracts/openapi/paths/{{MODULE_NAME}}.yaml

Templates canônicos de OpenAPI (paths e components) vivem em `.contract_driven/templates/api/api_rules.yaml` em `hbtrack_api_rules.contract_templates`.

Regra: este arquivo não deve duplicar templates de API. Use apenas a referência acima.


---

## 34A. Templates de OpenAPI Components

Templates canônicos de OpenAPI Components (parameters/schemas/responses/requestBodies) vivem em `.contract_driven/templates/api/api_rules.yaml` em `hbtrack_api_rules.contract_templates`.

Regra: este arquivo não deve duplicar templates de API. Use apenas a referência acima.

---

## 35. Module Template — contracts/schemas/{{MODULE_NAME}}/{{DOMAIN_ENTITY_SNAKE}}.schema.json

**Quando usar este template**: Aplicar quando a entidade for um **domain shape** — conceito canônico de domínio reutilizável, com identidade própria ou lifecycle mensurável. Para shapes exclusivamente HTTP-facing (DTOs de request/response sem reuso semântico), usar os templates de `components/schemas/` em `api_rules.yaml`. A decisão entre domain shape e HTTP DTO é governada por `.contract_driven/CONTRACT_SYSTEM_RULES.md` §14A.

**Nota sobre Lifecycle & Audit fields**: Os fields `status`, `createdAt`, `updatedAt` são **condicionais**. Incluí-los apenas quando a entidade tiver requisitos reais de lifecycle ou auditoria, conforme `.contract_driven/CONTRACT_SYSTEM_RULES.md` §14A.7 e §11.1 (Matriz de aplicabilidade). O template abaixo mostra a estrutura mínima obrigatória com fields condicionais como exemplos `$$comment_*` — descomentar e customizar quando necessário.

Template movido para: `.contract_driven/templates/modulos/schemas/{{DOMAIN_ENTITY_SNAKE}}.schema.json`


---

## 36. Regras de uso condicional

### 36.1 Usar `STATE_MODEL_{{MODULE_NAME_UPPER}}.md` quando
- existirem transições de status
- existir lógica de lifecycle

**Referência**: `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 11.1 define a matriz formal de aplicabilidade para STATE_MODEL.

**Impacto no template**: Quando STATE_MODEL não for aplicável:
- Remover `state_model_ref` do header YAML do README.md do módulo, ou manter comentado como referência não-operativa
- Omitir fields de lifecycle/state de JSON schemas (seção 35)
- Marcar TM-003 na TEST_MATRIX como "Quando aplicável" (seção 33)

### 36.2 Usar `PERMISSIONS_{{MODULE_NAME_UPPER}}.md` quando
- existirem regras específicas de RBAC

### 36.3 Usar `ERRORS_{{MODULE_NAME_UPPER}}.md` quando
- existir semântica de erro domain-specific

### 36.4 Usar `UI_CONTRACT_{{MODULE_NAME_UPPER}}.md` quando
- existir comportamento real de UI a ser restringido

### 36.5 Usar `SCREEN_MAP_{{MODULE_NAME_UPPER}}.md` quando
- existir navegação real screen-to-screen ou jornada multi-screen

### 36.6 Usar `contracts/workflows/{{MODULE_NAME}}/*.arazzo.yaml` quando
- a orquestração for multi-step e dependente

### 36.7 Usar `contracts/asyncapi/{{MODULE_NAME}}.yaml` quando
- existirem eventos reais

**Handball Trigger Rule**: Para a lista completa de tópicos de handebol que determinam quando `handball_rules_ref` é obrigatório no header YAML do módulo, ver `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 12 (Handball Trigger Rule).

### 36.8 Usar `SPORT_SCIENCE_RULES_{{MODULE_NAME_UPPER}}.md` quando
- o módulo depender de protocolos, cálculos, thresholds, baterias de teste, readiness, strain, HRV, força, HIIT, prescrição ou interpretação técnico-científica aplicada
- houver risco de contaminar `DOMAIN_RULES` com critério técnico-científico

**Referência**: `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 11.8 define a matriz formal de aplicabilidade para SPORT_SCIENCE_RULES.

---

## 37. Regra de interação agente/template

Templates não decidem aplicabilidade.
Aplicabilidade é governada por `.contract_driven/CONTRACT_SYSTEM_RULES.md`.

Se a tarefa atual exigir um template cujo artefato pré-requisito esteja ausente, o agente deve bloquear em vez de improvisar.

---

## 37A. Protocolo de bloqueio do agente

**Quando artefatos pré-requisito estiverem ausentes**, o agente deve usar os códigos de bloqueio definidos em `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 9 (Códigos de bloqueio).

**Cenários comuns de bloqueio ao usar templates**:
- Módulo ausente na taxonomia canônica → `BLOCKED_MISSING_MODULE`
- OpenAPI path file ausente → `BLOCKED_MISSING_OPENAPI_PATH`
- Schema ausente → `BLOCKED_MISSING_SCHEMA`
- Regra de domínio ausente → `BLOCKED_MISSING_DOMAIN_RULE`
- Invariante ausente → `BLOCKED_MISSING_INVARIANT`
- State model ausente quando aplicável → `BLOCKED_MISSING_STATE_MODEL`
- Permission model ausente quando aplicável → `BLOCKED_MISSING_PERMISSION_MODEL`
- UI contract ausente quando aplicável → `BLOCKED_MISSING_UI_CONTRACT`
- Referência de handebol ausente quando o gatilho aplicar → `BLOCKED_MISSING_HANDBALL_REFERENCE`
- Test matrix ausente → `BLOCKED_MISSING_TEST_MATRIX`
- Artefato canônico obrigatório ausente → `BLOCKED_MISSING_CANON_ARTIFACT`
- Convenção de API obrigatória ausente → `BLOCKED_MISSING_API_CONVENTION`
- Conflito entre fontes normativas → `BLOCKED_CONTRACT_CONFLICT`
- Artefato normativo fora do path canônico → `BLOCKED_NONCANONICAL_NORMATIVE_PATH`

**Agent operation modes**: Ao trabalhar com templates em um agent mode específico (contract_creation_mode, contract_revision_mode, implementation_mode, audit_mode), ver `.contract_driven/CONTRACT_SYSTEM_RULES.md` seção 20 (Modos de operação do agente) e seção 21 (Matriz mínima de boot por tipo de tarefa) para sequência obrigatória de boot e outputs esperados.

---

## 38. Regra final de templates

Templates nunca devem contradizer:
- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`

Se um template conflitar com uma regra normativa, a regra normativa vence.
