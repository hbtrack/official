"""L2 Gate: Validate cross-reference consistency across docs."""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent.parent


def load_yaml(path: Path) -> dict | list | None:
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        return None


def check_root_index(errors: list[str]) -> dict | None:
    index_path = ROOT / "docs" / "_INDEX.yaml"
    if not index_path.exists():
        errors.append("L2: docs/_INDEX.yaml not found")
        return None

    data = load_yaml(index_path)
    if not isinstance(data, dict):
        errors.append("L2: docs/_INDEX.yaml is not a valid YAML mapping")
        return None

    # Check all entrypoint paths exist
    for entry in data.get("entrypoints", []):
        ep_path = ROOT / entry.get("path", "")
        if not ep_path.exists():
            errors.append(f"L2: entrypoint '{entry.get('id')}' path not found: {entry.get('path')}")

    # Check derived_read_only_roots exist
    for dr_root in data.get("rules", {}).get("derived_read_only_roots", []):
        dr_path = ROOT / dr_root
        if not dr_path.exists():
            errors.append(f"L2: derived_read_only_root not found: {dr_root}")

    return data


def check_runtime_index(errors: list[str]) -> None:
    runtime_index_path = ROOT / "docs" / "product" / "runtime" / "_INDEX.yaml"
    if not runtime_index_path.exists():
        errors.append("L2: docs/product/runtime/_INDEX.yaml not found")
        return

    data = load_yaml(runtime_index_path)
    if not isinstance(data, dict):
        errors.append("L2: runtime _INDEX.yaml is not a valid YAML mapping")
        return

    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        errors.append("L2: runtime _INDEX.yaml 'scenarios' must be a list")
        return

    seen_ids = set()
    for i, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"L2: runtime scenario [{i}] must be a mapping")
            continue

        sid = scenario.get("id")
        spath = scenario.get("path")

        if not sid:
            errors.append(f"L2: runtime scenario [{i}] missing 'id'")
        elif sid in seen_ids:
            errors.append(f"L2: duplicate runtime scenario id: {sid}")
        else:
            seen_ids.add(sid)

        if not spath:
            errors.append(f"L2: runtime scenario [{i}] missing 'path'")
        else:
            full_path = ROOT / spath
            if not full_path.exists():
                errors.append(f"L2: runtime scenario '{sid}' path not found: {spath}")


def check_profile_refs(errors: list[str]) -> None:
    profile_path = ROOT / "docs" / "_canon" / "HB_TRACK_PROFILE.yaml"
    if not profile_path.exists():
        errors.append("L2: HB_TRACK_PROFILE.yaml not found")
        return

    data = load_yaml(profile_path)
    if not isinstance(data, dict):
        errors.append("L2: HB_TRACK_PROFILE.yaml is not a valid YAML mapping")
        return

    # Check truth.precedence_ref exists
    truth = data.get("truth", {})
    if isinstance(truth, dict):
        pref = truth.get("precedence_ref")
        if pref and not (ROOT / pref).exists():
            errors.append(f"L2: PROFILE precedence_ref not found: {pref}")

    # Check module canonical_doc paths
    for mod in data.get("modules", []):
        if isinstance(mod, dict):
            cdoc = mod.get("canonical_doc")
            if cdoc and not (ROOT / cdoc).exists():
                errors.append(f"L2: module '{mod.get('id')}' canonical_doc not found: {cdoc}")


def check_derived_not_manually_edited(errors: list[str]) -> None:
    """Check that _generated/ dir exists but don't enforce content rules yet."""
    gen_path = ROOT / "docs" / "_generated"
    if not gen_path.exists():
        errors.append("L2: docs/_generated/ directory not found")


def main():
    parser = argparse.ArgumentParser(description="L2 UDS consistency gate")
    parser.parse_args()

    errors: list[str] = []

    check_root_index(errors)
    check_runtime_index(errors)
    check_profile_refs(errors)
    check_derived_not_manually_edited(errors)

    if errors:
        print(f"FAIL: {len(errors)} consistency error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: L2 consistency check OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
