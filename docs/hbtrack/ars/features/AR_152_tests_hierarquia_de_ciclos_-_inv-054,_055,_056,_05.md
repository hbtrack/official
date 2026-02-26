# AR_152 — Tests: Hierarquia de Ciclos — INV-054, 055, 056, 057

**Status**: ✅ VERIFICADO
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
python -c "from pathlib import Path; b=Path('Hb Track - Backend/tests/training/invariants'); fs=[('test_inv_train_054_standalone_session.py','TestInvTrain054'),('test_inv_train_055_meso_overlap.py','TestInvTrain055'),('test_inv_train_056_micro_within_meso.py','TestInvTrain056'),('test_inv_train_057_session_within_microcycle.py','TestInvTrain057')]; missing=[fn for fn,cls in fs if not (b/fn).exists() or cls not in (b/fn).read_text(encoding='utf-8')]; assert not missing, 'FAIL: ausentes ou sem classe='+str(missing); [print('[OK] '+fn) for fn,_ in fs]; print('PASS AR_152: 4 arquivos de teste OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_152/executor_main.log`

## Notas do Arquiteto
Classe C2 (service com DB) para 054, 056, 057. Classe C1/policy para 055. Para INV-055, o teste de 'ausência de constraint' é: inserir 2 mesos de orgs diferentes com datas sobrepostas e verificar que AMBOS existem no DB após commit (anti-false-positive: o teste NÃO deve apenas verificar que um insert passa, mas que DOIS passam).

## Riscos
- Se training_microcycles não tem FK indexado para cycle_id (meso parent), query de containment pode ser lenta em testes

## Análise de Impacto
- **Arquivos lidos**: training_cycle_service.py (MicrocycleOutsideMesoError L36-41, INV-055 comment L44-46, guard create() L155-162), training_microcycle_service.py (containment guard L143-154 — raises ValidationError genérico), training_session_service.py (standalone=data.microcycle_id is None L220, SessionOutsideMicrocycleWeekError guard L222-240), app/core/exceptions.py (SessionOutsideMicrocycleWeekError L91-95), app/core/context.py (ExecutionContext dataclass), app/schemas/training_sessions.py (TrainingSessionCreate), app/schemas/training_cycles.py (TrainingCycleCreate), app/schemas/training_microcycles.py (TrainingMicrocycleCreate), tests/training/invariants/conftest.py (fixtures), test_inv_train_058_session_structure_mutable.py (padrão de fixtures locais)
- **Mudanças**: Criar 4 arquivos de teste (nenhum arquivo existente modificado)
- **INV-054**: Testado via TrainingSessionService.create() — standalone=data.microcycle_id is None setado no service (L220); testa sessão sem microciclo (standalone=True) e sessão com microciclo (standalone=False)
- **INV-055**: Policy test — inserção direta de 2 training_cycles type=meso de orgs/teams diferentes com datas sobrepostas via ORM; verifica que AMBOS existem no DB após flush (ausência de constraint de non-overlap)
- **INV-056**: Testado via TrainingCycleService.create() com type=meso — guarda em create() (L155-162) levanta MicrocycleOutsideMesoError quando datas do meso extrapolam o macro pai; MicrocycleOutsideMesoError importado de training_cycle_service.py
- **INV-057**: Testado via TrainingSessionService.create() — guarda em create() (L222-240) levanta SessionOutsideMicrocycleWeekError quando session_at.date() não está em [microcycle.week_start, microcycle.week_end]
- **Risco residual**: Nenhum — apenas criação de arquivos de teste; nenhuma alteração em arquivos de produção

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em eb88236
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "from pathlib import Path; b=Path('Hb Track - Backend/tests/training/invariants'); fs=[('test_inv_train_054_standalone_session.py','TestInvTrain054'),('test_inv_train_055_meso_overlap.py','TestInvTrain055'),('test_inv_train_056_micro_within_meso.py','TestInvTrain056'),('test_inv_train_057_session_within_microcycle.py','TestInvTrain057')]; missing=[fn for fn,cls in fs if not (b/fn).exists() or cls not in (b/fn).read_text(encoding='utf-8')]; assert not missing, 'FAIL: ausentes ou sem classe='+str(missing); [print('[OK] '+fn) for fn,_ in fs]; print('PASS AR_152: 4 arquivos de teste OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-26T16:47:22.640839+00:00
**Behavior Hash**: 7c9c341fe86b7648fd98267ab77c2bee87bebd62b4b6e55ab7c5dd46509b52d5
**Evidence File**: `docs/hbtrack/evidence/AR_152/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em eb88236
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_152_eb88236/result.json`

### Selo Humano em eb88236
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-26T18:52:59.467548+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_152_eb88236/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_152/executor_main.log`
