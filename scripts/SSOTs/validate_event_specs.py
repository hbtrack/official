#!/usr/bin/env python3
"""
Validação básica para specs de eventos e projeções.
Uso:
  python validate_event_specs.py path/to/events.yaml path/to/projections.yaml
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(2)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def validate_events(doc: dict[str, Any]) -> set[str]:
    if not isinstance(doc, dict):
        fail("events.yaml deve ser um objeto YAML")
    for field in ["module", "version", "status", "aggregate_root", "events"]:
        if field not in doc:
            fail(f"events.yaml ausente campo obrigatório: {field}")
    events = doc["events"]
    if not isinstance(events, list) or not events:
        fail("events.yaml deve conter lista não vazia em 'events'")

    names: set[str] = set()
    for idx, event in enumerate(events, start=1):
        prefix = f"events[{idx}]"
        for field in [
            "name",
            "event_version",
            "aggregate_type",
            "trigger",
            "description",
            "emission_mode",
            "transactional",
            "payload",
            "relations",
            "consumers",
        ]:
            if field not in event:
                fail(f"{prefix} ausente campo obrigatório: {field}")
        name = event["name"]
        if name in names:
            fail(f"nome de evento duplicado: {name}")
        names.add(name)
        payload = event["payload"]
        if "required" not in payload or "optional" not in payload:
            fail(f"{prefix}.payload deve conter 'required' e 'optional'")
        relations = event["relations"]
        for rel_key in ["contracts", "flows", "invariants"]:
            if rel_key not in relations:
                fail(f"{prefix}.relations ausente: {rel_key}")
        if event["emission_mode"] not in {"sync", "async", "batch"}:
            fail(f"{prefix}.emission_mode inválido: {event['emission_mode']}")
    ok(f"events.yaml validado com {len(names)} evento(s)")
    return names


def validate_projections(doc: dict[str, Any], known_events: set[str]) -> None:
    if not isinstance(doc, dict):
        fail("projections.yaml deve ser um objeto YAML")
    for field in ["module", "version", "status", "projections"]:
        if field not in doc:
            fail(f"projections.yaml ausente campo obrigatório: {field}")
    projections = doc["projections"]
    if not isinstance(projections, list) or not projections:
        fail("projections.yaml deve conter lista não vazia em 'projections'")

    names: set[str] = set()
    for idx, prj in enumerate(projections, start=1):
        prefix = f"projections[{idx}]"
        for field in [
            "name",
            "description",
            "source_events",
            "grain",
            "fields",
            "refresh_mode",
            "consistency_model",
            "storage_target",
            "rebuild_strategy",
            "consumers",
        ]:
            if field not in prj:
                fail(f"{prefix} ausente campo obrigatório: {field}")
        name = prj["name"]
        if name in names:
            fail(f"nome de projeção duplicado: {name}")
        names.add(name)
        for ev in prj["source_events"]:
            if ev not in known_events:
                fail(f"{prefix} referencia evento desconhecido: {ev}")
        if prj["refresh_mode"] not in {"sync", "async", "batch"}:
            fail(f"{prefix}.refresh_mode inválido: {prj['refresh_mode']}")
        if prj["consistency_model"] not in {"strong", "eventual"}:
            fail(f"{prefix}.consistency_model inválido: {prj['consistency_model']}")
    ok(f"projections.yaml validado com {len(names)} projeção(ões)")


def main() -> None:
    if len(sys.argv) != 3:
        print("Uso: python validate_event_specs.py <events.yaml> <projections.yaml>")
        raise SystemExit(4)

    events_path = Path(sys.argv[1])
    projections_path = Path(sys.argv[2])
    if not events_path.exists():
        fail(f"arquivo não encontrado: {events_path}")
    if not projections_path.exists():
        fail(f"arquivo não encontrado: {projections_path}")

    event_doc = load_yaml(events_path)
    projection_doc = load_yaml(projections_path)

    known_events = validate_events(event_doc)
    validate_projections(projection_doc, known_events)
    ok("specs de eventos/projeções consistentes")


if __name__ == "__main__":
    main()