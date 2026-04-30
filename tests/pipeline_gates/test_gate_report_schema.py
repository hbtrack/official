from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / ".dev" / "schemas" / "hb_gate_report.schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class TestGateReportSchemaExists:
    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists(), f"Schema ausente: {SCHEMA_PATH}"

    def test_schema_is_valid_json(self):
        data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_schema_has_required_top_level_fields(self):
        schema = _load_schema()
        required = schema.get("required", [])
        expected = [
            "gate_id", "agent", "platform", "role",
            "context_boundary", "status", "semantic_status",
            "commands", "evidence", "failure", "next_required_gate",
        ]
        for field in expected:
            assert field in required, f"Campo obrigatorio ausente no schema: {field}"

    def test_schema_enumerates_valid_platforms(self):
        schema = _load_schema()
        platform_enum = schema["properties"]["platform"]["enum"]
        assert "copilot" in platform_enum
        assert "claude" in platform_enum
        assert "codex" in platform_enum
        assert "ci" in platform_enum

    def test_schema_enumerates_valid_statuses(self):
        schema = _load_schema()
        status_enum = schema["properties"]["status"]["enum"]
        assert "PASS" in status_enum
        assert "FAIL" in status_enum
        assert "INCONCLUSIVE" in status_enum
        assert "BLOCKED" in status_enum

    def test_schema_enumerates_context_boundary(self):
        schema = _load_schema()
        cb_enum = schema["properties"]["context_boundary"]["enum"]
        assert "same_chat" in cb_enum
        assert "isolated_context" in cb_enum
        assert "sandbox" in cb_enum
        assert "ci" in cb_enum

    def test_schema_is_not_sovereign(self):
        text = SCHEMA_PATH.read_text(encoding="utf-8")
        schema_data = json.loads(text)
        description = schema_data.get("description", "")
        assert ("BRIDGE" in description or "nao canonico" in description.lower()
                or "experimental" in description or "nao canonico" in description.lower()), (
            "Schema deve se declarar nao canonico/experimental"
        )


class TestGateReportSchemaValidation:

    def _valid_base(self) -> dict:
        return {
            "gate_id": "test_gate_001",
            "agent": "hb-adversarial-tester",
            "platform": "claude",
            "role": "adversarial_tester",
            "context_boundary": "isolated_context",
            "status": "PASS",
            "semantic_status": "ADVERSARIAL_PASS_PENDING_GATE",
            "commands": [
                {"command": "python3 scripts/hb verify --task-type adversarial_test_execution", "exit_code": 0}
            ],
            "evidence": {
                "files_checked": ["_reports/implementation_flow/implementation_evidence_pack.json"],
                "claims_verified": ["PR remoto existe", "evidence_pack e schema-valid"],
            },
            "failure": {
                "category": "none",
                "root_cause": "",
            },
            "next_required_gate": "codex_gate",
        }

    def test_valid_pass_report_is_accepted(self):
        schema = _load_schema()
        report = self._valid_base()
        jsonschema.validate(instance=report, schema=schema)

    def test_valid_fail_report_is_accepted(self):
        schema = _load_schema()
        report = self._valid_base()
        report["status"] = "FAIL"
        report["semantic_status"] = "ADVERSARIAL_FAIL"
        report["evidence"]["claims_verified"] = []
        report["failure"] = {
            "category": "test_failure",
            "root_cause": "Endpoint POST /games retornou 500 sem mensagem de erro",
        }
        jsonschema.validate(instance=report, schema=schema)

    def test_invalid_platform_is_rejected(self):
        schema = _load_schema()
        report = self._valid_base()
        report["platform"] = "github_copilot_invalid"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_invalid_status_validated_is_rejected(self):
        schema = _load_schema()
        report = self._valid_base()
        report["status"] = "VALIDATED"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_invalid_status_approved_is_rejected(self):
        schema = _load_schema()
        report = self._valid_base()
        report["status"] = "APPROVED"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_pass_without_claims_verified_fails_schema(self):
        schema = _load_schema()
        report = self._valid_base()
        report["status"] = "PASS"
        report["evidence"]["claims_verified"] = []
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_missing_required_field_is_rejected(self):
        schema = _load_schema()
        report = self._valid_base()
        del report["gate_id"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)

    def test_additional_properties_rejected(self):
        schema = _load_schema()
        report = self._valid_base()
        report["unauthorized_field"] = "should_be_rejected"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=report, schema=schema)
