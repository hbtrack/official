from __future__ import annotations

import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

from check_live_ruleset_parity import compare_ruleset_parity  # noqa: E402
from generate_merge_policy import render_merge_policy  # noqa: E402


def _manifest() -> dict:
    return json.loads((ROOT / "merge-readiness.json").read_text(encoding="utf-8"))


def _snapshot() -> dict:
    return json.loads(
        (ROOT / ".github" / "rulesets" / "contract-gates.snapshot.json").read_text(encoding="utf-8")
    )


def _merge_policy_text() -> str:
    return (ROOT / ".github" / "merge-policy.md").read_text(encoding="utf-8")


def _docs_that_reference_merge_policy_authority() -> list[pathlib.Path]:
    return [
        ROOT / ".github" / "merge-policy.md",
        ROOT / ".github" / "BRANCH_PROTECTION_SETUP.md",
        ROOT / ".github" / "CI_FIX_EVIDENCE.md",
    ]


def test_local_snapshot_manifest_and_merge_policy_are_in_parity():
    violations = compare_ruleset_parity(
        manifest=_manifest(),
        live_ruleset=_snapshot(),
        snapshot=_snapshot(),
        merge_policy_text=_merge_policy_text(),
    )

    assert violations == []


def test_merge_policy_file_matches_generated_output():
    expected = render_merge_policy(manifest=_manifest(), snapshot=_snapshot())
    assert _merge_policy_text() == expected


def test_detects_required_context_drift():
    manifest = _manifest()
    live_ruleset = dict(_snapshot())
    live_ruleset["required_status_checks"] = [
        check for check in live_ruleset["required_status_checks"] if check != "Governance Tests"
    ]

    violations = compare_ruleset_parity(
        manifest=manifest,
        live_ruleset=live_ruleset,
        snapshot=_snapshot(),
        merge_policy_text=_merge_policy_text(),
    )

    assert any("Required checks do manifesto divergem do ruleset live." in item["message"] for item in violations)


def test_detects_merge_policy_workflow_drift():
    merge_policy_text = _merge_policy_text().replace(
        "| 6 | `ci / Validate Contracts` | `_reusable-ci.yml` |",
        "| 6 | `ci / Validate Contracts` | `ci.yml` |",
    )

    violations = compare_ruleset_parity(
        manifest=_manifest(),
        live_ruleset=_snapshot(),
        snapshot=_snapshot(),
        merge_policy_text=merge_policy_text,
    )

    assert any("Workflow de `ci / Validate Contracts`" in item["message"] for item in violations)


def test_detects_merge_policy_textual_drift_outside_required_table():
    merge_policy_text = _merge_policy_text().replace(
        "Nenhum. O ruleset normalizado expõe `bypass_actors: []`.",
        "Manual drift fora da tabela.",
    )

    violations = compare_ruleset_parity(
        manifest=_manifest(),
        live_ruleset=_snapshot(),
        snapshot=_snapshot(),
        merge_policy_text=merge_policy_text,
    )

    assert any(
        item["message"] == "merge-policy.md diverge do artefato gerado esperado."
        for item in violations
    )


def test_docs_do_not_treat_merge_policy_as_primary_truth():
    forbidden = "Fonte de verdade corrente: `.github/merge-policy.md` + ruleset live."
    for path in _docs_that_reference_merge_policy_authority():
        text = path.read_text(encoding="utf-8")
        assert forbidden not in text, f"{path.relative_to(ROOT)} ainda vende merge-policy como fonte primária."
