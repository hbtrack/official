---
description: Carregar quando a tarefa envolver models SQLAlchemy, autogen, guard/parity/requirements, baseline, schema.sql ou qualquer gate de validação.
applyTo: "Hb Track - Backend/scripts/**;Hb Track - Backend/app/models/**;Hb Track - Backend/.hb_guard/**;Hb Track - Backend/docs/_generated/**;docs/_generated/**;docs/_canon/05_MODELS_PIPELINE.md;docs/_canon/06_AGENT_PROMPTS_MODELS.md;docs/_canon/07_AGENT_ROUTING_MAP.md"
---
REGRAS MODELS/GATE (Determinístico):

- CWD obrigatório: `Set-Location "C:\HB TRACK\Hb Track - Backend"`.
- Antes de executar qualquer gate: `git status --porcelain` deve estar vazio. Se não estiver, ABORTAR e reportar.
- Capturar `$LASTEXITCODE` imediatamente após cada comando (sem pipeline). Se exit != 0, PARAR e colar output + exit + git status.
- PROIBIDO criar arquivos temporários/de backup no repo (inclui .tmp_*, *.bak, outputs de teste, scripts auxiliares).
- NÃO rodar snapshot baseline (`agent_guard.py snapshot`) sem autorização explícita do usuário.

PIPELINE PADRÃO (Lote):
- Para varredura/correção em lote, **use `.\scripts\models_batch.ps1` como comando padrão** (SSOT auto via schema.sql).
  - Varredura+correção (padrão): `.\scripts\models_batch.ps1`
  - Somente varredura: `.\scripts\models_batch.ps1 -SkipGate`
  - Excluir tabelas: `.\scripts\models_batch.ps1 -ExcludeTables "alembic_version"`
- O batch runner:
  - roda `inv.ps1 refresh` (a menos que `-SkipRefresh`),
  - executa requirements em todas as tabelas do SSOT,
  - roda `models_autogen_gate.ps1` apenas nas FAIL,
  - para no primeiro erro (fail-fast),
  - salva logs em `%TEMP%` e limpa `docs/_generated/*` via `git restore`.

PIPELINE (1 tabela):
- Quando solicitado explicitamente “1 tabela”, use:
  - `.\scripts\models_autogen_gate.ps1 -Table "<TABLE>" -Profile strict`
  - Para ciclo FK: `-Profile fk -AllowCycleWarning`

FONTES CANÔNICAS:
- Pipeline: `docs/_canon/05_MODELS_PIPELINE.md`
- Prompts prontos: `docs/_canon/06_AGENT_PROMPTS_MODELS.md`
- Roteamento de ações: `docs/_canon/07_AGENT_ROUTING_MAP.md`
- SSOT DB: `Hb Track - Backend/docs/_generated/schema.sql` (gerado por `C:\HB TRACK\scripts\inv.ps1 refresh`)

FIX LOOP (exit ≠ 0):
- Autoridade completa: `docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md` (seção "Exit Codes e Ações Corretivas")
- Machine-readable: `docs/_canon/_machine/exit_code_playbook.yaml`
- Máximo 3 iterações (fix → rerun gate). Se não convergir: STOP e escalar com evidências.
- Nunca snapshot baseline sem flag explícita (`-AllowBaselineSnapshot`) + autorização do usuário.
- Sempre rodar `git status --porcelain` antes de cada gate. Se sujo: ABORTAR.
- Após STOP, devolver: exit code, arquivos tocados, diff stat, relatórios, hipótese de causa.
