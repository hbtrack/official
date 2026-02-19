#!/usr/bin/env python3
"""
Executor Workflow Orchestrator
================================
Main script to orchestrate the complete Architect-Executor flow.
Integrates all validation steps and provides a unified interface.

Usage:
    # Full workflow (dry-run → execute → validate → commit)
    python scripts/executor_workflow.py docs/plans/FASE-5-3.md
    
    # Dry-run only
    python scripts/executor_workflow.py docs/plans/FASE-5-3.md --dry-run
    
    # Skip dry-run (dangerous!)
    python scripts/executor_workflow.py docs/plans/FASE-5-3.md --skip-dry-run
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from . import config
except ImportError:
    import config

SCRIPTS_PLANS_ROOT = config.SCRIPTS_PLANS_ROOT
PROJECT_ROOT = config.PROJECT_ROOT
HB_BACKEND_DIR = config.HB_BACKEND_DIR
IMPLEMENTED_DIR = config.IMPLEMENTED_DIR
PLANS_DIR = config.PLANS_DIR


class WorkflowError(Exception):
    """Workflow execution error."""
    pass


def run_command(cmd: str, description: str, can_fail: bool = False) -> bool:
    """Run a command and report status."""
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"{'='*80}")
    print(f"$ {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        if can_fail:
            print(f"\n⚠️  {description} — non-zero exit code (continuing)\n")
            return False
        else:
            print(f"\n❌ {description} — FAILED\n")
            raise WorkflowError(f"{description} failed with exit code {result.returncode}")
    
    print(f"\n✅ {description} — SUCCESS\n")
    return True


def check_prerequisites():
    """Check that required scripts exist."""
    required_scripts = [
        SCRIPTS_PLANS_ROOT / "generate_context_snapshot.py",
        SCRIPTS_PLANS_ROOT / "validate_plan_adherence.py",
        SCRIPTS_PLANS_ROOT / "check_locks.py",
        SCRIPTS_PLANS_ROOT / "plan_status.py",
    ]
    
    for script in required_scripts:
        if not script.exists():
            raise WorkflowError(f"Required script not found: {script}")


def validate_plan_file(plan_path: Path):
    """Basic validation of Plan file."""
    if not plan_path.exists():
        raise WorkflowError(f"Plan file not found: {plan_path}")
    
    content = plan_path.read_text()
    
    # Check for required sections
    required = ["TASK-ID", "Status", "Contrato de Entrada", "Critérios de Conclusão"]
    missing = [r for r in required if r not in content]
    
    if missing:
        raise WorkflowError(f"Plan missing required sections: {', '.join(missing)}")


def pre_execution_checks(plan_path: Path):
    """Run all pre-execution validation."""
    print("\n" + "="*80)
    print("PRE-EXECUTION CHECKS")
    print("="*80 + "\n")
    
    # 1. Check Plan status
    run_command(
        f"python scripts/plan_status.py {plan_path}",
        "Checking Plan status"
    )
    
    # 2. Check file locks
    run_command(
        f"python scripts/check_locks.py {plan_path}",
        "Checking file locks"
    )
    
    # 3. Verify git state
    print("\n" + "-"*80)
    print("Git State:")
    print("-"*80)
    subprocess.run("git status --short", shell=True)
    print()
    
    response = input("Git state OK to proceed? (y/n): ")
    if response.lower() != 'y':
        raise WorkflowError("Aborted by user — git state not clean")


def dry_run_phase(plan_path: Path):
    """Execute dry-run phase."""
    print("\n" + "="*80)
    print("DRY-RUN PHASE")
    print("="*80)
    print()
    print("In this phase, you should:")
    print("  1. Open VS Code")
    print("  2. Load the Plan file")
    print("  3. Ask the AI to analyze feasibility WITHOUT making changes")
    print("  4. Review AI's report for:")
    print("     - Missing dependencies")
    print("     - Invalid imports")
    print("     - Conflicting changes")
    print()
    
    response = input("Dry-run completed successfully? (y/n): ")
    if response.lower() != 'y':
        print("\n⚠️  Dry-run issues detected.")
        print("Action required:")
        print("  1. Report issues to Architect")
        print("  2. Get updated Plan (v1.1)")
        print("  3. Re-run this workflow with new Plan")
        sys.exit(1)


def execution_phase(plan_path: Path):
    """Execute the Plan with Executor."""
    print("\n" + "="*80)
    print("EXECUTION PHASE")
    print("="*80)
    print()
    print("Ready to execute with Executor AI.")
    print()
    print("IMPORTANT:")
    print("  - Create executor branch first: git checkout -b executor/TASK-ID")
    print("  - Give the AI both the Plan AND the Executor prompt")
    print("  - Monitor for blocking situations")
    print()
    
    response = input("Continue with execution? (y/n): ")
    if response.lower() != 'y':
        raise WorkflowError("Execution aborted by user")
    
    # Acquire locks
    run_command(
        f"python scripts/check_locks.py {plan_path} --acquire",
        "Acquiring file locks"
    )
    
    print("\n" + "-"*80)
    print("Execute in VS Code now.")
    print("Press ENTER when Executor reports completion...")
    input()


def post_execution_validation(plan_path: Path):
    """Run all post-execution checks."""
    print("\n" + "="*80)
    print("POST-EXECUTION VALIDATION")
    print("="*80 + "\n")
    
    # 1. Validate Plan adherence
    run_command(
        f"python scripts/validate_plan_adherence.py {plan_path}",
        "Validating Plan adherence",
        can_fail=True
    )
    
    # 2. Run test suite
    run_command(
        "pytest -v",
        "Running test suite"
    )
    
    # 3. Run linters
    run_command(
        "ruff check .",
        "Running ruff linter",
        can_fail=True
    )
    
    run_command(
        "mypy app/",
        "Running mypy type checker",
        can_fail=True
    )
    
    # 4. Validate invariants (if script exists)
    invariants_script = PROJECT_ROOT / "scripts" / "validate_invariants.py"
    if invariants_script.exists():
        run_command(
            f"python {invariants_script}",
            "Validating business invariants",
            can_fail=True
        )


def homologation_phase():
    """Manual homologation by human."""
    print("\n" + "="*80)
    print("HOMOLOGATION PHASE")
    print("="*80)
    print()
    print("Manual checks:")
    print("  □ Test the happy path manually")
    print("  □ Verify git diff makes sense")
    print("  □ Check audit logs generated correctly")
    print("  □ Implementation makes sense for business")
    print()
    
    response = input("Homologation passed? (y/n): ")
    if response.lower() != 'y':
        print("\n❌ Homologation FAILED")
        print()
        print("Action required:")
        print("  1. Document what's wrong")
        print("  2. Report to Architect for Plan update")
        print("  3. Delete executor branch: git branch -D executor/TASK-ID")
        print("  4. Release locks: python scripts/check_locks.py --release")
        sys.exit(1)


def finalization_phase(plan_path: Path):
    """Finalize execution — merge, commit, update status."""
    print("\n" + "="*80)
    print("FINALIZATION PHASE")
    print("="*80)
    print()
    
    # Get task ID from plan
    content = plan_path.read_text()
    import re
    match = re.search(r'TASK-ID[:\s]+([A-Z0-9-]+)', content, re.IGNORECASE)
    task_id = match.group(1) if match else "UNKNOWN"
    
    print("Recommended commit strategy:")
    print(f"  1. Review all changes: git diff")
    print(f"  2. Stage files: git add .")
    print(f"  3. Commit: git commit -m '[{task_id}] feat: description'")
    print(f"  4. Merge: git checkout main && git merge --squash executor/{task_id}")
    print()
    
    response = input("Create commits now? (y/n): ")
    if response.lower() != 'y':
        print("\n⚠️  Skipping commits. Remember to commit manually.")
    
    # Mark Plan as executed
    run_command(
        f"python scripts/plan_status.py {plan_path} --executed",
        "Marking Plan as EXECUTADO"
    )
    
    # Release locks
    implemented_path = IMPLEMENTED_DIR / plan_path.name
    run_command(
        f"python scripts/check_locks.py {implemented_path} --release",
        "Releasing file locks"
    )
    
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    print()
    print(f"Task {task_id} successfully executed!")
    print()
    print("Next steps:")
    print("  1. Push to remote: git push")
    print("  2. Update project kanban")
    print("  3. Deploy to staging for smoke tests")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/executor_workflow.py <plan.md>")
        print("  python scripts/executor_workflow.py <plan.md> --dry-run")
        print("  python scripts/executor_workflow.py <plan.md> --skip-dry-run")
        sys.exit(1)
    
    plan_path = config.resolve_plan_path(sys.argv[1])
    skip_dry_run = "--skip-dry-run" in sys.argv
    dry_run_only = "--dry-run" in sys.argv
    
    try:
        print("="*80)
        print("HB TRACK — EXECUTOR WORKFLOW")
        print("="*80)
        print(f"Plan: {plan_path}")
        print(f"Time: {datetime.now().isoformat()}")
        print("="*80)
        
        # Pre-flight
        check_prerequisites()
        validate_plan_file(plan_path)
        
        # Phase 1: Pre-execution
        pre_execution_checks(plan_path)
        
        # Phase 2: Dry-run
        if not skip_dry_run:
            dry_run_phase(plan_path)
        else:
            print("\n⚠️  SKIPPING DRY-RUN (--skip-dry-run flag)")
        
        if dry_run_only:
            print("\n✅ Dry-run complete. Exiting (--dry-run flag).")
            sys.exit(0)
        
        # Phase 3: Execution
        execution_phase(plan_path)
        
        # Phase 4: Post-execution validation
        post_execution_validation(plan_path)
        
        # Phase 5: Homologation
        homologation_phase()
        
        # Phase 6: Finalization
        finalization_phase(plan_path)
    
    except WorkflowError as e:
        print(f"\n❌ Workflow Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user.")
        print("State may be inconsistent. Check git status and file locks.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
