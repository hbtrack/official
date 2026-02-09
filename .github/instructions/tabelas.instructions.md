---
description: Carregar estas instruções sempre que eu pedir “varrer tabelas” / “checar models” / “requirements scan” no Hb Track - Backend.
applyTo: '**' 
---
OBJETIVO:
Fazer varredura das tabelas abaixo usando SOMENTE requirements (read-only) e retornar um resumo PASS/FAIL por tabela, sem autogen, sem snapshot, sem criar arquivos temporários no repo.

REGRAS:
- Rodar em: C:\HB TRACK\Hb Track - Backend
- Antes de começar: `git status --porcelain` deve estar vazio. Se não estiver, PARE e reporte (não limpe automaticamente).
- Rodar `inv.ps1 refresh` UMA vez antes da varredura (SSOT atualizado).
- Para cada tabela: executar requirements e registrar exit code imediatamente.
- Continuar varredura se exit=4 (violations). Parar somente se exit=1 (crash) EXCETO se o output indicar claramente “model da tabela não encontrado” (aí marcar como SKIP e continuar).
- Não criar nenhum arquivo temporário dentro do repo. Se precisar salvar resumo em arquivo, usar $env:TEMP.

COMANDOS:

1) Preparação
Set-Location "C:\HB TRACK\Hb Track - Backend"
Get-Location
git status --porcelain
# Se houver saída: ABORTAR.

2) SSOT refresh
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\HB TRACK\scripts\inv.ps1" refresh
$ec = $LASTEXITCODE; Write-Host "EXIT(inv_refresh)=$ec"
# Se $ec != 0: ABORTAR.

3) Varredura requirements (sem pipeline; capturar exit code imediatamente)
Usar a lista exata de tabelas:
advantage_states, alembic_version, athlete_badges, athletes, attendance, audit_logs, categories,
competition_matches, competition_opponent_teams, competition_phases, competition_seasons, competition_standings, competitions,
data_access_logs, data_retention_logs, defensive_positions, email_queue, event_subtypes, event_types,
exercise_favorites, exercise_tags, exercises, export_jobs, export_rate_limits, idempotency_keys,
match_events, match_periods, match_possessions, match_roster, match_teams, matches,
medical_cases, notifications, offensive_positions, org_memberships, organizations,
password_resets, permissions, person_addresses, person_contacts, person_documents, person_media, persons,
phases_of_play, role_permissions, roles, schooling_levels, seasons, session_templates,
team_memberships, team_registrations, team_wellness_rankings, teams,
training_alerts, training_analytics_cache, training_cycles, training_microcycles, training_session_exercises, training_sessions, training_suggestions,
users, wellness_post, wellness_pre, wellness_reminders

Implementação PowerShell (sem criar arquivos no repo):
- Guardar o resumo em memória e, opcionalmente, exportar para $env:TEMP.

SCRIPT:

$tables = @(
  "advantage_states","alembic_version","athlete_badges","athletes","attendance","audit_logs","categories",
  "competition_matches","competition_opponent_teams","competition_phases","competition_seasons","competition_standings","competitions",
  "data_access_logs","data_retention_logs","defensive_positions","email_queue","event_subtypes","event_types",
  "exercise_favorites","exercise_tags","exercises","export_jobs","export_rate_limits","idempotency_keys",
  "match_events","match_periods","match_possessions","match_roster","match_teams","matches",
  "medical_cases","notifications","offensive_positions","org_memberships","organizations",
  "password_resets","permissions","person_addresses","person_contacts","person_documents","person_media","persons",
  "phases_of_play","role_permissions","roles","schooling_levels","seasons","session_templates",
  "team_memberships","team_registrations","team_wellness_rankings","teams",
  "training_alerts","training_analytics_cache","training_cycles","training_microcycles","training_session_exercises","training_sessions","training_suggestions",
  "users","wellness_post","wellness_pre","wellness_reminders"
)

$results = @()
foreach ($t in $tables) {
  $profile = if ($t -in @("teams","seasons")) { "fk" } else { "strict" }

  Write-Host "`n=== REQUIREMENTS $t (profile=$profile) ==="
  $out = & "venv\Scripts\python.exe" scripts\model_requirements.py --table $t --profile $profile 2>&1
  $ec = $LASTEXITCODE
  $out | Write-Host
  Write-Host "EXIT(requirements:$t)=$ec"

  $status = if ($ec -eq 0) { "PASS" }
            elseif ($ec -eq 4) { "FAIL" }
            elseif ($ec -eq 1 -and ($out -match "not found|no model|could not locate|model.*table")) { "SKIP_NO_MODEL" }
            else { "CRASH" }

  $results += [pscustomobject]@{ table=$t; profile=$profile; exit=$ec; status=$status }

  if ($status -eq "CRASH") {
    Write-Host "`n[ABORT] crash em $t (exit=1). Cole este output e pare." -ForegroundColor Red
    break
  }
}

Write-Host "`n=== SUMMARY ==="
$results | Format-Table -AutoSize

# Opcional: salvar fora do repo
$csv = Join-Path $env:TEMP "hb_requirements_scan.csv"
$results | Export-Csv -NoTypeInformation -Encoding UTF8 $csv
Write-Host "Saved: $csv"

4) Pós-condição
git status --porcelain
# Deve continuar vazio (requirements não deve sujar repo). Se sujar, reporte paths.

ENTREGA (o que retornar pra mim):
- Tabela final com: table, profile, exit, status
- Lista separada de FAIL (exit=4)
- Lista de SKIP_NO_MODEL (se houver)
- Se CRASH: output completo do crash + tabela onde parou
