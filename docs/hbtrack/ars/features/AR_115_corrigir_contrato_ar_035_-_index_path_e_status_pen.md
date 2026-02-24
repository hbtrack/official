# AR_115 — Corrigir contrato AR_035 — INDEX path e status PENDENTE valido

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_035 (governance). Dois fixes: (1) path de indice desatualizado: 'docs/hbtrack/ars/_INDEX.md' deve ser 'docs/hbtrack/_INDEX.md' (sem subpath ars/); (2) remover a assercao que proibia o status PENDENTE no sentinela — PENDENTE passou a ser status valido no vocabulary v1.3.0. O check de integracao HBLock e os demais EXECUTOR_TRIGGERS e TESTER_TRIGGERS permanecem. Atualizar tambem subchecks na secao Analise de Impacto que referenciem o path antigo e o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_035 nao contem mais 'docs/hbtrack/ars/_INDEX.md' (old path)
- Secao Validation Command de AR_035 contem 'docs/hbtrack/_INDEX.md' (new path)
- Secao Validation Command de AR_035 nao contem assert sobre PENDENTE not in content
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_035 permanece SUCESSO

## Validation Command (Contrato)
```
python temp/validate_ar115.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_115/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/governance/AR_035_criar_scripts_run_hb_watch.py_-_sentinela_de_estad.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: (1) sentinela refatorado para mover _INDEX.md de docs/hbtrack/ars/ para docs/hbtrack/; (2) PENDENTE adicionado como status valido no vocabulary v1.3.0. AR file path tem caractere especial — usa write_scope [].

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-03-01
**Acoes**: Executado patch no VC de AR_035: corrigido INDEX_PATH de docs/hbtrack/ars/_INDEX.md para docs/hbtrack/_INDEX.md. Removido assert PENDENTE ausente.
**Impacto**: Baixo — apenas corrige contrato de verificacao do AR legado. Sem alteracao de codigo de produto.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 88fa5b2
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar115.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:32:24.573783+00:00
**Behavior Hash**: 4ab827461c6b56183efa8ba405b2fa16903a2c0fb12a20ee691b2566f32329b1
**Evidence File**: `docs/hbtrack/evidence/AR_115/executor_main.log`
**Python Version**: 3.11.9

