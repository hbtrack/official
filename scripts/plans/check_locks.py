#!/usr/bin/env python3
"""
File Lock Manager
==================
Manages file locks to prevent conflicts when multiple Plans execute in parallel.

Usage:
    # Check if a Plan can be executed
    python scripts/check_locks.py docs/plans/FASE-5-3.md
    
    # Acquire locks for a Plan
    python scripts/check_locks.py docs/plans/FASE-5-3.md --acquire
    
    # Release locks after completion
    python scripts/check_locks.py docs/plans/FASE-5-3.md --release
    
    # List all current locks
    python scripts/check_locks.py --list
"""

import sys
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, List

try:
    from . import config
except ImportError:
    import config

LOCKS_FILE = config.LOCKS_FILE


def ensure_locks_file():
    """Create locks file if it doesn't exist."""
    if not LOCKS_FILE.exists():
        LOCKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCKS_FILE.write_text("locked_files: {}\n")


def load_locks() -> Dict:
    """Load current locks."""
    ensure_locks_file()
    with open(LOCKS_FILE) as f:
        data = yaml.safe_load(f) or {}
    return data.get("locked_files", {})


def save_locks(locks: Dict):
    """Save locks to file."""
    ensure_locks_file()
    with open(LOCKS_FILE, "w") as f:
        yaml.dump({"locked_files": locks}, f, default_flow_style=False)


def parse_plan_locks(plan_path: str) -> Dict[str, str]:
    """Extract file locks from Plan.
    
    Returns dict: {filepath: lock_type} where lock_type is "exclusive" or "shared"
    """
    content = Path(plan_path).read_text()
    locks = {}
    
    # Look for "Arquivos com Lock Exclusivo" section
    exclusive_section = re.search(
        r'##\s*Arquivos com Lock Exclusivo(.*?)(?=##|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if exclusive_section:
        file_matches = re.findall(r'`?([a-z_/]+\.py)`?', exclusive_section.group(1))
        for filepath in file_matches:
            locks[filepath] = "exclusive"
    
    # Look for "Arquivos com Lock Compartilhado" section
    shared_section = re.search(
        r'##\s*Arquivos com Lock Compartilhado(.*?)(?=##|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if shared_section:
        file_matches = re.findall(r'`?([a-z_/]+\.py)`?', shared_section.group(1))
        for filepath in file_matches:
            if filepath not in locks:  # Exclusive takes precedence
                locks[filepath] = "shared"
    
    # Also check in new_files and modified_files sections
    new_files = re.search(r'2\.4\.1.*?Novos Arquivos(.*?)(?=2\.4\.|$)', content, re.DOTALL)
    if new_files:
        file_matches = re.findall(r'`([a-z_/]+\.py)`', new_files.group(1))
        for filepath in file_matches:
            if filepath not in locks:
                locks[filepath] = "exclusive"  # New files always exclusive
    
    modified = re.search(r'2\.4\.2.*?Arquivos Modificados(.*?)(?=2\.4\.|$)', content, re.DOTALL)
    if modified:
        file_matches = re.findall(r'`([a-z_/]+\.py)`', modified.group(1))
        for filepath in file_matches:
            if filepath not in locks:
                locks[filepath] = "exclusive"  # Modified files default to exclusive
    
    return locks


def get_task_id(plan_path: str) -> str:
    """Extract TASK-ID from Plan."""
    content = Path(plan_path).read_text()
    match = re.search(r'TASK-ID[:\s]+([A-Z0-9-]+)', content, re.IGNORECASE)
    return match.group(1) if match else Path(plan_path).stem


def check_conflicts(requested_locks: Dict[str, str], current_locks: Dict, task_id: str) -> List[str]:
    """Check if requested locks conflict with existing locks.
    
    Returns list of conflict messages (empty if no conflicts).
    """
    conflicts = []
    
    for filepath, lock_type in requested_locks.items():
        if filepath in current_locks:
            existing = current_locks[filepath]
            
            # Skip if it's our own lock
            if existing.get("locked_by") == task_id:
                continue
            
            # Exclusive locks always conflict
            if lock_type == "exclusive" or existing.get("lock_type") == "exclusive":
                conflicts.append(
                    f"❌ {filepath} — locked by {existing['locked_by']} "
                    f"(since {existing['locked_at']})"
                )
            # Shared locks can coexist
            elif lock_type == "shared" and existing.get("lock_type") == "shared":
                continue
    
    return conflicts


def acquire_locks(plan_path: str):
    """Acquire locks for a Plan."""
    task_id = get_task_id(plan_path)
    requested_locks = parse_plan_locks(plan_path)
    
    if not requested_locks:
        print(f"⚠️  No locks specified in Plan {plan_path}")
        print("Consider adding lock declarations to prevent conflicts.")
        return
    
    current_locks = load_locks()
    conflicts = check_conflicts(requested_locks, current_locks, task_id)
    
    if conflicts:
        print("❌ CANNOT ACQUIRE LOCKS — Conflicts detected:")
        print()
        for conflict in conflicts:
            print(f"  {conflict}")
        print()
        print("Wait for conflicting Plans to complete or resolve manually.")
        sys.exit(1)
    
    # Acquire locks
    timestamp = datetime.now().isoformat()
    for filepath, lock_type in requested_locks.items():
        current_locks[filepath] = {
            "locked_by": task_id,
            "lock_type": lock_type,
            "locked_at": timestamp,
            "plan_file": str(plan_path),
        }
    
    save_locks(current_locks)
    
    print(f"✅ Locks acquired for {task_id}")
    print()
    print("Locked files:")
    for filepath, lock_type in requested_locks.items():
        print(f"  {lock_type.upper()}: {filepath}")


def release_locks(plan_path: str):
    """Release locks for a Plan."""
    task_id = get_task_id(plan_path)
    current_locks = load_locks()
    
    # Remove locks owned by this task
    removed = []
    for filepath in list(current_locks.keys()):
        if current_locks[filepath].get("locked_by") == task_id:
            removed.append(filepath)
            del current_locks[filepath]
    
    save_locks(current_locks)
    
    if removed:
        print(f"✅ Locks released for {task_id}")
        print()
        print("Released files:")
        for filepath in removed:
            print(f"  {filepath}")
    else:
        print(f"⚠️  No locks found for {task_id}")


def list_locks():
    """List all current locks."""
    current_locks = load_locks()
    
    if not current_locks:
        print("No active locks.")
        return
    
    print("=" * 80)
    print("ACTIVE FILE LOCKS")
    print("=" * 80)
    print()
    
    # Group by task
    by_task = {}
    for filepath, lock_info in current_locks.items():
        task = lock_info.get("locked_by", "UNKNOWN")
        if task not in by_task:
            by_task[task] = []
        by_task[task].append((filepath, lock_info))
    
    for task, locks in sorted(by_task.items()):
        print(f"Task: {task}")
        print(f"Since: {locks[0][1].get('locked_at', 'unknown')}")
        print("Files:")
        for filepath, info in locks:
            lock_type = info.get("lock_type", "unknown").upper()
            print(f"  [{lock_type}] {filepath}")
        print()


def check_only(plan_path: str):
    """Check if Plan can be executed (without acquiring locks)."""
    task_id = get_task_id(plan_path)
    requested_locks = parse_plan_locks(plan_path)
    
    if not requested_locks:
        print(f"✅ {task_id} — No locks required, can execute.")
        return
    
    current_locks = load_locks()
    conflicts = check_conflicts(requested_locks, current_locks, task_id)
    
    if conflicts:
        print(f"❌ {task_id} — BLOCKED")
        print()
        for conflict in conflicts:
            print(f"  {conflict}")
        print()
        sys.exit(1)
    else:
        print(f"✅ {task_id} — No conflicts, can execute.")
        print()
        print("Files to lock:")
        for filepath, lock_type in requested_locks.items():
            print(f"  {lock_type.upper()}: {filepath}")


def main():
    if len(sys.argv) < 2 or "--list" in sys.argv:
        list_locks()
        return
    
    plan_path = config.resolve_plan_path(sys.argv[1])
    
    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)
    
    if "--acquire" in sys.argv:
        acquire_locks(plan_path)
    elif "--release" in sys.argv:
        release_locks(plan_path)
    else:
        check_only(plan_path)


if __name__ == "__main__":
    main()
