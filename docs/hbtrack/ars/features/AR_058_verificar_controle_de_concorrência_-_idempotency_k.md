# AR_058 — Verificar controle de concorrência — idempotency_keys + UNIQUE constraints

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Verificar controles de concorrência existentes no schema: (1) tabela idempotency_keys com UNIQUE(key, endpoint) — garante que retries idempotentes não duplicam operações; (2) UNIQUE constraint uq_idempotency_key_endpoint presente; (3) UNIQUE constraints de negócio críticos: uq_session_templates_org_name (nomes únicos por org), uq_wellness_reminders_session_athlete (um reminder por atleta/sessão), uq_team_wellness_rankings_team_month (um ranking por time/mês). Estes são os mecanismos de proteção contra double-submit e race conditions.

## Critérios de Aceite
- Tabela idempotency_keys declarada em schema.sql
- uq_idempotency_key_endpoint UNIQUE presente em schema.sql
- uq_session_templates_org_name UNIQUE presente
- uq_wellness_reminders_session_athlete UNIQUE presente
- uq_team_wellness_rankings_team_month UNIQUE presente
- hb report gera evidence exit 0

## Write Scope
- Hb Track - Backend/docs/ssot/schema.sql

## Validation Command (Contrato)
```
python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); checks={'idempotency_keys_table':('idempotency_keys' in s),'uq_idempotency_key_endpoint':('uq_idempotency_key_endpoint' in s),'uq_session_templates_org_name':('uq_session_templates_org_name' in s),'uq_wellness_reminders_session_athlete':('uq_wellness_reminders_session_athlete' in s),'uq_team_wellness_rankings_team_month':('uq_team_wellness_rankings_team_month' in s)}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS AR_058: {len(checks)} controles de concorrência verificados em schema.sql')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_058/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Backend/docs/ssot/schema.sql"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Verificação estática. Se algum UNIQUE estiver ausente do schema.sql mas existir em migration recente (0060/0061), o schema.sql SSOT está desatualizado — abrir AR para regenerar via gen_docs_ssot.py.

## Análise de Impacto
**Executor**: 2026-02-24

**Escopo**: Verificação estática pura - confirmar presença de controles de concorrência em schema.sql SSOT.

**Riscos**:
- **BAIXO**: Apenas leitura de schema.sql existente.
- **ATENÇÃO**: Se algum UNIQUE estiver ausente, indica dessincronia entre migrations DB e schema.sql SSOT.

**Dependências**:
- Arquivo: `Hb Track - Backend/docs/ssot/schema.sql` (SSOT gerado por gen_docs_ssot.py)
- Migrations recentes: 0060/0061 podem ter adicionado constraints

**Patch**:
- 0 arquivos modificados (verificação read-only)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em c5f1ba8
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; s=pathlib.Path('Hb Track - Backend/docs/ssot/schema.sql').read_text(encoding='utf-8'); checks={'idempotency_keys_table':('idempotency_keys' in s),'uq_idempotency_key_endpoint':('uq_idempotency_key_endpoint' in s),'uq_session_templates_org_name':('uq_session_templates_org_name' in s),'uq_wellness_reminders_session_athlete':('uq_wellness_reminders_session_athlete' in s),'uq_team_wellness_rankings_team_month':('uq_team_wellness_rankings_team_month' in s)}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS AR_058: {len(checks)} controles de concorrência verificados em schema.sql')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T22:51:18.938755+00:00
**Behavior Hash**: ef4da78efa5dad5e1095f6df4b0a2b65e7ea3d475b0b8cba001bcfd9d802c477
**Evidence File**: `docs/hbtrack/evidence/AR_058/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em f8f030f
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T23:39:55.373882+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_058_f8f030f/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_058/executor_main.log`

### Verificacao Testador em 529b87c
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_058_529b87c/result.json`
