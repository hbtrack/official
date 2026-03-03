# AR_181 — Atualizar exercise.py + criar exercise_media.py (scope/visibility/soft-delete)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar Hb Track - Backend/app/models/exercise.py para refletir campos adicionados pelo schema v0065: scope (String NOT NULL, server_default=ORG), visibility_mode (String NOT NULL, server_default=restricted), deleted_at (DateTime timezone=True nullable), deleted_reason (Text nullable), organization_id deve ser Mapped[Optional[UUID]] (nullable=True para SYSTEM exercises). Criar Hb Track - Backend/app/models/exercise_media.py com: id (PK uuid gen_random_uuid), exercise_id (FK exercises.id CASCADE), media_type (String NOT NULL), url (String 500 NOT NULL), title (String 200 nullable), order_index (SmallInteger NOT NULL default 1), created_by_user_id (FK users.id CASCADE), created_at (DateTime timezone), updated_at (DateTime timezone). Incluir UniqueConstraint uq_exercise_media_exercise_order em (exercise_id, order_index). Proibido: modificar exercise_acl.py (ja existe e correto). Proibido: criar ou modificar scripts de banco.

## Critérios de Aceite
1) exercise.py tem atributos scope, visibility_mode, deleted_at, deleted_reason como colunas SQLAlchemy. 2) organization_id e nullable=True no model. 3) exercise_media.py existe com campos exercise_id, media_type, url. 4) Imports de ambos os modelos funcionam sem erro de importacao. 5) ExerciseMedia tem UniqueConstraint em (exercise_id, order_index).

## Write Scope
- Hb Track - Backend/app/models/exercise.py
- Hb Track - Backend/app/models/exercise_media.py

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','models','exercise.py')).read(); [c.index(f) for f in ['scope','visibility_mode','deleted_at','deleted_reason']]; f2=os.path.join(b,'app','models','exercise_media.py'); c2=open(f2).read(); [c2.index(f) for f in ['exercise_id','media_type','url']]; print('PASS AR_181')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_181/executor_main.log`

## Notas do Arquiteto
exercise_acl.py JA EXISTE — proibido modificar. organization_id deve ser Mapped[Optional[UUID]] (nullable=True). exercise.py ja tem created_by_user_id — apenas adicionar scope, visibility_mode, deleted_at, deleted_reason. Sem migration nova.

## Riscos
- exercise.py usa HB-AUTOGEN:BEGIN/END block — adicionar campos fora do bloco auto-gerado para evitar overwrite acidental
- organization_id era NOT NULL — alterar para Optional pode quebrar code que assume not-null; Executor deve verificar usages

## Análise de Impacto
- **exercise.py (lido)**: HB-AUTOGEN:BEGIN/END L31-L50. organization_id na L41 como Mapped[UUID] nullable=False — alterar para Mapped[Optional[UUID]] nullable=True. Campos scope/visibility_mode/deleted_at/deleted_reason ausentes do model (service ja usa hasattr() para checar). exercise_service.py ja referencia direto: exercise.scope, exercise.visibility_mode, exercise.deleted_at, exercise.deleted_reason — sem hasattr apos AR_181.
- **exercise_acl.py (lido)**: correto, nao tocar. exercise_media.py: nao existe.
- **Mudancas**:
  1. exercise.py: organization_id -> Mapped[Optional[UUID]] nullable=True; ADD scope (String NOT NULL server_default=ORG), visibility_mode (String NOT NULL server_default=restricted), deleted_at (DateTime timezone nullable), deleted_reason (Text nullable) FORA do bloco HB-AUTOGEN
  2. exercise_media.py: CRIAR novo model com id/exercise_id/media_type/url/title/order_index/created_by_user_id/created_at/updated_at + UniqueConstraint(exercise_id, order_index)
- **Sem migration**: schema ja materializado pela migration 0065 (AR_144 REDO)
- **Risco organization_id**: exercise_service.create_exercise ja atribui organization_id=None para SYSTEM scope — nullable=True no model e correto

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; c=open(os.path.join(b,'app','models','exercise.py')).read(); [c.index(f) for f in ['scope','visibility_mode','deleted_at','deleted_reason']]; f2=os.path.join(b,'app','models','exercise_media.py'); c2=open(f2).read(); [c2.index(f) for f in ['exercise_id','media_type','url']]; print('PASS AR_181')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T02:59:10.531357+00:00
**Behavior Hash**: b2eae80e36c30272e1ee81538def7ad422097445e9a60e67f7fa2a24f0ad93ad
**Evidence File**: `docs/hbtrack/evidence/AR_181/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_181_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T03:48:51.161568+00:00
**Motivo**: 182
**TESTADOR_REPORT**: `_reports/testador/AR_181_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_181/executor_main.log`
