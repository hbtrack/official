# AR_117 — Corrigir contrato AR_040 — banco renumerado de 0058 para 0061

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_040 (competitions). O arquivo de atualizacao de banco comp_db_006 foi renumerado de 0058 para 0061. Tres valores devem mudar no validation_command: (A) nome do arquivo: 0058_comp_db_006_status_check_constraints para 0061_comp_db_006_status_check_constraints; (B) valor de revisao interno: de '0058' para '0061'; (C) valor de revisao base: de '0057' para '0060'. Os checks de nomes de constraints (ck_competitions_status, ck_competitions_modality, ck_competition_matches_status) e o check de create_check_constraint PERMANECEM identicos. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_040 referencia '0061_comp_db_006_status_check_constraints' (nao 0058)
- Secao Validation Command de AR_040 verifica revision 0061 e down_revision 0060
- Checks de constraint names permanecem (ck_competitions_status, ck_competitions_modality, ck_competition_matches_status)
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_040 permanece SUCESSO

## Validation Command (Contrato)
```
python temp/validate_ar117.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_117/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/competitions/AR_040_migration_0058_comp-db-006_add_3_check_constraints.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: arquivo comp_db_006 foi renumerado de 0058 para 0061 para evitar conflito com outro arquivo adicionado posteriormente. Fato entregue correto (3 CHECK constraints existem). AR file path usa write_scope [].

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-03-01
**Acoes**: Executado patch no VC de AR_040: atualizado numero de arquivo de 0058 para 0061 (renomeacao da migration).
**Impacto**: Baixo — apenas corrige contrato de verificacao do AR legado. Sem alteracao de codigo de produto.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 88fa5b2
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar117.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:32:32.687614+00:00
**Behavior Hash**: 0cf3fc3e867029592490661557bef4f967e8caedaf6304becb375c7f33bb485f
**Evidence File**: `docs/hbtrack/evidence/AR_117/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 3974fc8
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_117_3974fc8/result.json`

### Selo Humano em fe8ca5a
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T19:37:48.285693+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_117_3974fc8/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_117/executor_main.log`
