"""Testes de regressão para governança do pipeline."""

from __future__ import annotations

import datetime
import json

from scripts.contracts.validate import validate_contracts as gates


def test_handoff_coherence_detects_stale_date(tmp_path):
    handoff = tmp_path / "SESSION_HANDOFF.md"
    handoff.write_text("data_ultima_sessao: 2020-01-01\nbranch_ativo: main\n", encoding="utf-8")

    result = gates._g_handoff_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("BLOCKED_HANDOFF_INCOMPLETE" in str(item) for item in result.get("violations", []))


def test_module_status_coherence_blocks_with_adversarial_fail(tmp_path):
    canon = tmp_path / "docs" / "_canon"
    canon.mkdir(parents=True)
    (canon / "MODULE_REGISTRY.yaml").write_text(
        "modules:\n  training:\n    status: implementation_ready\n    expected_surfaces: []\n",
        encoding="utf-8",
    )
    adv_dir = tmp_path / "_reports" / "adversarial"
    adv_dir.mkdir(parents=True)
    (adv_dir / "training.adversarial.json").write_text(
        json.dumps({"module": "training", "overall_status": "FAIL", "risks": []}),
        encoding="utf-8",
    )

    result = gates._g_module_status_coherence(tmp_path)

    assert result["status"] == "FAIL"
    assert result["blocking_code"] == "BLOCKED_REGISTRY_MISMATCH"


def test_ui_alignment_detects_missing_operationid(tmp_path):
    oa_dir = tmp_path / "contracts" / "openapi"
    oa_dir.mkdir(parents=True)
    (oa_dir / "openapi.yaml").write_text("operationId: existingOperation\n", encoding="utf-8")
    ui_dir = tmp_path / "docs" / "hbtrack" / "modulos" / "training"
    ui_dir.mkdir(parents=True)
    (ui_dir / "UI_CONTRACT_TRAINING.md").write_text(
        "Use `getNonExistentOperationXyz` to fetch data.\n",
        encoding="utf-8",
    )

    result = gates._g14_ui_doc_validation(tmp_path)

    assert result["status"] == "FAIL"
    assert any("getNonExistentOperationXyz" in str(item) for item in result.get("violations", []))


def test_waiver_engine_accepts_valid_waiver(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "contracts" / "openapi" / "baseline"
    baseline_dir.mkdir(parents=True)
    (baseline_dir / "openapi_baseline.json").write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "paths": {
                    "/sessions": {
                        "get": {
                            "operationId": "listSessions",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    openapi_dir = tmp_path / "contracts" / "openapi"
    (openapi_dir / "openapi.yaml").write_text("openapi: 3.1.0\npaths: {}\n", encoding="utf-8")

    waivers_dir = tmp_path / "contracts" / "_waivers"
    waivers_dir.mkdir(parents=True)
    expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    (waivers_dir / "test_waiver.json").write_text(
        json.dumps(
            {
                "gate_id": "CONTRACT_BREAKING_CHANGE_GATE",
                "expires_at_utc": expiry,
            }
        ),
        encoding="utf-8",
    )

    original_which = gates.shutil.which
    monkeypatch.setattr(
        gates.shutil,
        "which",
        lambda name: None if name == "oasdiff" else original_which(name),
    )

    result = gates._g9_contract_breaking_change(tmp_path)

    assert result["status"] == "PASS"
    assert "waiver ativo" in result["summary"].lower()
