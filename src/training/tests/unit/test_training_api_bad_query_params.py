import uuid

import pytest
from django.test import RequestFactory
from ninja.errors import HttpError

import training.api as training_api


def test_list_mesocycles_invalid_organization_id_returns_400():
    request = RequestFactory().get("/api/training/mesocycles?organization_id=null")

    with pytest.raises(HttpError) as exc_info:
        training_api.list_mesocycles(request)

    assert exc_info.value.status_code == 400
    assert "organization_id" in str(exc_info.value.message)


def test_list_training_sessions_invalid_season_id_returns_400(monkeypatch):
    request = RequestFactory().get("/api/training/training-sessions?season_id=not-a-uuid")
    monkeypatch.setattr(training_api, "_get_actor_role", lambda req: training_api.RoleLabel.ADMIN)
    monkeypatch.setattr(training_api, "_get_actor_id", lambda req: uuid.uuid4())

    with pytest.raises(HttpError) as exc_info:
        training_api.list_training_sessions(request)

    assert exc_info.value.status_code == 400
    assert "season_id" in str(exc_info.value.message)
