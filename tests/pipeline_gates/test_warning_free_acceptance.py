"""
test_warning_free_acceptance.py
===============================
B9-002 — Politica ``warnings = failure``.

Garante que:
  1. ``PASS_WITH_WARNINGS`` não é mais um status final válido (exit_code != 0).
  2. Gates adversariais e de sincronismo normativo são **blocking**.
  3. Apenas gates da whitelist ``ALLOWED_SKIP_GATES`` podem retornar
     ``SKIP_NOT_APPLICABLE`` sem provocar falha.
  4. O relatório ``latest.json`` atual não contém warnings silenciosos.
"""
from __future__ import annotations

import json
import pathlib

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).parents[2]
REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"
LATEST_REPORT_PATH = REPO_ROOT / "_reports" / "contract_gates" / "latest.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_latest_report() -> dict:
    with open(LATEST_REPORT_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _read_allowed_skip_gates() -> set[str]:
    """Extract ALLOWED_SKIP_GATES from validate_contracts.py source."""
    import re
    text = VALIDATOR_PATH.read_text(encoding="utf-8")
    # Find the ALLOWED_SKIP_GATES block
    match = re.search(
        r'ALLOWED_SKIP_GATES[^=]*=\s*frozenset\(\{(.*?)\}\)',
        text,
        re.DOTALL,
    )
    assert match, "ALLOWED_SKIP_GATES not found in validate_contracts.py"
    block = match.group(1)
    return set(re.findall(r'"([A-Z_]+_GATE)"', block))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPassWithWarningsIsFailure:
    """PASS_WITH_WARNINGS must not be accepted as a valid final status."""

    def test_validator_rejects_pass_with_warnings(self):
        """The status 'PASS_WITH_WARNINGS' must not appear in the aggregation
        logic — it has been replaced by FAIL with exit_code=1."""
        text = VALIDATOR_PATH.read_text(encoding="utf-8")
        # The old PASS_WITH_WARNINGS assignment should no longer exist
        # (except possibly in comments/docs)
        import re
        assignments = re.findall(
            r'^\s+overall\s*=\s*["\']PASS_WITH_WARNINGS["\']',
            text,
            re.MULTILINE,
        )
        assert len(assignments) == 0, (
            "validate_contracts.py still assigns overall = 'PASS_WITH_WARNINGS'. "
            "B9-002 requires warnings to be failures."
        )

    def test_non_blocking_fail_returns_nonzero_exit(self):
        """When non-blocking gates FAIL, exit_code must be > 0."""
        text = VALIDATOR_PATH.read_text(encoding="utf-8")
        # After the 'elif any(g.get("status") == "FAIL"' block,
        # exit_code must not be 0
        import re
        match = re.search(
            r'elif any\(g\.get\("status"\) == "FAIL".*?\n\s+overall = "(\w+)"\s*\n\s+exit_code = (\d+)',
            text,
            re.DOTALL,
        )
        assert match, "Could not find non-blocking FAIL aggregation logic"
        assert match.group(1) == "FAIL", f"Expected overall='FAIL', got '{match.group(1)}'"
        assert int(match.group(2)) > 0, (
            f"Expected exit_code > 0 for non-blocking FAIL, got {match.group(2)}"
        )


class TestAdversarialAndSyncGatesAreBlocking:
    """Adversarial and sync/normative gates must be blocking per B9-002."""

    MUST_BE_BLOCKING = {
        "ADVERSARIAL_ANALYSIS_GATE",
        "API_NORMATIVE_DUPLICATION_GATE",
    }

    def test_registry_marks_gates_as_blocking(self):
        registry = _load_registry()
        gates_by_id = {g["gate_id"]: g for g in registry["gates"]}
        for gate_id in self.MUST_BE_BLOCKING:
            gate = gates_by_id.get(gate_id)
            assert gate is not None, f"{gate_id} not found in GATES_REGISTRY.yaml"
            assert gate.get("blocking") is True, (
                f"{gate_id} must be blocking=true in GATES_REGISTRY.yaml (found: {gate.get('blocking')})"
            )


class TestAllowedSkipGatesWhitelist:
    """Only whitelisted gates may return SKIP_NOT_APPLICABLE."""

    def test_allowed_skip_gates_constant_exists(self):
        allowed = _read_allowed_skip_gates()
        assert len(allowed) > 0, "ALLOWED_SKIP_GATES must not be empty"

    def test_allowed_skip_gates_are_in_registry(self):
        """Every gate in ALLOWED_SKIP_GATES must exist in the registry."""
        allowed = _read_allowed_skip_gates()
        registry = _load_registry()
        registry_ids = {g["gate_id"] for g in registry["gates"]}
        for gate_id in allowed:
            assert gate_id in registry_ids, (
                f"{gate_id} is in ALLOWED_SKIP_GATES but not in GATES_REGISTRY.yaml"
            )

    def test_skip_validation_logic_exists(self):
        """validate_contracts.py must enforce the SKIP whitelist."""
        text = VALIDATOR_PATH.read_text(encoding="utf-8")
        assert "unauthorized_skips" in text, (
            "validate_contracts.py must contain 'unauthorized_skips' enforcement logic (B9-002)"
        )
        assert "ALLOWED_SKIP_GATES" in text, (
            "validate_contracts.py must reference ALLOWED_SKIP_GATES (B9-002)"
        )
        # Must distinguish profile/stage skips from real SKIP_NOT_APPLICABLE
        assert "Pulado no" in text, (
            "validate_contracts.py must filter out profile/stage skips from unauthorized check"
        )

    @pytest.mark.skipif(
        not LATEST_REPORT_PATH.exists(),
        reason="latest.json not available",
    )
    def test_latest_report_has_no_unauthorized_skips(self):
        """The current latest.json must not contain unauthorized SKIP gates."""
        allowed = _read_allowed_skip_gates()
        report = _load_latest_report()
        for gate in report.get("gates", []):
            if gate.get("status") == "SKIP_NOT_APPLICABLE":
                assert gate["gate_id"] in allowed, (
                    f"Gate '{gate['gate_id']}' returned SKIP_NOT_APPLICABLE "
                    f"but is not in ALLOWED_SKIP_GATES: {allowed}"
                )


class TestLatestReportWarningFree:
    """The current pipeline report must be free of warnings."""

    @pytest.mark.skipif(
        not LATEST_REPORT_PATH.exists(),
        reason="latest.json not available",
    )
    def test_overall_status_is_pass(self):
        report = _load_latest_report()
        overall = report.get("overall_status")
        assert overall == "PASS", (
            f"Pipeline overall_status must be PASS, got '{overall}'. "
            "B9-002: CA only passes when execution has no relevant warnings."
        )

    @pytest.mark.skipif(
        not LATEST_REPORT_PATH.exists(),
        reason="latest.json not available",
    )
    def test_no_fail_gates(self):
        report = _load_latest_report()
        fails = [
            g["gate_id"] for g in report.get("gates", [])
            if g.get("status") == "FAIL"
        ]
        assert len(fails) == 0, (
            f"Pipeline has FAIL gates: {fails}. "
            "B9-002: no warnings or failures allowed in acceptance."
        )

    @pytest.mark.skipif(
        not LATEST_REPORT_PATH.exists(),
        reason="latest.json not available",
    )
    def test_exit_code_is_zero(self):
        report = _load_latest_report()
        assert report.get("exit_code") == 0, (
            f"Pipeline exit_code must be 0, got {report.get('exit_code')}. "
            "B9-002: warnings=failure policy requires clean exit."
        )
