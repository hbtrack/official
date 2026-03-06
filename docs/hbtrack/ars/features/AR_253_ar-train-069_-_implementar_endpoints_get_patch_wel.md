# AR_253 — AR-TRAIN-069 — Implementar endpoints GET/PATCH wellness-pre e wellness-post por ID (fix stubs 501)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar os 4 endpoints BE que retornam 501 Not Implemented. Sem mudancas de schema DB. Apenas service layer + router.

## ZONA 1 — WellnessPreService: adicionar get_wellness_pre_by_id e update_wellness_pre_by_id

Arquivo: Hb Track - Backend/app/services/wellness_pre_service.py

Adicionar dois metodos ao final da classe WellnessPreService:

### Metodo get_wellness_pre_by_id(self, wellness_id: UUID, user_id: UUID, user_role: str) -> WellnessPre
- SELECT WellnessPre WHERE id=wellness_id AND deleted_at IS NULL
- Se nao encontrado: raise NotFoundError
- Se user_role == 'athlete': verificar que athlete_id do registro == await self._get_athlete_id_from_user(user_id), senao raise PermissionDeniedError
- Se user_role in ['coach', 'coordinator']: buscar training_session do registro, verificar team_id in await self._get_user_team_ids(user_id), senao raise PermissionDeniedError
- Retornar wellness

### Metodo update_wellness_pre_by_id(self, wellness_id: UUID, data: dict, user_id: UUID, user_role: str) -> WellnessPre
- SELECT WellnessPre WHERE id=wellness_id AND deleted_at IS NULL
- Se nao encontrado: raise NotFoundError
- Verificar permissoes identicas a get_wellness_pre_by_id (R25/R26)
- Se wellness.locked_at IS NOT NULL: raise ValidationError('Wellness bloqueado para edicao.')
- Verificar janela de edicao: deadline = wellness.created_at + timedelta(hours=24). Se datetime.now(timezone.utc) >= deadline: raise ValidationError('Fora da janela de edicao (24h apos criacao)')
- Filtrar data: apenas campos de WellnessPreUpdate (sleep_hours, sleep_quality, fatigue_pre/fatigue, stress_level/stress, muscle_soreness, notes). Aplicar normalizacao: se 'fatigue' in data e 'fatigue_pre' not in data: data['fatigue_pre'] = data.pop('fatigue'). Se 'stress' in data e 'stress_level' not in data: data['stress_level'] = data.pop('stress').
- Aplicar campos com setattr, excluir Nones
- wellness.updated_at = datetime.now(timezone.utc)
- await self.db.flush()
- Retornar wellness

## ZONA 2 — WellnessPostService: adicionar get_wellness_post_by_id e update_wellness_post_by_id

Arquivo: Hb Track - Backend/app/services/wellness_post_service.py

Adicionar dois metodos ao final da classe WellnessPostService:

### Metodo get_wellness_post_by_id(self, wellness_id: UUID, user_id: UUID, user_role: str) -> WellnessPost
- Mesmo padrao do WellnessPreService.get_wellness_pre_by_id porem para WellnessPost
- SELECT WellnessPost WHERE id=wellness_id AND deleted_at IS NULL
- Permissoes R25/R26 identicas
- Retornar wellness

### Metodo update_wellness_post_by_id(self, wellness_id: UUID, data: dict, user_id: UUID, user_role: str) -> WellnessPost
- SELECT WellnessPost WHERE id=wellness_id AND deleted_at IS NULL
- Se nao encontrado: raise NotFoundError
- Verificar permissoes R25/R26
- Se wellness.locked_at IS NOT NULL: raise ValidationError('Wellness bloqueado para edicao.')
- Verificar janela: reutilizar await self._check_edit_window(wellness). Se fora: raise ValidationError('Fora da janela de edicao (24h apos criacao)')
- Filtrar data para campos permitidos (session_rpe, minutes_effective, internal_load, fatigue_after, mood_after, muscle_soreness_after, perceived_intensity, notes, flag_medical_followup, conversational_feedback, conversation_completed). Excluir Nones.
- Aplicar campos com setattr
- wellness.updated_at = datetime.now(timezone.utc)
- await self.db.flush()
- Chamar await self._invalidate_training_analytics_cache(training_session) e await self._trigger_overload_alert_on_wellness_post(training_session) — buscar training_session pela wellness.training_session_id antes
- Retornar wellness

## ZONA 3 — Router wellness_pre.py: implementar get_wellness_pre_by_id e update_wellness_pre

Arquivo: Hb Track - Backend/app/api/v1/routers/wellness_pre.py

Substituir as duas funcoes stub:

### get_wellness_pre_by_id (linha ~235)
- Converter de `def` para `async def`
- Adicionar parametro `current_user = Depends(get_current_user)` apos wellness_pre_id
- Implementar body:
  - Determinar user_role (mesmo padrao do list_wellness_pre_by_session)
  - service = WellnessPreService(db)
  - wellness = await service.get_wellness_pre_by_id(wellness_id=wellness_pre_id, user_id=_ctx_get(current_user, 'user_id'), user_role=user_role)
  - return wellness
  - Excecoes: NotFoundError→404, PermissionDeniedError→403, Exception→500

### update_wellness_pre (linha ~269)
- Converter de `def` para `async def`
- Adicionar parametro `current_user = Depends(get_current_user)` apos payload
- Implementar body:
  - Determinar user_role
  - service = WellnessPreService(db)
  - wellness = await service.update_wellness_pre_by_id(wellness_id=wellness_pre_id, data=payload.dict(exclude_none=True), user_id=_ctx_get(current_user, 'user_id'), user_role=user_role)
  - await db.commit()
  - return wellness
  - Excecoes: NotFoundError→404, PermissionDeniedError→403, ValidationError→409, Exception→500 com db.rollback()

## ZONA 4 — Router wellness_post.py: implementar get_wellness_post_by_id e update_wellness_post

Arquivo: Hb Track - Backend/app/api/v1/routers/wellness_post.py

Substituir as duas funcoes stub:

### get_wellness_post_by_id (linha ~231) — JA eh async def, apenas implementar
- Adicionar parametro `current_user = Depends(get_current_user)` apos wellness_post_id
- Implementar body:
  - Determinar user_role (mesmo padrao)
  - service = WellnessPostService(db)
  - wellness = await service.get_wellness_post_by_id(wellness_id=wellness_post_id, user_id=_ctx_get(current_user, 'user_id'), user_role=user_role)
  - return wellness
  - Excecoes: NotFoundError→404, PermissionDeniedError→403, Exception→500

### update_wellness_post (linha ~265)
- Converter de `def` para `async def`
- Adicionar parametro `current_user = Depends(get_current_user)` apos payload
- Implementar body:
  - Determinar user_role
  - service = WellnessPostService(db)
  - wellness = await service.update_wellness_post_by_id(wellness_id=wellness_post_id, data=payload.dict(exclude_none=True), user_id=_ctx_get(current_user, 'user_id'), user_role=user_role)
  - await db.commit()
  - return wellness
  - Excecoes: NotFoundError→404, PermissionDeniedError→403, ValidationError→409, Exception→500 com db.rollback()

## ZONA 5 — Sync documental

- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md: marcar AR-TRAIN-069 como VERIFICADO
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md: adicionar entry para AR-TRAIN-069 (contratos 031/032/037/038)
- docs/hbtrack/Hb Track Kanban.md: mover AR_253 para coluna VERIFICADO

## Critérios de Aceite
AC1: async def get_wellness_pre_by_id presente em wellness_pre.py (era def sync, bug corrigido).
AC2: async def update_wellness_pre presente em wellness_pre.py (era def sync, bug corrigido).
AC3: async def get_wellness_post_by_id presente em wellness_post.py (ja era async, implementado).
AC4: async def update_wellness_post presente em wellness_post.py (era def sync, bug corrigido).
AC5: metodo get_wellness_pre_by_id presente em wellness_pre_service.py.
AC6: metodo get_wellness_post_by_id presente em wellness_post_service.py.
AC7: metodo update_wellness_pre_by_id presente em wellness_pre_service.py.
AC8: metodo update_wellness_post_by_id presente em wellness_post_service.py.

## Write Scope
- Hb Track - Backend/app/services/wellness_pre_service.py
- Hb Track - Backend/app/services/wellness_post_service.py
- Hb Track - Backend/app/api/v1/routers/wellness_pre.py
- Hb Track - Backend/app/api/v1/routers/wellness_post.py
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md
- docs/hbtrack/Hb Track Kanban.md

## Validation Command (Contrato)
```
python -c "
import sys
c = {
  'pre_r': open('Hb Track - Backend/app/api/v1/routers/wellness_pre.py').read(),
  'post_r': open('Hb Track - Backend/app/api/v1/routers/wellness_post.py').read(),
  'pre_s': open('Hb Track - Backend/app/services/wellness_pre_service.py').read(),
  'post_s': open('Hb Track - Backend/app/services/wellness_post_service.py').read(),
}
checks = [
  ('async def get_wellness_pre_by_id' in c['pre_r'], 'AC1: async def get_wellness_pre_by_id in pre router'),
  ('async def update_wellness_pre' in c['pre_r'], 'AC2: async def update_wellness_pre in pre router'),
  ('async def get_wellness_post_by_id' in c['post_r'], 'AC3: async def get_wellness_post_by_id in post router'),
  ('async def update_wellness_post' in c['post_r'], 'AC4: async def update_wellness_post in post router'),
  ('get_wellness_pre_by_id' in c['pre_s'], 'AC5: get_wellness_pre_by_id in pre service'),
  ('get_wellness_post_by_id' in c['post_s'], 'AC6: get_wellness_post_by_id in post service'),
  ('update_wellness_pre_by_id' in c['pre_s'], 'AC7: update_wellness_pre_by_id in pre service'),
  ('update_wellness_post_by_id' in c['post_s'], 'AC8: update_wellness_post_by_id in post service'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS')
"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_253/executor_main.log`

## Análise de Impacto

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `Hb Track - Backend/app/services/wellness_pre_service.py` | Zona 1: adiciona `get_wellness_pre_by_id` e `update_wellness_pre_by_id` no final da classe WellnessPreService |
| `Hb Track - Backend/app/services/wellness_post_service.py` | Zona 2: adiciona `get_wellness_post_by_id` e `update_wellness_post_by_id` no final da classe WellnessPostService |
| `Hb Track - Backend/app/api/v1/routers/wellness_pre.py` | Zona 3: substitui `def get_wellness_pre_by_id` (sync, sem current_user, 501) por `async def` + Depends(get_current_user) + implementação real; idem para `def update_wellness_pre` |
| `Hb Track - Backend/app/api/v1/routers/wellness_post.py` | Zona 4: `async def get_wellness_post_by_id` já era async — adiciona current_user + implementação real; substitui `def update_wellness_post` (sync, 501) por `async def` + implementação real |
| `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md` | Zona 5: adiciona AR-TRAIN-069 na tabela e seção de detalhe |
| `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` | Zona 5: adiciona entry §9 AR-TRAIN-069 |
| `docs/hbtrack/Hb Track Kanban.md` | Zona 5: adiciona card Batch 31 com AR_253 |

### Impacto funcional
Mínimo e controlado — apenas remove stubs 501 e implementa a lógica planejada. Sem mudança de schema DB, sem nova migration, sem alteração de openapi.json. Os 4 endpoints passam de 501 para funcionais. Comportamento idêntico ao `list` existente para permissões R25/R26.

### Invariantes avaliadas
- INV-TRAIN-022 (cache_invalidation): impactada por `update_wellness_post_by_id` — chama `_invalidate_training_analytics_cache` e `_trigger_overload_alert_on_wellness_post` idêntico ao submit.
- INV-TRAIN-003 (wellness_post_deadline): janela de edição de 24h implementada via `_check_edit_window` existente no service.
- INV-TRAIN-002 (wellness_pre_deadline): janela de edição de 24h implementada inline (PRE usa janela de criação separada da de edição).
- DEC-TRAIN-001: GET/PATCH por ID não recebem athlete_id no payload. athlete_id inferido do registro existente no banco.

### ACs a satisfazer
- AC1: `async def get_wellness_pre_by_id` em wellness_pre.py (era `def` sync com 501)
- AC2: `async def update_wellness_pre` em wellness_pre.py (era `def` sync com 501)
- AC3: `async def get_wellness_post_by_id` em wellness_post.py (já era async, adicionar current_user + implementar)
- AC4: `async def update_wellness_post` em wellness_post.py (era `def` sync com 501)
- AC5: método `get_wellness_pre_by_id` em wellness_pre_service.py
- AC6: método `get_wellness_post_by_id` em wellness_post_service.py
- AC7: método `update_wellness_pre_by_id` em wellness_pre_service.py
- AC8: método `update_wellness_post_by_id` em wellness_post_service.py

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
c = {
  'pre_r': open('Hb Track - Backend/app/api/v1/routers/wellness_pre.py').read(),
  'post_r': open('Hb Track - Backend/app/api/v1/routers/wellness_post.py').read(),
  'pre_s': open('Hb Track - Backend/app/services/wellness_pre_service.py').read(),
  'post_s': open('Hb Track - Backend/app/services/wellness_post_service.py').read(),
}
checks = [
  ('async def get_wellness_pre_by_id' in c['pre_r'], 'AC1: async def get_wellness_pre_by_id in pre router'),
  ('async def update_wellness_pre' in c['pre_r'], 'AC2: async def update_wellness_pre in pre router'),
  ('async def get_wellness_post_by_id' in c['post_r'], 'AC3: async def get_wellness_post_by_id in post router'),
  ('async def update_wellness_post' in c['post_r'], 'AC4: async def update_wellness_post in post router'),
  ('get_wellness_pre_by_id' in c['pre_s'], 'AC5: get_wellness_pre_by_id in pre service'),
  ('get_wellness_post_by_id' in c['post_s'], 'AC6: get_wellness_post_by_id in post service'),
  ('update_wellness_pre_by_id' in c['pre_s'], 'AC7: update_wellness_pre_by_id in pre service'),
  ('update_wellness_post_by_id' in c['post_s'], 'AC8: update_wellness_post_by_id in post service'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS')
"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T10:34:04.657143+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_253/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
c = {
  'pre_r': open('Hb Track - Backend/app/api/v1/routers/wellness_pre.py').read(),
  'post_r': open('Hb Track - Backend/app/api/v1/routers/wellness_post.py').read(),
  'pre_s': open('Hb Track - Backend/app/services/wellness_pre_service.py').read(),
  'post_s': open('Hb Track - Backend/app/services/wellness_post_service.py').read(),
}
checks = [
  ('async def get_wellness_pre_by_id' in c['pre_r'], 'AC1: async def get_wellness_pre_by_id in pre router'),
  ('async def update_wellness_pre' in c['pre_r'], 'AC2: async def update_wellness_pre in pre router'),
  ('async def get_wellness_post_by_id' in c['post_r'], 'AC3: async def get_wellness_post_by_id in post router'),
  ('async def update_wellness_post' in c['post_r'], 'AC4: async def update_wellness_post in post router'),
  ('get_wellness_pre_by_id' in c['pre_s'], 'AC5: get_wellness_pre_by_id in pre service'),
  ('get_wellness_post_by_id' in c['post_s'], 'AC6: get_wellness_post_by_id in post service'),
  ('update_wellness_pre_by_id' in c['pre_s'], 'AC7: update_wellness_pre_by_id in pre service'),
  ('update_wellness_post_by_id' in c['post_s'], 'AC8: update_wellness_post_by_id in post service'),
]
bad = [msg for ok, msg in checks if not ok]
if bad: print('FAIL:', bad); sys.exit(1)
print('AC1..AC8 PASS')
"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T10:35:19.279821+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_253/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_253_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-06T10:47:32.484399+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_253_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_253/executor_main.log`
