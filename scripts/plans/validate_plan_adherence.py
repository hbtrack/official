#!/usr/bin/env python3
"""
Validate Plan Adherence
========================
Checks if the Executor followed the Plan exactly or deviated.

Usage:
    python scripts/validate_plan_adherence.py docs/plans/FASE-5-3-v1.0.md

Compares:
- Files created vs. specified in Plan
- Files modified vs. specified in Plan  
- Tests created vs. specified in Plan
- Any unexpected changes
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Set, Dict, List
from dataclasses import dataclass

try:
    from . import config
except ImportError:
    import config

PROJECT_ROOT = config.PROJECT_ROOT
BACKEND_TESTS_DIR = config.BACKEND_TESTS_DIR


@dataclass
class PlanSpec:
    """Parsed plan specifications."""
    task_id: str
    new_files: Set[str]
    modified_files: Set[str]
    test_ids: Set[str]
    branch: str


@dataclass
class ValidationReport:
    """Validation results."""
    unexpected_files: Set[str]
    missing_files: Set[str]
    unexpected_modifications: Set[str]
    missing_modifications: Set[str]
    extra_tests: Set[str]
    missing_tests: Set[str]
    
    def is_compliant(self) -> bool:
        return not any([
            self.unexpected_files,
            self.missing_files,
            self.unexpected_modifications,
            self.missing_modifications,
            self.extra_tests,
            self.missing_tests,
        ])


def parse_plan(plan_path: str) -> PlanSpec:
    """Extract specifications from Plan markdown."""
    content = Path(plan_path).read_text()
    
    # Extract TASK-ID
    task_match = re.search(r'TASK-ID[:\s]+([A-Z0-9-]+)', content, re.IGNORECASE)
    task_id = task_match.group(1) if task_match else "UNKNOWN"
    
    # Extract branch
    branch_match = re.search(r'Branch[:\s]+([a-z0-9/-]+)', content, re.IGNORECASE)
    branch = branch_match.group(1) if branch_match else "unknown"
    
    # Extract new files (section 2.4.1)
    new_files = set()
    new_files_section = re.search(r'2\.4\.1.*?Novos Arquivos(.*?)(?=2\.4\.|$)', content, re.DOTALL | re.IGNORECASE)
    if new_files_section:
        # Look for file paths in markdown tables or code blocks
        file_matches = re.findall(r'`([a-z_/]+\.py)`', new_files_section.group(1))
        new_files.update(file_matches)
    
    # Extract modified files (section 2.4.2)
    modified_files = set()
    mod_files_section = re.search(r'2\.4\.2.*?Arquivos Modificados(.*?)(?=2\.4\.|$)', content, re.DOTALL | re.IGNORECASE)
    if mod_files_section:
        file_matches = re.findall(r'`([a-z_/]+\.py)`', mod_files_section.group(1))
        modified_files.update(file_matches)
    
    # Extract test IDs (section 2.7)
    test_ids = set()
    tests_section = re.search(r'2\.7.*?Testes Obrigatórios(.*?)(?=2\.[89]|$)', content, re.DOTALL | re.IGNORECASE)
    if tests_section:
        test_matches = re.findall(r'T\d{3,4}', tests_section.group(1))
        test_ids.update(test_matches)
    
    return PlanSpec(
        task_id=task_id,
        new_files=new_files,
        modified_files=modified_files,
        test_ids=test_ids,
        branch=branch
    )


def get_git_changes(base_branch: str = "main") -> Dict[str, Set[str]]:
    """Get actual changes from git diff."""
    try:
        # Get diff against base branch
        diff_output = subprocess.run(
            f"git diff {base_branch}...HEAD --name-status",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        ).stdout
        
        new_files = set()
        modified_files = set()
        
        for line in diff_output.strip().split("\n"):
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            
            status, filepath = parts
            if filepath.endswith(".py"):
                if status == "A":
                    new_files.add(filepath)
                elif status == "M":
                    modified_files.add(filepath)
        
        return {"new": new_files, "modified": modified_files}
    
    except Exception as e:
        print(f"Error getting git changes: {e}", file=sys.stderr)
        return {"new": set(), "modified": set()}


def extract_test_ids_from_code() -> Set[str]:
    """Extract test IDs from actual test files."""
    test_ids = set()
    
    if not BACKEND_TESTS_DIR.exists():
        return test_ids
    
    for test_file in BACKEND_TESTS_DIR.rglob("test_*.py"):
        content = test_file.read_text()
        # Look for test IDs in docstrings, comments, or function names
        matches = re.findall(r'T\d{3,4}', content)
        test_ids.update(matches)
    
    return test_ids


def validate(plan_path: str, base_branch: str = "main") -> ValidationReport:
    """Main validation logic."""
    plan = parse_plan(plan_path)
    actual_changes = get_git_changes(base_branch)
    actual_test_ids = extract_test_ids_from_code()
    
    # File validation
    unexpected_files = actual_changes["new"] - plan.new_files
    missing_files = plan.new_files - actual_changes["new"]
    
    unexpected_mods = actual_changes["modified"] - plan.modified_files
    missing_mods = plan.modified_files - actual_changes["modified"]
    
    # Test validation
    extra_tests = actual_test_ids - plan.test_ids
    missing_tests = plan.test_ids - actual_test_ids
    
    return ValidationReport(
        unexpected_files=unexpected_files,
        missing_files=missing_files,
        unexpected_modifications=unexpected_mods,
        missing_modifications=missing_mods,
        extra_tests=extra_tests,
        missing_tests=missing_tests,
    )


def print_report(report: ValidationReport, plan_spec: PlanSpec):
    """Print validation report."""
    print("=" * 80)
    print(f"PLAN ADHERENCE VALIDATION — {plan_spec.task_id}")
    print("=" * 80)
    print()
    
    if report.is_compliant():
        print("✅ COMPLIANT — Executor followed the Plan exactly.")
        print()
        return
    
    print("❌ DEVIATIONS DETECTED")
    print()
    
    if report.unexpected_files:
        print("⚠️  UNEXPECTED FILES CREATED (not in Plan):")
        for f in sorted(report.unexpected_files):
            print(f"  + {f}")
        print()
    
    if report.missing_files:
        print("⚠️  MISSING FILES (specified in Plan but not created):")
        for f in sorted(report.missing_files):
            print(f"  - {f}")
        print()
    
    if report.unexpected_modifications:
        print("⚠️  UNEXPECTED MODIFICATIONS (not in Plan):")
        for f in sorted(report.unexpected_modifications):
            print(f"  M {f}")
        print()
    
    if report.missing_modifications:
        print("⚠️  MISSING MODIFICATIONS (specified in Plan but not done):")
        for f in sorted(report.missing_modifications):
            print(f"  - {f}")
        print()
    
    if report.extra_tests:
        print("⚠️  EXTRA TESTS (not specified in Plan):")
        for t in sorted(report.extra_tests):
            print(f"  + {t}")
        print()
    
    if report.missing_tests:
        print("⚠️  MISSING TESTS (specified in Plan but not implemented):")
        for t in sorted(report.missing_tests):
            print(f"  - {t}")
        print()
    
    print("=" * 80)
    print("ACTION REQUIRED:")
    print("- Review deviations with the Executor")
    print("- If deviations are justified, update the Plan")
    print("- If not justified, request Executor to fix")
    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_plan_adherence.py <plan_file.md> [base_branch]")
        sys.exit(1)
    
    plan_path = config.resolve_plan_path(sys.argv[1])
    base_branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    
    if not Path(plan_path).exists():
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)
    
    plan_spec = parse_plan(plan_path)
    report = validate(plan_path, base_branch)
    print_report(report, plan_spec)
    
    sys.exit(0 if report.is_compliant() else 1)


if __name__ == "__main__":
    main()
