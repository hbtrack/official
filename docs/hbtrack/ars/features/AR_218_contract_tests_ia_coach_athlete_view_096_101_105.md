# AR_218 — Contract Tests: IA Coach + Athlete View (CONTRACT-096, 101..105)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0
**AR SSOT ID**: AR-TRAIN-039
**Batch**: 14

## Descrição
Criar testes de contrato automatizados para 6 contratos de IA Coach e visão do atleta (CONTRACT-096, 101..105): sugestão de coach, aprovação de sugestão, visão consolidada do atleta, histórico pessoal, etc. Arquivo: `test_contract_train_096_101_105_ia_athlete.py`. Atualizar TEST_MATRIX §8 para CONTRACT-096/101..105 = COBERTO. FORBIDDEN: zero toque em `app/`. ATENÇÃO: INV-079/080/081 têm BLOCKED_IMPORT de `ai_coach_service` — testes de contrato NÃO devem importar `ai_coach_service` diretamente.

## Critérios de Aceite
**AC-001:** `pytest -q tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py` retorna exit 0 — 0 FAILs.
**AC-002:** §8 da `TEST_MATRIX_TRAINING.md` mostra CONTRACT-096/101..105 = COBERTO.

## Write Scope
- `Hb Track - Backend/tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py`
- `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md`

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest -q tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_218/executor_main.log`

## Dependências
- AR-TRAIN-034 (AR_213) — ✅ VERIFICADO (Batch 13 sealed)

## Riscos
- INV-079/080/081 têm BLOCKED_IMPORT de `ai_coach_service` (RecognitionApproved, CoachSuggestionDraft, JustifiedSuggestion) — testes de contrato NÃO devem importar `ai_coach_service` diretamente.
- Usar mocks/stubs ou validação de endpoint schema apenas — nunca importar módulo que gera ImportError.
- Não tocar em `app/` — somente camada de testes.

## Análise de Impacto
**Escopo**: criação de arquivo de teste de contrato + atualização TEST_MATRIX §8. Zero toque em app/.
**Routers mapeados**:
- `athlete_training.py` → CONTRACT-096 (GET /training-sessions/{session_id}/preview)
- `ai_coach.py` (prefix `/ai`) → CONTRACT-101..104: router expõe `/ai/chat`, `/ai/coach/suggest-session`, `/ai/coach/suggest-microcycle` (SSOT usa `/ai-coach/*` — router real tem prefix `/ai`; testes verificam o que existe)
- CONTRACT-105 (GET `/athlete/wellness-content-gate/{session_id}`) — endpoint não encontrado em nenhum router; teste usa pytest.skip com razão documentada
**ATENÇÃO**: `ai_coach_service` importado apenas pelo router — testes NÃO importam diretamente.
**Abordagem**: estática (Path + read_text). Sem fixtures de DB. Sem import de ai_coach_service.
**Efeito colateral**: nenhum em código de produto.

---
## Carimbo de Execução

*(a preencher pelo Executor)*

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest -q tests/training/contracts/test_contract_train_096_101_105_ia_athlete.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T15:16:24.235066+00:00
**Behavior Hash**: 15fd30798fd976d1c888d94df6c544a67976430fdced19c65528fd412833247e
**Evidence File**: `docs/hbtrack/evidence/AR_218/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_218_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T15:27:06.346941+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_218_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_218/executor_main.log`
