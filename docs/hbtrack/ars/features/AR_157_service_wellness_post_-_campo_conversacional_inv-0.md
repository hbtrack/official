# AR_157 — Service: wellness_post — campo conversacional (INV-070)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar fluxo conversacional pós-treino (INV-070):

1. Verificar schema atual de wellness_post: buscar na schema.sql pela tabela wellness_post (ou wellness_submissions) e verificar se há campo conversacional ou multi-step.

2. Se wellness_post NÃO tem suporte conversacional: adicionar campo conversation_completed BOOLEAN DEFAULT FALSE à tabela wellness_post (ou equivalente), com migration Alembic. Caso já exista lógica suficiente, apenas garantir que o service suporta envio em múltiplos passos.

3. O fluxo conversacional significa: atleta pode submeter wellness_post em partes (ex: primeiro RPE, depois comentário). O service deve aceitar partial submissions com conversation_completed=FALSE e final submission com conversation_completed=TRUE.

4. NOTA CRÍTICA: Antes de implementar, o Executor DEVE verificar se INV-070 está documentado no INVARIANTS_TRAINING.md com uma descrição clara do fluxo. Se a regra for ambígua ou não tiver âncora no schema, marcar como PENDING e reportar ao Arquiteto.

## Critérios de Aceite
1. wellness_post aceita submissão em etapas com conversation_completed=FALSE. 2. Submissão final seta conversation_completed=TRUE. 3. Relatório de atleta não considera wellness_post completa até conversation_completed=TRUE. OU, se INV-070 é policy sem schema change: documentar e criar teste de policy.

## Write Scope
- Hb Track - Backend/alembic/versions/0068_wellness_post_conversational.py (nova migration)
- Hb Track - Backend/app/services/wellness_post_service.py
- Hb Track - Backend/docs/ssot/schema.sql (SSOT derivado)
- Hb Track - Backend/docs/ssot/alembic_state.txt (SSOT derivado)

## SSOT Touches
- [x] docs/ssot/schema.sql (2 alterações: +conversational_feedback TEXT, +conversation_completed BOOLEAN)
- [x] docs/ssot/alembic_state.txt (head: 0067 → 0068)

## Validation Command (Contrato)
```
python -c "import re; schema_path='Hb Track - Backend/docs/ssot/schema.sql'; schema=open(schema_path,encoding='utf-8').read(); wellness_table=re.search(r'CREATE TABLE public\.wellness_post.*?(?=CREATE TABLE|ALTER TABLE|\Z)',schema,re.DOTALL); assert wellness_table,'FAIL: wellness_post table not found'; table_def=wellness_table.group(); assert 'conversational_feedback' in table_def,'FAIL: conversational_feedback column missing'; assert 'conversation_completed' in table_def,'FAIL: conversation_completed column missing'; alembic=open('Hb Track - Backend/docs/ssot/alembic_state.txt').read(); assert '0068' in alembic,'FAIL: migration 0068 not applied'; print('PASS AR_157: wellness_post schema conversacional OK (migration 0068)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_157/executor_main.log`

## Rollback Plan (Contrato)
```bash
# Rollback database migration
cd "Hb Track - Backend" && alembic downgrade -1
# Restore SSOT files
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
# Remove migration file if not committed
git clean -fd "Hb Track - Backend/alembic/versions/0068_*.py"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
**Classe A (DB Constraint/Schema Change)** — confirmado após análise.

**DECISÃO AR_157 (2026-02-26):**

Schema change definido:
```sql
-- Migration 0068_wellness_post_conversational.py
ALTER TABLE wellness_post 
  ADD COLUMN conversational_feedback TEXT,
  ADD COLUMN conversation_completed BOOLEAN DEFAULT FALSE;
```

**Rationale:**
- `conversational_feedback`: armazena input conversacional (texto/voz transcrito)
- `conversation_completed`: controle de fluxo (permite submissões parciais)
- Preserva campo `notes` existente (semântica tradicional não afetada)
- Permite coexistência: formulário tradicional + conversacional

**Service layer:**
- `wellness_post_service.py` deve aceitar `conversational_feedback` opcional
- Se `conversation_completed=FALSE`, registro é considerado parcial
- Atleta pode submeter em múltiplas etapas até `conversation_completed=TRUE`

**Implementação mínima (MVP):**
1. Migration adiciona 2 colunas (nullable)
2. Service aceita campos opcionais no create/update
3. Nenhuma validação complexa inicialmente (evolução futura: INV-071+)

## Riscos
- INV-070 pode ser puramente de UI/UX (frontend conversational flow) sem mudança de backend — verificar INVARIANTS_TRAINING.md
- Se wellness_post service não existe como arquivo separado, localizar onde wellness_post é processado antes de editar

## Análise de Impacto

### Arquivos Modificados
| Arquivo | Tipo | Mudança | Rationale |
|---|---|---|---|
| `db/alembic/versions/0068_wellness_post_conversational.py` | Migration | Criado (ALTER TABLE + 2 colunas) | Adiciona suporte schema para input conversacional |
| `app/services/wellness_post_service.py` | Service | +2 campos em allowed_fields | Permite create/update com conversational_feedback e conversation_completed |
| `docs/ssot/schema.sql` | SSOT (derivado) | +2 colunas em wellness_post | Auto-regenerado após migration |
| `docs/ssot/alembic_state.txt` | SSOT (derivado) | head 0067 → 0068 | Auto-regenerado após migration |

### Schema Changes (Migration 0068)
```sql
-- wellness_post table
ALTER TABLE wellness_post 
  ADD COLUMN conversational_feedback TEXT,            -- nullable, sem default
  ADD COLUMN conversation_completed BOOLEAN NOT NULL DEFAULT FALSE;
```

### Service Layer Changes
**wellness_post_service.py** (`submit_wellness_post`):
- `allowed_fields` agora aceita `conversational_feedback` e `conversation_completed`
- Nenhuma validação complexa no MVP (campos opcionais)
- Fluxo: Frontend pode submeter `conversation_completed=FALSE` para submissões parciais
- Submissão final com `conversation_completed=TRUE` marca wellness como completo

### Backward Compatibility
✅ **SEM BREAKING CHANGES**:
- Campos nullable/default → requests existentes continuam funcionando- Campo `notes` preservado (semântica tradicional)
- Frontend pode ignorar novos campos até implementar conversational UX

### Dependencies
- **DB Migration**: Requer PostgreSQL 12+ (server_default='false' suportado)
- **Model Auto-regen**: Execução de `gen_docs_ssot.py` regenera model com HB-AUTOGEN
- **Tests**: INV-070 (se existir test) precisa ser atualizado para validar novos campos

### Performance Impact
- Migration: < 1s (ALTER TABLE em wellness_post vazio ou com poucos registros)
- Query Impact: Nenhum (campos não indexados; filtros não afetados)
- Service: +2 fields no payload → impacto negligível

### Rollback Risk
- **BAIXO**: Migration downgrade() remove colunas sem dependências
- **Data Loss**: Se conversational_feedback foi preenchido, downgrade perde dados
- **Mitigação**: Testar migration em ambiente dev antes de prod

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 219da28
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar157_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T21:18:28.189665+00:00
**Behavior Hash**: 6abe66eaf6012de4559011f80e03d235070225de19d08c23a528ca8c89cc4dca
**Evidence File**: `docs/hbtrack/evidence/AR_157/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 219da28
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/ar157_validate.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T00:10:49.729441+00:00
**Behavior Hash**: 6abe66eaf6012de4559011f80e03d235070225de19d08c23a528ca8c89cc4dca
**Evidence File**: `docs/hbtrack/evidence/AR_157/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 219da28
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import re; schema_path='Hb Track - Backend/docs/ssot/schema.sql'; schema=open(schema_path,encoding='utf-8').read(); wellness_table=re.search(r'CREATE TABLE public\.wellness_post.*?(?=CREATE TABLE|ALTER TABLE|\Z)',schema,re.DOTALL); assert wellness_table,'FAIL: wellness_post table not found'; table_def=wellness_table.group(); assert 'conversational_feedback' in table_def,'FAIL: conversational_feedback column missing'; assert 'conversation_completed' in table_def,'FAIL: conversation_completed column missing'; alembic=open('Hb Track - Backend/docs/ssot/alembic_state.txt').read(); assert '0068' in alembic,'FAIL: migration 0068 not applied'; print('PASS AR_157: wellness_post schema conversacional OK (migration 0068)')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T00:36:20.440572+00:00
**Behavior Hash**: 6abe66eaf6012de4559011f80e03d235070225de19d08c23a528ca8c89cc4dca
**Evidence File**: `docs/hbtrack/evidence/AR_157/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 219da28
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_157_219da28/result.json`

### Selo Humano em 219da28
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T01:33:23.538847+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_157_219da28/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_157/executor_main.log`
