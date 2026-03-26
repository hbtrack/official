Segue a tabela de transformação.

Ela define como sair da **Matriz Canônica do Módulo** e chegar no **`MODULE_DECISION_IR.json`** sem deixar o agente “interpretar” demais. A lógica é:

* a **Matriz** é a camada de decisão governada;
* o **IR** é a camada compilável;
* tudo que permanecer em linguagem solta na passagem entre as duas camadas ainda é risco de alucinação.

---

# Tabela de Transformação — Matriz Canônica → `MODULE_DECISION_IR.json`

| Origem na Matriz Canônica  | Destino no `MODULE_DECISION_IR.json`                                                                        | Regra de transformação                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Versão`                   | `ir_version`                                                                                                | Copiar literal                                                                                                                                                   |
| `Módulo`                   | `module`                                                                                                    | Normalizar para chave canônica minúscula                                                                                                                         |
| `Status`                   | `status`                                                                                                    | Mapear `draft/proposed/approved` conforme enum do schema                                                                                                         |
| `Fonte primária`           | `source`                                                                                                    | Copiar path literal                                                                                                                                              |
| escopo da matriz           | `decision_scope`                                                                                            | Preencher como `full_module`, `feature` ou `revision`                                                                                                            |
| `Eixo soberano`            | `module_identity.operational_backbone`                                                                      | Converter sequência textual em array ordenado                                                                                                                    |
| identidade geral do módulo | `module_identity`                                                                                           | Consolidar missão, unidade soberana, backbone, benchmark, escopo por fase                                                                                        |
| `decision_id`              | `surface_mapping[].decision_ref` ou `rules[].unique_governance_id` ou `capabilities[].unique_governance_id` | Todo `decision_id` deve sobreviver no IR como identificador rastreável                                                                                           |
| `decision_name`            | `capabilities[].name` ou `rules[].statement_summary`                                                        | Escolha depende do tipo: capability se representar capacidade, rule se representar restrição, state model se representar lifecycle                               |
| `decision_stage`           | bloco alvo do IR                                                                                            | Mapear por estágio: `module_identity`, `need`, `objective`, `prescription`, `session`, `execution`, `response`, `review`, `adjustment`, `boundary`, `governance` |
| `decision_type`            | `rules[].type` ou metadado da capability                                                                    | Mapear `business`, `boundary`, `lifecycle`, `authorization`, `integrity`, `audit`                                                                                |
| `problem_real_world`       | `module_identity.problem_statement` ou `rules[].rationale`                                                  | Só entra onde houver slot de rationale; não deve virar contrato técnico                                                                                          |
| `operational_value_unit`   | `module_identity.real_world_operational_value_unit` ou `entities[]`                                         | Se for entidade do módulo, deve bater com entity id formal                                                                                                       |
| `entity_owner`             | `entities[].ownership` ou `integrations[].ownership_rule`                                                   | Normalizar para ownership canônico                                                                                                                               |
| `entities_touched`         | `capabilities[].entity_refs`, `rules[].subject_ref`, `surface_mapping[]`                                    | Cada entidade citada deve existir formalmente no IR                                                                                                              |
| `minimum_required_fields`  | `entities[].fields[]`                                                                                       | Regra crítica: não copiar em prosa. Expandir para campos tipados com `name`, `semantic_type_ref`, `required`, `nullable`, `description`                          |
| `allowed_origin`           | `rules[].allowed_origin` ou `api_use_cases[].preconditions`                                                 | Pode virar metadado de rule; se impactar API/state, deve virar guard explícito                                                                                   |
| `forbidden_origin`         | `forbidden_inference_global[]` ou `rules[]`                                                                 | Se for restrição global, vai para `forbidden_inference_global`; se local, vira rule                                                                              |
| `allowed_actor`            | `permissions.rules[]` ou `api_use_cases[].actors`                                                           | Normalizar para ator/role canônico                                                                                                                               |
| `forbidden_actor`          | `permissions.rules[]` ou `forbidden_inference_global[]`                                                     | Se for bloqueio de autorização, vai para permissions; se for restrição ampla, vira forbidden inference                                                           |
| `preconditions`            | `rules[].precondition_refs` ou `state_models[].transition_guards`                                           | Não deixar em texto livre se afetar transição                                                                                                                    |
| `postconditions`           | `rules[].postcondition_refs` ou `api_use_cases[].effects`                                                   | Usar apenas quando gera efeito determinístico                                                                                                                    |
| `state_impact`             | `state_models[]`                                                                                            | Converter para `entity_ref`, `initial_state`, `states`, `allowed_transitions`, `forbidden_transitions`, `transition_guards`                                      |
| `events_emitted`           | `events[]`                                                                                                  | Cada evento textual precisa virar objeto com `id`, `subject_ref`, `trigger`, `payload_entity_ref`                                                                |
| `invariants`               | `rules[]`                                                                                                   | Cada `INV-*` deve existir como `rule_ref` válido no IR                                                                                                           |
| `boundary_rules`           | `integrations[]`, `rules[]`, `forbidden_inference_global[]`                                                 | Separar boundary operativo de restrição global                                                                                                                   |
| `evidence_required`        | `rules[].formal_check_hint`                                                                                 | Se a evidência for verificável, vira hint formal                                                                                                                 |
| `gate_class`               | `rules[].blocking` ou `open_decisions[].blocking`                                                           | `blocking` => `true`; `warning` => `false` com revisão posterior                                                                                                 |
| `automation_level`         | metadado do rule/capability                                                                                 | Não gera superfície sozinho; serve para priorização de implementação                                                                                             |
| `materializes_in`          | `surface_mapping[]`                                                                                         | Transformar cada valor em mapping explícito `decision_ref -> target_surface -> required`                                                                         |

---

# Regras por Bloco da Matriz

## 1. Bloco “Identidade do Módulo”

Transforma em:

* `module_identity`
* parte de `capabilities`
* parte de `forbidden_inference_global`

| Bloco da Matriz        | Bloco do IR                    | Regra                                                 |
| ---------------------- | ------------------------------ | ----------------------------------------------------- |
| Bloco 1 — Identidade   | `module_identity`              | Consolidar missão, backbone, benchmark, phase scope   |
| decisões de identidade | `capabilities[]`               | Só quando descrevem capacidade do módulo              |
| “what it is not”       | `forbidden_inference_global[]` | Converter cada anti-identidade em proibição explícita |

---

## 2. Bloco “Need → Objective”

Transforma em:

* `entities[]`
* `rules[]`
* `api_use_cases[]`
* `events[]`

| Origem                       | Destino                      | Regra                                          |
| ---------------------------- | ---------------------------- | ---------------------------------------------- |
| `need_detected`              | `entities[]`                 | Criar entidade formal                          |
| `session_objective`          | `entities[]`                 | Criar entidade formal                          |
| origem rastreável            | `rules[]`                    | Virar regra bloqueante com `formal_check_hint` |
| recommendation advisory only | `rules[]` + `integrations[]` | Boundary rule + integration policy             |
| need/objective events        | `events[]`                   | Normalizar nome textual em evento formal       |

---

## 3. Bloco “Prescription → Session”

Transforma em:

* `entities[]`
* `state_models[]`
* `api_use_cases[]`
* `rules[]`

| Origem                           | Destino                                        | Regra                                        |
| -------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| `training_session`               | `entities[]`                                   | Entidade formal com fields tipados           |
| `session_block`                  | `entities[]`                                   | Entidade formal                              |
| publicação exige conteúdo mínimo | `rules[]` + `state_models[].transition_guards` | Regra bloqueante + guard de publish          |
| status lifecycle fechado         | `state_models[]`                               | Converter texto em máquina de estados formal |
| criação/publicação de sessão     | `api_use_cases[]`                              | Um use case por ação HTTP relevante          |

---

## 4. Bloco “Execution → Response”

Transforma em:

* `entities[]`
* `rules[]`
* `api_use_cases[]`
* `events[]`

| Origem                                   | Destino                                        | Regra                                         |
| ---------------------------------------- | ---------------------------------------------- | --------------------------------------------- |
| `execution_record`                       | `entities[]`                                   | Entidade formal                               |
| `session_adjustment`                     | `entities[]`                                   | Entidade formal                               |
| planned vs actual                        | `rules[]`                                      | Regra de imutabilidade e separação            |
| execução exige contexto                  | `rules[]`                                      | Constraint formal                             |
| completar sessão exige evidência         | `rules[]` + `state_models[].transition_guards` | Guard de transição `IN_PROGRESS -> COMPLETED` |
| `execution_recorded`, `session_adjusted` | `events[]`                                     | Eventos formais                               |

---

## 5. Bloco “Review → Adjustment”

Transforma em:

* `entities[]`
* `rules[]`
* `state_models[]`
* `api_use_cases[]`

| Origem                                 | Destino                | Regra                                      |
| -------------------------------------- | ---------------------- | ------------------------------------------ |
| `feedback_thread`                      | `entities[]`           | Entidade formal com lifecycle próprio      |
| feedback contextual                    | `rules[]`              | Constraint de âncora obrigatória           |
| conversa gera consequência operacional | `rules[]`              | Rule para fechamento de thread             |
| review exige evidência                 | `rules[]`              | Rule bloqueante ou warning conforme matriz |
| completed immutable                    | `rules[]` + `errors[]` | Regra + erro formal                        |

---

## 6. Bloco “Boundaries”

Transforma em:

* `integrations[]`
* `rules[]`
* `permissions[]`
* `forbidden_inference_global[]`

| Origem                                | Destino                          | Regra                              |
| ------------------------------------- | -------------------------------- | ---------------------------------- |
| consome medical, não soberaniza       | `integrations[]`                 | Integração com ownership explícito |
| analytics recomenda, treinador decide | `integrations[]` + `rules[]`     | Boundary + rule                    |
| notifications via intents             | `integrations[]` + `events[]`    | Integration + event                |
| audit transversal                     | `integrations[]` + `events[]`    | Integration + event                |
| identity_access governa permissões    | `permissions` + `integrations[]` | Policy root fora de Training       |

---

## 7. Bloco “Governança”

Transforma em:

* `rules[]`
* `permissions[]`
* `ui_flows[]`
* `open_decisions[]`

| Origem                                        | Destino                     | Regra                      |
| --------------------------------------------- | --------------------------- | -------------------------- |
| atleta inelegível bloqueia prescrição         | `rules[]` + `permissions[]` | Rule + override policy     |
| derived signals não substituem raw facts      | `rules[]`                   | Regra de integridade       |
| atenção do treinador é finita                 | `rules[]` + `ui_flows[]`    | Rule + UI relevance        |
| fricção adaptativa                            | `ui_flows[]` + `rules[]`    | Flow + guard               |
| raciocínio técnico sobrevive à troca de staff | `rules[]` + `entities[]`    | Rule + continuity entities |

---

# Transformação de Campos da Matriz para Blocos do IR

## A. `decision_id`

| Matriz          | IR                                                                      | Observação                     |
| --------------- | ----------------------------------------------------------------------- | ------------------------------ |
| `TRAIN-DEC-001` | `surface_mapping[].decision_ref`                                        | obrigatório                    |
| `TRAIN-DEC-001` | `capabilities[].unique_governance_id` ou `rules[].unique_governance_id` | um dos dois, conforme natureza |

## B. `minimum_required_fields`

| Forma na Matriz | Forma no IR             |
| --------------- | ----------------------- |
| texto humano    | lista de fields tipados |

Exemplo:

Da matriz:

```text
training_session: session_objective_ids (min 1), intervention_cycle_ref
```

Para o IR:

```json
{
  "id": "training.training_session",
  "fields": [
    {
      "name": "sessionObjectiveIds",
      "semantic_type_ref": "training.session_objective.id_array",
      "required": true,
      "nullable": false,
      "min_items": 1
    },
    {
      "name": "interventionCycleRef",
      "semantic_type_ref": "training.intervention_cycle.id",
      "required": true,
      "nullable": false
    }
  ]
}
```

## C. `state_impact`

| Forma na Matriz     | Forma no IR             |
| ------------------- | ----------------------- |
| `DRAFT → PUBLISHED` | `allowed_transitions[]` |

## D. `events_emitted`

| Forma na Matriz              | Forma no IR                         |
| ---------------------------- | ----------------------------------- |
| `training_session_published` | evento formal com trigger e payload |

## E. `invariants`

| Forma na Matriz | Forma no IR             |
| --------------- | ----------------------- |
| `INV-TRAIN-005` | `rules[]` ou `rule_ref` |

## F. `materializes_in`

| Forma na Matriz                 | Forma no IR                               |
| ------------------------------- | ----------------------------------------- |
| `DOMAIN_RULES, OpenAPI, Schema` | múltiplas entradas em `surface_mapping[]` |

---

# Regras de Transformação Obrigatórias

| Regra                                                                            | O que significa                                                    |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 1 decisão não pode sumir                                                         | todo `TRAIN-DEC-*` deve aparecer no IR ou em relatório de descarte |
| 1 campo não pode permanecer em prosa se afetar contrato                          | virar field tipado                                                 |
| 1 transição não pode permanecer em texto                                         | virar `state_models[]`                                             |
| 1 evento não pode permanecer só no nome                                          | virar objeto formal                                                |
| 1 invariant não pode ficar só referenciada                                       | precisa existir em `rules[]` ou registry                           |
| 1 `materializes_in` não pode ficar genérico                                      | precisa virar `surface_mapping[]` com path                         |
| 1 boundary não pode ficar só descritivo                                          | precisa virar `integrations[]` ou `forbidden_inference_global[]`   |
| 1 warning não bloqueante pode ir para `open_decisions[]` se ainda não compilável | evita materialização indevida                                      |

---

# Tabela de Saída Esperada por Classe

| Classe na Matriz       | Sai no IR como                                                  |
| ---------------------- | --------------------------------------------------------------- |
| decisão de identidade  | `module_identity`, `capabilities`, `forbidden_inference_global` |
| decisão operacional    | `capabilities`, `entities`, `api_use_cases`                     |
| decisão de lifecycle   | `state_models`, `rules`                                         |
| decisão de boundary    | `integrations`, `rules`, `permissions`                          |
| decisão de integridade | `rules`, `errors`                                               |
| decisão de auditoria   | `rules`, `events`                                               |
| decisão de UI/uso      | `ui_flows`, `surface_mapping`                                   |

---

# Critério de transformação concluída

A transformação da Matriz para o IR só está concluída quando:

* todo `TRAIN-DEC-*` estiver mapeado;
* todo `INV-*` usado estiver formalizado;
* todo campo crítico estiver tipado;
* toda relação tiver ownership e delete policy;
* toda transição estiver formalizada;
* todo evento estiver tipado;
* todo `materializes_in` virar `surface_mapping`;
* não restar ambiguidade que force o agente a escolher.

---

# Regra final

A matriz responde:
**“o que foi decidido?”**

O IR responde:
**“como essas decisões podem ser compiladas sem interpretação criativa?”**

