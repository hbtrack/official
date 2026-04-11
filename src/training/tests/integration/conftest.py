"""conftest para testes de integração do módulo training."""

import sys
import uuid

import pytest


FIXED_COACH_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")


@pytest.fixture(autouse=True)
def inject_training_actor(monkeypatch):
    """Injeta actor_id/role fixos para os testes de integração do módulo."""
    training_api = sys.modules.get("training.api")
    if training_api is None:
        import training.api as training_api

    monkeypatch.setattr(training_api, "_get_actor_id", lambda req: FIXED_COACH_ID)
    monkeypatch.setattr(training_api, "_get_actor_role", lambda req: training_api.RoleLabel.COACH)
