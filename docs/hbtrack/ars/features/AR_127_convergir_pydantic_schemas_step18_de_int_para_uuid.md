# AR_127 — Convergir Pydantic schemas Step18 de int para UUID

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar 2 arquivos de schemas Pydantic para usar UUID em vez de int nos campos de ID.

=== ARQUIVO 1: Hb Track - Backend/app/schemas/training_alerts.py ===
Campos afetados:
- AlertCreate.team_id: int -> UUID (remover Field(..., gt=0) se existir, gt nao se aplica a UUID)
- AlertUpdate.dismissed_by_user_id: int -> UUID (remover Field(..., gt=0) se existir)
- Quaisquer outros campos de ID que usem int para entidades UUID
- Adicionar 'from uuid import UUID' nos imports
- Atualizar json_schema_extra/examples com UUIDs validos (formato 550e8400-e29b-41d4-a716-446655440000)

=== ARQUIVO 2: Hb Track - Backend/app/schemas/training_alerts_step18.py ===
Campos afetados:
- SuggestionCreate.team_id: int -> UUID
- SuggestionCreate.origin_session_id: Optional[int] -> Optional[UUID]
- SuggestionCreate.target_session_ids: list[int] -> list[UUID]
- Remover ou adaptar validator validate_target_ids (valida gt=0, nao aplicavel a UUID)
- Atualizar json_schema_extra/examples com UUIDs validos
- Adicionar 'from uuid import UUID' nos imports (se nao existir)

ANCORAS SSOT:
- schema.sql: training_alerts.team_id uuid FK
- schema.sql: training_suggestions.team_id uuid FK, .origin_session_id uuid FK, .target_session_ids uuid[]

## Critérios de Aceite
1) AlertCreate.team_id e AlertUpdate.dismissed_by_user_id sao UUID.
2) SuggestionCreate.team_id, origin_session_id e target_session_ids usam UUID.
3) Nenhum Field(gt=0) aplicado a campos UUID.
4) Validators incompativeis com UUID removidos ou adaptados.
5) Exemplos nos schemas usam UUIDs validos.
6) from uuid import UUID presente em ambos os arquivos.

## Write Scope
- Hb Track - Backend/app/schemas/training_alerts.py
- Hb Track - Backend/app/schemas/training_alerts_step18.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "from app.schemas.training_alerts import AlertCreate, AlertUpdate; from uuid import UUID; a=AlertCreate.model_fields; assert a['team_id'].annotation is UUID or 'UUID' in str(a['team_id'].annotation), 'FAIL: team_id not UUID'; print('PASS: AlertCreate.team_id is UUID')" && python -c "from app.schemas.training_alerts_step18 import SuggestionCreate; from uuid import UUID; f=SuggestionCreate.model_fields; assert 'UUID' in str(f['team_id'].annotation), 'FAIL: team_id'; print('PASS: SuggestionCreate fields UUID')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_127/executor_main.log`

## Notas do Arquiteto
Os schemas Pydantic DEFINEM o contrato da API. Convergir para UUID garante que OpenAPI gerado mostrara format: uuid nos params.

## Riscos
- Validators com gt=0 devem ser removidos — UUID nao suporta comparacao numerica
- json_schema_extra com exemplos int deve ser atualizado para UUIDs validos para manter documentacao correta

## Análise de Impacto
**Executor:** 2026-02-25

**Arquivos modificados:** 2
- `Hb Track - Backend/app/schemas/training_alerts.py`
- `Hb Track - Backend/app/schemas/training_alerts_step18.py`

**training_alerts.py:**
- `AlertCreate.team_id: int` → `UUID`; `Field(gt=0)` removido (gt inaplicável a UUID)
- `AlertUpdate.dismissed_by_user_id: int` → `UUID`; `Field(gt=0)` removido
- `from uuid import UUID` adicionado
- Exemplos atualizados para UUIDs válidos

**training_alerts_step18.py:**
- `SuggestionCreate.team_id: int` → `UUID`; `Field(gt=0)` removido
- `SuggestionCreate.origin_session_id: Optional[int]` → `Optional[UUID]`; `gt=0` removido
- `SuggestionCreate.target_session_ids: list[int]` → `list[UUID]`
- Validator `validate_target_ids` removido (comparação `<= 0` inaplicável a UUID)
- Exemplos atualizados para UUIDs válidos
- `from uuid import UUID` adicionado

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 529b87c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "from app.schemas.training_alerts import AlertCreate, AlertUpdate; from uuid import UUID; a=AlertCreate.model_fields; assert a['team_id'].annotation is UUID or 'UUID' in str(a['team_id'].annotation), 'FAIL: team_id not UUID'; print('PASS: AlertCreate.team_id is UUID')" && python -c "from app.schemas.training_alerts_step18 import SuggestionCreate; from uuid import UUID; f=SuggestionCreate.model_fields; assert 'UUID' in str(f['team_id'].annotation), 'FAIL: team_id'; print('PASS: SuggestionCreate fields UUID')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-25T17:15:04.050956+00:00
**Behavior Hash**: 0f89e4cddcd4d3adb57a2e90fe9ff40369f29865a310a498c74e1e3311f5ee09
**Evidence File**: `docs/hbtrack/evidence/AR_127/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_127_529b87c/result.json`
