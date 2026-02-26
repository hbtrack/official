# AR_157 — Service: wellness_post — campo conversacional (INV-070)

**Status**: 🔲 PENDENTE
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
- schema.sql (2 alterações: +conversational_feedback TEXT, +conversation_completed BOOLEAN)
- alembic_state.txt (head: 0067 → 0068)

## Validation Command (Contrato)
```bash
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

