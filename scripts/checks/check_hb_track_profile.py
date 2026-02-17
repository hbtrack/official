"""L0/L1 Gate: Validate HB_TRACK_PROFILE.yaml structure and schema."""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


REQUIRED_TOP_KEYS = {"version", "project", "truth", "ssot_registry", "approved_commands", "gates", "modules"}
REQUIRED_PROJECT_KEYS = {"name", "profile_id"}
REQUIRED_SSOT_KEYS = {"artifact", "path", "kind", "required"}
REQUIRED_CMD_KEYS = {"id", "cmd", "purpose"}
REQUIRED_MODULE_KEYS = {"id"}


def validate_profile(profile_path: str) -> list[str]:
    """Return list of error strings. Empty = valid."""
    errors = []
    p = Path(profile_path)

    # L0: file exists and parses
    if not p.exists():
        return [f"L0: file not found: {profile_path}"]

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"L0: YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["L0: root must be a mapping"]

    # L1: schema validation
    missing_top = REQUIRED_TOP_KEYS - set(data.keys())
    if missing_top:
        errors.append(f"L1: missing top-level keys: {sorted(missing_top)}")

    # project
    project = data.get("project", {})
    if isinstance(project, dict):
        missing_proj = REQUIRED_PROJECT_KEYS - set(project.keys())
        if missing_proj:
            errors.append(f"L1: project missing keys: {sorted(missing_proj)}")
    else:
        errors.append("L1: 'project' must be a mapping")

    # ssot_registry
    ssot = data.get("ssot_registry", [])
    if isinstance(ssot, list):
        for i, entry in enumerate(ssot):
            if isinstance(entry, dict):
                missing = REQUIRED_SSOT_KEYS - set(entry.keys())
                if missing:
                    errors.append(f"L1: ssot_registry[{i}] missing keys: {sorted(missing)}")
            else:
                errors.append(f"L1: ssot_registry[{i}] must be a mapping")
    else:
        errors.append("L1: 'ssot_registry' must be a list")

    # approved_commands
    cmds = data.get("approved_commands", [])
    if isinstance(cmds, list):
        for i, entry in enumerate(cmds):
            if isinstance(entry, dict):
                missing = REQUIRED_CMD_KEYS - set(entry.keys())
                if missing:
                    errors.append(f"L1: approved_commands[{i}] missing keys: {sorted(missing)}")
            else:
                errors.append(f"L1: approved_commands[{i}] must be a mapping")
    else:
        errors.append("L1: 'approved_commands' must be a list")

    # gates
    gates = data.get("gates", {})
    if isinstance(gates, dict):
        if "blocking" not in gates:
            errors.append("L1: gates missing 'blocking' key")
    else:
        errors.append("L1: 'gates' must be a mapping")

    # modules
    modules = data.get("modules", [])
    if isinstance(modules, list):
        for i, entry in enumerate(modules):
            if isinstance(entry, dict):
                missing = REQUIRED_MODULE_KEYS - set(entry.keys())
                if missing:
                    errors.append(f"L1: modules[{i}] missing keys: {sorted(missing)}")
            else:
                errors.append(f"L1: modules[{i}] must be a mapping")
    else:
        errors.append("L1: 'modules' must be a list")

    return errors


def main():
    parser = argparse.ArgumentParser(description="L0/L1 PROFILE gate")
    parser.add_argument("--profile", default="docs/_canon/HB_TRACK_PROFILE.yaml")
    args = parser.parse_args()

    errors = validate_profile(args.profile)

    if errors:
        print(f"FAIL: {len(errors)} error(s) found:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: L0/L1 profile validation OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
