# AR_161 — Tests: Regressão final — todos os 84 invariantes

**Status**: 🔲 PENDENTE
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
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/ -v --tb=short -q 2>&1 | Select-String -Pattern 'passed|failed|error|warning'; Get-Content "../docs/_canon/specs/training_invariants_full_coverage_report.md" | Select-String -Pattern 'GAP_COBERTO|IMPLEMENTADO' | Measure-Object | Select-Object Count
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_161/executor_main.log`

## Notas do Arquiteto
Gate de qualidade final. NÃO implementa nada de novo — apenas executa e documenta. Se algum teste falhar (regressão), o Executor DEVE identificar qual task causou a regressão, reverter apenas aquela mudança, e reportar para o Arquiteto antes de re-submeter.

## Riscos
- Fixtures de DB podem ter side-effects entre testes se isolamento não for completo — usar rollback por transação ou test database reset
- IA Coach invariants (072-081) aparecerão como GAP_PENDENTE no relatório — isso é ESPERADO e documentado

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

