"""
Testes do schema experimental hb_gate_report.schema.json.

Provas positivas: gate reports válidos passam na validação.
Provas negativas: gate reports inválidos (PASS sem evidência, FAIL sem root_cause,
INCONCLUSIVE sem missing_evidence) são rejeitados.

Regra: schema deve estar em .dev/schemas/ — NUNCA em contracts/schemas/shared/.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / ".dev" / "schemas" / "hb_gate_report.schema.json"
FORBIDDEN_PATH = ROOT / "contracts" / "schemas" / "shared" / "hb_gate_report.schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(instance: dict) -> None:
    schema = _load_schema()
    jsonschema.validate(instance=instance, schema=schema)


def _valid_pass_report() -> dict:
    return {
        "gate_id": "test_gate_001",
        "agent": "claude-code",
        "platform": "claude",
        "role": "adversarial-tester",
        "context_boundary": "isolated_context",
        "status": "PASS",
        "semantic_status": "ADVERSARIAL_PASS_PENDING_GATE",
        "commands": [
            {
                "command": "pytest tests/ -q",
                "exit_code": 0,
                "stdout_ref": "_reports/test_output.txt"
            }
        ],
        "evidence": {
            "diff_ref": ".dev/evidence/diff.patch",
            "files_checked": ["src/training/api/views.py"],
            "logs_checked": ["_reports/test_output.txt"],
            "claims_verified": ["all acceptance criteria met", "no scope overflow"],
            "claims_rejected": []
        },
        "failure": {
            "category": "none",
            "root_cause": ""
        },
        "next_required_gate": "governance_gate"
    }


def _valid_fail_report() -> dict:
    return {
        "gate_id": "test_gate_002",
        "agent": "claude-code",
        "platform": "claude",
        "role": "governance-auditor",
        "context_boundary": "isolated_context",
        "status": "FAIL",
        "semantic_status": "GOVERNANCE_FAIL",
        "commands": [],
        "evidence": {
            "files_checked": ["CLAUDE.md", "AGENTS.md"],
            "claims_verified": [],
            "claims_rejected": ["bridge doc contradicts AI_EXECUTION_ROLES_POLICY.md"]
        },
        "failure": {
            "category": "governance_drift",
            "root_cause": "VALIDATED emitido em bridge doc sem associação a gate executável",
            "evidence_ref": "CLAUDE.md:line_52",
            "recommended_next_action": "Remover VALIDATED de bridge doc e associar apenas a CI"
        },
        "next_required_gate": "ci_validation_gate"
    }


class TestGateReportSchemaExists:
    def test_schema_exists_in_dev_schemas(self):
        """Schema deve existir em .dev/schemas/ (localização experimental)."""
        assert SCHEMA_PATH.exists(), (
            f".dev/schemas/hb_gate_report.schema.json não encontrado em {SCHEMA_PATH}"
        )

    def test_schema_not_in_contracts_shared(self):
        """Schema NÃO deve estar em contracts/schemas/shared/ (reservado para schemas canônicos)."""
        assert not FORBIDDEN_PATH.exists(), (
            "hb_gate_report.schema.json foi colocado em contracts/schemas/shared/ — "
            "schema experimental não pode ser canonizado sem entrada formal no GATES_REGISTRY"
        )

    def test_schema_is_valid_json(self):
        """Schema deve ser JSON válido."""
        schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
        parsed = json.loads(schema_text)
        assert isinstance(parsed, dict)
        assert "$schema" in parsed
        assert "type" in parsed


class TestGateReportSchemaPositive:
    def test_valid_pass_report_accepted(self):
        """Gate report com status PASS e claims_verified preenchido deve ser aceito."""
        _validate(_valid_pass_report())

    def test_valid_fail_report_accepted(self):
        """Gate report com status FAIL e root_cause preenchido deve ser aceito."""
        _validate(_valid_fail_report())

    def test_valid_inconclusive_report_accepted(self):
        """Gate report com status INCONCLUSIVE e category=missing_evidence deve ser aceito."""
        report = {
            "gate_id": "test_gate_003",
            "agent": "codex",
            "platform": "codex",
            "role": "hb-gate-auditor",
            "context_boundary": "sandbox",
            "status": "INCONCLUSIVE",
            "semantic_status": "GATE_INCONCLUSIVE",
            "commands": [],
            "evidence": {
                "files_checked": [],
                "claims_verified": [],
                "claims_rejected": []
            },
            "failure": {
                "category": "missing_evidence",
                "root_cause": "evidence_pack não encontrado no path esperado"
            },
            "next_required_gate": "retry_after_evidence"
        }
        _validate(report)

    def test_valid_blocked_report_accepted(self):
        """Gate report com status BLOCKED deve ser aceito."""
        report = {
            "gate_id": "test_gate_004",
            "agent": "copilot",
            "platform": "copilot",
            "role": "hb-implementer",
            "context_boundary": "same_chat",
            "status": "BLOCKED",
            "semantic_status": "BLOCKED_MISSING_REMOTE_PR",
            "commands": [],
            "evidence": {
                "files_checked": ["_reports/implementation_flow/current_state.json"],
                "claims_verified": [],
                "claims_rejected": ["PR remoto ausente"]
            },
            "failure": {
                "category": "blocked_dependency",
                "root_cause": "PR_URL não presente em implementation_evidence_pack.json"
            },
            "next_required_gate": "pr_creation_required"
        }
        _validate(report)


class TestGateReportSchemaNegative:
    def test_pass_without_claims_verified_rejected(self):
        """PASS sem claims_verified é inválido — ausência de evidência não pode ser PASS."""
        report = _valid_pass_report()
        report["evidence"]["claims_verified"] = []
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_fail_without_root_cause_rejected(self):
        """FAIL sem root_cause é incompleto e deve ser rejeitado."""
        report = _valid_fail_report()
        report["failure"]["root_cause"] = ""
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_inconclusive_wrong_category_rejected(self):
        """INCONCLUSIVE com category != missing_evidence deve ser rejeitado."""
        report = {
            "gate_id": "test_gate_005",
            "agent": "codex",
            "platform": "codex",
            "role": "hb-gate-auditor",
            "context_boundary": "sandbox",
            "status": "INCONCLUSIVE",
            "semantic_status": "GATE_INCONCLUSIVE",
            "commands": [],
            "evidence": {
                "files_checked": [],
                "claims_verified": [],
                "claims_rejected": []
            },
            "failure": {
                "category": "none",  # errado para INCONCLUSIVE
                "root_cause": "algo aconteceu"
            },
            "next_required_gate": "retry"
        }
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_invalid_platform_rejected(self):
        """Plataforma fora do enum é inválida."""
        report = _valid_pass_report()
        report["platform"] = "openai"  # não está no enum
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_invalid_status_rejected(self):
        """Status fora do enum é inválido."""
        report = _valid_pass_report()
        report["status"] = "VALIDATED"  # proibido — apenas CI pode emitir
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_missing_required_field_rejected(self):
        """Falta de campo obrigatório deve ser rejeitada."""
        report = _valid_pass_report()
        del report["gate_id"]
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)

    def test_invalid_context_boundary_rejected(self):
        """context_boundary fora do enum é inválido."""
        report = _valid_pass_report()
        report["context_boundary"] = "same_context"  # não está no enum
        with pytest.raises(jsonschema.ValidationError):
            _validate(report)
