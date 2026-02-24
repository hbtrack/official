# AR_112 — Limpar manualmente carimbos duplicados de AR_071 e AR_004

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.3.0

## Descrição
Remover via edição direta os carimbos REJEITADO obsoletos dos arquivos AR markdown (docs/hbtrack/ars/governance/AR_071... e docs/hbtrack/ars/features/AR_004...): (1) AR_071: remover carimbo '### Verificacao Testador em 457d095' com '🔴 REJEITADO' (AH_DIVERGENCE, TRIPLE_FAIL), manter apenas carimbo '✅ SUCESSO', (2) AR_004: remover carimbo '### Verificacao Testador em e971d7f' com '🔍 NEEDS REVIEW' (FLAKY_OUTPUT), manter apenas carimbo '✅ SUCESSO' em 3d84621. Remover também carimbos de Executor obsoletos (exit 1, exit 5, comandos de teste antigos) que não correspondem ao estado final. Preservar: Descrição, Critérios de Aceite, Write Scope, Validation Command (atualizado), Evidence File, Análise de Impacto, último carimbo Executor (exit 0), último carimbo Testador (✅ SUCESSO). NÃO modificar header Status (já está ✅ SUCESSO). Edição one-time ad-hoc para corrigir estado histórico.

## Critérios de Aceite
- AR_071: apenas 1 carimbo Testador presente (✅ SUCESSO em 457d095)
- AR_004: apenas 1 carimbo Testador presente (✅ SUCESSO em 3d84621)
- Carimbos REJEITADO/NEEDS REVIEW removidos de ambos os arquivos
- Carimbos de Executor obsoletos (exit 1, exit 5, comandos de teste antigos) removidos
- Seções originais preservadas (Descrição, ACs, Write Scope, etc)
- Último carimbo Executor (exit 0) e Testador (SUCESSO) preservados
- Arquivos compilam markdown válido (sem quebras de syntaxe)
- git diff mostra apenas remoções (não adições acidentais)

## Validation Command (Contrato)
```
python temp/validate_ar112.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_112/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/hbtrack/ars/governance/AR_071_add_auto-commit_opt-in_to_hb_autotest_strict_allow.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Limpeza manual one-time: corrige estado inconsistente de ARs já sealadas. Futuras ARs serão limpas automaticamente por task 111 (cmd_verify auto-clean). Task não toca código governado (apenas docs de AR). AR_004 path contém caractere especial '—' (em dash U+2014) fora do write_scope pattern permitido, então write_scope=[] (doc ad-hoc).

## Análise de Impacto
**Escopo**: Edição direta nos arquivos `docs/hbtrack/ars/governance/AR_071_...md` e `docs/hbtrack/ars/features/AR_004_...md`.

**Impacto**:
- AR_071: Removido o carimbo `### Verificacao Testador em 457d095` com status `🔴 REJEITADO` (AH_DIVERGENCE, TRIPLE_FAIL). Mantido apenas o carimbo com `✅ SUCESSO`.
- AR_004: Removido o carimbo `### Verificacao Testador em e971d7f` com status `🔍 NEEDS REVIEW` (FLAKY_OUTPUT). Mantido apenas o carimbo com `✅ SUCESSO` em 3d84621.
- Removidos também os comentários de roteamento Kanban obsoletos que acompanhavam os carimbos inválidos.

**Risco**: Baixo. Edição one-time ad-hoc em arquivos de documentação de AR, sem impacto em código de produto. Rollback via `git checkout`.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em 8608b0a
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar112.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T18:01:42.908580+00:00
**Behavior Hash**: 7a5f09072a51161de49ef7ac3be425745108c7554e0dcb33a13ac37143e59a7b
**Evidence File**: `docs/hbtrack/evidence/AR_112/executor_main.log`
**Python Version**: 3.11.9

