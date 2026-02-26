# AR_143 — Atualizar TEST_MATRIX com status atualizado

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar o TEST_MATRIX_TRAINING.md com o status atualizado de todas as 84 invariantes após execução deste plano. Incluir: invariantes com teste passando (COVERED), invariantes com teste corrigido (FIXED), invariantes com teste novo (NEW), invariantes PENDING (feature ausente), invariantes DEPRECATED. Incluir coluna de tier (0-3) e coluna de dependência (extends/depends_on).

## Critérios de Aceite
Relatório de cobertura gerado em docs/_canon/specs/ com todas as 84 invariantes, status de teste, tier, e dependências. Formato tabular legível. Mínimo 80 linhas referenciando invariantes.

## Write Scope
- docs/_canon/specs/training_invariants_coverage_report.md

## Validation Command (Contrato)
```
python -c "f=open('docs/_canon/specs/training_invariants_coverage_report.md','r'); c=f.read(); f.close(); lines=[l for l in c.split('\n') if 'INV-TRAIN' in l or 'EXB-ACL' in l]; print(f'Invariants in report: {len(lines)}'); assert len(lines)>=80, f'Expected >=80 invariants, got {len(lines)}'"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_143/executor_main.log`

## Notas do Arquiteto
Relatório de cobertura em docs/_canon/specs/ (governed). O Arquiteto usará este relatório para atualizar TEST_MATRIX_TRAINING.md posteriormente. 35 invariantes GAP devem aparecer como PENDING com nota 'feature not implemented'. Formato sugerido: | ID | Nome | Classe | Tier | Status Teste | Depende de | Notas |

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

