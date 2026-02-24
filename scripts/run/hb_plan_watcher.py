#!/usr/bin/env python3
"""
hb_plan_watcher.py - Plan Materialization Daemon with Atomic Claim

Monitors docs/_canon/planos/*.json and safely materializes ARs with:
- Atomic lockfile-based claim (prevents double-processing)
- Mandatory dry-run validation before materialize
- Git diff-based staging (only changed files)
- Structured logging with unique RUN_ID

Usage:
    python scripts/run/hb_plan_watcher.py [--once] [--dry-run] [--loop N]

Flags:
    --once     : Process once and exit (no loop)
    --dry-run  : Diagnostic mode, no plan materialization
    --loop N   : Poll interval in seconds (default: 5)
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set

# === CONFIG ===
PLANS_DIR = Path("docs/_canon/planos")
CLAIM_DIR = Path("_reports/dispatch/plan_watcher")
LOGS_DIR = CLAIM_DIR / "logs"
PROCESSED_LOG = CLAIM_DIR / "processed.log"
DEFAULT_LOOP_INTERVAL = 5

# === UTILITIES ===

def get_run_id() -> str:
    """Generate unique RUN_ID for this execution"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"RUN_{timestamp}_{id(object())}"

def get_plan_hash(plan_path: Path) -> str:
    """SHA-256 hash of plan file content"""
    content = plan_path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:16]

def get_new_plans() -> List[Path]:
    """Find all plan JSONs that haven't been processed yet"""
    all_plans = list(PLANS_DIR.rglob("*.json"))
    
    if not PROCESSED_LOG.exists():
        return all_plans
    
    processed = set(PROCESSED_LOG.read_text(encoding='utf-8').strip().split('\n'))
    processed.discard('')  # Remove empty lines
    
    new_plans = [p for p in all_plans if str(p.relative_to(Path.cwd())) not in processed]
    return new_plans

def claim_plan(plan_path: Path) -> bool:
    """Atomic claim via lockfile. Returns True if claim successful."""
    plan_hash = get_plan_hash(plan_path)
    lockfile = CLAIM_DIR / f"CLAIM_{plan_hash}.lock"
    
    CLAIM_DIR.mkdir(parents=True, exist_ok=True)
    
    if lockfile.exists():
        return False  # Already claimed
    
    try:
        lockfile.write_text(f"CLAIMED {datetime.now(timezone.utc).isoformat()}\n", encoding='utf-8')
        return True
    except FileExistsError:
        return False  # Race condition - another process claimed first

def run_hb_plan(plan_path: Path, dry_run: bool = False) -> subprocess.CompletedProcess:
    """Execute hb plan with optional dry-run"""
    cmd = ["python", "scripts/run/hb_cli.py", "plan", str(plan_path)]
    if dry_run:
        cmd.append("--dry-run")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def get_git_diff() -> List[str]:
    """Get list of changed files (staged + unstaged)"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        return []
    
    changed_files = result.stdout.strip().split('\n')
    return [f for f in changed_files if f]

def stage_diff(files: List[str]) -> None:
    """Stage only specified files"""
    if not files:
        return
    
    subprocess.run(["git", "add"] + files, check=False)

def mark_processed(plan_path: Path) -> None:
    """Mark plan as processed in persistent log"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    with PROCESSED_LOG.open('a', encoding='utf-8') as f:
        f.write(f"{plan_path.relative_to(Path.cwd())}\n")

def log_structured(run_id: str, event: str, data: dict) -> None:
    """Write structured log entry"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    log_file = LOGS_DIR / f"{run_id}.jsonl"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "event": event,
        **data
    }
    
    with log_file.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

# === MAIN LOOP ===

def process_plans(run_id: str, diagnostic_mode: bool = False) -> int:
    """
    Main processing loop for plan materialization.
    Returns number of plans processed.
    """
    new_plans = get_new_plans()
    
    if not new_plans:
        log_structured(run_id, "scan_complete", {"new_plans": 0})
        return 0
    
    log_structured(run_id, "scan_complete", {"new_plans": len(new_plans), "paths": [str(p) for p in new_plans]})
    
    processed_count = 0
    
    for plan_path in new_plans:
        plan_rel = plan_path.relative_to(Path.cwd())
        
        # Step 1: Atomic claim
        if not claim_plan(plan_path):
            log_structured(run_id, "claim_failed", {"plan": str(plan_rel), "reason": "already_claimed"})
            continue
        
        log_structured(run_id, "claim_success", {"plan": str(plan_rel)})
        
        # Step 2: Dry-run validation
        dry_result = run_hb_plan(plan_path, dry_run=True)
        
        if dry_result.returncode != 0:
            log_structured(run_id, "dry_run_failed", {
                "plan": str(plan_rel),
                "exit_code": dry_result.returncode,
                "stderr": dry_result.stderr[:500]
            })
            continue
        
        log_structured(run_id, "dry_run_pass", {"plan": str(plan_rel)})
        
        # Step 3: Materialize (skip if diagnostic mode)
        if diagnostic_mode:
            log_structured(run_id, "materialize_skipped", {"plan": str(plan_rel), "reason": "dry_run_mode"})
            mark_processed(plan_path)
            processed_count += 1
            continue
        
        before_diff = set(get_git_diff())
        
        materialize_result = run_hb_plan(plan_path, dry_run=False)
        
        if materialize_result.returncode != 0:
            log_structured(run_id, "materialize_failed", {
                "plan": str(plan_rel),
                "exit_code": materialize_result.returncode,
                "stderr": materialize_result.stderr[:500]
            })
            continue
        
        # Step 4: Stage only diff
        after_diff = set(get_git_diff())
        new_files = list(after_diff - before_diff)
        
        stage_diff(new_files)
        
        log_structured(run_id, "materialize_success", {
            "plan": str(plan_rel),
            "staged_files": new_files
        })
        
        mark_processed(plan_path)
        processed_count += 1
    
    return processed_count

def main():
    parser = argparse.ArgumentParser(
        description="HB Track Plan Watcher Daemon - Atomic Plan Materialization"
    )
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Diagnostic mode, no materialization")
    parser.add_argument("--loop", type=int, default=DEFAULT_LOOP_INTERVAL, 
                       help="Poll interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    run_id = get_run_id()
    
    log_structured(run_id, "daemon_start", {
        "mode": "once" if args.once else "loop",
        "dry_run": args.dry_run,
        "interval": args.loop
    })
    
    print(f"🔍 HB Plan Watcher {run_id}")
    print(f"   Mode: {'once' if args.once else f'loop (interval={args.loop}s)'}")
    print(f"   Dry-run: {args.dry_run}")
    
    try:
        if args.once:
            processed = process_plans(run_id, diagnostic_mode=args.dry_run)
            print(f"✅ Processed {processed} plans")
        else:
            while True:
                processed = process_plans(run_id, diagnostic_mode=args.dry_run)
                if processed > 0:
                    print(f"✅ Processed {processed} plans")
                
                time.sleep(args.loop)
    except KeyboardInterrupt:
        log_structured(run_id, "daemon_stop", {"reason": "keyboard_interrupt"})
        print("\n⏹️  Daemon stopped by user")
        sys.exit(0)
    except Exception as e:
        log_structured(run_id, "daemon_error", {"error": str(e)})
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
