# AR_161 — Tests: Regressão final — todos os 84 invariantes

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Gate final de regressão para confirmar que:
1. Todos os testes de invariantes existentes AINDA PASSAM após as mudanças das tasks 144-160
2. Os novos testes criados nas tasks 148, 152, 158, 160 passam
3. Os testes existentes das tasks 138-143 (plano anterior) continuam passando

Gerar relatório de cobertura:
- Contar: total de arquivos de test_inv_train_*.py
- Mapear: invariante → arquivo de teste (gap onde não há teste)
- Produzir sumário em: docs/_canon/specs/training_invariants_full_coverage_report.md
  Seções: IMPLEMENTADO+teste, PARCIAL+teste, GAP_COBERTO (novo), GAP_PENDENTE (IA Coach), DEPRECATED

## Critérios de Aceite
1. pytest tests/training/invariants/ exit code 0 (todos passam). 2. Nenhum teste que passava antes das tasks 144-160 agora falha (zero regressão). 3. Arquivo docs/_canon/specs/training_invariants_full_coverage_report.md criado com cobertura ≥ 84 invariantes documentados.

## Write Scope
- docs/_canon/specs/training_invariants_full_coverage_report.md

## Validation Command (Contrato)
```
python -c "from pathlib import Path; import glob; r=Path('docs/_canon/specs/training_invariants_full_coverage_report.md'); assert r.exists(), 'FAIL: training_invariants_full_coverage_report.md nao encontrado'; c=r.read_text(encoding='utf-8'); ts=glob.glob('Hb Track - Backend/tests/training/invariants/test_inv_train_*.py'); n=c.count('IMPLEMENTADO')+c.count('GAP_COBERTO'); assert n>=80, 'FAIL: cobertura insuficiente, n='+str(n); print('PASS AR_161: '+str(len(ts))+' testes, '+str(n)+' invariantes documentadas')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_161/executor_main.log`

## Notas do Arquiteto
Gate de qualidade final. NÃO implementa nada de novo — apenas executa e documenta. Se algum teste falhar (regressão), o Executor DEVE identificar qual task causou a regressão, reverter apenas aquela mudança, e reportar para o Arquiteto antes de re-submeter.

## Riscos
- Fixtures de DB podem ter side-effects entre testes se isolamento não for completo — usar rollback por transação ou test database reset
- IA Coach invariants (072-081) aparecerão como GAP_PENDENTE no relatório — isso é ESPERADO e documentado

## Análise de Impacto

**Executor:** Yan (GitHub Copilot — Modo Executor)
**Data:** 2026-02-27

**Inventário de testes existentes:**
- Total de arquivos `test_inv_train_*.py`: 74 arquivos em `Hb Track - Backend/tests/training/invariants/`
- Invariantes documentadas no SSOT: 85 (INV-TRAIN-001..081 + EXB-ACL-001..007; excluindo IDs não existentes 017, 038, 039, 042)

**Mapeamento de cobertura:**
| Categoria | Quantidade |
|---|---|
| IMPLEMENTADO (SSOT) + teste individual | 34 |
| PARCIAL/DIVERGENTE (SSOT) + teste individual | 9 |
| GAP_COBERTO via teste individual | 21 |
| GAP_COBERTO via test_148 (048, 051, 053, 060, 061, 062, EXB-ACL-002..007) | 11 |
| GAP_PENDENTE — IA Coach (072-081, sem teste, esperado) | 10 |
| DEPRECATED | 1 (028) |

**Risco de regressão:** Baixo. Esta AR não modifica código de produção — cria apenas `docs/_canon/specs/training_invariants_full_coverage_report.md` (documentação somente).

**WRITE_SCOPE impactado:** `docs/_canon/specs/training_invariants_full_coverage_report.md` (novo arquivo)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 079a8fd
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; import glob; r=Path('docs/_canon/specs/training_invariants_full_coverage_report.md'); assert r.exists(), 'FAIL: training_invariants_full_coverage_report.md nao encontrado'; c=r.read_text(encoding='utf-8'); ts=glob.glob('Hb Track - Backend/tests/training/invariants/test_inv_train_*.py'); n=c.count('IMPLEMENTADO')+c.count('GAP_COBERTO'); assert n>=80, 'FAIL: cobertura insuficiente, n='+str(n); print('PASS AR_161: '+str(len(ts))+' testes, '+str(n)+' invariantes documentadas')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-27T03:47:01.780807+00:00
**Behavior Hash**: 3fb895ffd835f52d75544cf9804db0e6d6eb1bdc5644b0906db967d445c39c12
**Evidence File**: `docs/hbtrack/evidence/AR_161/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 079a8fd
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_161_079a8fd/result.json`

### Selo Humano em 079a8fd
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-27T03:53:49.337661+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_161_079a8fd/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_161/executor_main.log`
