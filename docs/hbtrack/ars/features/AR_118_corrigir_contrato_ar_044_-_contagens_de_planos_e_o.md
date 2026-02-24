# AR_118 — Corrigir contrato AR_044 — contagens de planos e orphan check

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar secao Validation Command de AR_044 (drafts). Tres ajustes: (1) remover a assercao 'assert not orphans' (JSONs no diretorio raiz de planos sao validos para planos em elaboracao); (2) count de infra: '==3' deve ser '>=3' (quatro JSONs agora nessa pasta); (3) count de features: '==6' deve ser '>=4' (conta atual e 5). O check de subdiretorios existentes e o count governance >=11 permanecem. Atualizar tambem o carimbo historico Comando.

## Critérios de Aceite
- Secao Validation Command de AR_044 nao contem mais 'assert not orphans'
- Secao Validation Command de AR_044 usa '>=3' para infra e '>=4' para features
- Subdirs governance, competitions, infra, features ainda verificados como existentes
- Executar o novo validation_command retorna exit 0 com PASS na saida
- Status do AR_044 permanece SUCESSO

## Validation Command (Contrato)
```
python temp/validate_ar118.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_118/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/drafts/AR_044_git_mv_docs__canon_planos__→_governance_,_competit.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Causa raiz: novos planos foram criados pelo Arquiteto no root de docs/_canon/planos/ (pratica valida para planos em elaboracao pre-dispatch). Contagens de infra e features mudaram com adicao/remocao de planos. Fix: usar lower bounds (>=) em vez de exato (==), remover assert orphans. AR file path contem seta Unicode e virgula — usa write_scope [].

## Análise de Impacto
**Executor**: Executor HB Track
**Data**: 2026-03-01
**Acoes**: Executado patch no VC de AR_044: removido assert orphans, substituido comparacoes == por >= para counts.
**Impacto**: Baixo — apenas corrige contrato de verificacao do AR legado. Sem alteracao de codigo de produto.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 88fa5b2
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar118.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T19:32:33.890333+00:00
**Behavior Hash**: c9cf9f28caa60fb18bbf443a622f42c0302f796a21e00abc827b2d436532e7bf
**Evidence File**: `docs/hbtrack/evidence/AR_118/executor_main.log`
**Python Version**: 3.11.9

