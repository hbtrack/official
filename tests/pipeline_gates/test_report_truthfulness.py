from __future__ import annotations

from scripts.contracts.validate import validate_contracts as gates


def _gate(
    gate_id: str,
    status: str,
    *,
    blocking: bool = True,
    metadata: dict | None = None,
) -> dict:
    payload = {
        "gate_id": gate_id,
        "status": status,
        "blocking": blocking,
        "summary": "",
        "violations": [],
    }
    meta = {"blocking": blocking, **(metadata or {})}
    return gates._annotate_gate_result(payload, meta)


def test_partial_runs_never_resolve_to_full_pass():
    overall = gates._resolve_pipeline_overall_status(
        canonical_full_run=False,
        has_blocking_fails=False,
        has_degraded=False,
        has_non_blocking_fails=False,
        mandatory_ci_skip_count=0,
    )

    assert overall == "PARTIAL_PASS"


def test_mandatory_ci_skip_is_exposed_and_penalizes_health():
    executed_gate = _gate("AXIOM_INTEGRITY_GATE", "PASS", metadata={"proof_class": "semantic"})
    skipped_gate = _gate(
        "ARCHITECTURE_FACTUALITY_GATE",
        "SKIP_NOT_APPLICABLE",
        metadata={
            "proof_class": "semantic",
            "ci_required": True,
            "skip_allowed_in_ci": False,
        },
    )

    status_detail = gates._build_status_detail([executed_gate, skipped_gate])
    health = gates._compute_pipeline_health_metrics(
        gates=[executed_gate, skipped_gate],
        overall="FAIL",
        exit_code=2,
        run_id="test-run",
        ts="2026-04-24T00:00:00Z",
        execution_context={"profile": "ci", "canonical_scope": "full_pipeline"},
    )

    assert status_detail["mandatory_ci_skip_count"] == 1
    assert status_detail["mandatory_ci_skips"][0]["gate_id"] == "ARCHITECTURE_FACTUALITY_GATE"
    assert health["mandatory_ci_skip_count"] == 1
    assert health["health_score"] < 100
    assert health["gates_passed"] == 1


def test_optional_skip_does_not_inflate_failure_counts():
    executed_gate = _gate("AXIOM_INTEGRITY_GATE", "PASS", metadata={"proof_class": "semantic"})
    skipped_gate = _gate(
        "HTTP_RUNTIME_CONTRACT_GATE",
        "SKIP_NOT_APPLICABLE",
        metadata={
            "proof_class": "runtime",
            "ci_required": True,
            "skip_allowed_in_ci": True,
        },
    )

    status_detail = gates._build_status_detail([executed_gate, skipped_gate])
    health = gates._compute_pipeline_health_metrics(
        gates=[executed_gate, skipped_gate],
        overall="PASS",
        exit_code=0,
        run_id="test-run",
        ts="2026-04-24T00:00:00Z",
        execution_context={"profile": "ci", "canonical_scope": "full_pipeline"},
    )

    assert status_detail["mandatory_ci_skip_count"] == 0
    assert health["mandatory_ci_skip_count"] == 0
    assert health["health_score"] == 100


def test_report_truthfulness_gate_passes_for_partial_scope_with_partial_semantics():
    executed_gate = _gate("AXIOM_INTEGRITY_GATE", "PASS", metadata={"proof_class": "semantic"})

    result = gates._g_report_truthfulness(
        [executed_gate],
        canonical_full_run=False,
        profile="precommit",
    )

    assert result["status"] == "PASS", result


def test_report_truthfulness_gate_fails_for_mandatory_ci_skip():
    executed_gate = _gate("AXIOM_INTEGRITY_GATE", "PASS", metadata={"proof_class": "semantic"})
    skipped_gate = _gate(
        "LIVE_ENFORCEMENT_PARITY_GATE",
        "SKIP_NOT_APPLICABLE",
        metadata={
            "proof_class": "remote_live",
            "ci_required": True,
            "skip_allowed_in_ci": False,
        },
    )

    result = gates._g_report_truthfulness(
        [executed_gate, skipped_gate],
        canonical_full_run=True,
        profile="ci",
    )

    assert result["status"] == "FAIL"
    assert any("Execução canônica contém" in item["message"] for item in result["violations"])
