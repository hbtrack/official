---
module: "training"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
module_scope_ref: "./MODULE_SCOPE_TRAINING.md"
domain_rules_ref: "./DOMAIN_RULES_TRAINING.md"
invariants_ref: "./INVARIANTS_TRAINING.md"
test_matrix_ref: "./TEST_MATRIX_TRAINING.md"
contract_path_ref: "../../../../contracts/openapi/paths/training.yaml"
schemas_ref: "../../../../contracts/schemas/training/"
---

# training

## Objetivo
O módulo `training` é responsável por planejamento, execução, registro e análise de sessões de treinamento de handebol.

## Responsabilidades
- Planejar sessões de treino com exercícios, carga, foco e periodização
- Registrar execução de treinos (horário, duração, presença)
- Coletar dados de wellness pré e pós-treino
- Vincular sessões a equipes, temporadas e categorias
- Fornecer dados de carga e volume para módulo `analytics`
- Suportar periodização (macrociclo, mesociclo, microciclo, sessão)

## Fora do escopo
- Registro de partidas (responsabilidade do módulo `matches`)
- Gestão de lesões e tratamentos médicos (responsabilidade do módulo `medical`)
- Scout de jogos (responsabilidade do módulo `scout`)
- Analytics e dashboards (responsabilidade do módulo `analytics`)

## Artefatos do módulo
- `MODULE_SCOPE_TRAINING.md`
- `DOMAIN_RULES_TRAINING.md`
- `INVARIANTS_TRAINING.md`
- `TEST_MATRIX_TRAINING.md`
- `contracts/openapi/paths/training.yaml`
- `contracts/schemas/training/*.schema.json`

## Dependências
- Sistema: `SYSTEM_SCOPE.md`
- Domínio esportivo: `HANDBALL_RULES_DOMAIN.md` (HBR-014: Treino Orientado à Modalidade)
- Contrato HTTP: `contracts/openapi/paths/training.yaml`
- Schemas: `contracts/schemas/training/`

## Regras
1. Nenhuma interface pública do módulo existe fora do contrato OpenAPI.
2. Nenhuma entidade pública estável do módulo existe fora de schema.
3. Toda regra derivada do handebol deve apontar para `HANDBALL_RULES_DOMAIN.md`.
4. Invariantes devem ser verificáveis por testes automatizados.

## Navegação rápida
1. Leia `MODULE_SCOPE_TRAINING.md`
2. Leia `DOMAIN_RULES_TRAINING.md`
3. Leia `INVARIANTS_TRAINING.md`
4. Leia `TEST_MATRIX_TRAINING.md`
5. Leia os contratos do módulo
