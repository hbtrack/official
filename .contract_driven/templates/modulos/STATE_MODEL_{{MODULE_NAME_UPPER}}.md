---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/<module>/STATE_MODEL_{{MODULE_NAME_UPPER}}.md
# SOURCE: .contract_driven/templates/modulos/STATE_MODEL_{{MODULE_NAME_UPPER}}.md
module: "{{MODULE_NAME}}"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
type: "state-model"
diagram_format: "mermaid"
---

# STATE_MODEL_{{MODULE_NAME_UPPER}}.md

## Objetivo
Documentar os estados e transições válidas do módulo `{{MODULE_NAME}}`.

## Entidade principal
- `{{DOMAIN_ENTITY}}`

## Regras de modelagem
- Toda transição deve ter gatilho definido
- Toda transição inválida deve ser tratada como erro
- Toda transição crítica deve ter cobertura em `TEST_MATRIX_{{MODULE_NAME_UPPER}}.md`

## Diagrama de estados

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Active: {{TRIGGER_ACTIVATE}}
  Active --> Suspended: {{TRIGGER_SUSPEND}}
  Suspended --> Active: {{TRIGGER_RESUME}}
  Active --> Closed: {{TRIGGER_CLOSE}}
  Closed --> [*]
```

## Tabela de estados
| Estado | Descrição | Estado inicial | Estado terminal |
|---|---|---|---|
| Draft | {{STATE_DESCRIPTION_DRAFT}} | Sim | Não |
| Active | {{STATE_DESCRIPTION_ACTIVE}} | Não | Não |
| Suspended | {{STATE_DESCRIPTION_SUSPENDED}} | Não | Não |
| Closed | {{STATE_DESCRIPTION_CLOSED}} | Não | Sim |

## Tabela de transições
| De | Para | Gatilho | Regra | Erro se inválido |
|---|---|---|---|---|
| Draft | Active | {{TRIGGER_ACTIVATE}} | {{RULE}} | {{ERROR_CODE}} |
| Active | Suspended | {{TRIGGER_SUSPEND}} | {{RULE}} | {{ERROR_CODE}} |
| Suspended | Active | {{TRIGGER_RESUME}} | {{RULE}} | {{ERROR_CODE}} |
| Active | Closed | {{TRIGGER_CLOSE}} | {{RULE}} | {{ERROR_CODE}} |

## Observações
Se houver regra esportiva impactando estado, citar explicitamente `HANDBALL_RULES_DOMAIN.md`.
