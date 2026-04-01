from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _dump_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=False, sort_keys=False), encoding="utf-8")


def _write_minimal_workspace(root: Path, *, component_ref: str = "../../../../schemas/reports/report_job.schema.json", overlay_props: dict | None = None) -> None:
    overlay_props = overlay_props or {
        "statusLabel": {"type": "string", "enum": ["queued", "completed"]},
        "completedAt": {"type": "string"},
        "errorMessage": {"type": "string"},
    }

    _write(
        root / "generated" / "source_graph" / "reports" / "reports.schema_contract_view.yaml",
        yaml.safe_dump(
            {
                "module": "reports",
                "primary_schema_ref": "contracts/schemas/reports/report_job.schema.json",
                "openapi_projection_ref": "contracts/openapi/components/schemas/reports/report_job.yaml",
                "sovereign_fields": [
                    {"name": "id"},
                    {"name": "ownerUserId"},
                    {"name": "reportType"},
                ],
                "runtime_extension_fields": [
                    {"name": "statusLabel"},
                    {"name": "completedAt"},
                    {"name": "errorMessage"},
                ],
            },
            allow_unicode=False,
            sort_keys=False,
        ),
    )
    _write(
        root / "docs" / "hbtrack" / "modulos" / "reports" / "graph" / "module_manifest.yaml",
        yaml.safe_dump(
            {
                "module": "reports",
                "contract_surfaces": {
                    "openapi_paths": "contracts/openapi/paths/reports.yaml",
                },
            },
            allow_unicode=False,
            sort_keys=False,
        ),
    )
    _write(
        root / "contracts" / "schemas" / "reports" / "report_job.schema.json",
        json.dumps(
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["id", "ownerUserId", "reportType"],
                "properties": {
                    "id": {"type": "string"},
                    "ownerUserId": {"type": "string"},
                    "reportType": {"type": "string"},
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / "contracts" / "openapi" / "components" / "schemas" / "reports" / "report_job.yaml",
        yaml.safe_dump({"$ref": component_ref}, allow_unicode=False, sort_keys=False),
    )
    _dump_yaml(
        root / "contracts" / "openapi" / "paths" / "reports.yaml",
        {
            "/reports/jobs": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "array",
                                                "items": {
                                                    "allOf": [
                                                        {"$ref": "../components/schemas/reports/report_job.yaml"},
                                                        {
                                                            "type": "object",
                                                            "required": ["statusLabel"],
                                                            "properties": overlay_props,
                                                        },
                                                    ]
                                                },
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    )


def test_openapi_schema_equivalence_gate_passes_for_direct_ref_and_runtime_overlay(tmp_path):
    _write_minimal_workspace(tmp_path)

    result = gates._g8a_openapi_schema_equivalence(tmp_path)

    assert result["status"] == "PASS"


def test_openapi_schema_equivalence_gate_fails_for_manual_component_projection(tmp_path):
    _write_minimal_workspace(tmp_path, component_ref="#/inline/manual")

    result = gates._g8a_openapi_schema_equivalence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("report_job.yaml" in item["artifact"] for item in result.get("violations", []))


def test_openapi_schema_equivalence_gate_fails_when_overlay_redefines_sovereign_field(tmp_path):
    _write_minimal_workspace(
        tmp_path,
        overlay_props={
            "statusLabel": {"type": "string"},
            "reportType": {"type": "string"},
        },
    )

    result = gates._g8a_openapi_schema_equivalence(tmp_path)

    assert result["status"] == "FAIL"
    assert any("Projection drift" in item["message"] for item in result.get("violations", []))


def test_openapi_schema_equivalence_gate_is_wired_in_executor_and_registry():
    validator = (ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py").read_text(encoding="utf-8")
    registry = (ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml").read_text(encoding="utf-8")

    assert "OPENAPI_SCHEMA_EQUIVALENCE_GATE" in validator
    assert "_g8a_openapi_schema_equivalence" in validator
    assert "OPENAPI_SCHEMA_EQUIVALENCE_GATE" in registry
