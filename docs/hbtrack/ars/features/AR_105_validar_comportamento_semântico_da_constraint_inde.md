# AR_105 — Validar comportamento semântico da constraint/index em PostgreSQL 12

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Testar que o partial unique index (PG < 15) ou UNIQUE NULLS NOT DISTINCT (PG >= 15) impedem múltiplas rows com phase_id=NULL para mesmo competition+opponent. Cenário de teste: (1) Inserir row com competition_id=X, phase_id=NULL, opponent_team_id=Y, (2) Tentar inserir segunda row idêntica (deve FALHAR com constraint violation), (3) Inserir row com competition_id=X, phase_id=123, opponent_team_id=Y (deve PASSAR - phase_id diferente), (4) Cleanup (DELETE rows de teste). NÃO executar em produção (ambiente teste/dev apenas).

## Critérios de Aceite
- Teste insere row com phase_id=NULL e opponent_team_id=UUID
- Tentativa de inserir segunda row idêntica (phase_id=NULL, mesmo competition+opponent) FALHA com constraint violation
- Inserção com phase_id=123 (não NULL) para mesmo competition+opponent PASSA
- Cleanup deleta rows de teste
- Script de teste usa transaction ROLLBACK ou DELETE explícito (não deixa lixo)
- Documentação/comentário explica semântica: 'múltiplos phase_id=NULL para mesmo competition+opponent não permitidos'

## Validation Command (Contrato)
```
python temp/validate_ar105.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_105/executor_main.log`

## Rollback Plan (Contrato)
```
psql -c "TRUNCATE competition_standings RESTART IDENTITY CASCADE"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Rollback via TRUNCATE competition_standings (apenas ambiente test/staging, NUNCA em produção). Teste é idempotente (DELETE ao final do próprio comando). Regeneração de docs/ssot/schema.sql e alembic_state.txt: manual (fora de write_scope permitido).

## Análise de Impacto
**Escopo**: Teste de comportamento da constraint/index da migration 0060

**Impacto**:
- Insere e deleta rows temporárias em competition_standings (ambiente teste/dev)
- Valida que constraint impede múltiplas rows com phase_id=NULL (comportamento esperado)
- Cleanup automático (DELETE após teste)

**Risco**: Baixo (teste idempotente, sem side effects permanentes)

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 15ac28c
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar105.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T16:05:00.943509+00:00
**Behavior Hash**: 2229ce39231542dc3d76c6915cae1b43b4b45e02ffee5518bd94d593624cd540
**Evidence File**: `docs/hbtrack/evidence/AR_105/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 15ac28c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_105_15ac28c/result.json`

### Selo Humano em c9f6f40
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T16:20:52.877818+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_105_15ac28c/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_105/executor_main.log`
