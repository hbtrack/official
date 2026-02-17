param(
  [string]$ProfilePath = "docs/_canon/HB_TRACK_PROFILE.yaml",
  [string]$OutDir = "docs/_generated/_reports/gates"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

python scripts/checks/check_hb_track_profile.py --profile $ProfilePath 2>&1 |
  Out-File -FilePath (Join-Path $OutDir "gate_profile.log") -Encoding utf8

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
exit 0
