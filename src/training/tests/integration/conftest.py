"""conftest para testes de integração do módulo training."""

import sys
import uuid

import pytest

from training.domain.rules import RoleLabel

FIXED_COACH_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")

# Sub-módulos que definem handlers com _get_actor_id / _get_actor_role
_SUBMODULE_NAMES = [
    "analytics",
    "attendance",
    "attention",
    "blocks",
    "chat",
    "eligibility",
    "execution",
    "feedback",
    "planning",
    "recommendations",
    "sessions",
    "wellness",
]


@pytest.fixture(autouse=True)
def inject_training_actor(monkeypatch):
    """Injeta actor_id/role fixos para os testes de integração do módulo.

    Com a decomposição em sub-roteadores, cada sub-módulo importa
    _get_actor_id/_get_actor_role diretamente de deps.py (binding local).
    É necessário fazer patch em cada módulo individualmente.
    """
    import training.api  # garante que o pacote e sub-módulos estão carregados  # noqa: F401

    fixed_id = lambda req: FIXED_COACH_ID  # noqa: E731
    fixed_role = lambda req: RoleLabel.COACH  # noqa: E731

    for sub_name in _SUBMODULE_NAMES:
        mod = sys.modules.get(f"training.api.{sub_name}")
        if mod is None:
            continue
        if hasattr(mod, "_get_actor_id"):
            monkeypatch.setattr(mod, "_get_actor_id", fixed_id)
        if hasattr(mod, "_get_actor_role"):
            monkeypatch.setattr(mod, "_get_actor_role", fixed_role)
