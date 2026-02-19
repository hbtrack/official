#!/usr/bin/env python3
"""
Plan Status Manager
====================
Manages Plan lifecycle and prevents execution of obsolete Plans.

Status flow: RASCUNHO → EM_REVISAO → APROVADO → EXECUTADO

Usage:
    # Check Plan status
    python scripts/plan_status.py docs/plans/FASE-5-3.md
    
    # Update status
    python scripts/plan_status.py docs/plans/FASE-5-3.md --set APROVADO
    
    # Mark as executed (moves to implemented/)
    python scripts/plan_status.py docs/plans/FASE-5-3.md --executed
    
    # List all Plans by status
    python scripts/plan_status.py --list
"""

import re
import sys
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

try:
    from . import config
except ImportError:
    import config

PLANS_DIR = config.PLANS_DIR
IMPLEMENTED_DIR = config.IMPLEMENTED_DIR


VALID_STATUSES = ["RASCUNHO", "EM_REVISAO", "APROVADO", "EXECUTADO", "OBSOLETO"]


def get_plan_status(plan_path: Path) -> Optional[str]:
    """Extract current status from Plan file."""
    content = plan_path.read_text()
    match = re.search(r'\*\*Status:\*\*\s*([A-Z_]+)', content)
    if match:
        status = match.group(1)
        return status if status in VALID_STATUSES else None
    return None


def get_task_id(plan_path: Path) -> str:
    """Extract TASK-ID from Plan."""
    content = plan_path.read_text()
    match = re.search(r'TASK-ID[:\s]+([A-Z0-9-]+)', content, re.IGNORECASE)
    return match.group(1) if match else plan_path.stem


def set_plan_status(plan_path: Path, new_status: str):
    """Update Plan status."""
    if new_status not in VALID_STATUSES:
        print(f"Error: Invalid status '{new_status}'")
        print(f"Valid statuses: {', '.join(VALID_STATUSES)}")
        sys.exit(1)
    
    content = plan_path.read_text()
    
    # Check if status line exists
    if re.search(r'\*\*Status:\*\*', content):
        # Replace existing status
        new_content = re.sub(
            r'(\*\*Status:\*\*\s*)([A-Z_]+)',
            f'\\1{new_status}',
            content
        )
    else:
        # Add status after TASK-ID
        new_content = re.sub(
            r'(TASK-ID[:\s]+[A-Z0-9-]+)',
            f'\\1\n**Status:** {new_status}',
            content
        )
    
    # Add timestamp
    timestamp = datetime.now().isoformat()
    if "Status atualizado em:" in new_content:
        new_content = re.sub(
            r'Status atualizado em:.*',
            f'Status atualizado em: {timestamp}',
            new_content
        )
    else:
        new_content = new_content.replace(
            f"**Status:** {new_status}",
            f"**Status:** {new_status}\nStatus atualizado em: {timestamp}"
        )
    
    plan_path.write_text(new_content)
    print(f"✅ Status atualizado: {new_status}")
    print(f"   Timestamp: {timestamp}")


def mark_executed(plan_path: Path):
    """Mark Plan as executed and move to implemented/."""
    task_id = get_task_id(plan_path)
    current_status = get_plan_status(plan_path)
    
    if current_status != "APROVADO":
        print(f"⚠️  Warning: Plan status is '{current_status}', not 'APROVADO'")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Update status to EXECUTADO
    set_plan_status(plan_path, "EXECUTADO")
    
    # Move to implemented/
    IMPLEMENTED_DIR.mkdir(parents=True, exist_ok=True)
    dest = IMPLEMENTED_DIR / plan_path.name
    
    shutil.move(str(plan_path), str(dest))
    
    print()
    print(f"✅ Plan marked as EXECUTADO and moved to:")
    print(f"   {dest}")
    print()
    print("Next steps:")
    print("  1. Commit the Plan to git:")
    print(f"     git add {dest}")
    print(f"     git commit -m '[{task_id}] Plan executed'")
    print("  2. Release any file locks:")
    print(f"     python scripts/check_locks.py {dest} --release")


def validate_execution_allowed(plan_path: Path) -> bool:
    """Check if Plan can be executed."""
    status = get_plan_status(plan_path)
    task_id = get_task_id(plan_path)
    
    if status != "APROVADO":
        print(f"❌ Cannot execute: Plan status is '{status}', not 'APROVADO'")
        return False
    
    # Check if already executed
    implemented_file = IMPLEMENTED_DIR / plan_path.name
    if implemented_file.exists():
        print(f"❌ Cannot execute: Task {task_id} already executed")
        print(f"   See: {implemented_file}")
        return False
    
    return True


def list_plans():
    """List all Plans grouped by status."""
    plans_by_status: Dict[str, List[Path]] = {status: [] for status in VALID_STATUSES}
    
    # Scan plans directory
    if PLANS_DIR.exists():
        for plan_file in PLANS_DIR.glob("*.md"):
            status = get_plan_status(plan_file) or "UNKNOWN"
            if status not in plans_by_status:
                plans_by_status[status] = []
            plans_by_status[status].append(plan_file)
    
    # Scan implemented directory
    if IMPLEMENTED_DIR.exists():
        for plan_file in IMPLEMENTED_DIR.glob("*.md"):
            plans_by_status["EXECUTADO"].append(plan_file)
    
    print("=" * 80)
    print("PLANS BY STATUS")
    print("=" * 80)
    print()
    
    for status in VALID_STATUSES:
        plans = plans_by_status[status]
        if plans:
            print(f"{status} ({len(plans)}):")
            for plan in sorted(plans):
                task_id = get_task_id(plan)
                location = "implemented/" if plan.parent == IMPLEMENTED_DIR else "plans/"
                print(f"  [{task_id}] {location}{plan.name}")
            print()
    
    if "UNKNOWN" in plans_by_status and plans_by_status["UNKNOWN"]:
        print("⚠️  UNKNOWN STATUS (needs fixing):")
        for plan in plans_by_status["UNKNOWN"]:
            print(f"  {plan}")
        print()


def show_status(plan_path: Path):
    """Show Plan status and metadata."""
    task_id = get_task_id(plan_path)
    status = get_plan_status(plan_path) or "UNKNOWN"
    
    print("=" * 80)
    print(f"PLAN: {task_id}")
    print("=" * 80)
    print(f"File: {plan_path}")
    print(f"Status: {status}")
    print()
    
    # Check execution eligibility
    if status == "APROVADO":
        if validate_execution_allowed(plan_path):
            print("✅ Ready for execution")
        else:
            print("❌ Cannot be executed (see errors above)")
    elif status == "EXECUTADO":
        print("ℹ️  Already executed")
    elif status == "RASCUNHO":
        print("ℹ️  Needs review before approval")
    elif status == "EM_REVISAO":
        print("ℹ️  Under review")
    elif status == "OBSOLETO":
        print("⚠️  Obsolete — should not be executed")


def main():
    if "--list" in sys.argv:
        list_plans()
        return
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/plan_status.py <plan.md>                 # Show status")
        print("  python scripts/plan_status.py <plan.md> --set STATUS   # Update status")
        print("  python scripts/plan_status.py <plan.md> --executed     # Mark executed")
        print("  python scripts/plan_status.py --list                   # List all plans")
        print()
        print(f"Valid statuses: {', '.join(VALID_STATUSES)}")
        sys.exit(1)
    
    plan_path = config.resolve_plan_path(sys.argv[1])
    
    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)
    
    if "--set" in sys.argv:
        idx = sys.argv.index("--set")
        if idx + 1 >= len(sys.argv):
            print("Error: --set requires a status argument")
            sys.exit(1)
        new_status = sys.argv[idx + 1]
        set_plan_status(plan_path, new_status)
    elif "--executed" in sys.argv:
        mark_executed(plan_path)
    else:
        show_status(plan_path)


if __name__ == "__main__":
    main()
