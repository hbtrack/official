---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
type: "domain-rules"
---

# DOMAIN_RULES_TRAINING.md

## Objetivo
Registrar as regras de negócio do módulo `training`.

## Fonte do domínio
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md` (HBR-014: Treino Orientado à Modalidade)
- OpenAPI e schemas do módulo
- Invariantes documentadas em `INVARIANTS_TRAINING.md`

## Regras de negócio
| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-TRAIN-001 | Sessões só podem ser criadas por treinadores ou coordenadores | `TrainingSession` | RBAC + SYSTEM_SCOPE.md | Atores: Treinador (nível 3), Coordenador (nível 2) |
| DR-TRAIN-002 | Soma dos percentuais de foco (7 campos `focus_*_pct`) deve ser ≤ 120 | `TrainingSession` | Regra de produto | Permite sessões híbridas sem ultrapassar limite de consistência |
| DR-TRAIN-003 | Valores individuais de foco, quando presentes, devem estar em [0..100] | `TrainingSession` | Regra de produto | Validação de range por campo |
| DR-TRAIN-004 | Wellness pré-treino só pode ser submetido até 2h antes de `session_at` | `WellnessPre` | Regra de produto | Garante coleta "pré" com antecedência suficiente |
| DR-TRAIN-005 | Wellness pós-treino só pode ser editado até 24h após criação | `WellnessPost` | Regra de produto | Permite correção breve mas impede edições tardias |
| DR-TRAIN-006 | Sessões com `session_at` > 60 dias no passado são somente leitura | `TrainingSession` | Regra de produto | Estabilidade histórica e integridade de analytics |
| DR-TRAIN-007 | Janela de edição de sessão depende de papel e estado (ver INV-TRAIN-004) | `TrainingSession` | Regra de produto + RBAC | Autor: até 10min antes; Superior: até 24h após |

## Regras derivadas da modalidade
| ID | Regra derivada do handebol | Regra de produto | Referência em HANDBALL_RULES_DOMAIN.md |
|---|---|---|---|
| DR-TRAIN-H01 | Treino de handebol organiza-se por posições específicas | Sistema deve suportar classificação de exercícios por posição-alvo (goleiro, pontas, armadores, pivô) | HBR-014 |
| DR-TRAIN-H02 | Treino de handebol organiza-se por fases do jogo | Sistema deve suportar classificação de exercícios por fase (ataque organizado, contra-ataque, defesa fechada, transição) | HBR-014 |
| DR-TRAIN-H03 | Categorias etárias determinam volume e intensidade | Sistema deve vincular sessões a categorias (mini-handebol, infantil, juvenil, júnior, adulto) | HBR-014 |
| DR-TRAIN-H04 | Periodização segue estrutura: temporada → bloco → semana → sessão | Sistema deve suportar 4 níveis de periodização (macrociclo, mesociclo, microciclo, sessão) | HBR-014 |

## Prioridade de verdade
1. Regra oficial do esporte quando aplicável (HBR-014)
2. Regra global do sistema (GLOBAL_INVARIANTS.md)
3. Regra do módulo (esta seção)
4. Comportamento da implementação

## Regras proibidas
- Não inferir regra de negócio a partir de UI isolada
- Não inferir regra de negócio a partir de dado histórico sem contrato
- Não inferir comportamento público sem respaldo em documentação do módulo
