# AR_191 — Pós-treino conversacional: service + router

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar dois arquivos novos: (1) Hb Track - Backend/app/services/post_training_service.py — Service de feedback pós-treino conversacional. Responsabilidades: (a) Registrar feedback imediato do atleta após encerramento de sessão (INV-TRAIN-070: feedback pós-treino é registrado imediatamente após close; não pode ser editado após 24h). (b) Retornar resumo de performance da sessão encerrada para o atleta (exercícios realizados, cargas, comparação com planejado). (c) INV-TRAIN-077: feedback pós-treino deve ser privado do atleta — treinador acessa apenas resumo agregado, não o texto livre verbatim. Métodos mínimos: create_post_training_feedback(session_id, athlete_id, feedback_text, rating) → PostTrainingFeedback; get_session_summary(session_id, user_id) → SessionSummary; list_athlete_feedbacks(athlete_id, user_id) → List[PostTrainingFeedback]. (2) Hb Track - Backend/app/api/v1/routers/post_training.py — Router com endpoints: POST /training/sessions/{session_id}/post-training-feedback (atleta registra feedback após close); GET /training/sessions/{session_id}/summary (atleta e treinador — treinador vê apenas resumo agregado); GET /training/athletes/{athlete_id}/post-training-feedbacks (treinador: lista feedbacks agregados). Registrar o router em Hb Track - Backend/app/api/v1/api.py (import + include_router). NOTA: Executor deve escolher usar wellness_post como tabela base OU criar nova tabela. Se criar nova tabela, rodar Alembic + gen_docs_ssot.py e atualizar ssot_touches no evidence.

## Critérios de Aceite
1) post_training_service.py existe com métodos de create_feedback e get_session_summary. 2) post_training.py router existe com pelo menos POST .../post-training-feedback e GET .../summary. 3) Router registrado em api.py. 4) INV-TRAIN-070: feedback registrado após close — service verifica que sessão está closed antes de aceitar feedback. 5) INV-TRAIN-077: endpoint de treinador não retorna texto verbatim do atleta (retorna apenas resumo/rating/agregados). 6) Atleta autenticado pode registrar feedback apenas para suas próprias sessões.

## Write Scope
- Hb Track - Backend/app/services/post_training_service.py
- Hb Track - Backend/app/api/v1/routers/post_training.py
- Hb Track - Backend/app/api/v1/api.py

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; svc=open(os.path.join(b,'app','services','post_training_service.py')).read(); assert 'feedback' in svc.lower(), 'post_training_service missing feedback method'; assert 'summary' in svc.lower(), 'post_training_service missing summary method'; router=open(os.path.join(b,'app','api','v1','routers','post_training.py')).read(); assert 'post' in router.lower() or 'feedback' in router.lower(), 'router missing feedback endpoint'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'post_training' in api, 'router not registered in api.py'; print('PASS AR_191')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_191/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/api/v1/api.py
git clean -fd Hb Track - Backend/app/services/post_training_service.py
git clean -fd Hb Track - Backend/app/api/v1/routers/post_training.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
INV-TRAIN-077 é crítico: privacidade do atleta. O treinador NÃO deve receber texto verbatim do feedback — somente rating/média/resumo. Executor deve ler INV-TRAIN-070 e INV-TRAIN-077 em INVARIANTS_TRAINING.md antes de implementar. Se usar wellness_post como tabela base, adicionar campos necessários (feedback_text, rating) via migration. Se criar nova tabela, documentar no evidence.

## Riscos
- Decisão arquitetural: wellness_post vs nova tabela — Executor deve consultar INV-TRAIN-070/077 e decidir; documentar no evidence
- INV-TRAIN-077: risco de vazar texto verbatim do atleta para treinador — revisar todos os endpoints de listagem
- api.py: ao adicionar include_router, verificar prefixo e tags para não colidir com routers existentes

## Análise de Impacto

**Inspeção pré-implementação (2026-03-01)**:
- `wellness_post` table inspecionada: tem `training_session_id` FK, `athlete_id` FK, `session_rpe` (INT 0-10), `notes` (TEXT nullable), `locked_at` (timestamp). UNIQUE constraint em `(training_session_id, athlete_id)` — um registro por atleta por sessão.
- **Decisão arquitetural**: Usar `wellness_post` como backing store. `notes` serve como `feedback_text`, `session_rpe` serve como `rating`. Não é necessária nova tabela nem migration. Documentado aqui como evidência de decisão.
- INV-TRAIN-070: verificar `session.status == 'readonly'` antes de aceitar feedback.
- INV-TRAIN-077: endpoint de treinador retorna apenas `session_rpe` (rating médio) e contagem — NUNCA o `notes` text.
- `post_training_service.py`: arquivo novo — criar.
- `post_training.py` router: arquivo novo — criar.
- `api.py`: adicionar import + include_router sem colidir com routers existentes (prefixo `/training` existente — usar `/post-training`).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; svc=open(os.path.join(b,'app','services','post_training_service.py')).read(); assert 'feedback' in svc.lower(), 'post_training_service missing feedback method'; assert 'summary' in svc.lower(), 'post_training_service missing summary method'; router=open(os.path.join(b,'app','api','v1','routers','post_training.py')).read(); assert 'post' in router.lower() or 'feedback' in router.lower(), 'router missing feedback endpoint'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'post_training' in api, 'router not registered in api.py'; print('PASS AR_191')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T08:49:12.187003+00:00
**Behavior Hash**: a33c98eef55aac0d9f1fb241878e3001d23e09f8bdba16859c639c8769c3635e
**Evidence File**: `docs/hbtrack/evidence/AR_191/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_191_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T09:02:08.352477+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_191_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_191/executor_main.log`
