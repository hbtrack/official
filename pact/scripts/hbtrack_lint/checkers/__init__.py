"""
Pacote de checkers do módulo ATLETAS.

Cada módulo registra seus checkers via register_checker() do engine.
"""
from __future__ import annotations


def register_all_checkers() -> None:
    """Importa todos os módulos de checkers, disparando o registro automático."""
    from hbtrack_lint.checkers import (
        documents,
        cross,
        db,
        ui,
        invariants,
        handoff,
        events,
        side_effects,
        time,
        tests,
        anchors,
        restrictions,
        projections,
    )
