# .github/agents/README.md
# HB Track — Agents (Enterprise) — Precedência SSOT vs DERIVED + Handoff

Status: ENTERPRISE  
Compatible: Protocol v1.2.0+  
Compatible: AR Contract Schema v1.2.0 (schema_version)

## 1) Objetivo

Este diretório define os agentes do fluxo determinístico do HB Track e a forma correta de “handoff” (passagem de estado) sem comunicação direta entre agentes.

## 2) Precedência: SSOT vs DERIVED (regra dura)

SSOT (fonte de verdade) define regras e intenções. DERIVED (derivado) é gerado/mecanizado e não pode ser editado manualmente.

SSOT (editável, governado):
- `docs/_canon/contratos/Dev Flow.md` (fluxo e regras)
- `docs/_canon/contratos/Arquiteto Contract.md`
- `docs/_canon/contratos/Executor Contract.md`
- `docs/_canon/contratos/Testador Contract.md`
- `docs/_canon/contratos/ar_contract.schema.json` (schema_version 1.2.0)
- `docs/_canon/specs/GATES_REGISTRY.yaml`
- `docs/_canon/specs/GOVERNED_ROOTS.yaml`
- `docs/hbtrack/Hb Track Kanban.md` (**SSOT de planejamento/priorização**)

DERIVED (auto-gerado, MUST NOT editar manualmente):
- `docs/hbtrack/_INDEX.md` (registry de máquina de estados; gerado por hb)
- ARs materializadas: `docs/hbtrack/ars/AR_<id>_*.md` (corpo imutável após ✅ VERIFICADO)
- Evidence canônico do Executor: `docs/hbtrack/evidence/AR_<id>/executor_main.log` (gerado por `hb report`)
- TESTADOR_REPORT: `_reports/testador/AR_<id>_<git7>/*` (gerado por `hb verify`)

Regra de conflito:
- Kanban NÃO libera commit.
- Autoridade de commit é exclusivamente: **AR + evidence canônico + TESTADOR_REPORT + `_INDEX.md` + selo humano `hb seal` (✅ VERIFICADO)**.

## 3) Fluxo enterprise (handoff oficial)

Arquiteto → Executor → Testador → Humano (selo final)

Automação de workflow:
- Watcher canônico: `scripts/run/hb_watch.py` monitora _INDEX.md e gera inbox files em `_reports/dispatch`:
  - executor.todo (trigger automático após AR materializada)
  - testador.todo (trigger automático após evidence canônico staged)
  - humano.todo (trigger manual após ✅ SUCESSO do Testador)

3.1 Arquiteto (Planner)
- Cria Plan JSON em `docs/_canon/planos/` e valida:
  - `python scripts/run/hb_cli.py plan <plan.json> --dry-run`
- O Arquiteto NÃO implementa código e NÃO roda report/verify/seal.
- Entrega ao Executor: `plan_json_path`, `mode`, `write_scope`, gates e avisos.

3.2 Materialização (hb plan)
- Humano (ou automação autorizada) executa:
  - `python scripts/run/hb_cli.py plan docs/_canon/planos/<nome>.json`
- Gera ARs em `docs/hbtrack/ars/` e atualiza `docs/hbtrack/_INDEX.md` (DERIVED).

3.3 Executor (Implementer)
- Lê a AR, preenche “Análise de Impacto”, implementa patch mínimo no WRITE_SCOPE.
- Executa evidence canônico:
  - `python scripts/run/hb_cli.py report <id> "<validation_command>"`
- Resultado obrigatório:
  - `docs/hbtrack/evidence/AR_<id>/executor_main.log` (staged)

3.4 Testador (Independent Verifier)
- Pré-condição: workspace limpo (hard fail se sujo).
- Re-executa independentemente:
  - `python scripts/run/hb_cli.py verify <id>`
- Gera:
  - `_reports/testador/AR_<id>_<git7>/*` (staged)
- Atualiza Status na AR somente para:
  - ✅ SUCESSO | 🔴 REJEITADO | ⏸️ BLOQUEADO_INFRA
- Testador NÃO escreve ✅ VERIFICADO.

3.5 Humano (manual step — último gate)
- Último gate é o selo humano:
  - `python scripts/run/hb_cli.py seal <id> "<reason opcional>"`
- `hb seal` promove o Status para ✅ VERIFICADO após checar:
  - evidence canônico staged
  - TESTADOR_REPORT staged
  - `_INDEX.md` staged
  - consistência do resultado do Testador

## 4) Regras práticas de handoff (sem “chat relay”)

- Agentes não se comunicam diretamente. A AR é a única voz.
- O “estado real” é mecanizado (DERIVED) e validado por `hb check`.
- Qualquer tentativa de “pular” verify/seal é bloqueada por `hb check`.

## 5) Checklist de commit (determinístico)

Antes do commit em governed roots:
- AR relevante staged
- `docs/hbtrack/_INDEX.md` staged
- `docs/hbtrack/evidence/AR_<id>/executor_main.log` staged
- `_reports/testador/AR_<id>_<git7>/result.json` staged (e demais arquivos do report)
- AR com ✅ VERIFICADO (humano via hb seal)

Se qualquer item faltar: `hb check --mode pre-commit` MUST FAIL.