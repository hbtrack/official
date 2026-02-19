#!/usr/bin/env python3
"""
Generate Context Snapshot for Architect
========================================
Collects current repo state to send to the Architect AI.
Prevents the Architect from making technically impossible plans.

Usage:
    python scripts/generate_context_snapshot.py > context.txt
    # Then send context.txt to the Architect along with your request
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import re

try:
    from . import config
except ImportError:
    import config

# Global error/warning collector
SNAPSHOT_ERRORS = []
SNAPSHOT_WARNINGS = []

PROJECT_ROOT = config.PROJECT_ROOT
HB_BACKEND_DIR = config.HB_BACKEND_DIR
BACKEND_MODELS_DIR = config.BACKEND_MODELS_DIR
BACKEND_REQUIREMENTS = config.BACKEND_REQUIREMENTS
BACKEND_PYPROJECT = config.BACKEND_PYPROJECT
BACKEND_ALEMBIC_DIR = config.BACKEND_ALEMBIC_DIR
BACKEND_TESTS_DIR = config.BACKEND_TESTS_DIR


def sanitize_stderr(text: str, max_lines: int = 10, max_chars: int = 500) -> str:
    """Sanitize stderr: limit length, remove secrets."""
    if not text:
        return "(empty)"
    
    # Remove potential secrets (common patterns)
    secrets_patterns = [
        (r'DATABASE_URL=.*', 'DATABASE_URL=***'),
        (r'SECRET_KEY=.*', 'SECRET_KEY=***'),
        (r'API_KEY=.*', 'API_KEY=***'),
        (r'PASSWORD=.*', 'PASSWORD=***'),
        (r'TOKEN=.*', 'TOKEN=***'),
    ]
    
    for pattern, replacement in secrets_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Limit to first N lines
    lines = text.split('\n')[:max_lines]
    result = '\n'.join(lines)
    
    # Truncate to max chars
    if len(result) > max_chars:
        result = result[:max_chars] + "...(truncated)"
    
    return result


def run_cmd(cmd: str, cwd=None) -> str:
    """Execute shell command and return output."""
    if cwd is None:
        cwd = str(PROJECT_ROOT)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[ERROR: {e}]"


def get_git_info():
    """Collect Git state."""
    return {
        "branch": run_cmd("git branch --show-current"),
        "last_commit": run_cmd("git log -1 --oneline"),
        "uncommitted_files": run_cmd("git status --short"),
    }


def get_database_schema():
    """Collect current database schema info."""
    schema = {
        "current_migration": run_cmd("alembic current 2>/dev/null || echo 'N/A'", cwd=str(HB_BACKEND_DIR)),
        "pending_migrations": run_cmd("alembic heads 2>/dev/null || echo 'N/A'", cwd=str(HB_BACKEND_DIR)),
    }
    
    # Try to get table list from models
    if BACKEND_MODELS_DIR.exists():
        model_files = [f.name for f in BACKEND_MODELS_DIR.glob("*.py") if f.name != "__init__.py"]
        schema["model_files"] = model_files
    
    return schema


def get_file_structure():
    """Get relevant directory structure with deterministic ordering."""
    structure = {}
    SAMPLE_LIMIT = 20
    
    important_dirs = [
        ("app/models", BACKEND_MODELS_DIR),
        ("app/api", BACKEND_MODELS_DIR.parent / "api"),
        ("app/schemas", BACKEND_MODELS_DIR.parent / "schemas"),
        ("app/services", BACKEND_MODELS_DIR.parent / "services"),
        ("tests", BACKEND_TESTS_DIR),
    ]
    
    for label, dir_path in important_dirs:
        if dir_path.exists():
            # List Python files using pathlib (cross-platform) with deterministic sort
            py_files = sorted(dir_path.glob("*.py"), key=lambda p: p.name.lower())
            total_count = len(py_files)
            
            if py_files:
                sample = py_files[:SAMPLE_LIMIT]
                file_list = "\n".join(f"  - {f.name}" for f in sample)
                if total_count > SAMPLE_LIMIT:
                    structure[label] = f"{total_count} Python files (showing first {SAMPLE_LIMIT}):\n{file_list}"
                else:
                    structure[label] = f"{total_count} Python files:\n{file_list}"
            else:
                # Try recursive for tests
                py_files = sorted(dir_path.rglob("*.py"), key=lambda p: str(p).lower())
                total_count = len(py_files)
                
                if py_files:
                    sample = py_files[:SAMPLE_LIMIT]
                    file_list = "\n".join(f"  - {f.relative_to(dir_path)}" for f in sample)
                    if total_count > SAMPLE_LIMIT:
                        structure[label] = f"{total_count} files recursive (showing first {SAMPLE_LIMIT}):\n{file_list}"
                    else:
                        structure[label] = f"{total_count} files (recursive):\n{file_list}"
                else:
                    structure[label] = "(empty directory)"
        else:
            structure[label] = "(directory does not exist)"
    
    return structure


def get_test_stats():
    """Get test suite statistics (factual file count + optional pytest validation)."""
    if not BACKEND_TESTS_DIR.exists():
        return {
            "test_files_found": 0,
            "recent_tests": "(tests directory does not exist)",
            "pytest_collect_only_status": "SKIPPED",
            "pytest_collect_only_reason": "tests directory does not exist",
            "pytest_collect_only_cmd": "N/A",
        }
    
    # Count test files using pathlib (cross-platform, deterministic)
    test_files = sorted(BACKEND_TESTS_DIR.rglob("test_*.py"), key=lambda p: str(p).lower())
    test_count = len(test_files)
    
    # Get recently modified test files for context
    recent_tests = sorted(test_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    recent_list = "\n".join(f"  - {f.relative_to(BACKEND_TESTS_DIR)}" for f in recent_tests) if recent_tests else "(no test files)"
    
    # Optional: run pytest --collect-only for validation (with longer timeout)
    pytest_cmd = f"{sys.executable} -m pytest --collect-only -q"
    pytest_status = "SKIPPED"
    pytest_reason = "not executed"
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(HB_BACKEND_DIR),
            capture_output=True,
            text=True,
            timeout=30  # Increased from 5s to 30s for large test suites
        )
        
        if result.returncode == 0:
            # Extract collection summary from pytest output
            lines = result.stdout.strip().split("\n")
            summary = lines[-1] if lines else "collected"
            pytest_status = "OK"
            pytest_reason = summary
        else:
            # Analyze stderr to determine failure type
            stderr_clean = sanitize_stderr(result.stderr, max_lines=5, max_chars=200)
            
            if "No module named 'pytest'" in result.stderr or "No module named pytest" in result.stderr:
                pytest_status = "SKIPPED"
                pytest_reason = "pytest not installed in current environment"
                SNAPSHOT_WARNINGS.append({
                    "code": "SNAP-PYTEST-001",
                    "severity": "WARN",
                    "message": "pytest not installed - cannot validate test collection",
                    "action": "Install pytest to enable test validation"
                })
            elif "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
                first_error = stderr_clean.split("\n")[0]
                pytest_status = "FAIL"
                pytest_reason = f"import error: {first_error[:100]}"
                SNAPSHOT_ERRORS.append({
                    "code": "SNAP-PYTEST-002",
                    "severity": "ERROR",
                    "message": f"Test collection failed due to import error: {first_error[:80]}",
                    "action": "Fix import errors in tests/conftest before refactoring"
                })
            else:
                first_error = stderr_clean.split("\n")[0] if stderr_clean else "unknown error"
                pytest_status = "FAIL"
                pytest_reason = first_error[:100]
                SNAPSHOT_ERRORS.append({
                    "code": "SNAP-PYTEST-003",
                    "severity": "ERROR",
                    "message": f"Test collection failed: {first_error[:80]}",
                    "action": "Fix pytest collection errors before running tests"
                })
                
    except subprocess.TimeoutExpired:
        pytest_status = "TIMEOUT"
        pytest_reason = "collection took >30s (likely slow imports or large test suite)"
        SNAPSHOT_WARNINGS.append({
            "code": "SNAP-PYTEST-004",
            "severity": "WARN",
            "message": "pytest collection timeout >30s",
            "action": "Optimize test imports or increase timeout for large test suites"
        })
    except FileNotFoundError:
        pytest_status = "SKIPPED"
        pytest_reason = "pytest command not found in PATH"
    except Exception as e:
        pytest_status = "ERROR"
        pytest_reason = str(e)[:100]
    
    return {
        "test_files_found": test_count,
        "recent_tests": recent_list,
        "pytest_collect_only_status": pytest_status,
        "pytest_collect_only_reason": pytest_reason,
        "pytest_collect_only_cmd": pytest_cmd,
    }


def get_backend_health():
    """Check if backend can be imported (smoke test)."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import app; print('OK')"],
            cwd=str(HB_BACKEND_DIR),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "OK" in result.stdout:
            return "OK (app module imports successfully)"
        else:
            error_line = sanitize_stderr(result.stderr).split("\n")[0] if result.stderr else "FAIL"
            SNAPSHOT_ERRORS.append({
                "code": "SNAP-BACKEND-001",
                "severity": "ERROR",
                "message": f"Backend import failed: {error_line[:80]}",
                "action": "Fix import errors before refactoring core modules"
            })
            return f"FAIL (import error: {error_line[:80]})"
    except subprocess.TimeoutExpired:
        SNAPSHOT_WARNINGS.append({
            "code": "SNAP-BACKEND-002",
            "severity": "WARN",
            "message": "Backend import timeout >5s (possible circular import)",
            "action": "Investigate slow imports before adding new imports"
        })
        return "TIMEOUT (import took >5s)"
    except Exception as e:
        return f"ERROR ({str(e)[:50]})"


def get_dependencies():
    """Get installed dependencies."""
    deps = {}
    
    if BACKEND_REQUIREMENTS.exists():
        # Deterministic: sort dependencies alphabetically
        lines = BACKEND_REQUIREMENTS.read_text().strip().split("\n")
        deps["requirements"] = sorted([l for l in lines if l and not l.startswith("#")])[:20]
    
    if BACKEND_PYPROJECT.exists():
        deps["pyproject_exists"] = True
    
    return deps


def get_invariants():
    """Get documented invariants (deterministic order)."""
    invariants_file = PROJECT_ROOT / "docs" / "invariants.md"
    if invariants_file.exists():
        content = invariants_file.read_text()
        # Extract just the invariant IDs and sort deterministically
        lines = sorted([l.strip() for l in content.split("\n") if l.strip().startswith("INV-")])
        return lines[:20]  # First 20 invariants
    return []


def get_recent_migrations():
    """Get last 3 migrations."""
    migrations_dir = BACKEND_ALEMBIC_DIR / "versions"
    if migrations_dir.exists():
        migrations = sorted(migrations_dir.glob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [m.name for m in migrations[:3]]
    return []


def get_env_vars():
    """Get required environment variables (names only, not values)."""
    env_file = HB_BACKEND_DIR / ".env.example"
    if env_file.exists():
        lines = env_file.read_text().strip().split("\n")
        return [l.split("=")[0] for l in lines if "=" in l and not l.startswith("#")]
    return []


def main():
    print("=" * 80)
    print("HB TRACK — CONTEXT SNAPSHOT FOR ARCHITECT")
    print("=" * 80)
    print(f"Generated at: {datetime.now().isoformat()}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Backend dir: {HB_BACKEND_DIR}")
    print()
    
    print("## GIT STATE")
    print("-" * 80)
    git_info = get_git_info()
    for key, value in git_info.items():
        print(f"{key}: {value}")
    print()
    
    print("## BACKEND HEALTH CHECK")
    print("-" * 80)
    health = get_backend_health()
    print(f"import_smoke_test: {health}")
    print()
    
    print("## DATABASE SCHEMA")
    print("-" * 80)
    schema = get_database_schema()
    for key, value in schema.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")
    print()
    
    print("## FILE STRUCTURE")
    print("-" * 80)
    structure = get_file_structure()
    for dir_path, content in structure.items():
        print(f"\n{dir_path}:")
        print(content)
    print()
    
    print("## TEST STATISTICS")
    print("-" * 80)
    test_stats = get_test_stats()
    print(f"test_files_found: {test_stats.get('test_files_found', 0)}")
    print(f"pytest_collect_only_status: {test_stats.get('pytest_collect_only_status', 'N/A')}")
    print(f"pytest_collect_only_reason: {test_stats.get('pytest_collect_only_reason', 'N/A')}")
    print(f"pytest_collect_only_cmd: {test_stats.get('pytest_collect_only_cmd', 'N/A')}")
    print(f"\\nRecent test files:")
    print(test_stats.get('recent_tests', '(none)'))
    print()
    
    print("## DEPENDENCIES")
    print("-" * 80)
    deps = get_dependencies()
    if "requirements" in deps:
        print("Key requirements (first 20):")
        for req in deps["requirements"]:
            if req.strip():
                print(f"  - {req}")
    print()
    
    print("## INVARIANTS")
    print("-" * 80)
    invariants = get_invariants()
    if invariants:
        print(f"Total invariants documented: {len(invariants)}")
        for inv in invariants:
            print(f"  {inv}")
    else:
        print("No invariants documented yet.")
    print()
    
    print("## RECENT MIGRATIONS")
    print("-" * 80)
    migrations = get_recent_migrations()
    if migrations:
        print("Last 3 migrations:")
        for m in migrations:
            print(f"  - {m}")
    else:
        print("No migrations found.")
    print()
    
    print("## REQUIRED ENVIRONMENT VARIABLES")
    print("-" * 80)
    env_vars = get_env_vars()
    if env_vars:
        for var in env_vars:
            print(f"  - {var}")
    else:
        print("No .env.example found.")
    print()
    
    # NEW: Errors and Warnings section
    print("## SNAPSHOT DIAGNOSTICS")
    print("-" * 80)
    
    if SNAPSHOT_ERRORS:
        print("ERRORS:")
        for err in SNAPSHOT_ERRORS:
            print(f"  [{err['code']}] {err['severity']}: {err['message']}")
            print(f"    -> Action: {err['action']}")
    else:
        print("ERRORS: (none)")
    
    print()
    
    if SNAPSHOT_WARNINGS:
        print("WARNINGS:")
        for warn in SNAPSHOT_WARNINGS:
            print(f"  [{warn['code']}] {warn['severity']}: {warn['message']}")
            print(f"    -> Action: {warn['action']}")
    else:
        print("WARNINGS: (none)")
    print()
    
    # Summary of blocking conditions
    print("BLOCKING CONDITIONS:")
    backend_health = get_backend_health()  # Already called, but check again for summary
    has_blocking = False
    
    if "FAIL" in backend_health:
        print("  [BLOCK] Backend import FAIL -> BLOCKS plans modifying imports/core modules")
        has_blocking = True
    
    # Check pytest for FAIL with import error (not SKIPPED/TIMEOUT)
    pytest_status = test_stats.get('pytest_collect_only_status', '')
    pytest_reason = test_stats.get('pytest_collect_only_reason', '')
    if pytest_status == "FAIL" and ("import" in pytest_reason.lower() or "module" in pytest_reason.lower()):
        print("  [BLOCK] Pytest collection FAIL (import error) -> BLOCKS test refactoring")
        has_blocking = True
    
    if not has_blocking:
        print("  [OK] No blocking conditions detected")
    
    print()
    print("=" * 80)
    
    print("=" * 80)
    print("END OF SNAPSHOT")
    print("=" * 80)
    print()
    print("INSTRUCTIONS FOR ARCHITECT:")
    print("- Use this snapshot to understand current repo state")
    print("- Do NOT specify changes to files/tables that don't exist")
    print("- Do NOT create migrations for tables that already exist")
    print("- Verify your Plan against this snapshot before declaring it complete")


if __name__ == "__main__":
    main()
