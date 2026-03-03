# AR_177 — Fix wellness rankings BE: cálculo SSOT + response_model no OpenAPI

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir TeamWellnessRankingService e o router de wellness-rankings para operar exclusivamente com campos e tipos canônicos do SSOT.

=== ANCORA SSOT ===
- schema.sql: tabela attendance com presence_status (enum: present|absent|justified), NÃO booleano 'present'
- schema.sql: tabela team_wellness_ranking com team_id UUID PK
- openapi.json: /analytics/wellness-rankings deve expor response_model explícito
- INV-TRAIN-036: ranking de team/mês DEVE ser único por (team_id, month)
- INV-TRAIN-027: tarefa de refresh DEVE estar vinculada ao serviço de cálculo

=== LEITURA PRÉVIA (READ-ONLY) ===
1. Ler team_wellness_ranking_service.py — identificar uso de campos legados (Attendance.present, TeamMembership, athlete_id:int)
2. Ler team_wellness_ranking.py (model) — confirmar tipos dos campos
3. Ler analytics.py (router) — confirmar response_model nos endpoints wellness-rankings
4. Ler schema.sql linha attendance e team_wellness_ranking

=== CORREÇÕES OBRIGATÓRIAS ===
1. team_wellness_ranking_service.py:
   - Substituir qualquer referência a Attendance.present por attendance.presence_status IN ('present', 'justified')
   - Remover uso de TeamMembership para listar atletas — usar team_registrations ou athlete_team_assignment conforme SSOT
   - team_id e athlete_id DEVEM ser UUID em todas as queries
   - Cálculo de taxa: (count present + count justified) / total_attendance × 100

2. analytics.py (router wellness-rankings):
   - Adicionar response_model explícito em get_wellness_rankings, get_team_athletes_90plus e calculate_rankings_manually
   - response_model deve refletir schema Pydantic canônico (sem campos int onde SSOT é UUID)

=== ARQUIVOS A MODIFICAR ===
- Hb Track - Backend/app/services/team_wellness_ranking_service.py
- Hb Track - Backend/app/api/v1/routers/analytics.py
- Hb Track - Backend/app/models/team_wellness_ranking.py (se necessário para ajuste de type hint)

## Critérios de Aceite
1) get_wellness_rankings retorna team_id como UUID string, não int.
2) Cálculo de taxa usa presence_status IN (present, justified) — sem Attendance.present legado.
3) Sem uso de TeamMembership para listar atletas de um time (usar team_registrations/athlete_team_assignment).
4) response_model explícito presente nos 3 endpoints de wellness-rankings no OpenAPI (get, athletes-90plus, calculate).
5) test_inv_train_036_wellness_rankings_unique_runtime.py passa (sem duplicatas team/mês).
6) test_inv_train_027_refresh_training_rankings_task.py passa (tarefa de refresh vinculada ao cálculo).

## Write Scope
- Hb Track - Backend/app/services/team_wellness_ranking_service.py
- Hb Track - Backend/app/api/v1/routers/analytics.py
- Hb Track - Backend/app/models/team_wellness_ranking.py

## Validation Command (Contrato)
```
python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique_runtime.py','Hb Track - Backend/tests/training/invariants/test_inv_train_027_refresh_training_rankings_task.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_177 exit='+str(r.returncode); print('PASS AR_177')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_177/executor_main.log`

## Notas do Arquiteto
ANCORA: schema.sql tabela team_wellness_ranking e attendance. ANCORA: test_inv_train_036 (unicidade por team/mês) + test_inv_train_027 (refresh task). Dependência AR-TRAIN-004 (AR_176) ✅ VERIFICADO. Batch 2 TRAINING_BATCH_PLAN_v1.

## Riscos
- analytics.py contém outros endpoints de analytics além dos wellness-rankings — Executor deve atualizar APENAS os 3 endpoints de wellness-rankings, sem alterar team_summary, weekly_load, deviation_analysis ou prevention_effectiveness
- Se TeamMembership for usado em outros contextos do serviço (não Rankings), o Executor deve garantir que a remoção é cirúrgica e não quebra outros fluxos
- O model Pydantic de response pode não existir ainda — Executor deve criar se necessário, sem inventar campos não presentes no schema.sql

## Análise de Impacto

**Arquivos modificados:**

1. `Hb Track - Backend/app/services/team_wellness_ranking_service.py`
   - `_calculate_team_monthly_rates()`: substituído `Attendance.present == True` por `Attendance.presence_status.in_(['present', 'justified'])` — alinha com campo canônico SSOT (sem booleano legado)
   - `_count_athletes_90plus()`: removido join com `TeamMembership` (LEGADO); substituído por join com `TeamRegistration` (SSOT); `TeamMembership.active == True` → `TeamRegistration.deleted_at == None`; `Athlete.active == True` → `Athlete.deleted_at == None`; `Attendance.present == True` → `Attendance.presence_status.in_(...)`.
   - `get_team_athletes_90plus()`: mesmas substituições de join e condições.
   - Import local `TeamMembership` dentro das funções substituído por `TeamRegistration` do modelo correto.

2. `Hb Track - Backend/app/api/v1/routers/analytics.py`
   - Adicionados schemas Pydantic `WellnessRankingItemResponse`, `Athlete90PlusItemResponse`, `RankingCalculateResponse` (inline no router)
   - `team_id: int` → `team_id: str` em `get_team_athletes_90plus` (SSOT: UUID como string)
   - `response_model` adicionado nos 3 endpoints de wellness-rankings

**Sem DB migration necessária** — mudanças são exclusivamente na camada de service/router.

**Impacto em outros módulos:** Nenhum. Os métodos `_calculate_team_monthly_rates`, `_count_athletes_90plus` e `get_team_athletes_90plus` são privados ou chamados exclusivamente pelo serviço. O endpoint `get_team_athletes_90plus` recebe `team_id` como path param — clientes que passavam int continuam funcionando pois FastAPI aceita string representando UUID.

**Testes afetados:**
- `test_inv_train_027`: já passava (3/3) — não afetado.
- `test_inv_train_036`: runtime DB test (constraint UNIQUE); mudanças no serviço não afetam a constraint.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique_runtime.py','Hb Track - Backend/tests/training/invariants/test_inv_train_027_refresh_training_rankings_task.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_177 exit='+str(r.returncode); print('PASS AR_177')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T20:30:38.752453+00:00
**Behavior Hash**: 3cd0305429580561eaba3b745b7f5ba748da101440d7e731074a8ba6ce2a635d
**Evidence File**: `docs/hbtrack/evidence/AR_177/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T20:47:58.669172+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_177_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_177/executor_main.log`

### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_177_b123a58/result.json`
