# AR_271 — Reconciliacao documental: lifecycle canonico nos 3 artefatos de base TRAINING

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Este AR reconcilia semanticamente 3 artefatos de base do modulo TRAINING, eliminando vocabulario legado publish/close/PUBLISHED/CLOSED e promovendo lifecycle canonico. NENHUM arquivo de backend ou frontend e tocado.

ARQUIVO 1: docs/hbtrack/modulos/treinos/_INDEX.md
(a) Bump versao para v1.9.0.
(b) Adicionar changelog entry AR-TRAIN-REC-01 descrevendo a reconciliacao semantica.
(c) Na secao de autoridade/navegacao declarar explicitamente que lifecycle canonico e: draft -> scheduled -> in_progress -> pending_review -> readonly.
(d) Registrar que publish/close/PUBLISHED/CLOSED deixam de ser linguagem valida nos 3 artefatos de base.
(e) Promover formalmente TRAINING_SCOPE_REGISTRY.yaml v1.1.0 e TRAINING_PERF_LIMITS.json v1.1.0 como reconciliados por AR-TRAIN-REC-01.

ARQUIVO 2: docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml
(a) Bump versao para v1.1.0.
(b) Item training_sessions_lifecycle: substituir description com DRAFT->PUBLISHED->CLOSED por 'draft -> scheduled -> in_progress -> pending_review -> readonly (ciclo canonico unico); DRAFT/PUBLISHED/CLOSED sao vocabulario obsoleto nao mais valido'.
(c) Item ai_coach_core: adicionar mencao explicita ao ledger imutavel: Planned_State (imutavel apos insert), Adjustment_Logs (append-only, sequence_number), Realized_State (separado do plano).
(d) Varrer TODOS os itens: substituir ocorrencias residuais de PUBLISHED, CLOSED, published, closed, /publish, /close nos campos description e notes.

ARQUIVO 3: docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json
(a) Bump versao para v1.1.0.
(b) Renomear chave raiz 'limits' para 'operations' (necessario para validacao Gate 4).
(c) Remover chaves: training_session_publish, training_session_close.
(d) Adicionar: training_session_schedule (POST /training-sessions/{id}/schedule, scope CORE, max_response_time_ms 1000, p95_response_time_ms 800, max_payload_kb 64).
(e) Adicionar: training_session_finalize (POST /training-sessions/{id}/finalize, scope CORE, max_response_time_ms 2000, p95_response_time_ms 1500, max_payload_kb 64).
(f) Adicionar: task_update_session_statuses (Celery task — async, scope CORE, max_execution_time_ms 5000, max_sessions_per_run 1000, note 'FOR UPDATE SKIP LOCKED obrigatorio').
(g) Atualizar ai_coach_apply_draft: adicionar note 'transacional — cria Planned_State imutavel + Adjustment_Log entry; custo inclui 2 INSERTs atomicos'.

PROIBIDO: nao alterar codigo backend, nao alterar codigo frontend, nao criar adapter semantico publish->schedule.

## Critérios de Aceite
1) _INDEX.md versao v1.9.0 com changelog AR-TRAIN-REC-01, lifecycle canonico declarado e artefatos reconciliados promovidos.
2) TRAINING_SCOPE_REGISTRY.yaml versao v1.1.0 sem PUBLISHED/CLOSED e com lifecycle draft->scheduled->in_progress->pending_review->readonly em training_sessions_lifecycle.
3) ai_coach_core em TRAINING_SCOPE_REGISTRY.yaml menciona ledger imutavel (Planned_State ou Adjustment_Log ou append-only).
4) TRAINING_PERF_LIMITS.json versao v1.1.0 com chave raiz 'operations' (nao 'limits'), sem training_session_publish/close, com training_session_schedule + training_session_finalize + task_update_session_statuses presentes.
5) Todos os 5 gates da OS passam via validation_command Python.

## Write Scope
- docs/hbtrack/modulos/treinos/_INDEX.md
- docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml
- docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json

## Validation Command (Contrato)
```
python -c "import json,pathlib; base=pathlib.Path('docs/hbtrack/modulos/treinos'); idx=(base/'_INDEX.md').read_text(encoding='utf-8'); scope=(base/'TRAINING_SCOPE_REGISTRY.yaml').read_text(encoding='utf-8'); perf=json.loads((base/'TRAINING_PERF_LIMITS.json').read_text(encoding='utf-8')); assert 'PUBLISHED' not in scope,'FAIL Gate1: PUBLISHED em SCOPE_REGISTRY'; assert 'CLOSED' not in scope,'FAIL Gate1: CLOSED em SCOPE_REGISTRY'; ops=perf.get('operations'); assert ops is not None,'FAIL Gate4: chave operations ausente em PERF_LIMITS (renomear limits->operations)'; assert 'training_session_publish' not in ops,'FAIL Gate1: training_session_publish em PERF_LIMITS'; assert 'training_session_close' not in ops,'FAIL Gate1: training_session_close em PERF_LIMITS'; assert all(t in scope for t in ['draft','scheduled','in_progress','pending_review','readonly']),'FAIL Gate2: lifecycle canonico ausente em SCOPE_REGISTRY'; assert any(k in scope.lower() for k in ['ledger','planned_state','adjustment_log']),'FAIL Gate3: ledger/planned_state ausente em ai_coach_core'; assert all(k in ops for k in ['training_session_schedule','training_session_finalize','task_update_session_statuses','ai_coach_apply_draft']),'FAIL Gate4: ops novas ausentes em PERF_LIMITS'; assert all(t in idx for t in ['draft','scheduled','in_progress','pending_review','readonly']),'FAIL Gate5: lifecycle canonico ausente em _INDEX.md'; assert 'TRAINING_SCOPE_REGISTRY.yaml' in idx,'FAIL Gate5: TRAINING_SCOPE_REGISTRY.yaml nao promovido em _INDEX.md'; assert 'TRAINING_PERF_LIMITS.json' in idx,'FAIL Gate5: TRAINING_PERF_LIMITS.json nao promovido em _INDEX.md'; print('PASS AR_271: Gates 1-5 reconciliacao canonica OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_271/executor_main.log`

## Notas do Arquiteto
Gate 1 (Negative lexical): sem PUBLISHED/CLOSED/training_session_publish/training_session_close nos 3 artefatos. Gate 2 (Positive lifecycle): lifecycle canonico draft->scheduled->in_progress->pending_review->readonly em SCOPE_REGISTRY. Gate 3 (Positive ledger): ai_coach_core descreve ledger imutavel (Planned_State/Adjustment_Log/append-only). Gate 4 (Positive perf): PERF_LIMITS tem chave 'operations' com training_session_schedule + training_session_finalize + task_update_session_statuses. Gate 5 (Positive index): _INDEX.md v1.9.0 promove artefatos reconciliados com lifecycle canonico. ATENCAO Executor: _INDEX.md relevante e docs/hbtrack/modulos/treinos/_INDEX.md (modulo), NAO o _INDEX.md global em docs/hbtrack/_INDEX.md (auto-gerado). A chave 'limits' do PERF_LIMITS DEVE ser renomeada para 'operations'. Verificar scripts/ antes para dependencias da chave 'limits'.

## Riscos
- TRAINING_SCOPE_REGISTRY.yaml pode ter ocorrencias de PUBLISHED/CLOSED alem do campo training_sessions_lifecycle — varrer arquivo completo
- _INDEX.md pode ter referencias historicas a PUBLISHED/CLOSED em changelogs historicos — avaliar mana o Executor se changelogs historicos devem ser atualizados ou preservados como registro
- Renomear 'limits' para 'operations' no PERF_LIMITS.json pode quebrar scripts que leem a chave 'limits' diretamente — Executor deve verificar grep em scripts/ antes de renomear

## Análise de Impacto

**Executor**: GitHub Copilot (Executor mode) — 2026-03-09

**Arquivos impactados (write_scope)**:
1. `docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml` — bump v1.0.0→v1.1.0; substituição de description em `training_sessions_lifecycle` (DRAFT→PUBLISHED→CLOSED → lifecycle canônico); adição de ledger em `ai_coach_core`.
2. `docs/hbtrack/modulos/treinos/TRAINING_PERF_LIMITS.json` — bump v1.0.0→v1.1.0; rename chave raiz `limits`→`operations`; remoção de `training_session_publish` e `training_session_close`; adição de `training_session_schedule`, `training_session_finalize`, `task_update_session_statuses`; nota ledger em `ai_coach_apply_draft`.
3. `docs/hbtrack/modulos/treinos/_INDEX.md` — bump v1.8.0→v1.9.0; changelog AR-TRAIN-REC-01; declaração de lifecycle canônico e reconciliação semântica; promoção de SCOPE_REGISTRY v1.1.0 e PERF_LIMITS v1.1.0 no Mapa de Autoridade.

**Impacto em código de produto**: ZERO — nenhum arquivo backend/frontend é tocado.

**Risco chave `limits` → `operations`**: grep em `scripts/` confirma zero referências a `TRAINING_PERF_LIMITS` em qualquer script Python. Renomeação segura.

**Risco changelogs históricos em _INDEX.md**: changelogs históricos de v1.4.0..v1.8.0 mencionam PUBLISHED/CLOSED apenas como referência histórica (estado anterior dos artefatos). Validação Gate 1 checa apenas `TRAINING_SCOPE_REGISTRY.yaml` e `TRAINING_PERF_LIMITS.json` — o _INDEX.md é verificado apenas para presença de lifecycle canônico (Gate 5), não ausência de PUBLISHED/CLOSED. Changelogs históricos serão preservados como registro.

**Verificação de contaminação residual em SCOPE_REGISTRY**: apenas `training_sessions_lifecycle.description` contém PUBLISHED/CLOSED. Restante do yaml está limpo.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 284e769
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib; base=pathlib.Path('docs/hbtrack/modulos/treinos'); idx=(base/'_INDEX.md').read_text(encoding='utf-8'); scope=(base/'TRAINING_SCOPE_REGISTRY.yaml').read_text(encoding='utf-8'); perf=json.loads((base/'TRAINING_PERF_LIMITS.json').read_text(encoding='utf-8')); assert 'PUBLISHED' not in scope,'FAIL Gate1: PUBLISHED em SCOPE_REGISTRY'; assert 'CLOSED' not in scope,'FAIL Gate1: CLOSED em SCOPE_REGISTRY'; ops=perf.get('operations'); assert ops is not None,'FAIL Gate4: chave operations ausente em PERF_LIMITS (renomear limits->operations)'; assert 'training_session_publish' not in ops,'FAIL Gate1: training_session_publish em PERF_LIMITS'; assert 'training_session_close' not in ops,'FAIL Gate1: training_session_close em PERF_LIMITS'; assert all(t in scope for t in ['draft','scheduled','in_progress','pending_review','readonly']),'FAIL Gate2: lifecycle canonico ausente em SCOPE_REGISTRY'; assert any(k in scope.lower() for k in ['ledger','planned_state','adjustment_log']),'FAIL Gate3: ledger/planned_state ausente em ai_coach_core'; assert all(k in ops for k in ['training_session_schedule','training_session_finalize','task_update_session_statuses','ai_coach_apply_draft']),'FAIL Gate4: ops novas ausentes em PERF_LIMITS'; assert all(t in idx for t in ['draft','scheduled','in_progress','pending_review','readonly']),'FAIL Gate5: lifecycle canonico ausente em _INDEX.md'; assert 'TRAINING_SCOPE_REGISTRY.yaml' in idx,'FAIL Gate5: TRAINING_SCOPE_REGISTRY.yaml nao promovido em _INDEX.md'; assert 'TRAINING_PERF_LIMITS.json' in idx,'FAIL Gate5: TRAINING_PERF_LIMITS.json nao promovido em _INDEX.md'; print('PASS AR_271: Gates 1-5 reconciliacao canonica OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-09T04:51:40.724264+00:00
**Behavior Hash**: 52a4e90d49a5e63ed2a8efb7d50c2b6e379338a089aec44192bd316f38a1a82c
**Evidence File**: `docs/hbtrack/evidence/AR_271/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 284e769
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_271_284e769/result.json`

### Selo Humano em 284e769
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-09T05:54:26.210533+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_271_284e769/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_271/executor_main.log`
