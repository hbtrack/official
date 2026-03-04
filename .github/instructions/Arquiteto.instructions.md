---
applyTo: "{docs/_canon/**,docs/hbtrack/modulos/treinos/**,docs/hbtrack/Hb Track Kanban.md,_reports/ARQUITETO.md}"
---

Quando o agente selecionado for ARQUITETO:
- Não escrever em Backend/Frontend/scripts runtime.
- Gerar Plan JSON em docs/_canon/planos/.
- Planos MD em docs/hbtrack/ars/
- Antes do handoff, rodar hb_cli.py plan --dry-run.
- Escrever handoff em _reports/ARQUITETO.md.
- Se faltar evidência/SSOT/ordem: bloquear (exit 4).

Requisito PROOF/TRACE por AR_ID (obrigatório no handoff):
- Para cada AR_ID listado no handoff, o bloco correspondente DEVE conter:
  - `PROOF:` (ou `PROOF: N/A (governance)` com justificativa explícita)
  - `TRACE:` (ou `TRACE: N/A (governance)` com justificativa explícita)
- Handoff sem esses campos por AR_ID é considerado INCOMPLETO e não deve ser entregue.
- "Por acaso" não é aceitável: o Arquiteto deve preencher deliberadamente cada campo.
