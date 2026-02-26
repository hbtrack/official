# AR_152 — Tests: Hierarquia de Ciclos — INV-054, 055, 056, 057

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar testes de invariantes para hierarquia de ciclos. Seguir INVARIANTS_TESTING_CANON.md.

Arquivos a criar:
- tests/training/invariants/test_inv_train_054_standalone_session.py
  Classe C2: (1) criar sessão sem microciclo → válida, standalone=TRUE; (2) criar sessão com microciclo, session_at dentro da semana → válida

- tests/training/invariants/test_inv_train_055_meso_overlap.py
  Classe C1/Policy: DOIS mesociclos de equipes diferentes com datas sobrepostas são inseríveis sem erro. Anti-false-positive: provar que o que NÃO é bloqueado (ausência de constraint), não apenas que passa.

- tests/training/invariants/test_inv_train_056_micro_within_meso.py
  Classe C2: (1) micro com datas dentro do meso → válido; (2) micro com week_start antes de meso.start_date → MicrocycleOutsideMesoError; (3) micro com week_end depois de meso.end_date → MicrocycleOutsideMesoError

- tests/training/invariants/test_inv_train_057_session_within_microcycle.py
  Classe C2: (1) session_at dentro da semana do micro → válido; (2) session_at fora da semana → SessionOutsideMicrocycleWeekError

## Critérios de Aceite
Todos os 4 arquivos de teste criados. pytest todos os 4 arquivos PASSAM. INV-055 testa ausência de constraint (não apenas presença de dado).

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_054_standalone_session.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_055_meso_overlap.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_056_micro_within_meso.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_057_session_within_microcycle.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_054_standalone_session.py tests/training/invariants/test_inv_train_055_meso_overlap.py tests/training/invariants/test_inv_train_056_micro_within_meso.py tests/training/invariants/test_inv_train_057_session_within_microcycle.py -v --tb=short 2>&1 | Select-String -Pattern 'passed|failed|error'
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_152/executor_main.log`

## Notas do Arquiteto
Classe C2 (service com DB) para 054, 056, 057. Classe C1/policy para 055. Para INV-055, o teste de 'ausência de constraint' é: inserir 2 mesos de orgs diferentes com datas sobrepostas e verificar que AMBOS existem no DB após commit (anti-false-positive: o teste NÃO deve apenas verificar que um insert passa, mas que DOIS passam).

## Riscos
- Se training_microcycles não tem FK indexado para cycle_id (meso parent), query de containment pode ser lenta em testes

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

