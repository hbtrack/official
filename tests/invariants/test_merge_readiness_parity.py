"""Invariant tests: merge-readiness.json structure, schema, and workflow consistency."""
import json
import pathlib
import pytest

ROOT = pathlib.Path(__file__).parent.parent.parent


def _manifest():
    return json.loads((ROOT / "merge-readiness.json").read_text())


def _schema():
    return json.loads(
        (ROOT / "contracts/schemas/shared/merge-readiness.schema.json").read_text()
    )


def test_merge_readiness_schema():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(_manifest(), _schema())


def test_toolchain_schema():
    tc_path = ROOT / "toolchain.json"
    schema_path = ROOT / "contracts/schemas/shared/toolchain.schema.json"
    assert tc_path.exists(), "toolchain.json not found"
    if not schema_path.exists():
        pytest.skip("toolchain schema not found")
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(
        json.loads(tc_path.read_text()), json.loads(schema_path.read_text())
    )


def test_required_checks_have_local_equivalent():
    for check in _manifest()["checks"]:
        if check["category"] == "required":
            assert "local_equivalent" in check, (
                f"required check {check['context']!r} missing local_equivalent"
            )


def test_conditional_checks_have_condition():
    for check in _manifest()["checks"]:
        if check["category"] == "conditional":
            assert "condition" in check, (
                f"conditional check {check['context']!r} missing condition"
            )
            assert "reason" in check, (
                f"conditional check {check['context']!r} missing reason"
            )


def test_all_required_check_workflows_exist():
    for check in _manifest()["checks"]:
        if check["category"] == "required":
            wf = ROOT / ".github/workflows" / check["workflow"]
            assert wf.exists(), (
                f"workflow {check['workflow']!r} for check {check['context']!r} not found"
            )


def test_category_values_are_valid():
    valid = {"required", "informational", "conditional"}
    for check in _manifest()["checks"]:
        assert check["category"] in valid, (
            f"invalid category {check['category']!r} for {check['context']!r}"
        )
