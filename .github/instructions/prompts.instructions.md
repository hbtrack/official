---
description: "Carregar este prompt sempre que a tarefa envolver criar/corrigir models SQLAlchemy, rodar gates (guard/parity/requirements), atualizar SSOT (schema.sql) ou qualquer comando em Hb Track - Backend."
applyTo: "Hb Track - Backend/**,docs/_canon/**,docs/references/exit_codes.md,docs/ADR/008-ADR-TRAIN-governanca-por-artefatos.md,docs/ADR/_INDEX_ADR.md"
---
PROMPT PARA O AGENT — PIPELINE CANÔNICO (STOP ON FIRST FAILURE)

OBJETIVO:
Executar o pipeline determinístico para criar/corrigir models, garantindo “models perfeitos” (gate exit=0), sem drift e sem sair do escopo.

ESCOPO:
- Tabela(s) alvo: <TABLE_1> (e opcionalmente <TABLE_2>).
- Não tocar em outras tabelas/arquivos fora do necessário.
- Proibido criar arquivos temporários/backups dentro do repo.
- Não fazer snapshot do baseline sem ordem explícita (ver regra abaixo).

REGRA DE PARADA IMEDIATA (CRÍTICA):
Após QUALQUER comando, se $LASTEXITCODE != 0, PARE imediatamente.
Ao parar, cole: comando, output (últimas 80 linhas), $LASTEXITCODE, `git status --porcelain`, e `Get-Location`.

PASSO 0 — ROOT CORRETO
1) `Set-Location "C:\HB TRACK\Hb Track - Backend"`
2) `Get-Location` (deve mostrar o backend root)

PASSO 1 — PORCELAIN (Repo limpo antes de tudo)
Execute:
- `git status --porcelain`
Se houver qualquer linha:
- NÃO corrija automaticamente.
- PARE e reporte os paths encontrados.

PASSO 2 — BASELINE CHECK (somente verificação)
Execute guard CHECK (não snapshot):
- `& "venv\Scripts\python.exe" scripts\agent_guard.py check --root "." --baseline ".hb_guard/baseline.json" --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"`
Capture imediatamente:
- `$ec = $LASTEXITCODE; Write-Host "EXIT(guard_check)=$ec"`
Se $ec != 0:
- PARE e reporte (não faça snapshot, não edite baseline).

PASSO 3 — SSOT REFRESH (DB → schema.sql)
Execute:
- `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh`
Capture:
- `$ec = $LASTEXITCODE; Write-Host "EXIT(inv_refresh)=$ec"`
Se $ec != 0: PARE.

PASSO 4 — CRIAR/CORRIGIR MODEL + VALIDAR (Gate por tabela)
Para cada tabela <TABLE>:
Execute:
- `.\scripts\models_autogen_gate.ps1 -Table "<TABLE>" -Profile strict`
Capture imediatamente:
- `$ec = $LASTEXITCODE; Write-Host "EXIT(models_autogen_gate:<TABLE>)=$ec"`
Critério:
- Deve ser exit=0 para “model perfeito”.
Se $ec != 0: PARE e reporte.

PASSO 5 — LIMPAR ARTEFATOS GERADOS (para não sujar repo)
Ainda no backend root, execute:
- `git restore -- "docs/_generated/alembic_state.txt" "docs/_generated/manifest.json" "docs/_generated/parity_report.json" "docs/_generated/schema.sql"`
- `git restore -- "C:/HB TRACK/Hb Track - Backend/docs/_generated/alembic_state.txt" "C:/HB TRACK/Hb Track - Backend/docs/_generated/manifest.json" "C:/HB TRACK/Hb Track - Backend/docs/_generated/schema.sql" "C:/HB TRACK/Hb Track - Backend/docs/_generated/trd_training_permissions_report.txt"`
Se algum restore falhar: PARE e reporte.

PASSO 6 — PORCELAIN FINAL + EVIDÊNCIA
Execute:
- `git status --porcelain`
- `git --no-pager diff --stat`
Critério:
- Repo limpo OU apenas mudanças intencionais no model da(s) tabela(s) alvo (ex.: `app/models/<...>.py`).
Se aparecer lixo (untracked, docs/_generated, scripts fora do escopo): PARE e reporte.

IMPORTANTE (NÃO FAZER):
- NÃO rodar `scripts/agent_guard.py snapshot` (baseline update) sem eu pedir explicitamente.
- NÃO commitar nada automaticamente (apenas reportar). Eu decido commit/snapshot.
- NÃO executar comandos com pipeline tipo `| Select-Object ...` antes de capturar `$LASTEXITCODE`.
- Capturar `$LASTEXITCODE` imediatamente após cada comando.

FORMATO DO RELATÓRIO FINAL (obrigatório):
Para cada passo, reporte:
- Comando executado
- Exit code
- 10–30 linhas relevantes de output
E ao final:
- `git status --porcelain`
- `git diff --stat`
Se qualquer passo falhar, pare imediatamente e reporte conforme acima.