#!/usr/bin/env python3
"""
Documentation Index Validation Library

Validates docs/_INDEX.yaml against docs/_canon/SCHEMAS/index.schema.json
Exit codes:
  0 - OK (all validations pass)
  2 - VIOLATION (schema mismatch, duplicate ID, path not found, missing/invalid category)
  3 - ERROR (YAML parse error, schema file not found, missing dependencies)

Usage:
    python scripts/_lib/docs_index_lib.py
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Exit codes (contract)
EXIT_OK = 0
EXIT_VIOLATION = 2
EXIT_ERROR = 3

# Paths (relative to repo root)
REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "docs" / "_INDEX.yaml"
SCHEMA_PATH = REPO_ROOT / "docs" / "_canon" / "SCHEMAS" / "index.schema.json"


def load_yaml(path: Path) -> Tuple[int, Any]:
    """
    Load and parse YAML file.
    
    Returns:
        (exit_code, data) - (3, None) on parse error, (0, dict) on success
    """
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed. Install: pip install PyYAML", file=sys.stderr)
        return (EXIT_ERROR, None)
    
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return (EXIT_ERROR, None)
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return (EXIT_OK, data)
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parse error in {path}: {e}", file=sys.stderr)
        return (EXIT_ERROR, None)
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}", file=sys.stderr)
        return (EXIT_ERROR, None)


def load_schema(path: Path) -> Tuple[int, Any]:
    """
    Load JSON Schema file.
    
    Returns:
        (exit_code, schema) - (3, None) on error, (0, dict) on success
    """
    if not path.exists():
        print(f"[ERROR] Schema file not found: {path}", file=sys.stderr)
        return (EXIT_ERROR, None)
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return (EXIT_OK, schema)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in schema {path}: {e}", file=sys.stderr)
        return (EXIT_ERROR, None)
    except Exception as e:
        print(f"[ERROR] Failed to read schema {path}: {e}", file=sys.stderr)
        return (EXIT_ERROR, None)


def validate_schema(instance: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate instance against JSON Schema.
    
    Returns:
        List of error messages (empty if valid)
    """
    try:
        import jsonschema
    except ImportError:
        return ["[ERROR] jsonschema not installed. Install: pip install jsonschema"]
    
    try:
        validator = jsonschema.Draft202012Validator(schema)
        errors = []
        for err in sorted(validator.iter_errors(instance), key=lambda e: str(e.json_path)):
            errors.append(f"Schema violation at {err.json_path}: {err.message}")
        return errors
    except Exception as e:
        return [f"[ERROR] Schema validation failed: {e}"]


def check_unique_ids(items: List[Dict[str, Any]]) -> List[str]:
    """
    Check for duplicate document IDs.
    
    Returns:
        List of error messages (empty if all IDs unique)
    """
    errors = []
    seen_ids = set()
    
    for item in items:
        doc_id = item.get("id")
        if not doc_id:
            continue  # Schema validation will catch this
        
        if doc_id in seen_ids:
            errors.append(f"Duplicate ID: {doc_id}")
        else:
            seen_ids.add(doc_id)
    
    return errors


def check_paths_exist(items: List[Dict[str, Any]], repo_root: Path) -> List[str]:
    """
    Check that all document paths exist in filesystem.
    
    Returns:
        List of error messages (empty if all paths valid)
    """
    errors = []
    
    for item in items:
        path_str = item.get("path")
        if not path_str:
            continue  # Schema validation will catch this
        
        # Validate no path traversal
        if ".." in path_str:
            errors.append(f"Path not found: {path_str} (path traversal not allowed)")
            continue
        
        full_path = repo_root / path_str
        if not full_path.exists():
            doc_id = item.get("id", "UNKNOWN")
            errors.append(f"Path not found: {path_str} (ID: {doc_id})")
    
    return errors


def check_category_enum(items: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[str]:
    """
    Check that all items have valid category from schema enum.
    Note: Schema validation also checks this, but we provide clearer errors here.
    
    Returns:
        List of error messages (empty if all categories valid)
    """
    errors = []
    
    # Extract valid categories from schema
    try:
        valid_categories = schema.get("$defs", {}).get("documentItem", {}).get("properties", {}).get("category", {}).get("enum", [])
    except Exception:
        valid_categories = []
    
    for item in items:
        doc_id = item.get("id", "UNKNOWN")
        category = item.get("category")
        
        if not category:
            errors.append(f"Missing category for ID: {doc_id}")
        elif valid_categories and category not in valid_categories:
            errors.append(f"Invalid category '{category}' for ID: {doc_id} (valid: {', '.join(valid_categories)})")
    
    return errors


def main() -> int:
    """
    Main validation entry point.
    
    Returns:
        Exit code (0, 2, or 3)
    """
    print(f"[INFO] Validating documentation index...")
    print(f"[INFO] Index: {INDEX_PATH}")
    print(f"[INFO] Schema: {SCHEMA_PATH}")
    print()
    
    # Load YAML
    exit_code, index_data = load_yaml(INDEX_PATH)
    if exit_code != EXIT_OK:
        return exit_code
    
    # Load Schema
    exit_code, schema_data = load_schema(SCHEMA_PATH)
    if exit_code != EXIT_OK:
        return exit_code
    
    # Collect all errors
    all_errors = []
    
    # 1. Schema validation
    schema_errors = validate_schema(index_data, schema_data)
    all_errors.extend(schema_errors)
    
    # 2. Semantic validations (only if schema passed)
    if not schema_errors:
        items = index_data.get("items", [])
        
        # Check unique IDs
        id_errors = check_unique_ids(items)
        all_errors.extend(id_errors)
        
        # Check paths exist
        path_errors = check_paths_exist(items, REPO_ROOT)
        all_errors.extend(path_errors)
        
        # Check categories
        category_errors = check_category_enum(items, schema_data)
        all_errors.extend(category_errors)
    
    # Report results
    if all_errors:
        print("[VIOLATION] Documentation index validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        print()
        print(f"Fix errors in: {INDEX_PATH}")
        return EXIT_VIOLATION
    else:
        item_count = len(index_data.get("items", []))
        print(f"[OK] Documentation index valid ({item_count} items)")
        return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
