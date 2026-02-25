# Execute AR_059 report
$ErrorActionPreference = "Stop"
$cmd = Get-Content -Path "temp/ar059_cmd.txt" -Raw
python scripts/run/hb_cli.py report 059 $cmd.Trim()
