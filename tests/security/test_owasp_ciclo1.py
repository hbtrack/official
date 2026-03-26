"""
Testes de segurança OWASP — Task 4.3 (FASE 4).

Valida os 5 requisitos de segurança mínima do Ciclo 1:
  1. BFLA (API5:2023) — operações administrativas retornam 403 com role errado
  2. BOLA (API1:2023) — usuário vê apenas seus próprios recursos
  3. Passwords nunca em responses (API3:2023)
  4. Rate limiting declarado no Nginx
  5. Security headers presentes em responses Django

Os testes BFLA/BOLA são executados no nível de domínio (use cases) para cobrir
o ponto onde o controle é enforçado, sem dependência de JWT real.
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from django.test import RequestFactory


# ══════════════════════════════════════════════════════════════════════════════
# 1. BFLA — Broken Function Level Authorization (OWASP API5:2023)
# ══════════════════════════════════════════════════════════════════════════════

class TestBFLA:
    """
    Garante que operações administrativas retornam InsufficientPrivilege (→ 403)
    quando o caller não tem o role mínimo exigido.
    """

    def test_athlete_cannot_create_team(self):
        """BFLA: createTeam exige admin ou coordinator — athlete → InsufficientPrivilege."""
        from teams.domain.rules import assert_can_create_team, InsufficientPrivilege, RoleLabel

        with pytest.raises(InsufficientPrivilege):
            assert_can_create_team(RoleLabel.ATHLETE)

    def test_member_cannot_create_team(self):
        """BFLA: createTeam exige admin ou coordinator — member → InsufficientPrivilege."""
        from teams.domain.rules import assert_can_create_team, InsufficientPrivilege, RoleLabel

        with pytest.raises(InsufficientPrivilege):
            assert_can_create_team(RoleLabel.MEMBER)

    def test_coach_cannot_create_team(self):
        """BFLA: createTeam exige admin ou coordinator — coach → InsufficientPrivilege."""
        from teams.domain.rules import assert_can_create_team, InsufficientPrivilege, RoleLabel

        with pytest.raises(InsufficientPrivilege):
            assert_can_create_team(RoleLabel.COACH)

    def test_admin_can_create_team(self):
        """BFLA: admin pode criar time — sem exceção."""
        from teams.domain.rules import assert_can_create_team, RoleLabel

        assert_can_create_team(RoleLabel.ADMIN)  # não deve lançar

    def test_coordinator_can_create_team(self):
        """BFLA: coordinator pode criar time — sem exceção."""
        from teams.domain.rules import assert_can_create_team, RoleLabel

        assert_can_create_team(RoleLabel.COORDINATOR)  # não deve lançar

    def test_non_admin_cannot_assign_role(self):
        """BFLA: assignRole exige admin — coach → InsufficientPrivilege."""
        from identity_access.domain.rules import (
            assert_can_assign_or_revoke_role,
            InsufficientPrivilege,
        )

        with pytest.raises(InsufficientPrivilege):
            assert_can_assign_or_revoke_role(caller_roles=["coach"], target_role="athlete")

    def test_coordinator_cannot_assign_role(self):
        """BFLA: assignRole exige admin — coordinator → InsufficientPrivilege."""
        from identity_access.domain.rules import (
            assert_can_assign_or_revoke_role,
            InsufficientPrivilege,
        )

        with pytest.raises(InsufficientPrivilege):
            assert_can_assign_or_revoke_role(caller_roles=["coordinator"], target_role="athlete")

    def test_admin_can_assign_role(self):
        """BFLA: admin pode assignRole — sem exceção."""
        from identity_access.domain.rules import assert_can_assign_or_revoke_role

        assert_can_assign_or_revoke_role(caller_roles=["admin"], target_role="athlete")

    def test_athlete_cannot_revoke_other_session(self):
        """BOLA+BFLA: athlete não pode revogar sessão de outro usuário."""
        from identity_access.domain.rules import (
            assert_can_revoke_session,
            InsufficientPrivilege,
        )

        caller_id = uuid.uuid4()
        other_id = uuid.uuid4()

        with pytest.raises(InsufficientPrivilege):
            assert_can_revoke_session(
                caller_user_id=caller_id,
                caller_roles=["athlete"],
                session_principal_user_id=other_id,
            )

    def test_user_can_revoke_own_session(self):
        """BOLA: usuário pode revogar sua própria sessão."""
        from identity_access.domain.rules import assert_can_revoke_session

        user_id = uuid.uuid4()
        assert_can_revoke_session(
            caller_user_id=user_id,
            caller_roles=["athlete"],
            session_principal_user_id=user_id,
        )

    def test_admin_can_revoke_any_session(self):
        """BFLA: admin pode revogar qualquer sessão."""
        from identity_access.domain.rules import assert_can_revoke_session

        assert_can_revoke_session(
            caller_user_id=uuid.uuid4(),
            caller_roles=["admin"],
            session_principal_user_id=uuid.uuid4(),  # diferente
        )


# ══════════════════════════════════════════════════════════════════════════════
# 2. BOLA — Broken Object Level Authorization (OWASP API1:2023)
# ══════════════════════════════════════════════════════════════════════════════

class TestBOLA:
    """
    Garante que listagens filtram recursos pelo vínculo do ator.
    Testado no nível de use case (comportamento observável no domínio).
    """

    def test_athlete_list_teams_limited_to_own_teams(self):
        """BOLA: athlete só recebe os times onde está vinculado."""
        from teams.application.use_cases import ListTeamsInput, ListTeamsUseCase
        from teams.domain.rules import RoleLabel
        from teams.domain.entities import Team, TeamStatus

        team_a1 = uuid.uuid4()
        team_a2 = uuid.uuid4()

        # Mock repo retorna dois times; use case deve filtrar
        repo = MagicMock()
        repo.list_teams.return_value = (
            [Team(id=team_a1, organization_id=uuid.uuid4(), name="Time A1",
                  category_label="SENIOR", status_label=TeamStatus.ACTIVE)],
            1,
        )

        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(
                actor_role=RoleLabel.ATHLETE,
                actor_team_ids=[team_a1],  # apenas team_a1
                organization_id=None,
            )
        )

        # Use case deve ter passado team_ids_filter ao repo
        call_kwargs = repo.list_teams.call_args.kwargs
        assert call_kwargs["team_ids_filter"] == [team_a1], (
            "BOLA violada: athlete deveria filtrar apenas seus team_ids"
        )

    def test_member_list_teams_returns_empty(self):
        """BOLA: member não acessa listagem de times — retorna vazio sem chamar repo."""
        from teams.application.use_cases import ListTeamsInput, ListTeamsUseCase
        from teams.domain.rules import RoleLabel

        repo = MagicMock()

        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(
                actor_role=RoleLabel.MEMBER,
                actor_team_ids=[],
            )
        )

        assert result.total == 0
        assert result.data == []
        repo.list_teams.assert_not_called()

    def test_admin_list_teams_unrestricted(self):
        """BOLA (negativo): admin não tem restrição de team_ids_filter."""
        from teams.application.use_cases import ListTeamsInput, ListTeamsUseCase
        from teams.domain.rules import RoleLabel

        repo = MagicMock()
        repo.list_teams.return_value = ([], 0)

        ListTeamsUseCase(repo).execute(
            ListTeamsInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                organization_id=uuid.uuid4(),
            )
        )

        call_kwargs = repo.list_teams.call_args.kwargs
        assert call_kwargs["team_ids_filter"] is None, (
            "BOLA violada: admin não deveria ter team_ids_filter"
        )

    def test_athlete_cannot_read_other_team(self):
        """BOLA: athlete não pode ver time onde não está vinculado."""
        from teams.domain.rules import assert_can_read_team, InsufficientPrivilege, RoleLabel

        athlete_team = uuid.uuid4()
        other_team = uuid.uuid4()

        with pytest.raises(InsufficientPrivilege):
            assert_can_read_team(
                actor_role=RoleLabel.ATHLETE,
                actor_team_ids=[athlete_team],
                team_id=other_team,
            )

    def test_athlete_can_read_own_team(self):
        """BOLA (positivo): athlete vê seu próprio time."""
        from teams.domain.rules import assert_can_read_team, RoleLabel

        own_team = uuid.uuid4()
        assert_can_read_team(
            actor_role=RoleLabel.ATHLETE,
            actor_team_ids=[own_team],
            team_id=own_team,
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3. Passwords nunca em responses (OWASP API3:2023)
# ══════════════════════════════════════════════════════════════════════════════

class TestPasswordsNotInResponses:
    """
    Garante que nenhum schema de saída dos módulos do Ciclo 1 expõe campos
    de senha, hash ou credencial.
    """

    _FORBIDDEN_FIELDS = {"password", "password_hash", "hashed_password", "secret", "token_raw"}

    def _get_output_schema_fields(self, schema_cls) -> set[str]:
        """Retorna todos os campos de um Schema Pydantic/Ninja."""
        return set(schema_cls.model_fields.keys())

    def test_user_profile_out_no_password(self):
        from users.schemas import UserProfileOut

        fields = self._get_output_schema_fields(UserProfileOut)
        forbidden = fields & self._FORBIDDEN_FIELDS
        assert not forbidden, f"UserProfileOut expõe campo proibido: {forbidden}"

    def test_login_out_no_password(self):
        """LoginOut só deve ter tokens — nunca password de volta."""
        from identity_access.schemas import LoginOut

        fields = self._get_output_schema_fields(LoginOut)
        assert "password" not in fields
        # accessToken e refreshToken são opacos (JWTs), não senhas
        assert "accessToken" in fields
        assert "refreshToken" in fields

    def test_auth_session_out_no_password(self):
        from identity_access.schemas import AuthSessionOut

        fields = self._get_output_schema_fields(AuthSessionOut)
        forbidden = fields & self._FORBIDDEN_FIELDS
        assert not forbidden, f"AuthSessionOut expõe campo proibido: {forbidden}"

    def test_team_out_no_password(self):
        from teams.schemas import TeamOut

        fields = self._get_output_schema_fields(TeamOut)
        forbidden = fields & self._FORBIDDEN_FIELDS
        assert not forbidden, f"TeamOut expõe campo proibido: {forbidden}"

    def test_user_list_out_no_password(self):
        from users.schemas import UserListOut

        # UserListOut contém lista de UserProfileOut
        fields = self._get_output_schema_fields(UserListOut)
        forbidden = fields & self._FORBIDDEN_FIELDS
        assert not forbidden, f"UserListOut expõe campo proibido: {forbidden}"

    def test_refresh_out_no_password(self):
        """RefreshOut só retorna tokens novos — nunca password."""
        from identity_access.schemas import RefreshOut

        fields = self._get_output_schema_fields(RefreshOut)
        assert "password" not in fields


# ══════════════════════════════════════════════════════════════════════════════
# 4. Security headers em responses Django (OWASP API7:2023)
# ══════════════════════════════════════════════════════════════════════════════

class TestSecurityHeaders:
    """
    Garante que SecurityHeadersMiddleware injeta os headers de segurança
    em todos os responses Django (complemento ao Nginx em produção).
    """

    _REQUIRED_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "X-XSS-Protection": "1; mode=block",
    }

    def test_health_endpoint_has_security_headers(self, client):
        """GET /health deve retornar todos os security headers."""
        response = client.get("/health")
        for header, expected_value in self._REQUIRED_HEADERS.items():
            actual = response.get(header)
            assert actual == expected_value, (
                f"Header '{header}' ausente ou incorreto. "
                f"Esperado: '{expected_value}', Recebido: '{actual}'"
            )

    def test_x_flow_id_present(self, client):
        """X-Flow-ID deve estar em todos os responses (FlowIDMiddleware)."""
        response = client.get("/health")
        assert response.get("X-Flow-ID"), "X-Flow-ID ausente no response"

    def test_nginx_rate_limit_configured(self):
        """
        Confirma que o nginx.conf declara rate limiting >= 100r/s (OWASP API4:2023).
        Lê o arquivo diretamente — não é possível testar rate limiting em unit tests.
        """
        import pathlib

        nginx_conf = pathlib.Path(__file__).parents[2] / "infra" / "nginx" / "nginx.conf"
        content = nginx_conf.read_text()

        assert "rate=100r/s" in content, (
            "nginx.conf não declara rate limiting de 100r/s (OWASP API4:2023)"
        )
        assert "limit_req zone=api_limit" in content, (
            "nginx.conf não aplica o limit_req_zone ao location /api/"
        )

    def test_nginx_security_headers_configured(self):
        """Confirma que o nginx.conf declara os security headers obrigatórios."""
        import pathlib

        nginx_conf = pathlib.Path(__file__).parents[2] / "infra" / "nginx" / "nginx.conf"
        content = nginx_conf.read_text()

        required = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Strict-Transport-Security",
            "Referrer-Policy",
        ]
        for header in required:
            assert header in content, (
                f"nginx.conf não configura header de segurança: {header}"
            )
