import uuid

from django.test import Client
from django.test import RequestFactory

import identity_access.api as identity_api
from identity_access.domain.rules import InvalidRole
from identity_access.schemas import AssignRoleIn


def test_list_active_sessions_invalid_page_token_returns_400(monkeypatch):
    request = RequestFactory().get("/api/auth/sessions?pageToken=not-a-uuid")
    monkeypatch.setattr(identity_api, "_extract_roles", lambda req: ["admin"])

    status, payload = identity_api.list_active_sessions(request, pageToken="not-a-uuid")

    assert status == 400
    assert payload["title"] == "Bad Request"
    assert "pageToken" in payload["detail"]


def test_assign_role_invalid_role_returns_400(monkeypatch):
    request = RequestFactory().post(f"/api/auth/users/{uuid.uuid4()}/roles")
    monkeypatch.setattr(identity_api, "_extract_roles", lambda req: ["admin"])

    class StubAssignRoleUseCase:
        def __init__(self, repo):
            self.repo = repo

        def execute(self, **kwargs):
            raise InvalidRole("roleLabel inválido")

    monkeypatch.setattr(identity_api, "AssignRoleUseCase", StubAssignRoleUseCase)

    status, payload = identity_api.assign_role(
        request,
        uuid.uuid4(),
        AssignRoleIn(roleLabel=""),
    )

    assert status == 400
    assert payload["title"] == "Bad Request"
    assert payload["detail"] == "roleLabel inválido"


def test_auth_login_invalid_credentials_returns_problem_json(monkeypatch):
    class StubLoginUseCase:
        def __init__(self, repo):
            self.repo = repo

        def execute(self, **kwargs):
            raise ValueError("Credenciais inválidas.")

    monkeypatch.setattr(identity_api, "LoginUseCase", StubLoginUseCase)

    response = Client().post(
        "/api/auth/login",
        data={"email": "coach@hbtrack.app", "password": "wrong-password"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json()["detail"] == "Credenciais inválidas."
