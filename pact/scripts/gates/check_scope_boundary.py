#!/usr/bin/env python3
"""
check_scope_boundary.py — Validador de Scope Boundary entre Módulos

Detecta referências cross-module indevidas em artefatos contratuais (OpenAPI, Schema, Arazzo, AsyncAPI).
Integrado ao pipeline de pre-contrato em Fase 1 (após MODULE_REGISTRY_GATE).

Exit codes:
  0: PASS — sem violações de boundary
  1: BLOCKED_SCOPE_OVERFLOW — violação de boundary detectada
  2: ERROR_ARTIFACT_MALFORMED — artefato inválido (JSON/YAML)
  3: ERROR_POLICY_MISSING — SCOPE_BOUNDARY_POLICY.md não encontrado
  4: ERROR_MODULE_UNKNOWN — módulo de origem não reconhecido

Uso:
  check_scope_boundary.py <artifact_path> [--module <module_name>] [--json]

Exemplos:
  check_scope_boundary.py contracts/openapi/paths/users.yaml
  check_scope_boundary.py contracts/schemas/training/session.schema.json --module training
  check_scope_boundary.py contracts/workflows/training.arazzo.yaml --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    yaml = None


# ============================================================================
# CONSTANTS
# ============================================================================

CANONICAL_MODULES = {
    "users",
    "seasons",
    "teams",
    "training",
    "wellness",
    "medical",
    "competitions",
    "matches",
    "scout",
    "exercises",
    "analytics",
    "reports",
    "ai_ingestion",
    "identity_access",
    "audit",
    "notifications",
    "video",
}

EXIT_CODES = {
    "PASS": 0,
    "BLOCKED_SCOPE_OVERFLOW": 1,
    "ERROR_ARTIFACT_MALFORMED": 2,
    "ERROR_POLICY_MISSING": 3,
    "ERROR_MODULE_UNKNOWN": 4,
}


# ============================================================================
# UTILS: File Loading
# ============================================================================

def load_yaml_or_json(path: str) -> Optional[Dict[str, Any]]:
    """Load YAML or JSON file safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try YAML first (YAML is superset of JSON)
        if yaml:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                pass

        # Fallback to JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    except (IOError, OSError):
        return None


def load_policy(workspace_root: str = ".") -> Optional[Dict[str, Any]]:
    """Load SCOPE_BOUNDARY_POLICY.md and parse YAML block."""
    policy_path = os.path.join(workspace_root, "docs/_canon/SCOPE_BOUNDARY_POLICY.md")
    if not os.path.exists(policy_path):
        return None

    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter + module sections
        # Policy structure: YAML header + Markdown sections with YAML blocks
        # We'll parse the allowed_references and forbidden_references by module

        policy = {"modules": {}}

        # Parse each module section (## 2. Matriz de Boundaries por Módulo)
        # Sections are like: ### users
        #                    allowed_references: ...
        #                    forbidden_references: ...

        # For robustness, we'll use regex to find module blocks and extract YAML
        module_pattern = r"^### (\w+)\s*\n(.*?)(?=^### |\Z)"
        for match in re.finditer(module_pattern, content, re.MULTILINE | re.DOTALL):
            module_name = match.group(1)
            module_content = match.group(2)

            # Extract allowed_references (list after "allowed_references:")
            allowed = _extract_yaml_list(module_content, "allowed_references")
            forbidden = _extract_yaml_list(module_content, "forbidden_references")

            policy["modules"][module_name] = {
                "allowed_references": allowed,
                "forbidden_references": forbidden,
            }

        return policy if policy["modules"] else None

    except Exception as e:
        print(f"DEBUG: Error loading policy: {e}", file=sys.stderr)
        return None


def _extract_yaml_list(text: str, key: str) -> Set[str]:
    """Extract list of module names from YAML block for a specific key.
    
    Handles format:
      allowed_references:
        - module: users
          reason: "..."
          examples: [...]
        - module: teams
        ...
    
    Stops at next key (forbidden_references, exceptions, etc.)
    """
    result = set()

    # Find the line "allowed_references:" or "forbidden_references:"
    key_line_pattern = rf"{re.escape(key)}:\s*$"
    key_match = re.search(key_line_pattern, text, re.MULTILINE)
    
    if not key_match:
        return result

    # Start from after the key line and find all "- module: <name>" until next key
    start_idx = key_match.end()
    rest_of_text = text[start_idx:]
    
    # Look for the next key-like pattern: "word:" or "word: " at beginning of line or after newline
    # But be careful not to stop at indented content
    # A key is: line starting with "^[a-z_]+:", possibly with spaces before it
    next_key_pattern = r"^[a-z_]+:\s*$"
    next_key_match = re.search(next_key_pattern, rest_of_text, re.MULTILINE)
    
    if next_key_match:
        section = rest_of_text[:next_key_match.start()]
    else:
        section = rest_of_text

    # Extract module names from "- module: <module_name>" patterns
    pattern = r"-\s+module:\s+(\w+)"
    for match in re.finditer(pattern, section):
        module = match.group(1)
        if module in CANONICAL_MODULES:
            result.add(module)

    return result


# ============================================================================
# MODULE EXTRACTION
# ============================================================================

def extract_module_from_path(artifact_path: str) -> Optional[str]:
    """
    Extract module name from artifact path.
    
    Conventions:
      contracts/openapi/paths/{module}.yaml
      contracts/schemas/{module}/*.schema.json
      contracts/workflows/{module}.arazzo.yaml
      contracts/asyncapi/{module}/*.yaml
    
    Examples:
      contracts/openapi/paths/users.yaml → users
      contracts/schemas/training/session.schema.json → training
      contracts/workflows/training.arazzo.yaml → training
    """
    path = artifact_path.lower().replace("\\", "/")

    # Pattern 1: contracts/openapi/paths/{module}.yaml
    match = re.search(r"contracts/openapi/paths/(\w+)\.yaml", path)
    if match:
        return match.group(1)

    # Pattern 2: contracts/schemas/{module}/
    match = re.search(r"contracts/schemas/(\w+)/", path)
    if match:
        return match.group(1)

    # Pattern 3: contracts/workflows/{module}.arazzo.yaml
    match = re.search(r"contracts/workflows/(\w+)\.arazzo\.yaml", path)
    if match:
        return match.group(1)

    # Pattern 4: contracts/asyncapi/{module}/
    match = re.search(r"contracts/asyncapi/(\w+)/", path)
    if match:
        return match.group(1)

    # Pattern 5: contracts/{module}/
    match = re.search(r"contracts/(\w+)/", path)
    if match:
        module = match.group(1)
        if module not in ["openapi", "schemas", "workflows", "asyncapi", "consumers"]:
            return module

    return None


# ============================================================================
# REFERENCE EXTRACTION
# ============================================================================

def extract_references(artifact: Dict[str, Any], artifact_type: str = "unknown") -> Set[str]:
    """
    Extract all cross-module references from an artifact.
    
    Returns set of module names referenced.
    Handles:
      - OpenAPI: operationId, servers, $ref
      - JSON Schema: $ref
      - Arazzo: workflows refs
      - AsyncAPI: channels, servers
    """
    refs = set()

    # $ref patterns (JSON Schema, OpenAPI)
    refs.update(_extract_refs_recursive(artifact))

    # operationId patterns (OpenAPI)
    refs.update(_extract_operation_ids(artifact))

    # servers patterns
    refs.update(_extract_servers(artifact))

    # AsyncAPI channels
    refs.update(_extract_asyncapi_channels(artifact))

    return refs


def _extract_refs_recursive(obj: Any, visited: Optional[Set[int]] = None) -> Set[str]:
    """Recursively extract $ref values from nested structure."""
    if visited is None:
        visited = set()

    refs = set()

    # Avoid infinite loops on circular references
    obj_id = id(obj)
    if obj_id in visited:
        return refs
    visited.add(obj_id)

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                # Extract module from $ref
                # Formats: "#/components/schemas/TrainingSession"
                #          "training/session.schema.json"
                refs.update(_parse_ref_string(value))

            elif isinstance(value, (dict, list)):
                refs.update(_extract_refs_recursive(value, visited))

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                refs.update(_extract_refs_recursive(item, visited))

    return refs


def _parse_ref_string(ref: str) -> Set[str]:
    """Parse $ref string to extract potential module references."""
    modules = set()

    # Format: file reference like "training/session.schema.json"
    match = re.match(r"^(\w+)/", ref)
    if match:
        modules.add(match.group(1))

    # Format: internal reference like "#/components/schemas/TrainingSession"
    # These are typically not cross-module, but we could infer from naming
    # For now, we skip these as they're internal

    return modules


def _extract_operation_ids(obj: Any, refs: Optional[Set[str]] = None) -> Set[str]:
    """Extract module hints from operationId patterns."""
    if refs is None:
        refs = set()

    if isinstance(obj, dict):
        # operationId format: "{module}.{operation}"
        if "operationId" in obj and isinstance(obj["operationId"], str):
            op_id = obj["operationId"]
            # Format: "training.create_session"
            if "." in op_id:
                module = op_id.split(".")[0]
                if module in CANONICAL_MODULES:
                    refs.add(module)

        for value in obj.values():
            if isinstance(value, (dict, list)):
                _extract_operation_ids(value, refs)

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _extract_operation_ids(item, refs)

    return refs


def _extract_servers(obj: Any, refs: Optional[Set[str]] = None) -> Set[str]:
    """Extract module hints from servers/base_path."""
    if refs is None:
        refs = set()

    if isinstance(obj, dict):
        # servers[*].url format: "/api/v1/training/sessions"
        if "servers" in obj and isinstance(obj["servers"], list):
            for server in obj["servers"]:
                if isinstance(server, dict) and "url" in server:
                    url = server["url"]
                    # Extract module from URL path
                    match = re.search(r"/(\w+)/", url)
                    if match:
                        module = match.group(1)
                        if module in CANONICAL_MODULES:
                            refs.add(module)

        for value in obj.values():
            if isinstance(value, (dict, list)):
                _extract_servers(value, refs)

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _extract_servers(item, refs)

    return refs


def _extract_asyncapi_channels(obj: Any, refs: Optional[Set[str]] = None) -> Set[str]:
    """Extract module hints from AsyncAPI channels."""
    if refs is None:
        refs = set()

    if isinstance(obj, dict):
        if "channels" in obj and isinstance(obj["channels"], dict):
            for channel_name in obj["channels"].keys():
                # Channel format: "training.session.created"
                if "." in channel_name:
                    module = channel_name.split(".")[0]
                    if module in CANONICAL_MODULES:
                        refs.add(module)

        for value in obj.values():
            if isinstance(value, (dict, list)):
                _extract_asyncapi_channels(value, refs)

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _extract_asyncapi_channels(item, refs)

    return refs


# ============================================================================
# VALIDATION
# ============================================================================

def validate_scope_boundaries(
    module_origin: str,
    module_refs: Set[str],
    policy: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """
    Validate that all referenced modules are in allowed_references.
    
    Returns:
        (is_valid, list_of_violations)
    """
    violations = []

    if module_origin not in policy.get("modules", {}):
        # Policy doesn't have explicit entry for this module
        # Treat as "no references allowed"
        if module_refs - {module_origin}:
            violations.append(
                f"Module '{module_origin}' has no explicit policy;"
                f" found references: {module_refs - {module_origin}}"
            )
        return (False, violations) if violations else (True, [])

    module_policy = policy["modules"][module_origin]
    allowed = module_policy.get("allowed_references", set())
    forbidden = module_policy.get("forbidden_references", set())

    for ref_module in module_refs:
        # Intra-module reference is always OK
        if ref_module == module_origin:
            continue

        # Check if explicitly allowed
        if ref_module in allowed:
            continue

        # Check if explicitly forbidden
        if ref_module in forbidden:
            violations.append(
                f"Module '{module_origin}' references forbidden module '{ref_module}'"
            )
            continue

        # Not in allowed or forbidden → implicitly forbidden (fail-safe)
        violations.append(
            f"Module '{module_origin}' references module '{ref_module}' which is not in allowed_references"
        )

    return (len(violations) == 0, violations)


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate cross-module scope boundaries in HB Track contracts."
    )
    parser.add_argument(
        "artifact_path",
        help="Path to artifact (OpenAPI, Schema, Arazzo, AsyncAPI)",
    )
    parser.add_argument(
        "--module",
        help="Override detected module name (for testing)",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Load policy
    policy = load_policy(args.workspace)
    if not policy:
        result = {
            "status": "ERROR_POLICY_MISSING",
            "message": f"SCOPE_BOUNDARY_POLICY.md not found at {args.workspace}/docs/_canon/",
            "artifact_path": args.artifact_path,
        }
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ERROR: {result['message']}", file=sys.stderr)
        return EXIT_CODES["ERROR_POLICY_MISSING"]

    # Load artifact
    artifact = load_yaml_or_json(args.artifact_path)
    if artifact is None:
        result = {
            "status": "ERROR_ARTIFACT_MALFORMED",
            "message": f"Failed to parse {args.artifact_path} (invalid JSON/YAML)",
            "artifact_path": args.artifact_path,
        }
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ERROR: {result['message']}", file=sys.stderr)
        return EXIT_CODES["ERROR_ARTIFACT_MALFORMED"]

    # Extract or override module
    module_origin = args.module or extract_module_from_path(args.artifact_path)
    if not module_origin:
        result = {
            "status": "ERROR_MODULE_UNKNOWN",
            "message": f"Could not extract module from path: {args.artifact_path}",
            "artifact_path": args.artifact_path,
        }
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ERROR: {result['message']}", file=sys.stderr)
        return EXIT_CODES["ERROR_MODULE_UNKNOWN"]

    if module_origin not in CANONICAL_MODULES:
        result = {
            "status": "ERROR_MODULE_UNKNOWN",
            "message": f"Module '{module_origin}' is not in canonical modules: {sorted(CANONICAL_MODULES)}",
            "artifact_path": args.artifact_path,
            "module": module_origin,
        }
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ERROR: {result['message']}", file=sys.stderr)
        return EXIT_CODES["ERROR_MODULE_UNKNOWN"]

    # Extract references
    module_refs = extract_references(artifact)

    # Validate boundaries
    is_valid, violations = validate_scope_boundaries(module_origin, module_refs, policy)

    # Format output
    if is_valid:
        result = {
            "status": "PASS",
            "message": f"Scope boundaries valid for module '{module_origin}'",
            "artifact_path": args.artifact_path,
            "module": module_origin,
            "references": sorted(module_refs),
        }
        exit_code = EXIT_CODES["PASS"]
    else:
        result = {
            "status": "BLOCKED_SCOPE_OVERFLOW",
            "message": "Scope boundary violations detected",
            "artifact_path": args.artifact_path,
            "module": module_origin,
            "references": sorted(module_refs),
            "violations": violations,
        }
        exit_code = EXIT_CODES["BLOCKED_SCOPE_OVERFLOW"]

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {result['message']}")
        if args.verbose or not is_valid:
            print(f"  Artifact: {args.artifact_path}")
            print(f"  Module: {module_origin}")
            print(f"  References: {sorted(module_refs)}")
            if violations:
                print("  Violations:")
                for violation in violations:
                    print(f"    - {violation}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
