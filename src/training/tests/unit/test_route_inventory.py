"""
Inventário congelado de rotas expostas pelo router training.

Falha se qualquer operação HTTP (método + path + response codes) for adicionada,
removida ou alterada de forma não-intencional. Snapshot gerado na Fase 0.5 a
partir do estado da branch refactor/training-decomposition base em
origin/main@b40763df.

Atualizar `_route_snapshot.json` apenas quando:
  1. O contrato em contracts/openapi/paths/training.yaml foi alterado de forma
     consciente E o OPENAPI_POLICY_RULESET_GATE reflete a mudança.
  2. O path/method/response mapping é movido para outro handler durante refatoração
     estrutural mas o contrato HTTP externo permanece idêntico.

Em qualquer outro caso, falha neste teste é regressão.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_SNAPSHOT_PATH = Path(__file__).parent / "_route_snapshot.json"


def _collect_operations(r: Any, inventory: list[dict[str, Any]]) -> None:
    """Percorre recursivamente o Router e sub-roteadores coletando operações."""
    for path, path_view in r.path_operations.items():
        for op in path_view.operations:
            inventory.append(
                {
                    "methods": sorted(op.methods),
                    "path": path,
                    "response_codes": (
                        sorted(str(c) for c in op.response_models.keys())
                        if op.response_models
                        else []
                    ),
                }
            )
    for entry in r._routers:
        # Ninja armazena (path, router) sem kwargs adicionais
        sub_path, sub_router = entry[0], entry[1]  # suporta 2-tuple e 3-tuple
        _ = sub_path  # caminho foi registrado como "" — rotas já têm path completo
        _collect_operations(sub_router, inventory)


def _current_inventory() -> list[dict[str, Any]]:
    from training.api import router

    inventory: list[dict[str, Any]] = []
    _collect_operations(router, inventory)
    inventory.sort(key=lambda r: (r["path"], r["methods"]))
    return inventory


def test_route_inventory_frozen() -> None:
    current = _current_inventory()
    frozen = json.loads(_SNAPSHOT_PATH.read_text())
    assert current == frozen, (
        "Inventário de rotas divergiu do snapshot. "
        "Se intencional: atualizar _route_snapshot.json e garantir que "
        "contracts/openapi/paths/training.yaml reflete a mudança."
    )


def test_route_inventory_has_expected_cardinality() -> None:
    """Guarda secundária: total de operações."""
    current = _current_inventory()
    frozen = json.loads(_SNAPSHOT_PATH.read_text())
    assert len(current) == len(frozen), (
        f"Contagem de operações mudou: atual={len(current)} snapshot={len(frozen)}"
    )
