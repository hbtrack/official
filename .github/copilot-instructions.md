# HB Track — Copilot Instructions (Repo-wide)

NÃO use histórico do chat como fonte de verdade. Fonte de verdade = arquivos SSOT do repositório.

Regras gerais:
- Não expandir escopo. Siga o papel do agente selecionado (Arquiteto/Executor/Testador).
- Proibido criar scripts .sh/.ps1. Infra/automação: somente Python (.py).
- Proibidos comandos destrutivos: git reset --hard, git checkout -- ., git clean -fd*, git restore (qualquer forma).
- Kanban é SSOT de ordem/estado operacional, mas NÃO autoriza commit.
- ✅ VERIFICADO é exclusivo do humano via hb seal.

SSOT principais:
- docs/_canon/contratos/Dev Flow.md
- docs/_canon/contratos/ar_contract.schema.json
- docs/_canon/specs/GOVERNED_ROOTS.yaml
- docs/_canon/specs/GATES_REGISTRY.yaml
- docs/_canon/specs/Hb cli Spec.md
- docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md (normas operacionais — SSOT vence em conflito)

Invariantes operacionais (SSOT normativo global):
- Antes de qualquer ação, consultar docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md.
- Se houver conflito entre instruções e este SSOT, o SSOT vence.
- Nunca inventar regras não presentes no SSOT; se faltar, marcar como GAP.

## Módulo TRAINING — cadeia canônica

Para qualquer tarefa no módulo TRAINING, a cadeia canônica obrigatória é:

1. `docs/hbtrack/modulos/treinos/_INDEX.md`
2. `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
3. `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
4. `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
5. `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
6. `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
7. `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
8. `docs/hbtrack/modulos/treinos/TRAINING_ROADMAP.md`

Regra:
- `TRAINING_BATCH_PLAN_v1.md` não é SSOT ativo do módulo TRAINING.
- Em caso de conflito, prevalecem `_INDEX.md`, `INVARIANTS_TRAINING.md`, `TRAINING_FRONT_BACK_CONTRACT.md` e `TEST_MATRIX_TRAINING.md`.

## Pipeline spec-driven do TRAINING

Quando a tarefa tocar contrato FE↔BE, o agente deve seguir o pipeline abaixo:

1. `OPENAPI_SPEC_QUALITY`
2. `CONTRACT_DIFF_GATE`
3. `GENERATED_CLIENT_SYNC`
4. `RUNTIME CONTRACT VALIDATION`
5. `TRUTH_BE`

Ferramentas oficiais:
- Redocly CLI
- oasdiff
- OpenAPI Generator
- Schemathesis

Regras:
- `src/api/generated/*` é artefato derivado e não pode ser editado manualmente.
- `src/lib/api/*` é camada adapter/manual e não pode redefinir contrato já tipado no OpenAPI.
- Mudança contratual sem os gates acima é incompleta.
- Baseline canônico do `CONTRACT_DIFF_GATE`: `contracts/openapi/baseline/openapi_baseline.json` (não é SSOT; é baseline governado para oasdiff).

## TRUTH_FE (futuro)

Quando os testes de frontend do módulo TRAINING forem materializados, a ferramenta oficial prevista é:
- Playwright

Até lá:
- `TRUTH_BE` continua sendo a verdade operacional principal do módulo;
- mudanças de UI/UX devem respeitar `TRAINING_SCREENS_SPEC.md`, `TRAINING_USER_FLOWS.md` e o cliente FE gerado.

Comandos destrutivos proibidos (hard-fail):
- git restore (qualquer forma)
- git reset --hard
- git checkout -- .
- git clean -fd*

Política HB Track:
- Scripts de automação/infra: somente Python (.py). Sem .sh/.ps1.
- Kanban orienta ordem/estado operacional, NÃO autoriza commit.

Se houver divergência entre Roadmap / Backlog / Kanban:
- parar e reportar BLOCKED_INPUT (exit 4) com nota objetiva.

Regra (TRAINING):
- `TRAINING_BATCH_PLAN_v1.md` não é SSOT ativo. Se houver divergência de “batch”/ordem, use: Kanban + `AR_BACKLOG_TRAINING.md` + `TRAINING_ROADMAP.md` (ou bloqueie se o SSOT não definir).
