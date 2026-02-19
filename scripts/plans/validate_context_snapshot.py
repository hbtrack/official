#!/usr/bin/env python3
"""
Validate Context Snapshot Against Schema v2.0
==============================================
Ensures generated snapshot complies with the schema contract.

Usage:
    python validate_context_snapshot.py snapshot.txt
    # Exit code 0 = PASS, 1 = FAIL
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from . import config
except ImportError:
    import config


# Schema validation rules (extracted from context_snapshot_schema.yaml)
REQUIRED_SECTIONS = [
    "GIT STATE",
    "BACKEND HEALTH CHECK",
    "DATABASE SCHEMA",
    "FILE STRUCTURE",
    "TEST STATISTICS",
    "DEPENDENCIES",
    "SNAPSHOT DIAGNOSTICS"
]

REQUIRED_FIELDS = {
    "GIT STATE": ["branch", "last_commit"],
    "BACKEND HEALTH CHECK": ["import_smoke_test"],
    "TEST STATISTICS": [
        "test_files_found",
        "pytest_collect_only_status",
        "pytest_collect_only_reason",
        "pytest_collect_only_cmd"
    ],
}

VALID_ENUM_VALUES = {
    "import_smoke_test": ["OK", "FAIL", "TIMEOUT", "ERROR"],
    "pytest_collect_only_status": ["OK", "FAIL", "SKIPPED", "TIMEOUT", "ERROR"],
}


def parse_snapshot(content: str) -> Dict[str, str]:
    """Parse snapshot into sections."""
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith("## "):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            # Start new section
            current_section = line.replace("## ", "").strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def extract_field_value(content: str, field_name: str) -> str:
    """Extract field value from section content."""
    pattern = rf"^{re.escape(field_name)}:\s*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def validate_snapshot(snapshot_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate snapshot against schema.
    
    Returns:
        (is_valid, errors_list)
    """
    errors = []
    
    # Read snapshot
    try:
        content = snapshot_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read snapshot: {e}"]
    
    # Check header
    if "HB TRACK" not in content[:200]:
        errors.append("Missing snapshot header 'HB TRACK — CONTEXT SNAPSHOT'")
    
    # Parse sections
    sections = parse_snapshot(content)
    
    # Validate required sections exist
    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"Missing required section: {section}")
    
    # Validate required fields in sections
    for section, fields in REQUIRED_FIELDS.items():
        if section not in sections:
            continue  # Already reported above
        
        section_content = sections[section]
        
        for field in fields:
            value = extract_field_value(section_content, field)
            if value is None:
                errors.append(f"Missing required field '{field}' in section '{section}'")
            else:
                # Validate enum values
                if field in VALID_ENUM_VALUES:
                    # Extract just the status part (before parenthesis)
                    status = value.split('(')[0].strip()
                    if status not in VALID_ENUM_VALUES[field]:
                        errors.append(
                            f"Invalid value '{status}' for field '{field}'. "
                            f"Expected one of: {', '.join(VALID_ENUM_VALUES[field])}"
                        )
    
    # Validate SNAPSHOT DIAGNOSTICS structure
    if "SNAPSHOT DIAGNOSTICS" in sections:
        diag_content = sections["SNAPSHOT DIAGNOSTICS"]
        
        if "ERRORS:" not in diag_content:
            errors.append("SNAPSHOT DIAGNOSTICS missing 'ERRORS:' subsection")
        
        if "WARNINGS:" not in diag_content:
            errors.append("SNAPSHOT DIAGNOSTICS missing 'WARNINGS:' subsection")
        
        if "BLOCKING CONDITIONS:" not in diag_content:
            errors.append("SNAPSHOT DIAGNOSTICS missing 'BLOCKING CONDITIONS:' subsection")
    
    # Validate test_files_found is a number
    if "TEST STATISTICS" in sections:
        test_files = extract_field_value(sections["TEST STATISTICS"], "test_files_found")
        if test_files and not test_files.isdigit():
            errors.append(f"test_files_found should be integer, got: {test_files}")
    
    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_context_snapshot.py <snapshot_file>")
        print("\nOr generate and validate in one step:")
        print("  python generate_context_snapshot.py PLAN.md > temp_snapshot.txt")
        print("  python validate_context_snapshot.py temp_snapshot.txt")
        sys.exit(1)
    
    snapshot_path = Path(sys.argv[1])
    
    if not snapshot_path.exists():
        print(f"❌ ERROR: Snapshot file not found: {snapshot_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("CONTEXT SNAPSHOT VALIDATOR v2.0")
    print("=" * 80)
    print(f"Validating: {snapshot_path}")
    print()
    
    is_valid, errors = validate_snapshot(snapshot_path)
    
    if is_valid:
        print("✅ PASS: Snapshot is valid and complies with schema v2.0")
        print()
        print("Validated:")
        print(f"  - All {len(REQUIRED_SECTIONS)} required sections present")
        print(f"  - All required fields present with valid types")
        print(f"  - Enum values conform to allowed values")
        print(f"  - SNAPSHOT DIAGNOSTICS structure correct")
        sys.exit(0)
    else:
        print(f"❌ FAIL: Found {len(errors)} validation error(s):")
        print()
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print()
        print("Action: Fix snapshot generation to comply with schema v2.0")
        print("Schema: scripts/plans/docs/context_snapshot_schema.yaml")
        sys.exit(1)


if __name__ == "__main__":
    main()
