# AR_268 — Criar TRAINING_PERF_LIMITS.json

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json conforme exigido pela Seção 5.3 do DONE_CONTRACT_TRAINING.md.

Este arquivo define os limites quantitativos mínimos (SLOs) para todos os itens CORE do módulo. Sem ele, itens CORE com dependência de desempenho não são elegíveis para DONE_PRODUTO.

ESTRUTURA OBRIGATÓRIA DO ARQUIVO:
```json
{
  "module": "TRAINING",
  "version": "v1.0.0",
  "last_revised": "2026-03-08",
  "authority": "DONE_CONTRACT_TRAINING.md §5.3 + §9",
  "note": "SLOs mínimos baseline — revisão via AR futura com evidência de load test",
  "limits": {
    "training_sessions_list": {
      "scope": "CORE",
      "operation": "GET /training-sessions (paginado)",
      "max_response_time_ms": 1000,
      "p95_response_time_ms": 800,
      "max_page_size": 100,
      "max_payload_kb": 256
    },
    "training_session_get": {
      "scope": "CORE",
      "operation": "GET /training-sessions/{id}",
      "max_response_time_ms": 500,
      "p95_response_time_ms": 400,
      "max_payload_kb": 64
    },
    "training_session_create": {
      "scope": "CORE",
      "operation": "POST /training-sessions",
      "max_response_time_ms": 1500,
      "p95_response_time_ms": 1200,
      "max_payload_kb": 64
    },
    "training_session_publish": {
      "scope": "CORE",
      "operation": "POST /training-sessions/{id}/publish",
      "max_response_time_ms": 1000,
      "p95_response_time_ms": 800,
      "max_payload_kb": 64
    },
    "training_session_close": {
      "scope": "CORE",
      "operation": "POST /training-sessions/{id}/close",
      "max_response_time_ms": 2000,
      "p95_response_time_ms": 1500,
      "max_payload_kb": 64
    },
    "attendance_list": {
      "scope": "CORE",
      "operation": "GET /training_sessions/{id}/attendance",
      "max_response_time_ms": 800,
      "p95_response_time_ms": 600,
      "max_athletes_per_session": 100,
      "max_payload_kb": 128
    },
    "attendance_batch": {
      "scope": "CORE",
      "operation": "POST /training_sessions/{id}/attendance/batch",
      "max_response_time_ms": 2000,
      "p95_response_time_ms": 1500,
      "max_batch_size": 100,
      "max_payload_kb": 128
    },
    "wellness_pre_submit": {
      "scope": "CORE",
      "operation": "POST /wellness-pre/.../wellness_pre",
      "max_response_time_ms": 1000,
      "p95_response_time_ms": 800,
      "max_payload_kb": 32
    },
    "wellness_post_submit": {
      "scope": "CORE",
      "operation": "POST /wellness-post/.../wellness_post",
      "max_response_time_ms": 1000,
      "p95_response_time_ms": 800,
      "max_payload_kb": 32
    },
    "cycles_list": {
      "scope": "CORE",
      "operation": "GET /training-cycles",
      "max_response_time_ms": 800,
      "p95_response_time_ms": 600,
      "max_payload_kb": 128
    },
    "microcycles_list": {
      "scope": "CORE",
      "operation": "GET /training-microcycles",
      "max_response_time_ms": 800,
      "p95_response_time_ms": 600,
      "max_payload_kb": 256
    },
    "exercise_bank_list": {
      "scope": "CORE",
      "operation": "GET /exercises (paginado)",
      "max_response_time_ms": 1200,
      "p95_response_time_ms": 1000,
      "max_page_size": 200,
      "max_payload_kb": 512
    },
    "session_exercises_list": {
      "scope": "CORE",
      "operation": "GET /training-sessions/{id}/exercises",
      "max_response_time_ms": 800,
      "p95_response_time_ms": 600,
      "max_exercises_per_session": 100,
      "max_payload_kb": 256
    },
    "export_pdf": {
      "scope": "CORE",
      "operation": "GET /training-sessions/export-pdf (DEC-TRAIN-004)",
      "max_response_time_ms": 10000,
      "p95_response_time_ms": 8000,
      "max_payload_kb": 4096,
      "note": "endpoint assíncrono ou com polling — SLO inclui wait time de geração"
    },
    "ai_coach_apply_draft": {
      "scope": "CORE",
      "operation": "PATCH apply-draft (CONTRACT-100)",
      "max_response_time_ms": 3000,
      "p95_response_time_ms": 2500,
      "max_payload_kb": 64
    },
    "analytics_deviation": {
      "scope": "CORE",
      "operation": "GET /training-sessions/{id}/deviation",
      "max_response_time_ms": 1500,
      "p95_response_time_ms": 1200,
      "max_payload_kb": 64
    }
  },
  "global_limits": {
    "max_concurrent_users_per_team": 50,
    "max_request_body_kb": 1024,
    "auth_overhead_ms": 50,
    "db_connection_pool_min": 5,
    "db_connection_pool_max": 20
  }
}
```

O Executor DEVE criar o arquivo com esta estrutura. Os valores numéricos são SLOs mínimos baseline — podem ser revisados via AR futura com evidência.

## Critérios de Aceite
1) docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json existe. 2) Arquivo é JSON válido. 3) Contém chaves de topo: module, version, limits, global_limits. 4) module == 'TRAINING'. 5) limits tem pelo menos 8 itens CORE. 6) Cada item de limits tem scope e pelo menos dois limites numéricos (ex: max_response_time_ms, p95_response_time_ms ou max_payload_kb).

## Write Scope
- docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json

## Validation Command (Contrato)
```
python temp_validate_ar268.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_268/executor_main.log`

## Notas do Arquiteto
Classe: A (spec artifact). PROOF: N/A (governance). Arquivo novo — não existe ainda. Valores são SLOs baseline mínimos — podem ser revisados com evidência de load test.

## Riscos
- SLOs muito restritivos podem gerar FAILs prematuros em testes de performance — usar valores conservadores
- export_pdf tem SLO alto (10s) por ser operação assíncrona — não reduzir sem evidência

## Análise de Impacto
Artefato novo de governança (SLOs baseline). Escopo exclusivo: `docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json`.
Nenhum código de produto alterado. Sem impacto em API/FE/BE. Batch 35 — classe A.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp_validate_ar268.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-08T14:57:58.253646+00:00
**Behavior Hash**: 2bc8e7286afdf6c97778f29e39cd62101153957d9b6d3da50b40645873bd7f68
**Evidence File**: `docs/hbtrack/evidence/AR_268/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_268_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-08T16:11:33.697584+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_268_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_268/executor_main.log`
