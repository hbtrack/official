# SCRIPTS_GUIDE — Contrato Enterprise para Scripts HB Track

Status: CANONICAL
Version: 1.0.0
Last Updated: 2026-02-13
Applies To: `scripts/**`, `Hb Track - Backend/scripts/**`, `Hb Track - Fronted/scripts/**`, `docs/scripts/**`

---

## 1) Objetivo

Definir o contrato mínimo para qualquer script operacional no monorepo, com foco em:
- Interface padronizada
- Logs estruturados (JSON)
- Idempotência para scripts de fix/migração
- Arquivamento seguro (`_archived/`) em vez de delete físico

---

## 2) Contrato mínimo de interface (obrigatório para INCORPORAR)

Todo script candidato a produção/guia deve aceitar, quando aplicável:

- `--tenant-id <id>` (quando o script atua em escopo multi-tenant)
- `--dry-run` (simular sem aplicar mudanças)
- `--output json` (ou saída JSON por padrão)
- `--verbose` (opcional para diagnósticos)

### Exit codes esperados
- `0`: sucesso
- `1`: erro interno
- `2+`: códigos específicos de domínio (documentar no próprio script)

---

## 3) Logs estruturados (obrigatório para INCORPORAR)

Formato mínimo por evento (JSON Lines) ou bloco JSON final:

```json
{
  "timestamp": "2026-02-13T14:00:00-03:00",
  "script": "models_batch.ps1",
  "action": "scan",
  "tenant_id": "global",
  "dry_run": true,
  "status": "ok",
  "details": {"table": "athletes"}
}
```

Campos obrigatórios: `timestamp`, `script`, `action`, `status`.

---

## 4) Idempotência (obrigatório para fix/migração)

Scripts de correção, seed ou migração devem ser idempotentes:
- Rodar 1x e 2x deve manter estado final equivalente
- Quando não idempotente por natureza, deve ser classificado como `DIVIDA_TECNICA`
- `--dry-run` deve antecipar diffs sem alterar estado

Checklist mínimo de validação:
1. Executar com `--dry-run` (sem alterações)
2. Executar sem `--dry-run` (aplica)
3. Executar novamente sem `--dry-run` (sem alterações adicionais)

---

## 5) Política de arquivamento (compliance)

- Proibido delete físico de arquivos da auditoria
- Destino obrigatório: `_archived/YYYY-MM-DD/<dominio>/...`
- Arquivo arquivado deve constar no relatório de auditoria
- Diretórios `_archived/` devem permanecer no `.gitignore`

---

## 6) Estrutura funcional alvo (organização)

Estrutura recomendada para evolução gradual (sem quebra):

- `scripts/core/` → orquestração principal (`inv.ps1`, gates globais)
- `scripts/validation/` → validações e checks
- `scripts/migration/` → migração/correção de dados
- `scripts/audit/` → auditoria e compliance
- `scripts/docs-tools/` → geração/validação documental
- `_archived/YYYY-MM-DD/...` → legado/descontinuado

> Observação: a migração física deve ser incremental e acompanhada de smoke tests dos scripts críticos.

---

## 7) Scripts críticos (smoke tests obrigatórios)

Lista inicial (defaults autorizados):

1. `scripts/inv.ps1`
2. `scripts/run_invariant_gate.ps1`
3. `scripts/run_invariant_gate_all.ps1`
4. `Hb Track - Backend/scripts/parity_scan.ps1`
5. `Hb Track - Backend/scripts/parity_gate.ps1`
6. `Hb Track - Backend/scripts/models_autogen_gate.ps1`
7. `Hb Track - Backend/scripts/models_batch.ps1`
8. `Hb Track - Backend/scripts/model_requirements.py`
9. `Hb Track - Backend/scripts/agent_guard.py`
10. `Hb Track - Fronted/scripts/sync_openapi.ps1`
11. `Hb Track - Backend/scripts/fix_superadmin.py` — fix superadmin (idempotente, JSON logging, CLI standards) ✅
12. `scripts/compact_exec_logs.py` — Compact execution logs (idempotente, JSON logging, CLI standards) ✅
13. `Hb Track - Backend/scripts/seed_v1_2_initial.py` — Foundation data seeding (idempotente via idempotency_keys, JSON logging, CLI standards) ✅
14. `Hb Track - Backend/scripts/seed_permissions.py` — RBAC permissions seeding (idempotente via idempotency_keys, JSON logging, CLI standards) ✅
15. `Hb Track - Backend/scripts/seed_role_permissions.py` — RBAC role-permission mapping seeding (idempotente via idempotency_keys, JSON logging, CLI standards) ✅

---

## 8) Classificação de decisão por arquivo

Valores permitidos:
- `INCORPORAR`
- `REFATORAR_ANTES_DE_INCORPORAR`
- `DIVIDA_TECNICA`
- `ARQUIVAR`

Regra mandatória:
- Sem interface padrão + JSON log => não pode ser `INCORPORAR`
- Fix/migração sem idempotência comprovada => `DIVIDA_TECNICA`

**Exceções (INCORPORAR após refactoring):**
- `fix_superadmin.py` → **INCORPORAR** (idempotência comprovada via smoke tests, JSON logging, CLI standards implementados; ref: AR-2026-02-14)
- `compact_exec_logs.py` → **INCORPORAR** (idempotência comprovada via smoke tests, JSON logging, CLI standards implementados; exit codes explícitos 0=noop, 1=updated; ref: AR-2026-02-15)
- `seed_v1_2_initial.py` → **INCORPORAR** (idempotência comprovada via idempotency_keys table, JSON logging, CLI standards implementados; exit codes 0=noop, 1=seeded, 3=error; ref: AR-2026-02-16)
- `seed_permissions.py` → **INCORPORAR** (idempotência comprovada via idempotency_keys table, JSON logging, CLI standards implementados; exit codes 0=noop, 1=seeded, 3=error; GATE-A idempotency validated in SMOKE-3; ref: AR-2026-02-17)
- `seed_role_permissions.py` → **INCORPORAR** (idempotência comprovada via idempotency_keys table, JSON logging, CLI standards implementados; exit codes 0=noop, 1=seeded, 3=error; GATE-A idempotency mechanism validated; ref: AR-2026-02-18)

---

## 9) Evidência obrigatória por mudança

Para cada script alterado/reclassificado:
- path
- decisão
- evidência de contrato (CLI + JSON)
- evidência de idempotência (quando aplicável)
- ação de arquivamento (quando aplicável)
