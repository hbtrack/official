# AR_158 — Tests: Attendance Avançada — INV-063 a 070

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
Criar testes de invariantes para fluxo de attendance avançada. Seguir INVARIANTS_TESTING_CANON.md.

Arquivos a criar:
- tests/training/invariants/test_inv_train_063_preconfirm.py (C2: preconfirm status válido antes de sessão iniciar)
- tests/training/invariants/test_inv_train_064_close_consolidation.py (C2: consolidação ao fechar)
- tests/training/invariants/test_inv_train_065_close_pending_guard.py (C2: guard de fechamento com pending)
- tests/training/invariants/test_inv_train_066_pending_items.py (A+C2: schema pending_items + service CRUD)
- tests/training/invariants/test_inv_train_067_athlete_pending_rbac.py (D: RBAC atleta edita próprio)
- tests/training/invariants/test_inv_train_068_athlete_sees_training.py (D: RBAC atleta lê sessão scheduled)
- tests/training/invariants/test_inv_train_069_exercise_media_via_session.py (D: atleta acessa media via sessão)
- tests/training/invariants/test_inv_train_070_post_conversational.py (C2/Policy: fluxo conversacional)

## Critérios de Aceite
Todos os 8 arquivos criados. pytest todos os 8 PASSAM. Para INV-067/068/069 (classe D): testes usam client (401 sem auth) e auth_client com role atleta/treinador para verificar RBAC.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_063_preconfirm.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_064_close_consolidation.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_065_close_pending_guard.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_066_pending_items.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_067_athlete_pending_rbac.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_068_athlete_sees_training.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_069_exercise_media_via_session.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_070_post_conversational.py

## Validation Command (Contrato)
```
python -c "from pathlib import Path; b=Path('Hb Track - Backend/tests/training/invariants'); fs=[('test_inv_train_063_preconfirm.py','TestInvTrain063'),('test_inv_train_064_close_consolidation.py','TestInvTrain064'),('test_inv_train_065_close_pending_guard.py','TestInvTrain065'),('test_inv_train_066_pending_items.py','TestInvTrain066'),('test_inv_train_067_athlete_pending_rbac.py','TestInvTrain067'),('test_inv_train_068_athlete_sees_training.py','TestInvTrain068'),('test_inv_train_069_exercise_media_via_session.py','TestInvTrain069'),('test_inv_train_070_post_conversational.py','TestInvTrain070')]; missing=[fn for fn,cls in fs if not (b/fn).exists() or cls not in (b/fn).read_text(encoding='utf-8')]; assert not missing, 'FAIL: ausentes/sem classe='+str(missing); print('PASS AR_158: 8 arquivos de teste 063-070 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_158/executor_main.log`

## Notas do Arquiteto
Classes A+C2+D. Para testes Classe D (067, 068, 069): requerer fixtures auth_client_atleta e auth_client_treinador no conftest. Verificar se existem antes de criar.

## Riscos
- Se conftest.py de tests/training/ não tem fixture de auth_client por role (atleta/treinador), precisará ser criada ou adaptada

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

