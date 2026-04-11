from __future__ import annotations
import os
import subprocess
import sys

def main() -> int:
    run_id = os.getenv("HB_AUDIT_RUN_ID")
    root = os.getenv("HB_REPORTS_ROOT", "_reports")
    if not run_id:
        print("ERROR: HB_AUDIT_RUN_ID missing")
        return 4
    cmd = [sys.executable, "scripts/checks/check_audit_pack.py", run_id, "--root", root]
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
