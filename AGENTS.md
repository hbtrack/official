# HB Track — Instruções Globais para Agentes (VS Code Copilot)

Fonte de verdade (SSOT) é o repositório — nunca “memória do chat”.

Referências canônicas globais:
- `docs/_canon/contratos/Dev Flow.md`
- `docs/_canon/contratos/Arquiteto Contract.md`
- `docs/_canon/contratos/Executor Contract.md`
- `docs/_canon/contratos/Testador Contract.md`
- `docs/invariantes/INVARIANTS_OPERACIONAIS_HBTRACK.md`
- Instruções repo-wide do Copilot: `.github/copilot-instructions.md`

Regras duras (anti-alucinação):
- Não expandir escopo: seguir o papel do agente (Arquiteto/Executor/Testador) e o `write_scope` da AR quando aplicável.
- Se faltar SSOT/arquivo/evidência: parar e reportar `BLOCKED_INPUT` (exit 4) com nota objetiva.
- Proibido criar scripts `.sh`/`.ps1` (infra/automação: somente Python `.py`).
- Proibidos comandos destrutivos: `git reset --hard`, `git checkout -- .`, `git clean -fd*`, `git restore` (qualquer forma).
- `✅ VERIFICADO` é exclusivo do humano via `hb seal`.

## Módulo TRAINING — cadeia canônica

Para qualquer tarefa no módulo TRAINING, ler e obedecer esta cadeia (ordem/autoridade):
1. `docs/hbtrack/modulos/treinos/_INDEX.md`
2. `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md`
3. `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`
4. `docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md`
5. `docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md`
6. `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`
7. `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md`
8. `docs/hbtrack/modulos/treinos/TRAINING_ROADMAP.md`

Regras:
- `TRAINING_BATCH_PLAN_v1.md` não é SSOT ativo.
- Baseline canônico do `CONTRACT_DIFF_GATE` (oasdiff): `contracts/openapi/baseline/openapi_baseline.json`.

