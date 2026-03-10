import pathlib

content = """# TESTADOR -- Batch Verify Report
Gerado em: 2026-02-24 | git7: f8f030f | Protocol: v1.2.1

---

TESTADOR_REPORT:
- ar_id: 056
- status: SUCESSO
- triple_consistency: OK
- consistency: OK
- report_path: _reports/testador/AR_056_f8f030f/result.json
- rejection_reason:
- next: hb seal executado

---

TESTADOR_REPORT:
- ar_id: 058
- status: SUCESSO
- triple_consistency: OK
- consistency: OK
- report_path: _reports/testador/AR_058_f8f030f/result.json
- rejection_reason:
- next: hb seal executado

---

TESTADOR_REPORT:
- ar_id: 059
- status: REJEITADO
- triple_consistency: nao executado (pre-condicao falhou)
- consistency: AH_DIVERGENCE (validation_command invalido)
- report_path: (sem report -- rejeitado antes do triple-run)
- rejection_reason: TypeError -- any() recebe bool em vez de iteravel no validation_command
- next: arquiteto deve revisar plano

---

## PARA O ARQUITETO

AR_059 permanece em status FALHA aguardando correcao do validation_command.
O Executor ja descreveu o problema em EXECUTOR.yaml:
- Erro: any() recebe bool em vez de iteravel
- Correcao sugerida: remover any() da assertion, usar direto:
    assert ('Context Map' in c or 'context_map' in c.lower() or 'Mapa' in c), "FAIL: cabecalho context map ausente"
- A implementacao docs/_canon/context_map.md esta COMPLETA (124 linhas) e passa validacao manual.

Acao requerida: corrigir validation_command da AR_059 e alterar status para PENDENTE.

## STATUS FINAL BATCH

AR_056: VERIFICADO
AR_058: VERIFICADO
AR_059: REJEITADO (AH_DIVERGENCE) -> Arquiteto
"""

target = pathlib.Path("_reports/TESTADOR.yaml")
target.write_text(content, encoding="utf-8")
print(f"Written: {target.resolve()}")
