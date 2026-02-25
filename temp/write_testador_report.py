import pathlib

content = """# TESTADOR -- Batch Verify Report
Gerado em: 2026-02-24 | git7: f8f030f | Protocol: v1.2.1

---

TESTADOR_REPORT:
- ar_id: 002
- status: SUCESSO
- triple_consistency: OK
- consistency: OK
- report_path: _reports/testador/AR_002_f8f030f/result.json
- rejection_reason:
- next: hb seal executado

---

TESTADOR_REPORT:
- ar_id: 036
- status: SUCESSO
- triple_consistency: OK
- consistency: OK
- report_path: _reports/testador/AR_036_f8f030f/result.json
- rejection_reason:
- next: hb seal executado

---

## PARA O ARQUITETO

AR_059 BLOQUEADA -- action required:
- Implementacao: COMPLETA (docs/_canon/context_map.md, 124 linhas, todas secoes presentes)
- Blocker: TypeError no validation_command -- any() recebe bool em vez de iteravel
- Correcao: remover wrapper any(), usar assert direto:
  assert ('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c), 'FAIL: cabecalho context map ausente'
- Evidence: docs/hbtrack/evidence/AR_059/executor_main.log (exit=1)

## PARA O EXECUTOR

AR_002 e AR_036: VERIFICADO.
AR_059: aguardando correcao validation_command pelo Arquiteto antes de re-hb report.
"""

out = pathlib.Path("_reports/TESTADOR.md")
out.write_text(content, encoding="utf-8")
print(f"TESTADOR.md written OK ({len(content)} chars)")

