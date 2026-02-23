# HB Track — CONTRACT (SSOT)

meta:
  document: HB_TRACK_CONTRACT
  version: "0.1"
  status: SSOT
  ssot_scope: canon_docs
  path: docs/_canon/contratos/Kanban Hb Track.md
  last_updated: 2026-02-20
  registries:
    global_index: docs/_INDEX.yaml
    project_profile: docs/_canon/HB_TRACK_PROFILE.yaml
    gates_registry: docs/_canon/_agent/GATES_REGISTRY.yaml
    failure_to_gates: docs/_canon/_agent/FAILURE_TO_GATES.yaml
    correction_allowlist: docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml
    runtime_index: docs/product/runtime/_INDEX.yaml
    ops_registry: scripts_roadmap.yaml
  canonical_exit_codes_source: docs/_canon/_agent/GATES_REGISTRY.yaml:meta.canonical_exit_codes

1. Objetivo

Este contrato define o modo determinístico de desenvolvimento do HB Track com IA, impondo:
(a) escopo de escrita, (b) gates mínimos, (c) evidência reexecutável, (d) rollback determinístico, (e) aceite binário.

2. Papéis

2.1 HUMAN_OWNER MUST:
- Aceitar/rejeitar Evidence Pack no estágio AUDIT.
- Encerrar o card com decisão binária: PASS (DONE) ou FAIL (volta para READY/BACKLOG).

2.2 ARCHITECT_AGENT MUST:
- Produzir card READY executável (Definition of Ready completo).
- Selecionar gates exclusivamente via registries canônicos.
- Bloquear o card se algum gate requerido estiver MISSING.

2.3 EXECUTOR_AGENT MUST:
- Executar estritamente dentro do WRITE_SCOPE.
- Rodar os comandos dos gates declarados no card.
- Produzir Evidence Pack reexecutável e íntegro em `_reports/audit/<RUN_ID>/`.

3. Fonte Única de Gates e Códigos Canônicos

3.1 Gates MUST ser referenciados por ID e MUST existir em:
- `docs/_canon/_agent/GATES_REGISTRY.yaml`

3.2 Exit codes MUST seguir `meta.canonical_exit_codes` do registry:
- 0 = PASS
- 2 = FAIL_ACTIONABLE
- 3 = ERROR_INFRA
- 4 = BLOCKED_INPUT

3.3 Regra de bloqueio determinístico:
- Se qualquer gate requerido tiver `lifecycle: MISSING`, o card MUST ser classificado como BLOCKED e MUST NOT avançar para EXECUTING.

4. Definition of Ready (DoR) — obrigatório

Um card só entra em READY se contiver TODOS os campos abaixo. Ausência => MUST permanecer em BACKLOG/BLOCKED.

4.1 Identidade
- CARD_ID
- CAPABILITY (deve existir no SPEC)
- FAILURE_TYPE (deve existir em FAILURE_TO_GATES)

4.2 SSOT e Escopo
- SSOT_REFERENCES (paths)
- WRITE_SCOPE (paths)
- FORBIDDEN (paths)
- ALLOWLIST_MATCH (quando aplicável: compatível com CORRECTION_WRITE_ALLOWLIST)

4.3 Gates e Comandos
- GATES_REQUIRED (IDs; MUST existir no GATES_REGISTRY)
- GATES_MINIMUM (baseline do repo; ver Seção 5)
- COMMANDS (texto exato OU referência ao registry aprovado no PROFILE / scripts_roadmap)

4.4 Evidência e Rollback
- EVIDENCE_EXPECTED (por gate)
- ROLLBACK_PLAN (preferência: git revert do commit do card; se houver estado, declarar como desfazer)

4.5 AC Binário
- ACCEPTANCE_CRITERIA (PASS/FAIL)

5. Baseline Gates (mínimos do processo)

Para qualquer card que produza Evidence Pack, o baseline MUST incluir:
- AUDIT_PACK_INTEGRITY (IMPLEMENTED)

Para cards que alterem docs canônicos/processo (CONTRACT/SPEC/Kanban/_INDEX), o baseline MUST incluir:
- DOCS_CANON_CHECK (IMPLEMENTED)
- DOCS_INDEX_CHECK (MISSING hoje → portanto BLOCKED até implementar)

Nota: cards podem ter baseline adicional conforme escopo:
- POLICY_FILES_CONSISTENCY (somente se tocar scripts/_policy)

6. Evidence Pack (obrigatório)

Evidence Pack MUST estar em `_reports/audit/<RUN_ID>/` e MUST ser validado por:
- gate: AUDIT_PACK_INTEGRITY

Evidence Pack MUST conter:
- CARD_ID + CAPABILITY + FAILURE_TYPE
- Lista de comandos executados (texto exato) e seus exit codes
- Stdout/stderr (ou logs referenciados)
- Diff summary (arquivos alterados/criados/removidos)
- Commit hash (ou snapshot aceito)

7. Definition of Done (DoD)

Um card só é DONE quando:
- Todos os gates do card estão PASS
- Evidence Pack íntegro (AUDIT_PACK_INTEGRITY PASS)
- HUMAN_OWNER aceita em AUDIT
- Rollback está definido (e validado quando aplicável)

8. Change Control

Mudanças neste CONTRACT:
- MUST ser feitas por card CAPABILITY=OPS_GOV
- MUST atualizar meta.version
- MUST produzir Evidence Pack