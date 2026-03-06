# AR_248 — AR_248 | AR-TRAIN-064 | Fix user.organization_id not a column (unblock xfail INV-148)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
PLANO_FINAL.md Fase 2.2 + Fase 3. Bucket B (Contrato/Endpoint) — o servico acessa user.organization_id que nao existe como coluna no modelo User. Correto enforcement point: app/services/exercise_acl_service.py (metodo _validate_same_org). O fix deve adicionar organizacao do usuario via org_membership (relacao ORM real) em vez de atributo direto inexistente. Procedimento (Fase 3): (1) Reproduzir isolado: reset + pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py. (2) Identificar enforcement point: exercise_acl_service.py metodo _validate_same_org. (3) Corrigir o produto (nunca o teste): substituir acesso a user.organization_id por query ou relacao ORM real de org_membership. (4) Reexecutar isolado ate PASS. (5) Reexecutar TRUTH SUITE completa. DoD: test_inv_train_148 converte de xfail para PASS na TRUTH SUITE. Dependencia: AR_247 concluido (triage confirmado). SSOT: INVARIANTS_TRAINING.md (INV-EXB-ACL-002..007), exercise_acl_service.py.

## Critérios de Aceite
AC-001: pytest test_inv_train_148_exercise_bank_services.py retorna PASS (sem xfail marker ativo). AC-002: TRUTH SUITE completa retorna 0 xfailed para este arquivo. AC-003: Nenhum mock/MagicMock introduzido no codigo de producao ou de teste. AC-004: rg RH-09a retorna 0 matches em tests/training/invariants/test_inv_train_148*. AC-005: openapi.json nao foi modificado (fix e apenas de service layer).

## Write Scope
- Hb Track - Backend/app/services/exercise_acl_service.py

## Validation Command (Contrato)
```
python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v 2>&1 | python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"
```

**REPLAN-3 (2026-03-05)**: dois fixes Windows aplicados:
- P1 (UnicodeEncodeError): prefixo `$env:PYTHONUTF8='1'` — reset_hb_track_test.py linha 84 imprime U+2192 (`->`) que falha em cp1252.
- P2 (`tail` nao existe no Windows): substituido por `python -c` inline que filtra as ultimas 30 linhas mostrando apenas resultados de teste.

**REPLAN-4 (2026-03-05)**: fix cmd.exe compat:
- P3 (shell=True → cmd.exe): `hb_cli.py` usa `subprocess.run(shell=True)` que invoca `cmd.exe /c`, NAO PowerShell. `$env:PYTHONUTF8='1';` e `;` como separador sao sintaxe PowerShell-only — exit=255 no cmd.exe.
- Fix P3: substituido `$env:PYTHONUTF8='1';` por `set PYTHONUTF8=1 &&` e todos os `;` separadores por `&&`.

**REPLAN-5 (2026-03-05)**: fix definitivo Unicode:
- P4 (espaço à direita antes do &&): `set PYTHONUTF8=1 &&` define o valor como `"1 "` (com espaço trailing) — Python retorna "Fatal Python error: environment variable PYTHONUTF8 must be '1' or '0'" com exit=1.
- Fix P4: substituido `set PYTHONUTF8=1 && python scripts/db/reset_hb_track_test.py` por `python -X utf8 scripts/db/reset_hb_track_test.py` — flag direta `-X utf8`, sem variável de ambiente, funciona em cmd.exe e PowerShell.

PROOF: tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v
TRACE: test_inv_train_148_exercise_bank_services.py:336 (xfail marker INV-EXB-ACL-003)

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_248/executor_main.log`

## Notas do Arquiteto
Classe: B (Regra de Dominio/Service). Fase: PLANO_FINAL Fase 2.2 + 3. Enforcement point: exercise_acl_service.py metodo _validate_same_org. O modelo User nao tem coluna organization_id — o servico deve recuperar org do usuario via ORM (org_membership ou similar). NAO alterar o teste para contornar — corrigir o service. Apos fix, o xfail marker no teste deve ser removido ou o teste deve converter para PASS organicamente.

## Riscos
- Fix pode afetar outros metodos do exercise_acl_service que tambem acessam organization_id — verificar todos os usos.
- Mudanca no service pode quebrar outros testes que dependem de _validate_same_org — rodar TRUTH SUITE completa apos fix.
- Nao usar MagicMock ou monkeypatch no service — apenas ORM real.

## Análise de Impacto
**Classe**: B — fix de service layer (produto). Nenhum arquivo de teste alterado.

**Write scope restrito a**: `Hb Track - Backend/app/services/exercise_acl_service.py`

**Causa raiz confirmada**: `_validate_same_org` (linhas 76-85 do service) acessa `user.organization_id` — atributo inexistente no modelo `User`. O modelo `User` não possui FK direta para `organizations`; o vínculo é via `org_memberships` (`person_id → persons.id`, `organization_id`).

**Fix aplicado**: substituir `user.organization_id` por query ORM a `OrgMembership` onde `person_id = user.person_id AND organization_id = exercise.organization_id AND deleted_at IS NULL AND end_at IS NULL`. Se nenhum registro encontrado → `AclCrossOrgError`.

**Impacto em outros testes**:
- `test_acl_003_cross_org_blocked`: beneficiado — converterá de xfail para PASS.
- `test_acl_006_duplicate_grant_blocked`: usa bypass `service._validate_same_org = _noop_same_org` → inalterado.
- `test_acl_004_non_owner_cannot_grant`: falha em `_validate_creator_authority` antes de atingir `_validate_same_org` → inalterado.
- Restante da TRUTH SUITE: sem impacto (fix isolado no service).

**AC-005 (openapi.json)**: não modificado — fix é exclusivamente de service layer.

**Risco**: `validation_command` usa `tail -20` que capturará timing de execução → provável FLAKY_OUTPUT no Testador (mesmo padrão de AR_247). Registrado como nota — decisão de REPLAN é do Arquiteto.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `python scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v 2>&1 | tail -20`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-05T14:41:14.847942+00:00
**Behavior Hash**: a7fcaac17dbec17a5315052c25b8f61810824e8318b3f8ec949ccdc8f14380e1
**Evidence File**: `docs/hbtrack/evidence/AR_248/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `$env:PYTHONUTF8='1'; python scripts/db/reset_hb_track_test.py; cd "Hb Track - Backend"; python -m pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v 2>&1 | python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-05T15:17:41.380811+00:00
**Behavior Hash**: 327d028bcb70b50fa0b985d9404aba96cbbd96ab0e6d89396352a405b48ed5fe
**Evidence File**: `docs/hbtrack/evidence/AR_248/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: ❌ FALHA
**Comando**: `set PYTHONUTF8=1 && python scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v 2>&1 | python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 1
**Timestamp UTC**: 2026-03-05T15:29:05.242651+00:00
**Behavior Hash**: 321c73c21d6fdd9c423c174c0d8f83dba279333001cb1f2e825823facbe2bacb
**Evidence File**: `docs/hbtrack/evidence/AR_248/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -X utf8 scripts/db/reset_hb_track_test.py && cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_148_exercise_bank_services.py -v 2>&1 | python -c "import sys; lines=sys.stdin.readlines(); [print(l.rstrip()) for l in lines[-30:] if any(w in l for w in ['PASSED','FAILED','ERROR','xfailed','xpassed','passed','failed','error','XFAIL','XPASS']) and 'warnings' not in l] or [print(lines[-1].rstrip())]"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-05T15:51:45.440313+00:00
**Behavior Hash**: df44f0d19e2e33eb1883a864770048119125825292fe06884fe51d8e17f5714d
**Evidence File**: `docs/hbtrack/evidence/AR_248/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_248_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-05T18:26:15.932311+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_248_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_248/executor_main.log`
