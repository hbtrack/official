# AR_058 — Verificar controle de concorrência — idempotency_keys + UNIQUE constraints

**Status**: 🔲 PENDENTE
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
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

