"""Shared helpers for codegen parity tests."""
from __future__ import annotations

import ast
import re
import uuid
from pathlib import Path
from typing import Any, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440010")
FROZEN_UUID2 = uuid.UUID("550e8400-e29b-41d4-a716-446655440020")


class InMemoryRepo:
    """Generic in-memory repo matching generated repository interface."""

    def __init__(self, entities: list | None = None):
        self._store: dict[uuid.UUID, Any] = {}
        for e in entities or []:
            self._store[e.id] = e

    def save(self, entity):
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, entity_id):
        return self._store.get(entity_id)

    def list_entities(self, page_size=20, page_token=None):
        items = list(self._store.values())
        offset = int(page_token) if page_token and str(page_token).isdigit() else 0
        selected = items[offset : offset + page_size]
        next_token = str(offset + page_size) if (offset + page_size) < len(items) else None
        return selected, next_token


_PARAM_RE = re.compile(r"\{[^}]+\}")


def _normalize_route(route: str) -> str:
    """Normalize route for comparison: strip param names, normalize empty/slash."""
    normalized = _PARAM_RE.sub("{_}", route)
    if normalized == "":
        normalized = "/"
    return normalized


def route_surface(path: Path) -> list[dict[str, Any]]:
    """Extract HTTP route (method, path) pairs from an api.py via AST."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    routes: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            if not isinstance(dec.func.value, ast.Name) or dec.func.value.id != "router":
                continue
            route = ast.literal_eval(dec.args[0])
            routes.append({"method": dec.func.attr.upper(), "route": route})
    return routes


def route_set(routes: list[dict]) -> set[tuple[str, str]]:
    """Convert route list to {(METHOD, normalized_path)} set for comparison."""
    return {(r["method"], _normalize_route(r["route"])) for r in routes}


def route_methods(routes: list[dict]) -> dict[str, int]:
    """Count routes per HTTP method for structural comparison."""
    counts: dict[str, int] = {}
    for r in routes:
        m = r["method"]
        counts[m] = counts.get(m, 0) + 1
    return counts


def source_graph_methods(module: str) -> dict[str, int]:
    """Count endpoints per HTTP method from the module's source graph endpoints.yaml."""
    ep_path = REPO_ROOT / "docs" / "hbtrack" / "modulos" / module / "graph" / "endpoints.yaml"
    data = yaml.safe_load(ep_path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for ep in data.get("endpoints", []):
        m = ep["method"].upper()
        counts[m] = counts.get(m, 0) + 1
    return counts
