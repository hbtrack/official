# AR_144 — DB: Exercise Bank — schema foundation

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Migração Alembic para adicionar colunas e tabelas do Exercise Bank:

1. ALTER TABLE exercises:
   - ADD COLUMN scope VARCHAR(10) NOT NULL DEFAULT 'ORG' CONSTRAINT ck_exercises_scope CHECK (scope IN ('SYSTEM','ORG'))
   - ADD COLUMN visibility_mode VARCHAR(20) NOT NULL DEFAULT 'restricted' CONSTRAINT ck_exercises_visibility_mode CHECK (visibility_mode IN ('org_wide','restricted'))
   - ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE
   - ADD COLUMN deleted_reason TEXT
   - ADD CONSTRAINT ck_exercises_deleted_reason CHECK ((deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL))
   - ADD CONSTRAINT ck_exercises_org_scope CHECK ((scope='SYSTEM' AND organization_id IS NULL) OR (scope='ORG' AND organization_id IS NOT NULL))
   - ALTER COLUMN organization_id DROP NOT NULL (necessário para exercises SYSTEM)

2. Renomear uq de exercise_favorites SE não existe named constraint:
   - Verificar se PK (user_id, exercise_id) já satisfaz unicidade — se sim, apenas adicionar CONSTRAINT uq_exercise_favorites_user_exercise UNIQUE (user_id, exercise_id) como alias explícito OU documentar que PK supre INV-050

3. CREATE TABLE exercise_media (
   id UUID DEFAULT gen_random_uuid() NOT NULL,
   exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
   media_type VARCHAR(20) NOT NULL CONSTRAINT ck_exercise_media_type CHECK (media_type IN ('video','image','gif','document')),
   url VARCHAR(500) NOT NULL,
   title VARCHAR(200),
   order_index SMALLINT NOT NULL DEFAULT 1,
   created_by_user_id UUID NOT NULL,
   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
   PRIMARY KEY (id),
   CONSTRAINT uq_exercise_media_exercise_order UNIQUE (exercise_id, order_index)
)

4. CREATE TABLE exercise_acl (
   id UUID DEFAULT gen_random_uuid() NOT NULL,
   exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
   granted_by_user_id UUID NOT NULL REFERENCES users(id),
   granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
   PRIMARY KEY (id),
   CONSTRAINT uq_exercise_acl_exercise_user UNIQUE (exercise_id, user_id)
)

5. Gerar migração Alembic: alembic revision --autogenerate -m 'exercise_bank_schema_foundation'
6. Atualizar docs/ssot/schema.sql e docs/ssot/alembic_state.txt via gen_docs_ssot.py

## Critérios de Aceite
1. exercises table tem colunas scope, visibility_mode, deleted_at, deleted_reason, ck_exercises_scope, ck_exercises_visibility_mode, ck_exercises_org_scope, ck_exercises_deleted_reason. 2. exercises.organization_id aceita NULL. 3. exercise_media table existe com uq_exercise_media_exercise_order. 4. exercise_acl table existe com uq_exercise_acl_exercise_user. 5. Alembic upgrade head roda sem erro. 6. docs/ssot/schema.sql reflete todas as mudanças.

## Write Scope
- Hb Track - Backend/alembic/versions/

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python temp/ar144_validate.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_144/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py alembic -- downgrade -1
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Classe A (DB Constraint). organization_id DROP NOT NULL é a mudança mais arriscada — verificar se há código que assume NOT NULL antes de executar. DEFAULT 'ORG' para scope garante backward compat de todos os exercises existentes. DEFAULT 'restricted' para visibility_mode idem. NOTA: exercise_favorites PK (user_id, exercise_id) já é unique — se não houver named constraint, adicionar UNIQUE alternativa apenas como âncora semântica para testes.

## Riscos
- ALTER COLUMN organization_id DROP NOT NULL pode falhar se há constraints dependentes que assumem NOT NULL
- Dados existentes em exercises têm organization_id preenchido — DEFAULT 'ORG' para scope e nullable org_id é retro-compatível
- Se exercise_favorites PK já supre INV-050, adicionar UNIQUE duplicado pode causar erro — verificar antes e documentar

## Análise de Impacto

**Tipo**: DB Schema — Migration Alembic
**Risco**: Médio — altera tabela existente (exercises), cria 2 novas tabelas
**Arquivos afetados**:
- CREATE: `Hb Track - Backend/db/alembic/versions/0065_exercise_bank_schema_foundation.py`

**Mudanças em exercises table**:
- ADD COLUMN scope VARCHAR(10) NOT NULL DEFAULT 'ORG' + CHECK IN ('SYSTEM','ORG')
- ADD COLUMN visibility_mode VARCHAR(20) NOT NULL DEFAULT 'restricted' + CHECK IN ('org_wide','restricted')
- ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE (nullable)
- ADD COLUMN deleted_reason TEXT (nullable)
- ADD CHECK ck_exercises_deleted_reason (ambos ou nenhum)
- ADD CHECK ck_exercises_org_scope (SYSTEM→NULL org_id, ORG→NOT NULL org_id)
- ALTER COLUMN organization_id DROP NOT NULL

**Novas tabelas**:
- exercise_media (id, exercise_id, media_type, url, title, order_index, created_by, timestamps)
- exercise_acl (id, exercise_id, user_id, granted_by, granted_at)

**Backward compat**: DEFAULT 'ORG' e DEFAULT 'restricted' garantem que exercises existentes continuam válidos

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 017cc0c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar144_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T13:03:46.981360+00:00
**Behavior Hash**: d119f2257051979433e551a55a79ee9feee889c4c770724a953a224d6225cc85
**Evidence File**: `docs/hbtrack/evidence/AR_144/executor_main.log`
**Python Version**: 3.11.9

