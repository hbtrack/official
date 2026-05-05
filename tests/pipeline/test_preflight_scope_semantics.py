import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
_LOADER = SourceFileLoader("hb_cli_preflight_scope", str(ROOT / "scripts" / "hb"))
_SPEC = importlib.util.spec_from_loader(_LOADER.name, _LOADER)
_HB_MODULE = importlib.util.module_from_spec(_SPEC)
_LOADER.exec_module(_HB_MODULE)


def _write_handoff(workspace: Path, modulo_foco: str) -> None:
    (workspace / "SESSION_HANDOFF.md").write_text(
        f"---\nmodulo_foco: {modulo_foco}\n---\n",
        encoding="utf-8",
    )


def _build_cli(workspace: Path):
    cli = _HB_MODULE.HBCLIv2.__new__(_HB_MODULE.HBCLIv2)
    cli.root = workspace
    cli.module_registry = {
        "modules": {
            "training": {},
            "notifications": {},
            "video": {},
        }
    }
    return cli


def test_diff_outside_handoff_scope_ignores_noncanonical_area_focus(tmp_path):
    _write_handoff(tmp_path, "architecture")
    cli = _build_cli(tmp_path)

    changed_files = [
        "src/training/api/sessions.py",
        "src/notifications/tasks.py",
        "src/shared/middleware.py",
    ]

    assert cli._detect_diff_outside_handoff_scope(changed_files) is False


def test_diff_outside_handoff_scope_blocks_other_module_for_canonical_focus(tmp_path):
    _write_handoff(tmp_path, "training")
    cli = _build_cli(tmp_path)

    changed_files = [
        "src/training/api/sessions.py",
        "src/notifications/tasks.py",
    ]

    assert cli._detect_diff_outside_handoff_scope(changed_files) is True


# ---------------------------------------------------------------------------
# Tests: formal_activation_evidence for canonical_status_transition
# ---------------------------------------------------------------------------

def _write_merge_readiness_blocking_canonical_transition(root: Path) -> None:
    """merge-readiness.json com canonical_status_transition bloqueante."""
    (root / "merge-readiness.json").write_text(
        json.dumps(
            {
                "version": "2.0.0",
                "target_branch": "main",
                "checks": [],
                "diff_classification": {"classes": []},
                "semantic_requirements": {
                    "rules": [
                        {
                            "when": "canonical_status_transition",
                            "require": ["formal_activation_evidence"],
                            "block_if_missing": True,
                        }
                    ]
                },
                "reviewability": {
                    "max_changed_files": 150,
                    "max_commits": 20,
                    "max_cross_domain_areas": 3,
                    "split_required_when_exceeded": True,
                },
                "execution_plan": {
                    "baseline_steps": [],
                    "required_check_strategy": "run_all_required",
                    "conditional_check_strategy": "run_matching_conditionals",
                    "decision_policy": "block_on_required_fail_or_missing_evidence",
                    "output_report": "_reports/preflight/latest.json",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_valid_activation_evidence(root: Path, artifact: str = ".contract_driven/waivers.json") -> None:
    """Cria evidência formal válida em _reports/activation_evidence/."""
    ev_path = root / "_reports" / "activation_evidence" / "formal_activation_evidence.json"
    ev_path.parent.mkdir(parents=True, exist_ok=True)
    ev_path.write_text(
        json.dumps(
            {
                "evidence_type": "formal_activation_evidence",
                "transition": "canonical_status_transition",
                "artifact": artifact,
                "from": "absent",
                "to": "ACTIVE",
                "entry_id": "GOV-F1-REDOCLY-SCHEMA-REF",
                "reason": "Fase 1/1.1: waiver formal para OPENAPI_ROOT_STRUCTURE_GATE",
                "validated_by": ["python3 scripts/hb validate --profile ci"],
                "created_at_utc": "2026-05-04T00:00:00Z",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _mock_preflight_infrastructure(monkeypatch, cli, triggered: bool = True) -> None:
    """Mocka infraestrutura de git/fs exceto o mecanismo de evidência."""
    monkeypatch.setattr(cli, "_get_diff_files", lambda _: [".contract_driven/waivers.json", "_reports/activation_evidence/formal_activation_evidence.json"])
    monkeypatch.setattr(cli, "_get_commit_count", lambda _: 1)
    monkeypatch.setattr(cli, "cmd_survival_suite", lambda: 0)
    monkeypatch.setattr(cli, "_detect_schema_field_removed", lambda _f, _t: False)
    monkeypatch.setattr(cli, "_detect_canonical_status_transition", lambda _f, _t: triggered)
    monkeypatch.setattr(cli, "_detect_bridge_doc_authority_language", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_new_cross_module_boundary", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_diff_outside_handoff_scope", lambda _f: False)
    monkeypatch.setattr(
        cli,
        "_verify_preflight_artifact_integrity",
        lambda *a, **kw: {"status": "SKIP", "message": "skipped", "reasons": []},
    )
    # Evita hashing de scripts/hb no tmp_path
    monkeypatch.setattr(
        cli,
        "_attach_preflight_artifact_integrity",
        lambda report_core, **kw: report_core,
    )


def test_canonical_status_transition_without_evidence_blocks(tmp_path, monkeypatch):
    """canonical_status_transition sem evidência formal → BLOCK (exit 2)."""
    _write_merge_readiness_blocking_canonical_transition(tmp_path)
    cli = _build_cli(tmp_path)
    _mock_preflight_infrastructure(monkeypatch, cli, triggered=True)

    result = cli.cmd_preflight()
    assert result == 2, f"esperado BLOCK (2), obtido {result}"


def test_canonical_status_transition_with_valid_evidence_passes(tmp_path, monkeypatch):
    """canonical_status_transition com evidência formal válida → PASS (exit 0)."""
    _write_merge_readiness_blocking_canonical_transition(tmp_path)
    _write_valid_activation_evidence(tmp_path)
    cli = _build_cli(tmp_path)
    _mock_preflight_infrastructure(monkeypatch, cli, triggered=True)

    result = cli.cmd_preflight()
    assert result == 0, f"esperado PASS (0), obtido {result}"


def test_canonical_status_transition_with_wrong_artifact_still_blocks(tmp_path, monkeypatch):
    """Evidência com artefato errado → ainda BLOCK (exit 2)."""
    _write_merge_readiness_blocking_canonical_transition(tmp_path)
    # Escreve evidência com artefato diferente do que está em changed_files
    _write_valid_activation_evidence(tmp_path, artifact="some/other/file.json")
    cli = _build_cli(tmp_path)
    _mock_preflight_infrastructure(monkeypatch, cli, triggered=True)

    result = cli.cmd_preflight()
    assert result == 2, f"evidência com artefato errado deve bloquear, obtido {result}"


def test_canonical_status_transition_evidence_file_not_in_diff_blocks(tmp_path, monkeypatch):
    """Evidência válida mas arquivo de evidência NÃO está em changed_files → BLOCK (exit 2)."""
    _write_merge_readiness_blocking_canonical_transition(tmp_path)
    _write_valid_activation_evidence(tmp_path)
    cli = _build_cli(tmp_path)
    # Mocka infraestrutura mas sem o arquivo de evidência no diff
    monkeypatch.setattr(cli, "_get_diff_files", lambda _: [".contract_driven/waivers.json"])
    monkeypatch.setattr(cli, "_get_commit_count", lambda _: 1)
    monkeypatch.setattr(cli, "cmd_survival_suite", lambda: 0)
    monkeypatch.setattr(cli, "_detect_schema_field_removed", lambda _f, _t: False)
    monkeypatch.setattr(cli, "_detect_canonical_status_transition", lambda _f, _t: True)
    monkeypatch.setattr(cli, "_detect_bridge_doc_authority_language", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_new_cross_module_boundary", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_diff_outside_handoff_scope", lambda _f: False)
    monkeypatch.setattr(
        cli,
        "_verify_preflight_artifact_integrity",
        lambda *a, **kw: {"status": "SKIP", "message": "skipped", "reasons": []},
    )
    monkeypatch.setattr(
        cli,
        "_attach_preflight_artifact_integrity",
        lambda report_core, **kw: report_core,
    )

    result = cli.cmd_preflight()
    assert result == 2, f"sem evidence_rel no diff deve bloquear, obtido {result}"


def test_canonical_status_transition_evidence_file_in_diff_passes(tmp_path, monkeypatch):
    """Evidência válida e arquivo de evidência ESTÁ em changed_files → PASS (exit 0)."""
    _write_merge_readiness_blocking_canonical_transition(tmp_path)
    _write_valid_activation_evidence(tmp_path)
    cli = _build_cli(tmp_path)
    # Inclui o evidence file no diff explicitamente
    monkeypatch.setattr(
        cli, "_get_diff_files",
        lambda _: [".contract_driven/waivers.json", "_reports/activation_evidence/formal_activation_evidence.json"]
    )
    monkeypatch.setattr(cli, "_get_commit_count", lambda _: 1)
    monkeypatch.setattr(cli, "cmd_survival_suite", lambda: 0)
    monkeypatch.setattr(cli, "_detect_schema_field_removed", lambda _f, _t: False)
    monkeypatch.setattr(cli, "_detect_canonical_status_transition", lambda _f, _t: True)
    monkeypatch.setattr(cli, "_detect_bridge_doc_authority_language", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_new_cross_module_boundary", lambda _f: False)
    monkeypatch.setattr(cli, "_detect_diff_outside_handoff_scope", lambda _f: False)
    monkeypatch.setattr(
        cli,
        "_verify_preflight_artifact_integrity",
        lambda *a, **kw: {"status": "SKIP", "message": "skipped", "reasons": []},
    )
    monkeypatch.setattr(
        cli,
        "_attach_preflight_artifact_integrity",
        lambda report_core, **kw: report_core,
    )

    result = cli.cmd_preflight()
    assert result == 0, f"com evidence_rel no diff deve passar, obtido {result}"
