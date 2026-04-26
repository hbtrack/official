from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"


def _load_hb_module():
    spec = importlib.util.spec_from_loader(
        "hb_module_preflight_integrity",
        importlib.machinery.SourceFileLoader("hb_module_preflight_integrity", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hb_module = _load_hb_module()
HBCLIv2 = hb_module.HBCLIv2


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_minimal_workspace(root: Path) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "hb").write_text(HB_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    _write_json(
        root / "merge-readiness.json",
        {
            "version": "2.0.0",
            "target_branch": "main",
            "checks": [],
            "diff_classification": {"classes": []},
            "semantic_requirements": {"rules": []},
            "reviewability": {
                "max_changed_files": 150,
                "max_commits": 20,
                "max_cross_domain_areas": 3,
                "split_required_when_exceeded": True,
            },
            "execution_plan": {
                "baseline_steps": ["survival_suite"],
                "required_check_strategy": "run_all_required",
                "conditional_check_strategy": "run_matching_conditionals",
                "decision_policy": "block_on_required_fail",
                "output_report": "_reports/preflight/latest.json",
            },
        },
    )


def _build_cli(workspace: Path) -> HBCLIv2:
    cli = HBCLIv2.__new__(HBCLIv2)
    cli.root = workspace
    return cli


def _valid_report(cli: HBCLIv2, workspace: Path) -> dict:
    core = {
        "generated_at": "2026-04-26T00:00:00+00:00",
        "branch_target": "main",
        "diff_classes": [],
        "checks_run": [],
        "checks_failed": [],
        "missing_evidence": [],
        "semantic_findings": [],
        "reviewability_check": {
            "changed_files": 0,
            "max_changed_files": 150,
            "commits": 0,
            "max_commits": 20,
            "cross_domain_areas": 0,
            "max_cross_domain_areas": 3,
            "exceeded": False,
            "split_required": False,
        },
        "final_decision": "PASS",
    }
    return cli._attach_preflight_artifact_integrity(
        core,
        manifest_path=workspace / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="main",
    )


def test_verify_preflight_artifact_integrity_passes_for_generated_artifact(tmp_path):
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(report_path, report)

    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="main",
    )

    assert result["status"] == "PASS", result


def test_verify_preflight_artifact_integrity_fails_for_tampered_payload(tmp_path):
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report["final_decision"] = "BLOCK"
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(report_path, report)

    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="main",
    )

    assert result["status"] == "FAIL"
    assert "payload_sha256_mismatch" in result["reasons"]


def test_verify_preflight_artifact_integrity_marks_legacy_artifact_as_legacy(tmp_path):
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(
        report_path,
        {
            "generated_at": "2026-04-25T00:00:00+00:00",
            "branch_target": "main",
            "diff_classes": [],
            "checks_run": [],
            "checks_failed": [],
            "missing_evidence": [],
            "semantic_findings": [],
            "reviewability_check": {"changed_files": 0, "commits": 0, "cross_domain_areas": 0, "exceeded": False},
            "final_decision": "PASS",
        },
    )

    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="main",
    )

    assert result["status"] == "LEGACY", result


def test_verify_preflight_artifact_integrity_marks_source_drift_as_stale(tmp_path):
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(report_path, report)
    (tmp_path / "merge-readiness.json").write_text(
        json.dumps(
            {
                "version": "2.0.1",
                "target_branch": "main",
                "checks": [],
                "diff_classification": {"classes": []},
                "semantic_requirements": {"rules": []},
                "reviewability": {
                    "max_changed_files": 150,
                    "max_commits": 20,
                    "max_cross_domain_areas": 3,
                    "split_required_when_exceeded": True,
                },
                "execution_plan": {
                    "baseline_steps": ["survival_suite"],
                    "required_check_strategy": "run_all_required",
                    "conditional_check_strategy": "run_matching_conditionals",
                    "decision_policy": "block_on_required_fail",
                    "output_report": "_reports/preflight/latest.json",
                },
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="main",
    )

    assert result["status"] == "STALE", result
    assert "manifest_sha256" in result["reasons"]


def test_verify_preflight_artifact_integrity_target_branch_change_is_stale(tmp_path):
    """Mudança legítima em target_branch deve retornar STALE, não FAIL (Codex P2)."""
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(report_path, report)

    # Artefato gravado com target_branch=main; agora invoca com target_branch=develop
    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/latest.json",
        target_branch="develop",
    )

    assert result["status"] == "STALE", result
    assert "report_target_mismatch" in result["reasons"]
    assert result["exit_code"] == 0


def test_verify_preflight_artifact_integrity_output_report_change_is_stale(tmp_path):
    """Mudança legítima em output_report (execution_plan) deve retornar STALE, não FAIL (Codex P2)."""
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    _write_json(report_path, report)

    # Artefato gravado com output_report padrão; agora invoca com caminho diferente
    result = cli._verify_preflight_artifact_integrity(
        report_path,
        manifest_path=tmp_path / "merge-readiness.json",
        output_report="_reports/preflight/custom.json",
        target_branch="main",
    )

    assert result["status"] == "STALE", result
    assert "report_target_mismatch" in result["reasons"]
    assert result["exit_code"] == 0


def test_cmd_preflight_blocks_when_existing_artifact_was_manually_tampered(tmp_path, monkeypatch):
    _write_minimal_workspace(tmp_path)
    cli = _build_cli(tmp_path)
    report = _valid_report(cli, tmp_path)
    report["checks_failed"] = ["Validate Contract Gates"]
    report_path = tmp_path / "_reports" / "preflight" / "latest.json"
    original_text = json.dumps(report, indent=2, ensure_ascii=False)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(original_text, encoding="utf-8")

    monkeypatch.setattr(cli, "_get_diff_files", lambda _target: [])
    monkeypatch.setattr(cli, "_get_commit_count", lambda _target: 0)
    monkeypatch.setattr(cli, "cmd_survival_suite", lambda: 0)
    monkeypatch.setattr(cli, "_detect_schema_field_removed", lambda _files, _target: False)
    monkeypatch.setattr(cli, "_detect_canonical_status_transition", lambda _files, _target: False)
    monkeypatch.setattr(cli, "_detect_bridge_doc_authority_language", lambda _files: False)
    monkeypatch.setattr(cli, "_detect_new_cross_module_boundary", lambda _files: False)
    monkeypatch.setattr(cli, "_detect_diff_outside_handoff_scope", lambda _files: False)

    assert cli.cmd_preflight() == 2
    assert report_path.read_text(encoding="utf-8") == original_text
