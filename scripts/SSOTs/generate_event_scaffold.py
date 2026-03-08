#!/usr/bin/env python3
"""
Gera um scaffold mínimo de runtime de eventos a partir de events.yaml.
Uso:
  python generate_event_scaffold.py path/to/events.yaml output_dir/
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def snake(name: str) -> str:
    return name.lower().replace("-", "_")


def py_value(type_hint: str) -> str:
    mapping = {
        "uuid": "str",
        "string": "str",
        "int": "int",
        "bool": "bool",
        "datetime": "str",
    }
    return mapping.get(type_hint.split("|")[0].replace("null", "str"), "object")


def render_helpers(module: str, events: list[dict[str, Any]]) -> str:
    lines = [
        '"""Helpers gerados para emissão de eventos de domínio."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "from datetime import datetime, timezone",
        "from typing import Any",
        "from uuid import uuid4",
        "",
        "@dataclass(frozen=True)",
        "class DomainEvent:",
        "    event_id: str",
        "    event_type: str",
        "    event_version: int",
        "    aggregate_type: str",
        "    aggregate_id: str",
        "    occurred_at: str",
        "    actor_user_id: str | None",
        "    payload: dict[str, Any]",
        "",
        "def append_event(store: list[DomainEvent], event: DomainEvent) -> None:",
        "    store.append(event)",
        "",
    ]
    for event in events:
        name = snake(event["name"])
        required = event["payload"].get("required", {})
        args = ["aggregate_id: str", "actor_user_id: str | None = None"]
        payload_parts = []
        for field, type_hint in required.items():
            args.append(f"{field}: {py_value(type_hint)}")
            payload_parts.append(f'        "{field}": {field},')
        lines.extend([
            f"def emit_{name}(store: list[DomainEvent], {', '.join(args)}) -> DomainEvent:",
            "    event = DomainEvent(",
            "        event_id=str(uuid4()),",
            f'        event_type="{event["name"]}",',
            f'        event_version={event["event_version"]},',
            f'        aggregate_type="{event["aggregate_type"]}",',
            "        aggregate_id=aggregate_id,",
            "        occurred_at=datetime.now(timezone.utc).isoformat(),",
            "        actor_user_id=actor_user_id,",
            "        payload={",
            *payload_parts,
            "        },",
            "    )",
            "    append_event(store, event)",
            "    return event",
            "",
        ])
    return "\n".join(lines)


def render_sql_schema() -> str:
    return """-- event_store mínimo\nCREATE TABLE IF NOT EXISTS event_store (\n    id UUID PRIMARY KEY,\n    event_type TEXT NOT NULL,\n    event_version INTEGER NOT NULL,\n    aggregate_type TEXT NOT NULL,\n    aggregate_id TEXT NOT NULL,\n    occurred_at TIMESTAMPTZ NOT NULL,\n    actor_user_id TEXT NULL,\n    payload_json JSONB NOT NULL\n);\n\nCREATE INDEX IF NOT EXISTS idx_event_store_aggregate\n    ON event_store (aggregate_type, aggregate_id, occurred_at);\n\nCREATE INDEX IF NOT EXISTS idx_event_store_type\n    ON event_store (event_type, occurred_at);\n"""


def render_test_stub(module: str, events: list[dict[str, Any]]) -> str:
    lines = [
        '"""Testes básicos gerados para eventos."""',
        "from generated.event_helpers import DomainEvent",
        "",
    ]
    for event in events:
        fn = snake(event["name"])
        lines.extend([
            f"def test_{fn}_name_constant():",
            f"    assert \"{event['name']}\" == \"{event['name']}\"",
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 3:
        print("Uso: python generate_event_scaffold.py <events.yaml> <output_dir>")
        raise SystemExit(4)

    events_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = load_yaml(events_path)
    module = doc["module"]
    events = doc["events"]

    generated_dir = out_dir / "generated"
    tests_dir = out_dir / "tests"
    generated_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    (generated_dir / "event_helpers.py").write_text(render_helpers(module, events), encoding="utf-8")
    (generated_dir / "event_store.sql").write_text(render_sql_schema(), encoding="utf-8")
    (tests_dir / "test_generated_events.py").write_text(render_test_stub(module, events), encoding="utf-8")

    print(f"PASS: scaffold gerado em {out_dir}")


if __name__ == "__main__":
    main()