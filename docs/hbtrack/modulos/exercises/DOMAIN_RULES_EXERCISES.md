---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/exercises/DOMAIN_RULES_EXERCISES.md
# SOURCE: .contract_driven/templates/modulos/DOMAIN_RULES_{{MODULE_NAME_UPPER}}.md
module: "exercises"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/exercises.yaml"
schemas_ref: "../../../../contracts/schemas/exercises/"
type: "domain-rules"
updated: "2026-03-16"
---

# DOMAIN_RULES_EXERCISES.md

## Objetivo
Registrar as regras de negócio do módulo `exercises`.

## Fonte do domínio
- `SYSTEM_SCOPE.md`
- `HANDBALL_RULES_DOMAIN.md` (quando aplicável)
- OpenAPI e schemas do módulo (`contracts/openapi/paths/exercises.yaml`, `contracts/openapi/components/schemas/exercises/`)
- Decisões arquiteturais: TRAIN-DEC-047, TRAIN-DEC-048 (`docs/hbtrack/decisoes/ARCH_DECISIONS_TRAINING.md`)
- `docs/hbtrack/modulos/exercises/graph/entities.yaml`
- `docs/hbtrack/modulos/exercises/graph/errors.yaml`
- `docs/hbtrack/modulos/exercises/graph/endpoints.yaml`

## Regras de negócio

| ID | Regra | Entidades afetadas | Fonte | Observações |
|---|---|---|---|---|
| DR-EXB-001 | Exercício é imutável por versão. Editar = criar nova `exercise_version`. `current_version_id` avança. | `Exercise`, `ExerciseVersion` | TRAIN-DEC-048 | Versões antigas permanecem acessíveis |
| DR-EXB-002 | `training` DEVE referenciar `exercise_id + exercise_version_id`. Referência apenas com `exercise_id` → 422. | `SessionExercise` | TRAIN-DEC-047 | Contexto fixado ou executado |
| DR-EXB-003 | Exercícios `scope = SYSTEM` e `editorial_status = ACTIVE` são visíveis para todos os usuários autenticados. | `Exercise` | Regra de produto | Sem filtro de organização |
| DR-EXB-004 | `scope = ORG`: `RESTRICTED` (default) = criador + ACL; `ORG_WIDE` = qualquer membro da organização. | `Exercise`, `ExerciseACL` | Regra de produto | Mudança para ORG_WIDE é ação explícita do criador |
| DR-EXB-005 | Relações semânticas são direcionais e tipadas: PROGRESSION, REGRESSION, VARIATION, CONTRAINDICATION. Relação reflexiva → inválida. Tupla duplicada → 422. | `ExerciseRelation` | Regra de produto | Ver detalhe abaixo |
| DR-EXB-006 | `maxAthletes >= minAthletes`. `minAthletes >= 1`. `maxAthletes <= 50`. Violação → 422. | `Exercise`, `ExerciseVersion` | Regra de produto | CHECK constraint |
| DR-EXB-007 | `complexity` (1..5) é avaliação editorial do criador. O sistema não calcula complexidade automaticamente. | `Exercise`, `ExerciseVersion` | Regra editorial | Dimensão pedagógica subjetiva |
| DR-EXB-008 | `GET /exercises` retorna apenas Preview DTO. Atributos ricos disponíveis somente em `GET /exercises/{id}`. | `Exercise` | Decisão 14 — coach-grade UX | Scan em ~15 segundos |
| DR-EXB-009 | Usuário ORG não pode editar exercício SYSTEM → 403. Usa `POST /exercises/{id}/copy` para criar cópia ORG editável. | `Exercise` | Regra de produto | Original SYSTEM permanece inalterado |
| DR-EXB-010 | Criador (`created_by_user_id`) de exercício ORG mantém acesso independentemente da ACL configurada. | `ExerciseACL` | Regra de produto | Nenhuma ACL pode remover acesso do criador |

## Regras derivadas da modalidade

| ID | Regra derivada do handebol | Regra de produto | Referência em HANDBALL_RULES_DOMAIN.md |
|---|---|---|---|
| DR-EXB-H01 | Fases de jogo (positional attack, transition, set piece, etc.) são categorias canônicas do handebol | `game_phase` ∈ DOMAIN_AXIOMS `exercise_game_phase` | HBR-014 (Treino Orientado à Modalidade) |
| DR-EXB-H02 | Categorias etárias (Sub-12 a Adulto) seguem estrutura federativa | `age_category` ∈ DOMAIN_AXIOMS `exercise_age_category` | Regulamento de competições de handebol |
| DR-EXB-H03 | Fases de sessão (WARMUP → COOLDOWN) refletem estrutura pedagógica canônica do treino de handebol | `session_phase` ∈ DOMAIN_AXIOMS `session_block_phase` | HBR-014 |

## Prioridade de verdade
1. Regra oficial do esporte, quando aplicável
2. Regra global do sistema
3. Regra do módulo
4. Comportamento da implementação

## Regras proibidas
- Não inferir regra de negócio a partir de UI isolada
- Não inferir regra de negócio a partir de dado histórico sem contrato
- Não inferir comportamento público sem respaldo em documentação do módulo

---

## Detalhe das regras

### DR-EXB-001 — Exercício é imutável por versão (TRAIN-DEC-048)

Uma vez criada, uma `exercise_version` tem seus campos congelados. Nenhum campo de uma versão existente pode ser alterado.

Editar um exercício = criar nova versão com `version_number = MAX(version_number) + 1`.

Consequência: o exercício em si (`exercise`) tem um ponteiro `current_version_id` que avança com cada edição. Versões antigas permanecem acessíveis via `GET /exercises/{id}/versions/{versionId}`.

---

### DR-EXB-002 — `training` referencia exercise_version_id (TRAIN-DEC-047)

Qualquer entidade de `training` que usa um exercício em contexto de execução ou planejamento fixo (ex.: `session_exercise`, futuramente `session_block`) DEVE referenciar `exercise_id + exercise_version_id`.

Referência com apenas `exercise_id` é inválida em contexto de sessão fixada ou executada. Inválido → 422.

---

### DR-EXB-003 — Exercícios SYSTEM são visíveis para todos os usuários autenticados

`scope = SYSTEM` e `editorial_status = ACTIVE` → qualquer usuário autenticado pode ler. Sem filtro de organização.

---

### DR-EXB-004 — Visibilidade de exercícios ORG

`scope = ORG`:
- `visibility_mode = RESTRICTED` (default): apenas criador e usuários na ACL podem ler.
- `visibility_mode = ORG_WIDE`: qualquer usuário da organização pode ler.

Mudança de `RESTRICTED` para `ORG_WIDE` é ação explícita do criador (não automática).

---

### DR-EXB-005 — Relações semânticas são direcionais e tipadas

`exercise_relation(from_exercise_id, to_exercise_id, relation_type)`:
- `PROGRESSION`: `from` é mais simples; `to` é mais complexo. Indica caminho de evolução.
- `REGRESSION`: inverso de PROGRESSION — `to` é mais simples; útil para retorno-ao-jogo.
- `VARIATION`: mesma família pedagógica, variação de regras/espaço/carga. Pedagogicamente bidirecional, armazenado como unidirecional.
- `CONTRAINDICATION`: `from` não deve ser usado junto ou sequenciado com `to` (ex.: carga conflitante, contraindicação médica de contexto).

Relação reflexiva (`from_id = to_id`) é inválida. A mesma tupla `(from, to, type)` não pode ser duplicada.

---

### DR-EXB-006 — `maxAthletes >= minAthletes`

Violação é inválida (422). `minAthletes >= 1`. `maxAthletes <= 50`.

---

### DR-EXB-007 — Complexidade é avaliação editorial, não calculada

`complexity` (1..5) é atribuído pelo criador do exercício. O sistema não calcula complexidade automaticamente. É uma dimensão editorial baseada no conhecimento do treinador/curador.

---

### DR-EXB-008 — Preview DTO para listagem (Decisão 14 — coach-grade UX)

O endpoint de listagem `GET /exercises` retorna apenas o Preview DTO — subconjunto mínimo de campos necessários para decisão rápida de seleção (scan em ~15 segundos):

`id, name, sessionPhase, primaryObjective, physicalLoad, estimatedDurationMinutes, spaceRequired, ageCategories, skillLevel, scope, thumbnailUrl, currentVersionId, currentVersionNumber`

Atributos ricos (`instructions`, `coachingCues`, `safetyNotes`, `relations`, `fullMedia`, `materials`) estão disponíveis apenas em `GET /exercises/{id}`.

---

### DR-EXB-009 — Exercício SYSTEM não pode ser editado por usuário ORG

Tentativa de PATCH/DELETE por usuário não-curador → 403. Para adaptar um exercício SYSTEM, o treinador usa `POST /exercises/{id}/copy` que cria uma cópia ORG editável. O exercício SYSTEM original permanece inalterado.

---

### DR-EXB-010 — Criador de exercício ORG mantém acesso independentemente da ACL

O criador (`created_by_user_id`) não precisa estar na ACL. Tem acesso garantido. Nenhuma configuração de ACL pode remover o acesso do próprio criador.

## Âncoras estruturadas
- As entidades soberanas e seus campos mapeados para runtime estão em `docs/hbtrack/modulos/exercises/graph/entities.yaml`.
- O mapa mínimo de operações e permissões publicadas está em `docs/hbtrack/modulos/exercises/graph/endpoints.yaml`.
- O mapa mínimo de erros transport/domain do módulo está em `docs/hbtrack/modulos/exercises/graph/errors.yaml`.
