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
- Hb Track - Backend/app/services/wellness_post_service.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_070_post_conversational.py -v --tb=short 2>&1 | Select-String -Pattern 'PASSED|FAILED|ERROR'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_157/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
git checkout -- "Hb Track - Backend/docs/ssot/alembic_state.txt"
python scripts/run/hb_cli.py alembic -- downgrade -1
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Classe C2 (ou A se schema change). PENDÊNCIA CONDICIONAL: se wellness_post table não tem suporte estrutural para multi-step, a task pode virar DB-touch (adicionar ssot_touches). Executor DEVE resolver antes de implementar. Se schema change necessária, atualizar ssot_touches no plano.

## Riscos
- INV-070 pode ser puramente de UI/UX (frontend conversational flow) sem mudança de backend — verificar INVARIANTS_TRAINING.md
- Se wellness_post service não existe como arquivo separado, localizar onde wellness_post é processado antes de editar

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

