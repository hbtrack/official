# AR_160 — Tests: Wellness Obrigatória — INV-071, 076, 078

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar testes de invariantes para o módulo de Wellness Obrigatória. Seguir INVARIANTS_TESTING_CANON.md.

Arquivos a criar:
- tests/training/invariants/test_inv_train_071_content_gate.py
  Classe C1/C2: (1) sem wellness_pre hoje → check_content_access() retorna gate com allows_minimum=True; (2) com wellness_pre hoje → AccessGranted; (3) anti-false-positive: allows_minimum=True não é AccessGranted

- tests/training/invariants/test_inv_train_076_wellness_policy.py
  Classe C2: (1) has_completed_daily_wellness() False quando sem wellness_pre; (2) True quando com wellness_pre + wellness_post do último treino; (3) retorna lista dos campos faltantes

- tests/training/invariants/test_inv_train_078_progress_gate.py
  Classe C1/C2: (1) sem wellness completo → check_progress_access() retorna AccessGated; (2) com wellness → AccessGranted

## Critérios de Aceite
3 arquivos criados. pytest todos PASSAM. Anti-false-positive implementado: em cada teste, verificar que o ESTADO CONTRÁRIO (sem gate) produz resultado diferente.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_071_content_gate.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_076_wellness_policy.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_078_progress_gate.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; b=Path('Hb Track - Backend/tests/training/invariants'); fs=[('test_inv_train_071_content_gate.py','TestInvTrain071'),('test_inv_train_076_wellness_policy.py','TestInvTrain076'),('test_inv_train_078_progress_gate.py','TestInvTrain078')]; missing=[fn for fn,cls in fs if not (b/fn).exists() or cls not in (b/fn).read_text(encoding='utf-8')]; assert not missing, 'FAIL: ausentes/sem classe='+str(missing); [print('[OK] '+fn) for fn,_ in fs]; print('PASS AR_160: 3 arquivos de teste 071/076/078 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_160/executor_main.log`

## Notas do Arquiteto
Classes C1+C2. Testes DEVEM usar fixtures mínimas (apenas usuário + wellness records). Não usar fixtures de sessão se não necessário para simplificar setup.

## Riscos
- wellness_pre/post models podem não ter schema de fixture disponível no conftest — criar inline no teste se necessário

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

