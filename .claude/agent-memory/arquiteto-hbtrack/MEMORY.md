# HB Track Arquiteto — Memória Persistente

## Estado TRAINING (atualizado 2026-03-05 pos-Batch29)

- FASE_2: COMPLETO — AR-TRAIN-001..054 todos VERIFICADOS
- FASE_3: COMPLETO — AR-TRAIN-055..067 todos VERIFICADOS (Batches 26-29)
- BATCH 29: SEALED — AR-TRAIN-063..067 (AR_247..251) todos VERIFICADOS (2026-03-05)
- TEST_MATRIX_TRAINING.md: v3.7.0 (§9 Batch 29 + baseline RH-08 615p/0s/0xf/0f)
- Suite backend (baseline TRUTH pos-Batch29): 615p/0s/0xf/0f (NO_MOCKS_GLOBAL atingido)
- Ultimo batch selado: Batch 29 (AR_247..251 / AR-TRAIN-063..067)
- Proximo batch: NENHUM — modulo em estado DONE_TRAINING_ATINGIDO
- AR_BACKLOG versao atual: v3.3.0
- DONE_GATE_TRAINING.md: v1.7.0 (tabela Batch 29 adicionada; RH-01/03/05 atualizados)

## IDs TRAINING Module

- ARs backlog: AR-TRAIN-001..067 (todas VERIFICADO)
- ARs numericas: AR_247..251 (Batch 29 — selado)
- TEST_MATRIX versao atual: v3.7.0
- AR_BACKLOG versao atual: v3.3.0
- BatchPlan versao atual: v1.7.0
- DONE_GATE versao atual: v1.7.0

## Paths criticos

- Plan Batch 29: `docs/_canon/planos/ar_batch29_plano_final_truth_suite_063_067.json`
- openapi.json (local): `Hb Track - Backend/docs/ssot/openapi.json`
- training-phase3.ts: `Hb Track - Frontend/src/lib/api/training-phase3.ts`
- PLANO_FINAL.md: `docs/hbtrack/modulos/treinos/PLANO_FINAL.md`
- DONE_GATE_TRAINING.md: `docs/hbtrack/modulos/treinos/DONE_GATE_TRAINING.md` (v1.7.0)

## TRUTH SUITE pos-Batch29

Baseline pos-Batch29: 615p/0s/0xf/0f (NO_MOCKS_GLOBAL atingido — rg=0 matches em tests/training/).
- AR_248: fix exercise_acl_service._validate_same_org (user.organization_id -> ORM query via org_membership)
- AR_249: fix session_exercise_service guards (4 skips test_058/059 -> PASS)
- AR_250: 9 LEGACY_INVALID -> TRUTH (test_003/004/005/018/022/023/027/071/078)

## Padroes de PROOF no handoff (check_handoff_contract.py)

O check_handoff_contract.py extrai blocos por heading `## AR_NNN`. Cada bloco DEVE conter `PROOF:` no texto. Para ARs de governança usar `PROOF: N/A (governance)`. Sem isso = WARN.

## Lições aprendidas

- TRAINING_BATCH_PLAN_v1.md tem caracteres unicode que causam UnicodeError no shell Windows — usar `io.open(..., encoding='utf-8')` e substituição via Python.
- Edit tool falha silenciosamente com chars unicode em old_string. Usar Python script para edições.
- Kanban deve ser atualizado via script Python (temp/_append_kanban_batch*.py).
- `docs/ssot/openapi.json` (raiz) NAO e governed root — apenas `Hb Track - Backend/docs/ssot/openapi.json`.
- check_handoff_contract.py WARN suprimido com `PROOF: N/A (governance)` para ARs documentais.
- hb plan usa task.id como ID da AR criada — NAO usar 001..005 se ARs existentes ja usam esses numeros (E_AR_COLLISION). Usar o numero real da AR (ex: 247).
- evidence_file pattern exige exatamente 3 digitos: `AR_[0-9]{3}`.
- write_scope nao pode incluir `_reports/EXECUTOR.yaml` — esta fora de governed roots.
- gen_docs_ssot.py DEVE ser rodado antes de qualquer planejamento.
- hb plan --dry-run com ARs ja existentes: usar --skip-existing para evitar E_AR_COLLISION.
- plan JSON "version" deve ser exatamente "1.2.0" (schema_version fixo) — nao bumpar.

## REGRA GLOBAL Windows validation_command (REPLAN-5 fix definitivo, 2026-03-05)

SHELL REAL = cmd.exe — hb_cli.py usa subprocess.run(shell=True) que invoca cmd.exe /c, NAO PowerShell.

PROIBIDO em validation_command:
- grep, tail, head, sed, awk, find (Unix-only)
- `$env:VAR=valor` (PowerShell-only — exit=255 no cmd.exe)
- `;` como separador de comandos (PowerShell-only no contexto de cmd.exe)
- `set PYTHONUTF8=1 && python ...` (espaço trailing antes do && corrompe valor: "1 " e invalido — Fatal Python error)

PADRAO OBRIGATORIO para Unicode: `python -X utf8 script.py` (flag direta, sem variavel de ambiente, funciona em cmd.exe e PowerShell)

PADRAO OBRIGATORIO para separar comandos: `&&` (funciona em cmd.exe E PowerShell)

PADRAO OBRIGATORIO para filtrar output de pytest:
  `python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`

EXCECAO: `rg` (ripgrep) e cross-platform e pode ser usado sem adaptacao.

PROOF/TRACE devem estar na AR.md diretamente (nao apenas em ARQUITETO.yaml) — gate DOC/STITCH verifica a AR.md.

NOTA check_handoff_contract.py: heading `## REPLAN-X` NAO pode conter `AR_NNN` no proprio titulo (senao o script extrai esse bloco como o bloco da AR_NNN e o PROOF do bloco real nao e encontrado). Usar nomes neutros como `## REPLAN-5 — fix definitivo Unicode ...` sem mencionar AR_NNN no heading.
