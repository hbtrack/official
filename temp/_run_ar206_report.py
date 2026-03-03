import subprocess, sys, os

os.chdir(r"c:\HB TRACK")
cmd = 'cd "Hb Track - Backend" && pytest tests/training/contracts/test_contract_train_077_085_alerts_suggestions.py -v --tb=short 2>&1'
result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "206", cmd],
    capture_output=False,
)
sys.exit(result.returncode)
