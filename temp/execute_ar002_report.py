"""Executor wrapper for AR_002 hb report"""
import subprocess
import sys
from pathlib import Path

# Change to workspace root
workspace = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace))

# AR_002 validation command (from AR file)
validation_command = """python -c "import sys; sys.path.insert(0, 'Hb Track - Backend'); from app.models.competition_standing import CompetitionStanding; assert hasattr(CompetitionStanding, 'team_id'), 'FAIL: team_id not found'; print('PASS: team_id present in CompetitionStanding')" """

# Execute hb report command
cmd = [
    sys.executable,
    "scripts/run/hb_cli.py",
    "report",
    "002",
    validation_command
]

print(f"[AR_002] Running hb report...")
print(f"[AR_002] Command: {' '.join(cmd)}")
print(f"[AR_002] Validation: {validation_command}")
print("-" * 80)

result = subprocess.run(
    cmd,
    cwd=workspace,
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)

sys.exit(result.returncode)
