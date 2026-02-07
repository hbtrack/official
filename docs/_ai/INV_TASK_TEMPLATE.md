# INV TASK TEMPLATE (CANONICAL)

Objetivo: instalar 1 nova invariante de `TRAINING` com zero alucinação, usando SSOT + Gate.

## Fontes (SSOT) — Obrigatório

1. `Hb Track - Backend/docs/_generated/openapi.json`
2. `Hb Track - Backend/docs/_generated/schema.sql`
3. `Hb Track - Backend/docs/_generated/alembic_state.txt`
4. `docs/_ai/INVARIANTS_AGENT_GUARDRAILS.md`
5. `docs/_ai/INVARIANTS_AGENT_PROTOCOL.md`

Candidates (opcional): `docs/_generated/training_invariants_candidates.md`

---

## Prompt Contract (Short Prompt → Execução Confiável)

Um “prompt curto” SÓ é válido se contiver, explicitamente, os campos abaixo. Se faltar qualquer item, o agent deve responder `NEEDS_EVIDENCE` e pedir o mínimo faltante.

### Campos obrigatórios (mínimo)

1) Template

- `Use docs/_ai/INV_TASK_TEMPLATE.md.`

2) Ação (uma)

- `INSTALL` (padrão deste template; instalar 1 nova INV)
- `UPDATE` (ajuste em INV existente; se aplicável)

> Nota: este template é focado em `INSTALL` de 1 INV. Outras ações devem ter template próprio.

3) `INV_ID`

- Formato: `INV-TRAIN-###` (ex.: `INV-TRAIN-045`).

4) Evidência SSOT (DB / API)

- Para DB (mais comum neste template):
  - `anchor=schema.sql:<linha>` (ex.: `schema.sql:3917`)
  - `token=` onde `token` é um identificador real e explícito: `ck_* | uq_* | fk_* | tr_* | fn_* | idx_*`
  - Se `idx_*` for UNIQUE INDEX parcial: incluir também `where="<cláusula>"` (ex.: `where="deleted_at IS NULL"`).

5) Regra de término (obrigatória)

- "Finish only with full GATE VERDICT."
- "If EXIT=3 and VERIFY_EXIT=0 and PYTEST_EXIT=0: drift → promote → all until EXIT_ALL=0."

---

### Prompt Contract — Modo AUTO (a partir de candidates)

Aceita prompt curto que NÃO traz `INV_ID`/`anchor`/`token`, desde que:

- Fonte: `training_invariants_candidates.md`.
- Filtro: Ação Sugerida = `promover`.
- Seleção determinística: primeiro item elegível no arquivo.
- O agent DEVE extrair `anchor`+`token` do candidato (SSOT). Se não houver `anchor`+`token` explícitos, pular para o próximo elegível.
- `INV_ID`: se o candidato não trouxer, usar `max(INV-TRAIN-### em INVARIANTS_TRAINING.md) + 1`.
- Finalização: obrigatória via gate; se `EXIT=3` com `VERIFY=0` e `PYTEST=0` → `drift→promote→all` até `EXIT_ALL=0`.

### Micro-regra: `idx_*` parcial exige `where=`

Se `token` começar com `idx_` e o `anchor` em `schema.sql` indicar que o índice é parcial (há `WHERE (...)` na definição), então o prompt DEVE incluir `where="..."` exatamente com a cláusula do índice.

Exemplos:

- Válido: `token=idx_session_exercises_session_order_unique anchor=schema.sql:3917 where="deleted_at IS NULL"`.
- Inválido: `token=idx_session_exercises_session_order_unique anchor=schema.sql:3917` (faltou `where`).

---

### Exemplos de prompts curtos válidos

- INSTALL (UNIQUE INDEX parcial):

  `Use docs/_ai/INV_TASK_TEMPLATE.md. INSTALL INV-TRAIN-045 token=idx_session_exercises_session_order_unique anchor=schema.sql:3917 where="deleted_at IS NULL". Finish only with full GATE VERDICT; if EXIT=3 then drift→promote→all until EXIT_ALL=0.`

- UPDATE (ex.: corrigir anchors/DoD da INV):

  `Use docs/_ai/INV_TASK_TEMPLATE.md. UPDATE INV-TRAIN-045 anchor=schema.sql:3917 token=idx_session_exercises_session_order_unique. Finish only with full GATE VERDICT; if EXIT=3 then drift→promote→all until EXIT_ALL=0.`

### Anti-patterns (prompt inválido)

- Falta `INV_ID`, ou falta `anchor`, ou falta `token`.
- Prompt pede “finalizar” sem exigir `GATE VERDICT` / `EXIT_ALL=0` quando aplicável.

---

## Procedimento (Obrigatório)

0) Refresh SSOT

- Executar: `.\scripts\inv.ps1 refresh`.
- Se `EXIT != 0`: parar e resolver o erro.

1) Confirmar o candidato

- Ler `docs/_generated/training_invariants_candidates.md`.
- Extrair: tabela, constraint/index/trigger/regra, tabela/colunas, tipo e `anchor (schema.sql:linha)`.

2) Criar SPEC + teste

- Criar SPEC YAML completo no padrão do repositório (campos: `id`, `status`, `test_required`, `units`, `anchors`, `tests`).
- Criar teste runtime (DB ou service) conforme o tipo.
- Para DB constraints (IntegrityError), usar helper canônico:

  `from tests._helpers.pg_error import assert_pg_constraint_violation`

### Obrigação B (Constraints DB)

- `constraint_name` deve ser um token explícito no docstring/SPEC: `ck_/uq_/fk_/tr_/fn_/idx_*`.
- Se for UNIQUE INDEX (partial), incluir a cláusula `WHERE` na âncora (ex.: `idx_teams_deleted WHERE deleted_at IS NULL`).
- Para CHECK constraints: citar `ck_*` no docstring + `SQLSTATE 23514`.
- Para UNIQUE constraints/indexes: citar `uq_*` ou `idx_*` no docstring + `SQLSTATE 23505`.

### Classe B — Modos aceitos (B1 / B2)

- **B1 (Column Doc, legado)**
  - Anchors: `db.table + db.column + db.comment`.
  - Valida existência de `COMMENT ON COLUMN` no `schema.sql`.
  - Usar quando a evidência é documentação de coluna.

- **B2 (Enforcement, preferido)**
  - Anchors: `db.table + db.trigger + db.function`.
  - Valida no `schema.sql`:
    1. Existe `CREATE TRIGGER`.
    2. Trigger é `ON public.` (table = onde o trigger dispara, não onde faz efeito).
    3. Trigger `EXECUTE FUNCTION public.`.
    4. Existe `CREATE FUNCTION`.
  - Usar quando há trigger/function real no schema.

### Regras anti-alucinação para Classe B

- Se usar `db.column` → `COMMENT ON COLUMN` é obrigatório no schema.
- Se usar `db.trigger` / `db.function` → binding no `schema.sql` é obrigatório.
- Proibido declarar `db.trigger` ou `db.function` que não existem no schema (o verifier barra).
- `db.table` em B2 deve ser a tabela onde o trigger está anexado (`ON`), não a tabela afetada.

3) Rodar gate individual

- Executar: `.\scripts\inv.ps1 gate <INV-ID>`.
- Capturar e colar o `GATE VERDICT` completo.

4) Regras de decisão por EXIT

- `EXIT=0`: pronto — finalizar.
- `EXIT=1`: corrigir (verifier/pytest) e re-rodar gate.
- `EXIT=3`: `DRIFT` / `OUTDATED` / `MISSING` → NÃO finalizar.
  - Se `VERIFY_EXIT=0` e `PYTEST_EXIT=0`: promover via bulk: `.\scripts\inv.ps1 promote` e depois `.\scripts\inv.ps1 all`.
  - Só finalizar quando `EXIT_ALL=0`.

5) Regras de Execução (Edge Cases)

- ORM ausente: se faltar suporte no ORM, usar SQL Core / raw SQL (não bloquear por falta de model).
- Shell Aborta: se comandos shell falharem repetidamente, pedir intervenção humana e parar.
- Infra Patch: se precisar alterar infra / scripts de gate, PARE e peça aprovação explícita (não fazer "refactor oportunista").

---

## Deliverables (Obrigatórios no retorno do agent)

A) SPEC YAML completo (trecho final).

B) Path do teste + nome da classe.

C) Output completo do `GATE VERDICT`.

D) Se houve promoção: output do `promote` + output do `all` (ou `Gate All Summary` final).

---

## Proibições

- Proibido responder "DONE" sem anexar (C) `GATE VERDICT` completo e, quando aplicável, (D) output do `promote` + output do `all`.
- Proibido promover com `VERIFY_EXIT != 0` ou `PYTEST_EXIT != 0`.
- Proibido pular `refresh` quando houver mudança estrutural / canônica.

