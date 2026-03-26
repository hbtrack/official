---
# TEMPLATE: module-doc-template
# DEST: docs/hbtrack/modulos/exercises/INVARIANTS_EXERCISES.md
# SOURCE: .contract_driven/templates/modulos/INVARIANTS_{{MODULE_NAME_UPPER}}.md
module: "exercises"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: true
contract_path_ref: "../../../../contracts/openapi/paths/exercises.yaml"
schemas_ref: "../../../../contracts/schemas/exercises/"
type: "invariants"
updated: "2026-03-16"
---

# INVARIANTS_EXERCISES.md

## Objetivo
Registrar invariantes do módulo `exercises`.

## Definição
Invariantes são condições que devem permanecer verdadeiras independentemente do fluxo, endpoint ou interface.

## Invariantes globais vinculantes
- `.contract_driven/DOMAIN_AXIOMS.json`
- `docs/_canon/GLOBAL_INVARIANTS.md`

## Tabela de invariantes

| ID | Invariante | Entidades | Fonte | Como verificar |
|---|---|---|---|---|
| INV-EXB-001 | `scope` ∈ {`SYSTEM`, `ORG`}. Exercício sem scope válido é rejeitado. | `Exercise` | DOMAIN_AXIOMS `exercise_scope` | Validação de enum no schema; CROSS_SPEC_ALIGNMENT_GATE |
| INV-EXB-002 | `scope = ORG` → `organization_id NOT NULL`; `scope = SYSTEM` → `organization_id IS NULL`. | `Exercise` | Regra de produto | CHECK constraint; teste de criação ORG sem org_id |
| INV-EXB-003 | `max_athletes >= min_athletes`. | `Exercise` | Regra de produto | CHECK constraint; teste de payload inválido (max < min) |
| INV-EXB-004 | `min_athletes >= 1` e `max_athletes <= 50`. | `Exercise` | Regra de produto | CHECK constraint |
| INV-EXB-005 | `version_number` é sequencial por exercício: nova versão = `MAX(version_number) + 1`. Unicidade de `(exercise_id, version_number)`. | `ExerciseVersion` | Regra de produto (TRAIN-DEC-048) | UNIQUE constraint; teste de edição simultânea |
| INV-EXB-006 | `ExerciseVersion` é append-only. Nenhum campo de versão existente pode ser alterado após criação. | `ExerciseVersion` | ADR-018 (HYBRID) | Proibição de PATCH em `/versions/{versionId}`; trigger BEFORE UPDATE → RAISE |
| INV-EXB-007 | `session_exercise` e qualquer entidade de `training` que referencia exercício em contexto fixo DEVE incluir `exercise_version_id` explícito. Referência sem versão → 422. | `SessionExercise` | TRAIN-DEC-047, TRAIN-DEC-048 | Validação de campo obrigatório; teste de criação sem version_id |
| INV-EXB-008 | Usuário `scope = ORG` não pode criar, editar nem excluir exercício `scope = SYSTEM` → 403. | `Exercise` | DR-EXB-009 | Teste de autorização; middleware RBAC |
| INV-EXB-009 | `created_by_user_id` mantém acesso ao exercício ORG independentemente da ACL configurada. | `ExerciseACL` | DR-EXB-010 | Teste de remoção do criador da ACL + acesso verificado |
| INV-EXB-010 | ACL só pode existir para exercício `scope = ORG` com `visibility_mode = RESTRICTED`. ACL em `ORG_WIDE` ou em `SYSTEM` → 422. | `ExerciseACL` | DR-EXB-004 | Validação no endpoint POST /exercises/{id}/acl |
| INV-EXB-011 | Usuário na ACL DEVE pertencer à mesma organização do exercício. Cross-org ACL → 422. | `ExerciseACL` | Isolamento multi-tenant | Validação de membership de organização no endpoint |
| INV-EXB-012 | Tupla `(exercise_id, user_id)` é única em `ExerciseACL`. Duplicata → 422. | `ExerciseACL` | Integridade | UNIQUE constraint |
| INV-EXB-013 | Relação semântica `(from_exercise_id, to_exercise_id, relation_type)` é única. Duplicata → 422. | `ExerciseRelation` | DR-EXB-005 | UNIQUE constraint |
| INV-EXB-014 | `from_exercise_id ≠ to_exercise_id`. Relação reflexiva → 422. | `ExerciseRelation` | DR-EXB-005 | CHECK constraint |
| INV-EXB-015 | `complexity` ∈ {1, 2, 3, 4, 5}. | `Exercise` / `ExerciseVersion` | DOMAIN_AXIOMS | CHECK constraint; validação de schema |
| INV-EXB-016 | `estimated_duration_minutes` ∈ [1, 180]. | `Exercise` / `ExerciseVersion` | Regra de produto | CHECK constraint |
| INV-EXB-017 | Exercício referenciado por `session_exercise` histórica NÃO PODE ser hard-deleted. Soft-delete (+ tombstone) preserva referência. | `Exercise` | TRAIN-DEC-047, ADR-018 | Trigger BEFORE DELETE; teste de tentativa de hard-delete com referências |
| INV-EXB-018 | `current_version_id` do exercício deve apontar para uma `exercise_version` existente e válida com `exercise_id` correspondente. | `Exercise` | Integridade referencial | FK constraint; teste de violação |

## Regras de uso
1. Nenhum endpoint pode violar invariantes.
2. Nenhuma automação assíncrona pode violar invariantes.
3. Nenhuma UI pode assumir transição que quebre invariantes.
4. Toda violação deve bloquear merge ou exigir exceção formal.

## Relação com outros documentos
- `DOMAIN_RULES_EXERCISES.md`
- `STATE_MODEL_EXERCISES.md`
- `TEST_MATRIX_EXERCISES.md`

## Nota sobre versionamento

`ExerciseVersion` segue o padrão HYBRID (ADR-018): é um fato append-only. O ponteiro `current_version_id` no `Exercise` é o único campo mutable do agregado principal — ele avança com cada nova versão criada.

Histórico completo de versões: `GET /exercises/{id}/versions`
Versão específica: `GET /exercises/{id}/versions/{versionId}`