# AR_159 — Service: athlete_content_gate_service.py — Wellness Obrigatória

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Criar novo arquivo Hb Track - Backend/app/services/athlete_content_gate_service.py:

1. INV-076 (policy check): Implementar has_completed_daily_wellness(athlete_id, date) que verifica:
   - wellness_pre submetida para hoje (date)
   - wellness_post submetida para último treino concluído
   Retorna (bool, list_of_missing) para UI poder exibir o que falta.

2. INV-071 (content gate): Implementar check_content_access(athlete_id, resource_type) que:
   - Se athlete NÃO completou wellness diário obrigatório: retorna AccessGated(reason='wellness_missing', allows_minimum=True)
   - 'allows_minimum' = True significa que o atleta pode ver conteúdo mínimo (ex: horário do próximo treino) mas não conteúdo completo
   - Se completou: retorna AccessGranted()

3. INV-078 (progress gate): Implementar check_progress_access(athlete_id) que:
   - Se wellness não está em dia: retorna AccessGated para telas de progresso/relatório
   - Se em dia: retorna AccessGranted

## Critérios de Aceite
1. has_completed_daily_wellness() retorna False quando wellness_pre não submetida hoje. 2. check_content_access() retorna AccessGated com allows_minimum=True quando wellness em falta. 3. check_content_access() retorna AccessGranted quando wellness completa. 4. check_progress_access() retorna AccessGated quando wellness em falta.

## Write Scope
- Hb Track - Backend/app/services/athlete_content_gate_service.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/athlete_content_gate_service.py'); assert f.exists(), 'FAIL: athlete_content_gate_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'gate' in c.lower() or 'wellness' in c.lower() or 'content' in c.lower(), 'FAIL: logica de gate/wellness ausente'; print('PASS AR_159: athlete_content_gate_service.py OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_159/executor_main.log`

## Notas do Arquiteto
Classe C2 (Service com DB). Depende de: wellness_pre e wellness_post tables existirem no schema. Executor DEVE verificar nomes exatos das tabelas wellness no schema.sql antes de implementar queries. Se as tabelas se chamam 'wellness_submissions' ou similar, adaptar.

## Riscos
- Se wellness_pre/post não têm campo de date separado (apenas created_at TIMESTAMP), usar DATE(created_at) = today para query — verificar timezone handling (UTC vs local)
- INV-076: 'último treino concluído' pode ser ambíguo — usar máximo de training_sessions.closed_at onde team_registration_id do atleta coincida

## Análise de Impacto
**Executor:** Criação de `athlete_content_gate_service.py` — service puro (Classe C2).

**Âncoras schema confirmadas:**
- `wellness_pre`: tabela confirmada (linha 3080 schema.sql). Campo de data: `filled_at` (timestamp TZ). Vínculo: `athlete_id` + `training_session_id`.
- `wellness_post`: tabela confirmada (linha 3016 schema.sql). Campo de data: `filled_at`. Vínculo: `athlete_id` + `training_session_id`. Soft-delete via `deleted_at`.
- `training_sessions.closed_at`: define "último treino concluído" (IS NOT NULL = encerrado).

**Estratégia de implementação:**
- `has_completed_daily_wellness(athlete_id, date)`: DATE(filled_at AT TIME ZONE 'UTC') = date via `func.date()` do SQLAlchemy.
- `check_content_access` / `check_progress_access`: delegam para `has_completed_daily_wellness`; retornam dataclasses `AccessGranted` ou `AccessGated`.
- Sem efeitos colaterais. Sem escrita em DB. Seguro para uso concorrente.

**Arquivo criado:**
- `Hb Track - Backend/app/services/athlete_content_gate_service.py`

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 4ccde93
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; f=Path('Hb Track - Backend/app/services/athlete_content_gate_service.py'); assert f.exists(), 'FAIL: athlete_content_gate_service.py nao encontrado'; c=f.read_text(encoding='utf-8'); assert 'gate' in c.lower() or 'wellness' in c.lower() or 'content' in c.lower(), 'FAIL: logica de gate/wellness ausente'; print('PASS AR_159: athlete_content_gate_service.py OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T02:45:52.576883+00:00
**Behavior Hash**: b586f55f6065556e09a84facf8d3b641dda6dd1c7ffad66c2de33470936ca945
**Evidence File**: `docs/hbtrack/evidence/AR_159/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 4ccde93
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_159_4ccde93/result.json`

### Selo Humano em 48e7eed
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T04:39:53.467179+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_159_4ccde93/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_159/executor_main.log`
