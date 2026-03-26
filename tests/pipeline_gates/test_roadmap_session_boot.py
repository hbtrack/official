import json

import jsonschema


def test_session_start_schema_accepts_roadmap_execution():
    with open("contracts/schemas/shared/session_start.schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_session = {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "session_timestamp": "2026-03-23T12:00:00Z",
        "branch": "hb-track-contratos-driven",
        "pipeline_version": "1.0.0",
        "boot_profile_id": "roadmap_execution",
        "task_type": "execute_roadmap_phase",
        "module": "training",
        "stage": 0,
        "write_scope": "roadmap",
        "worker_id": "execute_roadmap_phase",
    }

    jsonschema.validate(valid_session, schema)
