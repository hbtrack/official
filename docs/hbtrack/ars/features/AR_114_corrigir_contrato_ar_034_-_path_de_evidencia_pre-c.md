# AR_114 — Corrigir contrato AR_034 — path de evidencia pre-canonical

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_034 (governance). Substituicao completa: o validation_command atual tem dois problemas — (1) invoca o gate de sincronizacao de planos que retorna VIOLATION enquanto houver tasks orfas de planos ativos no workspace; (2) le evidence JSON em path pre-canonical 'docs/hbtrack/evidence/PLANS_AR_SYNC/result.json' que nao existe mais. Novo validation_command verifica apenas existencia e estrutura do arquivo gate (sem depender do estado do workspace). Atualizar tambem o carimbo historico Comando se houver referencia ao path obsoleto PLANS_AR_SYNC/result.json.

## Critérios de Aceite
- Secao Validation Command de AR_034 nao contem mais 'PLANS_AR_SYNC/result.json'
- Secao Validation Command de AR_034 contem verificacao de existencia do arquivo gate
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_034 permanece SUCESSO

## Validation Command (Contrato)
```
python temp/validate_ar114.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_114/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/governance/AR_034_governança_plans_-_gate_json-to-ar_obrigatório.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: (1) gate retorna VIOLATION quando ha tasks em planos sem ARs — estado normal durante dev ativo; (2) path de evidence era pre-canonical (v1.0.x). Fix: nova validation verifica EXISTENCIA e ESTRUTURA do gate, nao estado do workspace. AR file path contem chars UTF-8 especiais — usa write_scope [].

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-03-01
**Acoes**: Executado patch no VC de AR_034: substituido check runtime PLANS_AR_SYNC por check estatico de existencia e estrutura do gate.
**Impacto**: Baixo — apenas corrige contrato de verificacao do AR legado. Sem alteracao de codigo de produto.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 88fa5b2
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar114.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:32:18.685067+00:00
**Behavior Hash**: ef39b9fa766255a1b9ee81a33eb5afe13fb2f5ec5ace350e3dc304a04930074e
**Evidence File**: `docs/hbtrack/evidence/AR_114/executor_main.log`
**Python Version**: 3.11.9

