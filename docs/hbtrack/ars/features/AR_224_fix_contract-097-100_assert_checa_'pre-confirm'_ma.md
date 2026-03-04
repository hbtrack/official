# AR_224 — Fix CONTRACT-097-100: assert checa 'pre-confirm' mas implementação usa 'preconfirm'

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em tests/training/contracts/test_contract_train_097_100_presence_pending.py (gerado em AR_208/Batch 10), a função test_contract_097_098_routes_defined (~linha 27) contém:

  assert 'pre-confirm' in content

onde content = attendance.py lido como texto. A implementação AR_185 (✅ VERIFICADO + sealed 2026-03-01) usa a URL '/attendance/sessions/{session_id}/preconfirm' (sem hífen). A string literal 'pre-confirm' não existe em attendance.py, causando 1 FAIL.

Fix: mudar a assertion para:

  assert 'preconfirm' in content

Justificativa: AR_185 foi verificada e selada com 'preconfirm'; a assertion deve refletir o que está implementado e verificado, não uma variante hipotética de URL. O contrato funcional (INV-TRAIN-063) está satisfeito pela rota existente.

## Critérios de Aceite
pytest tests/training/contracts/test_contract_train_097_100_presence_pending.py -v --tb=short retorna 0 FAILs e 0 ERRORs; assertion 'preconfirm' in content passa (string existe em attendance.py); Apenas a linha de assert com 'pre-confirm' modificada.

## Write Scope
- Hb Track - Backend/tests/training/contracts/test_contract_train_097_100_presence_pending.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_097_100_presence_pending.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_224/executor_main.log`

## Riscos
- Verificar que 'close' também existe em attendance.py (segunda assertion do mesmo teste) — confirmado na investigação do Arquiteto (L500 do router).
- Não alterar a assertion de 'close' nem 'pending-items' — essas já passam.
- Nota SSOT: CONTRACT-TRAIN-097 documenta URL como '/training-sessions/{session_id}/pre-confirm'. Após este fix, o test estará alinhado com a implementação selada mas levemente divergente do SSOT de contrato. Uma AR de governança futura pode uniformizar a URL e o SSOT se necessário — fora do escopo deste fix operacional.

## Análise de Impacto

**Arquivo modificado**: `Hb Track - Backend/tests/training/contracts/test_contract_train_097_100_presence_pending.py`

**Mudança**: função `test_contract_097_098_routes_defined` — `assert "pre-confirm" in content` → `assert "preconfirm" in content`

**Impacto em produto**: zero — arquivo de teste apenas, sem toque em `app/`, `db/` ou Frontend.

**Impacto em outros testes**: zero — as assertions de `"close"` e `"pending-items"` não são alteradas.

**Verificação pré-patch**: `attendance.py` contém `preconfirm` (L439: `/attendance/sessions/{session_id}/preconfirm`) e `close` e `pending-items` — confirmado pelo Arquiteto.

**Divergência SSOT anotada**: CONTRACT-TRAIN-097 documenta `/training-sessions/{id}/pre-confirm`; implementação AR_185 (sealed) usa `/attendance/sessions/{id}/preconfirm`. Fix alinha o teste com o que foi verificado e selado.

**Rollback**: `git checkout -- "Hb Track - Backend/tests/training/contracts/test_contract_train_097_100_presence_pending.py"`

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_097_100_presence_pending.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T18:00:11.702385+00:00
**Behavior Hash**: e6c3e5ac5fee5aaae975740e15f7665448df363405de36f3dc8081c26970a0e0
**Evidence File**: `docs/hbtrack/evidence/AR_224/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_224_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T18:35:50.249711+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_224_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_224/executor_main.log`
