import subprocess, sys, os

os.chdir(r"c:\HB TRACK")
cmd = 'cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_032_wellness_post_rpe.py -v --tb=short 2>&1'
result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "205", cmd],
    capture_output=False,
)
sys.exit(result.returncode)
