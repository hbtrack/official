# HB Track — Kanban (Processo determinístico para IA)

meta:
  document: HB_TRACK_KANBAN
  version: "0.2"
  status: CANON_PROCESS
  path: docs/hbtrack/Hb Track Kanban.md
  last_updated: 2026-02-20
  ssot_governance:
    contract: docs/_canon/contratos/HB_TRACK_CONTRACT.md
    spec: docs/_canon/specs/HB_TRACK_SPEC.md
  registries:
    gates_registry: docs/_canon/_agent/GATES_REGISTRY.yaml
    failure_to_gates: docs/_canon/_agent/FAILURE_TO_GATES.yaml
    correction_allowlist: docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml
    project_profile: docs/_canon/HB_TRACK_PROFILE.yaml
  evidence_pack_root: "_reports/audit/<RUN_ID>/"

1. Colunas

Fluxo obrigatório:
- BACKLOG
- READY
- EXECUTING
- EVIDENCE_PACK
- AUDIT
- DONE

WIP:
- EXECUTING MUST ter WIP=1 (máximo 2 em exceção documentada no card).

2. Regras determinísticas (essência)

- Nenhum card entra em READY sem DoR completo.
- Nenhum card entra em DONE sem Evidence Pack íntegro.
- Gate lifecycle=MISSING => card MUST ser BLOCKED (exit code canônico 4 = BLOCKED_INPUT).

3. Baseline Gates (mínimos)

3.1 Evidence Pack (qualquer card que gere evidência)
- AUDIT_PACK_INTEGRITY (IMPLEMENTED)
  command: `python scripts/checks/check_audit_pack.py ${RUN_ID}`

3.2 Docs canônicos/processo (CONTRACT/SPEC/Kanban/docs/_INDEX.yaml)
- DOCS_CANON_CHECK (IMPLEMENTED)
  command: `python scripts/checks/check_docs_canon.py ${RUN_ID}`
- DOCS_INDEX_CHECK (MISSING)
  command atual no registry: `python scripts/audit/gate_stub_blocked.py DOCS_INDEX_CHECK`
  efeito: cards que exigem este gate ficam BLOCKED até implementar.

4. Definition of Ready (DoR) — checklist binário

CARD_ID:
TITLE:
CAPABILITY: (MUST existir no SPEC)
FAILURE_TYPE: (MUST existir no FAILURE_TO_GATES)

SSOT_REFERENCES:
- (paths)

WRITE_SCOPE:
- (paths)
FORBIDDEN:
- (paths)
ALLOWLIST_MATCH:
- (se aplicável, justificar compatibilidade com CORRECTION_WRITE_ALLOWLIST)

GATES_REQUIRED (IDs):
- (MUST existir no GATES_REGISTRY)
GATES_MINIMUM (baseline):
- (se Evidence Pack) AUDIT_PACK_INTEGRITY
- (se docs/processo) DOCS_CANON_CHECK + DOCS_INDEX_CHECK

EVIDENCE_EXPECTED:
- Para cada gate: exit_code esperado + marcador de stdout/stderr + artefato/arquivo (se houver)

ROLLBACK_PLAN:
- git revert <commit>
- validação de rollback (quais gates comprovam baseline)

ACCEPTANCE_CRITERIA:
- AC-001 (PASS/FAIL)
- AC-002 (PASS/FAIL)

Regra:
- Se qualquer campo acima estiver ausente => READY = FAIL (card permanece em BACKLOG/BLOCKED).

5. Execução (EXECUTING → EVIDENCE_PACK)

O Executor MUST:
- Aplicar mudanças somente no WRITE_SCOPE.
- Rodar todos os gates do card.
- Coletar evidências e estruturar o Evidence Pack em `_reports/audit/<RUN_ID>/`.

6. Evidence Pack (formato mínimo obrigatório)

Em `_reports/audit/<RUN_ID>/` MUST existir:
- card.yaml (CARD_ID, CAPABILITY, FAILURE_TYPE, SSOT_REFERENCES, WRITE_SCOPE)
- commands.log (comandos exatos + cwd + env pré-requisitos)
- exit_codes.json (map command -> exit code)
- stdout.log / stderr.log (ou por comando)
- diff_summary.txt (arquivos alterados)
- commit.txt (hash)

Gate obrigatório:
- AUDIT_PACK_INTEGRITY MUST PASS

7. AUDIT e DONE

AUDIT:
- Humano valida se evidência prova os ACs e se não houve “PASS por acidente”.

DONE:
- Só com PASS de todos os gates + Evidence Pack íntegro + aceite humano.

8. Template de Card (copiar/colar)

CARD_ID:
TITLE:
STATUS: BACKLOG | READY | EXECUTING | EVIDENCE_PACK | AUDIT | DONE | BLOCKED

CAPABILITY:
FAILURE_TYPE:
SCOPE_NOTE:

SSOT_REFERENCES:
- ...

WRITE_SCOPE:
- ...
FORBIDDEN:
- ...
ALLOWLIST_MATCH:
- ...

GATES_REQUIRED:
- ...
GATES_MINIMUM:
- ...

EVIDENCE_EXPECTED:
- gate_id: exit_code=0 + stdout markers + artifacts

ROLLBACK_PLAN:
- ...

ACCEPTANCE_CRITERIA:
- AC-001:
- AC-002:

EVIDENCE_PACK:
- RUN_ID:
- (links/paths em _reports/audit/<RUN_ID>/)