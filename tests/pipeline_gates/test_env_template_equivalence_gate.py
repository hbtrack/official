from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_env_template_equivalence_gate_passes_against_repo():
    result = gates._g2u_env_template_equivalence(ROOT)

    assert result["status"] == "PASS", result


def test_env_template_equivalence_gate_fails_for_compiler_drift(monkeypatch):
    def _fake_compile_expected(root: Path):
        return {}

    def _fake_check_expected(root: Path, expected):
        return [
            SimpleNamespace(
                relpath="infra/env/.env.staging.template",
                reason="content_mismatch",
            )
        ]

    monkeypatch.setattr(
        gates,
        "_load_ops_compiler_api",
        lambda root: (_fake_compile_expected, _fake_check_expected),
    )

    result = gates._g2u_env_template_equivalence(ROOT)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == gates.BLOCKED_ENV_TEMPLATE_EQUIVALENCE
    assert any(
        violation["artifact"] == "infra/env/.env.staging.template"
        for violation in result["violations"]
    )
