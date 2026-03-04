# AR_229 — Sync app layer: modelos (INV-010/035/036/054/060) + serviços (contrato v1.3.0) + stubs IA Coach

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Sincronização deterministíca em 3 zonas — app/models/, app/services/, stubs IA:

## ZONA 1 — Modelos (app/models/)

### athlete.py
- Verificar que campos `athlete_name` (str, NOT NULL) e `birth_date` (date) estão presentes conforme TRAINING_CLOSSARY.yaml.
- Se `athlete_name` mapeado como outro nome (ex: `name` ou campo da tabela `person`), alinhar ao vocabulário do Glossário sem renomear coluna DB — usar `column_property` ou `property` se necessário.

### exercise.py
- Garantir `visibility_mode` com `server_default='restricted'` (INV-TRAIN-060).
- server_default deve ser 'restricted', não 'public'.

### training_session.py
- Adicionar UniqueConstraint para INV-TRAIN-010 (uniqueness de wellness_post por sessão+atleta, se o campo existir no modelo ou referenciado via FK).
- Verificar integridade com INV-TRAIN-010 antes de adicionar constraint.

### attendance.py
- Verificar ForeignKey para athlete_id (INV-TRAIN-036: attendance deve ter FK para athlete, não apenas field solto).
- Se FK já existe, confirmar OnDelete behavior (CASCADE ou RESTRICT conforme invariante).

### training_cycle.py
- Verificar ForeignKey hierarchy (INV-TRAIN-054: macro→meso→micro). Garantir que `parent_cycle_id` FK aponta para a própria tabela `training_cycles`.
- Se já existe, confirmar que nullable=True para o nível macro.

## ZONA 2 — Serviços (app/services/)

### exercise_service.py
- Localizar método `update_exercise` e ajustar assinatura para aceitar `(self, exercise_id: UUID, data: dict, organization_id: UUID)` conforme CONTRACT-TRAIN-091..095.
- Se o método já aceita esses parâmetros com nomes diferentes, alinhar sem quebrar callers internos.
- Aplicar `visibility_mode=restricted` como default em criação de exercícios SYSTEM e ORG.

### attendance_service.py
- Para GAP-CONTRACT-7 (presença): adicionar stub mínimo para closure de presença se método ausente.
- Stub deve retornar estrutura mínima esperada pelo contrato (dict ou Pydantic model stub).

## ZONA 3 — Stubs IA Coach (app/services/ai_coach_service.py)
- Adicionar ao módulo as 3 classes exportáveis:
  ```python
  from dataclasses import dataclass

  @dataclass
  class RecognitionApproved:
      athlete_id: str
      message: str = ""

  @dataclass
  class CoachSuggestionDraft:
      suggestion_id: str
      justification: str = ""
      approved: bool = False

  @dataclass
  class JustifiedSuggestion:
      suggestion_id: str
      justification: str
      approved_by: str = ""
  ```
- Estas classes são stubs mínimos importáveis — não implementar lógica de negócio real.

## ZONA 4 — OpenAPI (docs/ssot/openapi.json)
- Se assinatura de `PATCH /exercises/{exercise_id}` mudou com o ajuste do exercise_service, atualizar o requestBody schema correspondente.
- Se não houve mudança breaking, não alterar.

## PROCESSO SUGERIDO
1. Ler cada arquivo antes de editar — verificar estado atual
2. Zonas 1 e 3 são independentes — podem ser feitas em sequência
3. Zona 2 (exercise_service.py): verificar `list_code_usages` de `update_exercise` antes de alterar assinatura
4. Ao final: rodar validation_command
5. Se surgir necessidade de arquivo fora do write_scope → BLOCKED (reportar ao Arquiteto)

## Critérios de Aceite
AC-001: app/models/athlete.py contém campos athlete_name (str) e birth_date (date) alinhados ao Glossário canônico.
AC-002: app/models/exercise.py declara visibility_mode com server_default='restricted' (INV-TRAIN-060).
AC-003: app/services/exercise_service.py → método update_exercise aceita (self, exercise_id, data: dict, organization_id) ou assinatura equivalente compatível com CONTRACT-TRAIN-091..095.
AC-004: app/services/ai_coach_service.py exporta RecognitionApproved, CoachSuggestionDraft, JustifiedSuggestion (importáveis sem erro).
AC-005: pytest tests/training/invariants/ nos arquivos test_inv_train_079*.py / 080*.py / 081*.py = 0 ERRORs de coleta.
AC-006: pytest tests/training/ -q --tb=no sem aumento de FAILs/ERRORs vs baseline pré-AR (suite não pode piorar).

## Write Scope
- Hb Track - Backend/app/models/athlete.py
- Hb Track - Backend/app/models/exercise.py
- Hb Track - Backend/app/models/training_session.py
- Hb Track - Backend/app/models/attendance.py
- Hb Track - Backend/app/models/training_cycle.py
- Hb Track - Backend/app/services/exercise_service.py
- Hb Track - Backend/app/services/ai_coach_service.py
- Hb Track - Backend/app/services/attendance_service.py
- Hb Track - Backend/docs/ssot/openapi.json

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_079_individual_recognition_no_intimate_leak.py tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py -q --tb=short 2>&1 && python -m pytest tests/training/ -q --tb=no 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_229/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch19_sync_app_layer_048.json --dry-run
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- Modelos alterados podem exigir alembic revision --autogenerate se novas Column/UniqueConstraint forem adicionadas. Executor DEVE verificar antes do hb report.
- update_exercise pode ter outros callers (routers, testes de contrato) — verificar usages antes de alterar assinatura.
- ai_coach_service.py pode ter imports circulares se já importa de modelos — verificar estrutura do arquivo antes de adicionar dataclasses.
- visibility_mode server_default='restricted' é DDL-level — se já existente com default diferente, pode exigir migração para dados existentes.
- attendance_service.py stub para GAP-CONTRACT-7: se método já existe com assinatura diferente, ajustar sem criar duplicata.

## Análise de Impacto

**Data:** 2026-03-03  
**Executor:** Copilot Executor  

### Diagnóstico (leitura dos 9 arquivos pré-edição)

| Arquivo | Estado | Ação |
|---|---|---|
| `app/models/athlete.py` | `athlete_name` (str) e `birth_date` (date) presentes | Nenhuma — AC-001 já satisfeito |
| `app/models/exercise.py` | `visibility_mode` com `server_default='restricted'` presente | Nenhuma — AC-002 já satisfeito |
| `app/models/training_session.py` | **`standalone` ausente** (causa dos 8 FAILs do AR_228) | Adicionar `standalone: Mapped[bool]` antes de `# HB-AUTOGEN:END` |
| `app/models/attendance.py` | FK `athlete_id → athletes.id` com `ondelete='RESTRICT'` presente | Nenhuma — correto |
| `app/models/training_cycle.py` | `parent_cycle_id FK → training_cycles.id, nullable=True` presente | Nenhuma — correto |
| `app/services/exercise_service.py` | `update_exercise(self, exercise_id, data: dict, organization_id=None)` presente | Nenhuma — AC-003 já satisfeito |
| `app/services/ai_coach_service.py` | `RecognitionApproved`, `CoachSuggestionDraft`, `JustifiedSuggestion` **ausentes** | Adicionar 3 dataclasses no final do arquivo |
| `app/services/attendance_service.py` | `close_session_attendance` presente | Nenhuma — correto |
| `docs/ssot/openapi.json` | `update_exercise` não mudou | Nenhuma |

### Impacto dos patches
1. **`training_session.py`** — adição de coluna `standalone boolean DEFAULT true NOT NULL` (já existe no DB per schema.sql:2833). Sem migração extra necessária. Resolve os 8 FAILs do AR_228.
2. **`ai_coach_service.py`** — adição de 3 dataclasses mínimas após o bloco final de constantes. Sem risco de circular import (dataclasses não importam do domínio).  
3. Nenhuma alteração de rota/OpenAPI necessária.  
4. Invariante `UniqueConstraint INV-TRAIN-010`: `wellness_post` não é campo do modelo (apenas relationship), sem FK na tabela — constraint não aplicável nesta AR.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_079_individual_recognition_no_intimate_leak.py tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py -q --tb=short 2>&1 && python -m pytest tests/training/ -q --tb=no 2>&1`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-03T23:34:34.811489+00:00
**Behavior Hash**: eaae936401d0815621b34055dc2defbafc4a7db63408aac274716823e5199314
**Evidence File**: `docs/hbtrack/evidence/AR_229/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_079_individual_recognition_no_intimate_leak.py tests/training/invariants/test_inv_train_080_ai_coach_draft_only.py tests/training/invariants/test_inv_train_081_ai_suggestion_requires_justification.py -q --tb=short 2>&1 && python -m pytest tests/training/ -q --tb=no 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T00:34:13.658069+00:00
**Behavior Hash**: 822d43694f137ae38aeacb49a696f76362f5a7d80572072257b180468dc0e631
**Evidence File**: `docs/hbtrack/evidence/AR_229/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_229_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T01:14:16.121152+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_229_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_229/executor_main.log`
