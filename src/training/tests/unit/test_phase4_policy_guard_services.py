"""
Testes de Fase 4: SessionAccessPolicy, SessionGuard e TrainingServices.

Cobre:
- SessionAccessPolicy: require_readable, require_mutable, require_in_progress,
  require_valid_transition, require_write_access, require_deletable
- SessionGuard: todos os métodos load_for_*
- TrainingServices: façade expõe somente métodos (nenhum atributo de repositório)
- TrainingServices: mock injection via configure_for_testing / reset_testing_overrides (N3.1)
"""
from __future__ import annotations

import inspect
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from training.domain.entities import TrainingSession, TrainingSessionStatus
from training.domain.policies.session_access import SessionAccessPolicy, SessionGuard
from training.domain.rules import (
    CAN_ARCHIVE_SESSION,
    CAN_DELETE_SESSION,
    MUTABLE_STATES,
    STAFF_ROLES,
    InsufficientPrivilege,
    RoleLabel,
    SessionNotMutable,
    TrainingSessionNotFound,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_session(status: TrainingSessionStatus = TrainingSessionStatus.DRAFT) -> TrainingSession:
    return TrainingSession(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        session_at=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        session_type="regular",
        status=status,
        created_by_user_id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture()
def policy():
    return SessionAccessPolicy()


@pytest.fixture()
def session_draft():
    return _make_session(TrainingSessionStatus.DRAFT)


@pytest.fixture()
def session_in_progress():
    return _make_session(TrainingSessionStatus.IN_PROGRESS)


@pytest.fixture()
def session_completed():
    return _make_session(TrainingSessionStatus.COMPLETED)


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_readable
# ---------------------------------------------------------------------------

class TestRequireReadable:
    def test_staff_roles_can_read(self, policy, session_draft):
        for role in STAFF_ROLES:
            policy.require_readable(session_draft, role, uuid.uuid4(), [])  # sem exceção

    def test_athlete_in_session_can_read(self, policy, session_draft):
        athlete_id = uuid.uuid4()
        policy.require_readable(session_draft, RoleLabel.ATHLETE, athlete_id, [athlete_id])

    def test_athlete_not_in_session_raises(self, policy, session_draft):
        with pytest.raises(InsufficientPrivilege, match="BOLA"):
            policy.require_readable(session_draft, RoleLabel.ATHLETE, uuid.uuid4(), [])

    def test_member_role_raises(self, policy, session_draft):
        with pytest.raises(InsufficientPrivilege):
            policy.require_readable(session_draft, RoleLabel.MEMBER, uuid.uuid4(), [])


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_mutable
# ---------------------------------------------------------------------------

class TestRequireMutable:
    @pytest.mark.parametrize("status", list(MUTABLE_STATES))
    def test_staff_can_modify_mutable(self, policy, status):
        session = _make_session(status)
        for role in STAFF_ROLES:
            policy.require_mutable(session, role)  # sem exceção

    def test_athlete_cannot_modify(self, policy, session_draft):
        with pytest.raises(InsufficientPrivilege):
            policy.require_mutable(session_draft, RoleLabel.ATHLETE)

    def test_completed_session_not_mutable(self, policy, session_completed):
        with pytest.raises(SessionNotMutable):
            policy.require_mutable(session_completed, RoleLabel.ADMIN)

    def test_in_progress_not_in_mutable_states(self, policy, session_in_progress):
        """IN_PROGRESS não está em MUTABLE_STATES — require_mutable deve rejeitar."""
        assert TrainingSessionStatus.IN_PROGRESS not in MUTABLE_STATES
        with pytest.raises(SessionNotMutable):
            policy.require_mutable(session_in_progress, RoleLabel.ADMIN)


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_in_progress
# ---------------------------------------------------------------------------

class TestRequireInProgress:
    def test_staff_can_use_in_progress(self, policy, session_in_progress):
        for role in STAFF_ROLES:
            policy.require_in_progress(session_in_progress, role)  # sem exceção

    def test_athlete_cannot_record(self, policy, session_in_progress):
        with pytest.raises(InsufficientPrivilege):
            policy.require_in_progress(session_in_progress, RoleLabel.ATHLETE)

    def test_draft_session_not_in_progress(self, policy, session_draft):
        with pytest.raises(SessionNotMutable):
            policy.require_in_progress(session_draft, RoleLabel.ADMIN)


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_valid_transition
# ---------------------------------------------------------------------------

class TestRequireValidTransition:
    def test_staff_can_transition_draft_to_scheduled(self, policy, session_draft):
        """DRAFT → SCHEDULED é válida pelo FSM canônico."""
        for role in STAFF_ROLES:
            policy.require_valid_transition(
                session_draft, TrainingSessionStatus.SCHEDULED, role
            )

    def test_non_staff_cannot_transition(self, policy, session_draft):
        with pytest.raises(InsufficientPrivilege):
            policy.require_valid_transition(
                session_draft, TrainingSessionStatus.SCHEDULED, RoleLabel.ATHLETE
            )

    def test_non_archive_role_cannot_archive(self, policy, session_completed):
        """COACH está em STAFF_ROLES mas não em CAN_ARCHIVE_SESSION."""
        assert RoleLabel.COACH in STAFF_ROLES
        assert RoleLabel.COACH not in CAN_ARCHIVE_SESSION
        with pytest.raises(InsufficientPrivilege, match="arquivar"):
            policy.require_valid_transition(
                session_completed, TrainingSessionStatus.ARCHIVED, RoleLabel.COACH
            )

    def test_admin_can_archive_completed(self, policy, session_completed):
        policy.require_valid_transition(
            session_completed, TrainingSessionStatus.ARCHIVED, RoleLabel.ADMIN
        )


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_write_access
# ---------------------------------------------------------------------------

class TestRequireWriteAccess:
    def test_staff_has_write_access(self, policy):
        for role in STAFF_ROLES:
            policy.require_write_access(role)  # sem exceção

    def test_athlete_no_write_access(self, policy):
        with pytest.raises(InsufficientPrivilege):
            policy.require_write_access(RoleLabel.ATHLETE)


# ---------------------------------------------------------------------------
# SessionAccessPolicy — require_deletable
# ---------------------------------------------------------------------------

class TestRequireDeletable:
    def test_can_delete_roles(self, policy, session_draft):
        for role in CAN_DELETE_SESSION:
            policy.require_deletable(session_draft, role)  # sem exceção

    def test_coach_cannot_delete(self, policy, session_draft):
        """COACH está em STAFF_ROLES mas não em CAN_DELETE_SESSION."""
        assert RoleLabel.COACH not in CAN_DELETE_SESSION
        with pytest.raises(InsufficientPrivilege):
            policy.require_deletable(session_draft, RoleLabel.COACH)

    def test_in_progress_session_not_deletable(self, policy, session_in_progress):
        with pytest.raises(InsufficientPrivilege, match="DR-TRAIN-027"):
            policy.require_deletable(session_in_progress, RoleLabel.ADMIN)


# ---------------------------------------------------------------------------
# SessionGuard
# ---------------------------------------------------------------------------

def _mock_repo(session=None):
    repo = MagicMock()
    repo.get_by_id.return_value = session
    return repo


class TestSessionGuard:
    def test_load_for_update_returns_session(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        result = guard.load_for_update(session.id, RoleLabel.ADMIN)
        assert result is session

    def test_load_for_update_not_found_raises(self):
        guard = SessionGuard(_mock_repo(None))
        with pytest.raises(TrainingSessionNotFound):
            guard.load_for_update(uuid.uuid4(), RoleLabel.ADMIN)

    def test_load_for_update_non_mutable_raises(self):
        session = _make_session(TrainingSessionStatus.COMPLETED)
        guard = SessionGuard(_mock_repo(session))
        with pytest.raises(SessionNotMutable):
            guard.load_for_update(session.id, RoleLabel.ADMIN)

    def test_load_for_in_progress_returns_session(self):
        session = _make_session(TrainingSessionStatus.IN_PROGRESS)
        guard = SessionGuard(_mock_repo(session))
        result = guard.load_for_in_progress(session.id, RoleLabel.COACH)
        assert result is session

    def test_load_for_in_progress_wrong_status_raises(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        with pytest.raises(SessionNotMutable):
            guard.load_for_in_progress(session.id, RoleLabel.ADMIN)

    def test_load_for_transition_valid(self):
        """DRAFT → SCHEDULED é uma transição válida pelo FSM canônico."""
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        result = guard.load_for_transition(
            session.id, TrainingSessionStatus.SCHEDULED, RoleLabel.ADMIN
        )
        assert result is session

    def test_load_for_read_staff(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        result = guard.load_for_read(session.id, RoleLabel.ADMIN, uuid.uuid4(), [])
        assert result is session

    def test_load_for_read_athlete_not_in_session_raises(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        with pytest.raises(InsufficientPrivilege, match="BOLA"):
            guard.load_for_read(session.id, RoleLabel.ATHLETE, uuid.uuid4(), [])

    def test_load_for_delete_valid(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        result = guard.load_for_delete(session.id, RoleLabel.ADMIN)
        assert result is session

    def test_load_for_delete_in_progress_raises(self):
        session = _make_session(TrainingSessionStatus.IN_PROGRESS)
        guard = SessionGuard(_mock_repo(session))
        with pytest.raises(InsufficientPrivilege, match="DR-TRAIN-027"):
            guard.load_for_delete(session.id, RoleLabel.ADMIN)

    def test_load_with_write_access_staff(self):
        session = _make_session(TrainingSessionStatus.IN_PROGRESS)
        guard = SessionGuard(_mock_repo(session))
        # IN_PROGRESS é aceito — write_access não checa estado
        result = guard.load_with_write_access(session.id, RoleLabel.ADMIN)
        assert result is session

    def test_load_with_write_access_athlete_raises(self):
        session = _make_session(TrainingSessionStatus.DRAFT)
        guard = SessionGuard(_mock_repo(session))
        with pytest.raises(InsufficientPrivilege):
            guard.load_with_write_access(session.id, RoleLabel.ATHLETE)


# ---------------------------------------------------------------------------
# TrainingServices — enforcement de facade
# ---------------------------------------------------------------------------

class TestTrainingServicesFacade:
    def test_exposes_only_factories(self):
        """
        REGRA: TrainingServices não deve ter atributos de repositório.
        Todos os membros públicos devem ser métodos callable.
        """
        from training.application.common.services import TrainingServices

        svc = TrainingServices()
        for name in dir(svc):
            if name.startswith("_"):
                continue
            member = getattr(svc, name)
            assert callable(member), (
                f"TrainingServices.{name} é atributo não-callable — "
                "use factory method em vez de atributo de repositório"
            )

    def test_no_repository_attributes_on_instance(self):
        """TrainingServices não deve ter repositórios armazenados em __dict__."""
        from training.application.common.services import TrainingServices

        svc = TrainingServices()
        for attr_name, attr_value in vars(svc).items():
            # Verifica que nenhum atributo de instância é um repositório
            type_name = type(attr_value).__name__
            assert "Repository" not in type_name, (
                f"TrainingServices.{attr_name} armazena {type_name} — "
                "repositórios devem ser criados nos factory methods, não no __init__"
            )

    def test_services_can_be_instantiated_without_args(self):
        from training.application.common.services import TrainingServices

        svc = TrainingServices()
        assert svc is not None

    def test_session_guard_factory(self):
        from training.application.common.services import TrainingServices

        svc = TrainingServices()
        guard = svc.session_guard()
        assert isinstance(guard, SessionGuard)


# ---------------------------------------------------------------------------
# TrainingServices — mock injection via configure_for_testing (N3.1)
# ---------------------------------------------------------------------------

class TestTrainingServicesMockInjection:
    """
    Valida a API de injeção de mocks via configure_for_testing / reset_testing_overrides.

    Garante que testes unitários de UseCases podem usar TrainingServices sem
    precisar de unittest.mock.patch no nível de módulo (fechamento de P15).
    """

    def teardown_method(self):
        """Limpeza obrigatória — remove overrides para não vazar entre testes."""
        from training.application.common.services import TrainingServices
        TrainingServices.reset_testing_overrides()

    def test_configure_for_testing_injects_mock_use_case(self):
        """override de factory retorna o mock, não o UseCase real."""
        from unittest.mock import MagicMock
        from training.application.common.services import TrainingServices
        from training.application.sessions.commands import CreateTrainingSessionUseCase

        mock_uc = MagicMock(spec=CreateTrainingSessionUseCase)
        TrainingServices.configure_for_testing(
            create_training_session_uc=lambda: mock_uc
        )
        svc = TrainingServices()
        result = svc.create_training_session_uc()
        assert result is mock_uc

    def test_non_overridden_factories_still_work(self):
        """Factory sem override continua retornando objeto real."""
        from unittest.mock import MagicMock
        from training.application.common.services import TrainingServices
        from training.application.sessions.commands import CreateTrainingSessionUseCase

        mock_uc = MagicMock(spec=CreateTrainingSessionUseCase)
        TrainingServices.configure_for_testing(
            create_training_session_uc=lambda: mock_uc
        )
        svc = TrainingServices()
        guard = svc.session_guard()
        assert isinstance(guard, SessionGuard)

    def test_reset_restores_original_behavior(self):
        """Após reset, factory retorna o UseCase real novamente."""
        from unittest.mock import MagicMock
        from training.application.common.services import TrainingServices
        from training.application.sessions.commands import CreateTrainingSessionUseCase

        mock_uc = MagicMock(spec=CreateTrainingSessionUseCase)
        TrainingServices.configure_for_testing(
            create_training_session_uc=lambda: mock_uc
        )
        TrainingServices.reset_testing_overrides()
        svc = TrainingServices()
        result = svc.create_training_session_uc()
        assert isinstance(result, CreateTrainingSessionUseCase)
        assert result is not mock_uc

    def test_overrides_are_class_level_not_instance_level(self):
        """_test_overrides não aparece em vars(svc) — não viola regra de no-repo-attributes."""
        from training.application.common.services import TrainingServices

        TrainingServices.configure_for_testing(
            get_training_session_uc=lambda: object()
        )
        svc = TrainingServices()
        # _test_overrides é class var — não deve aparecer em vars(svc)
        assert "_test_overrides" not in vars(svc)

    def test_multiple_overrides_simultaneously(self):
        """Múltiplos overrides independentes coexistem sem conflito."""
        from unittest.mock import MagicMock
        from training.application.common.services import TrainingServices
        from training.application.sessions.commands import CreateTrainingSessionUseCase
        from training.application.sessions.queries import GetTrainingSessionUseCase

        mock_create = MagicMock(spec=CreateTrainingSessionUseCase)
        mock_get = MagicMock(spec=GetTrainingSessionUseCase)
        TrainingServices.configure_for_testing(
            create_training_session_uc=lambda: mock_create,
            get_training_session_uc=lambda: mock_get,
        )
        svc = TrainingServices()
        assert svc.create_training_session_uc() is mock_create
        assert svc.get_training_session_uc() is mock_get

    def test_configure_for_testing_and_reset_are_public_callable(self):
        """configure_for_testing e reset_testing_overrides são callables públicos."""
        from training.application.common.services import TrainingServices

        assert callable(TrainingServices.configure_for_testing)
        assert callable(TrainingServices.reset_testing_overrides)
