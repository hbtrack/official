# AR_002 — Simple Command Test

**Status**: DRAFT
**Versão do Protocolo**: 1.0.4

## Descrição
Test task with simple command that works cross-platform without complex shell escaping

## Critérios de Aceite
Command must execute successfully and evidence file must be created

## Validation Command (Contrato)
```
python -c "import sys; sys.exit(0)"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_002_simple_test.log`

## Notas do Arquiteto
Using simple exit code for testing

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

