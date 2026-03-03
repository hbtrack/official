# AR_176 — Fix wellness BE: self-only (athlete_id do JWT) + payload minimo + LGPD log staff

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir wellness_pre_service.py e wellness_post_service.py para operar em modelo self-only e payload minimo, com logging LGPD para acesso staff.

=== ANCORA SSOT ===
- INV-TRAIN-002: POST wellness pre DEVE falhar se fora do prazo da sessao
- INV-TRAIN-003: POST wellness post DEVE falhar se fora do prazo
- INV-TRAIN-026: Acesso de staff a wellness de outro atleta DEVE gerar data_access_logs
- DEC-TRAIN-001 RESOLVIDA: atleta NAO envia athlete_id; backend infere de current_user.id
- schema.sql: wellness_pre.athlete_id UUID FK -> athletes.id

=== PASSO 0 — FIX OBRIGATORIO NO ARQUIVO DE TESTE (antes de qualquer service) ===
Bug em test_inv_train_026_lgpd_access_logging.py: 6 ocorrencias de
  Path(__file__).parent.parent.parent / "app"
devem ser trocadas por:
  Path(__file__).parent.parent.parent.parent / "app"
Motivo: o arquivo esta em tests/training/invariants/ (3 niveis abaixo de tests/),
enao em tests/ (2 niveis). Sem este fix, todas as asserções falham com
FileNotFoundError em tests/app/services/ (inexistente).

=== LEITURA PREVIA (READ-ONLY) ===
1. Ler wellness_pre_service.py (assinatura de create_wellness_pre, get_my_wellness_pre)
2. Ler wellness_post_service.py (idem para post)
3. Ler router wellness_pre (verificar como athlete_id e passado hoje)
4. Checar se data_access_logs table existe no schema.sql

=== CORRECOES OBRIGATORIAS ===
1. create_wellness_pre(session_id, data, current_user):
   - NAO aceitar athlete_id como parametro do payload do atleta
   - Inferir athlete_id internamente: buscar athletes.id WHERE user_id = current_user.id
   - Payload minimo: nao exigir organization_id nem created_by_membership_id do chamador
   - Backend preenche organization_id a partir do contexto do atleta autenticado

2. create_wellness_post: mesma correcao de self-only

3. get_wellness_pre_for_staff(athlete_id, session_id, requester_user):
   - Se requester nao eh o proprio atleta: INSERT em data_access_logs
   - Campos minimos do log: user_id (requester), resource_type='wellness_pre', resource_id, accessed_at

4. get_wellness_post_for_staff: mesma logica de logging LGPD

=== ARQUIVOS A MODIFICAR ===
- Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py (fix path bug)
- Hb Track - Backend/app/services/wellness_pre_service.py
- Hb Track - Backend/app/services/wellness_post_service.py

## Critérios de Aceite
1) create_wellness_pre/post nao aceita athlete_id de fora: apenas current_user para inferir.
2) Payload minimo: atleta pode submeter wellness sem organization_id ou created_by_membership_id.
3) Staff lendo wellness de outro atleta gera registro em data_access_logs.
4) test_inv_train_026 PASSA (LGPD access logging funcional).
5) test_inv_train_002 PASSA (deadline wellness pre respeitado).
6) test_inv_train_003 PASSA (deadline wellness post respeitado).

## Write Scope
- Hb Track - Backend/app/services/wellness_pre_service.py
- Hb Track - Backend/app/services/wellness_post_service.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py

## Validation Command (Contrato)
```
python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py','Hb Track - Backend/tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py','Hb Track - Backend/tests/training/invariants/test_inv_train_003_wellness_post_deadline.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_176 exit='+str(r.returncode); print('PASS AR_176')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_176/executor_main.log`

## Notas do Arquiteto
ANCORA: INV-TRAIN-026 LGPD access logging. ANCORA: DEC-TRAIN-001 (self-only). ANCORA: schema wellness_pre.athlete_id UUID FK. Dependencia AR-TRAIN-003 DONE (AR_169-170 VERIFICADO 2026-02-28). Se data_access_logs nao existir no schema, escalar para Arquiteto antes de implementar. BUG CONHECIDO em test_inv_train_026_lgpd_access_logging.py: todas as 6 ocorrencias de Path(__file__).parent.parent.parent devem ser trocadas por Path(__file__).parent.parent.parent.parent (o arquivo esta em tests/training/invariants/, portanto 3x parent chega em tests/ e 4x parent chega no backend root onde app/ existe). Executor DEVE aplicar esse fix no arquivo de teste ANTES de implementar os services.

## Riscos
- Se router tiver athlete_id como path param obrigatorio, o router tambem deve ser ajustado — Executor deve verificar antes
- data_access_logs table deve existir no schema; se nao existir, o Executor deve reportar BLOCKED e escalar para Arquiteto (migracao fora do escopo desta AR)
- Mudanca de self-only pode quebrar endpoints de staff que legitimamente passavam athlete_id explicitamente — Executor deve separar rota atleta vs rota staff se necessario
- INV-TRAIN-002/003 (deadline) podem ja estar implementados; Executor nao deve regredir comportamento existente ao refatorar self-only

## Análise de Impacto
**Data**: 2026-02-28  
**Executor run**: ARQUITETO-AR175-AR176-FIX-VALIDATION-COMMAND-20260228 (re-execução)

**Causa da re-execução**: `validation_command` anterior usava `python -m pytest -q ... 2>&1`, propagando timings do pytest para stdout → `behavior_hash` não-determinístico (FLAKY_OUTPUT). REJEITADO pelo Testador em b123a58.

**Implementação verificada (staged antes desta execução)**:
- `Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py`: 7 ocorrências de `.parent×3` → `.parent×4` (path depth fix — arquivo em tests/training/invariants/, não em tests/).
- `Hb Track - Backend/app/services/wellness_pre_service.py` e `wellness_post_service.py`: self-only (athlete_id do JWT), payload mínimo, LGPD data_access_logs para staff.

**Arquivos fora do write_scope**: nenhum alterado.

**Dependências**: AR-TRAIN-003 (AR_169-170) VERIFICADO. data_access_logs tabela confirmada no schema.sql.

**Regressão**: zero — INV-TRAIN-002/003 (deadline) mantidos; apenas self-only + LGPD log adicionados.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py','Hb Track - Backend/tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py','Hb Track - Backend/tests/training/invariants/test_inv_train_003_wellness_post_deadline.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_176 exit='+str(r.returncode); print('PASS AR_176')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T19:32:24.550354+00:00
**Behavior Hash**: 386b5d5092ca75638b0610b0775c316537a51a7190140b90f5a4abe0a487050c
**Evidence File**: `docs/hbtrack/evidence/AR_176/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py','Hb Track - Backend/tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py','Hb Track - Backend/tests/training/invariants/test_inv_train_003_wellness_post_deadline.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_176 exit='+str(r.returncode); print('PASS AR_176')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T19:39:54.775784+00:00
**Behavior Hash**: 386b5d5092ca75638b0610b0775c316537a51a7190140b90f5a4abe0a487050c
**Evidence File**: `docs/hbtrack/evidence/AR_176/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import subprocess; r=subprocess.run(['pytest','Hb Track - Backend/tests/training/invariants/test_inv_train_026_lgpd_access_logging.py','Hb Track - Backend/tests/training/invariants/test_inv_train_002_wellness_pre_deadline.py','Hb Track - Backend/tests/training/invariants/test_inv_train_003_wellness_post_deadline.py','-q'],capture_output=True); assert r.returncode==0,'FAIL AR_176 exit='+str(r.returncode); print('PASS AR_176')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T19:42:21.878810+00:00
**Behavior Hash**: 386b5d5092ca75638b0610b0775c316537a51a7190140b90f5a4abe0a487050c
**Evidence File**: `docs/hbtrack/evidence/AR_176/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_176_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T19:48:08.571718+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_176_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_176/executor_main.log`
