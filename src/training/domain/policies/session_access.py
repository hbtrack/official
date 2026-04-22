"""
Domain policy: controla acesso a sessões de treino.

Consolida a lógica de assert_can_* de domain/rules.py numa interface
orientada a *intenção* (readable / mutable / in_progress) em vez de
verbos de operação (create / modify / delete).

Também expõe SessionGuard — helper de application layer que encapsula
o padrão "load → NotFound → policy.require_* → return" repetido em 10+
UseCases. SessionGuard fica neste arquivo porque ele depende apenas de
entidades de domínio e da policy — sem Django, sem HTTP.

Não importa Django. Não importa infrastructure.
"""
from __future__ import annotations

import uuid

from ..entities import TrainingSession, TrainingSessionStatus
from ..rules import (
    CAN_ARCHIVE_SESSION,
    CAN_DELETE_SESSION,
    MUTABLE_STATES,
    STAFF_ROLES,
    InsufficientPrivilege,
    RoleLabel,
    SessionNotMutable,
    assert_valid_transition,
)


class SessionAccessPolicy:
    """
    Centraliza verificações de autorização para acesso a sessões.

    Cada método levanta a exceção de domínio adequada se a condição
    não for satisfeita. Sem efeitos colaterais.
    """

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def require_readable(
        self,
        session: TrainingSession,
        role: RoleLabel,
        actor_id: object,
        athlete_ids: list | tuple,
    ) -> None:
        """
        BOLA — OWASP API1:2023.
        Staff acessa qualquer sessão; athlete só acessa sessão onde está.
        """
        if role in STAFF_ROLES:
            return
        if role == RoleLabel.ATHLETE:
            if actor_id not in athlete_ids:
                raise InsufficientPrivilege(
                    "BOLA: athlete não pertence a esta sessão"
                )
            return
        raise InsufficientPrivilege(f"role={role} não tem acesso a sessões de treino")

    # ------------------------------------------------------------------
    # Escrita — estado mutável
    # ------------------------------------------------------------------

    def require_mutable(
        self,
        session: TrainingSession,
        role: RoleLabel,
    ) -> None:
        """
        Staff pode modificar; sessão deve estar em MUTABLE_STATES.
        Equivalente a assert_can_modify_session + assert_session_mutable.
        """
        if role not in STAFF_ROLES:
            raise InsufficientPrivilege(
                f"role={role} não tem permissão para modificar sessões"
            )
        if session.status not in MUTABLE_STATES:
            raise SessionNotMutable(
                f"Sessão em estado {session.status} não permite edição"
            )

    # ------------------------------------------------------------------
    # Escrita — sessão em andamento (IN_PROGRESS)
    # ------------------------------------------------------------------

    def require_in_progress(
        self,
        session: TrainingSession,
        role: RoleLabel,
    ) -> None:
        """
        Staff pode registrar; sessão deve estar IN_PROGRESS.
        Usado por CreateExecutionRecordUseCase.
        """
        if role not in STAFF_ROLES:
            raise InsufficientPrivilege(
                f"role={role} não tem permissão para registrar execução"
            )
        if session.status != TrainingSessionStatus.IN_PROGRESS:
            raise SessionNotMutable(
                f"Sessão em estado {session.status} não está IN_PROGRESS"
            )

    # ------------------------------------------------------------------
    # Transição de status (FSM)
    # ------------------------------------------------------------------

    def require_valid_transition(
        self,
        session: TrainingSession,
        target_status: TrainingSessionStatus,
        role: RoleLabel,
    ) -> None:
        """
        Verifica permissão de role + validade da transição FSM.
        Para ARCHIVED verifica também CAN_ARCHIVE_SESSION.
        """
        if role not in STAFF_ROLES:
            raise InsufficientPrivilege(
                f"role={role} não tem permissão para transitar sessões"
            )
        if target_status == TrainingSessionStatus.ARCHIVED:
            if role not in CAN_ARCHIVE_SESSION:
                raise InsufficientPrivilege(
                    "Apenas admin/coordinator podem arquivar sessões"
                )
        assert_valid_transition(session.status, target_status)

    def require_write_access(self, role: RoleLabel) -> None:
        """
        Verifica que o role pode escrever em sessões (staff only).
        Não verifica o estado da sessão — usado quando o UseCase
        aplica suas próprias regras de estado (ex: CreateSessionObjective).
        """
        if role not in STAFF_ROLES:
            raise InsufficientPrivilege(
                f"role={role} não tem permissão para modificar sessões"
            )

    def require_deletable(
        self,
        session: TrainingSession,
        role: RoleLabel,
    ) -> None:
        """
        DR-TRAIN-027: apenas admin/coordinator podem excluir;
        sessões IN_PROGRESS não podem ser excluídas fisicamente.
        """
        if role not in CAN_DELETE_SESSION:
            raise InsufficientPrivilege(
                f"role={role} não pode excluir sessões (somente admin/coordinator)"
            )
        if session.status == TrainingSessionStatus.IN_PROGRESS:
            raise InsufficientPrivilege(
                "DR-TRAIN-027: sessão IN_PROGRESS não pode ser excluída — use cancelamento lógico"
            )


# ---------------------------------------------------------------------------
# SessionGuard — application-layer helper
# ---------------------------------------------------------------------------

class SessionGuard:
    """
    Encapsula o padrão "load → NotFound → policy.require_* → return"
    repetido em 12+ UseCases.

    Uso típico (mutable):
        guard = SessionGuard(session_repo, policy)
        session = guard.load_for_update(inp.session_id, inp.actor_role)

    Uso típico (readable):
        session = guard.load_for_read(inp.session_id, inp.actor_role,
                                       inp.actor_id, inp.session_athlete_ids)
    """

    def __init__(self, session_repo: object, policy: SessionAccessPolicy | None = None) -> None:
        self._repo = session_repo
        self._policy = policy or SessionAccessPolicy()

    def load_for_update(
        self,
        session_id: uuid.UUID,
        role: RoleLabel,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica que o actor pode modificá-la.
        Levanta TrainingSessionNotFound ou SessionNotMutable/InsufficientPrivilege.
        """
        from ...domain.rules import TrainingSessionNotFound  # evita circular no topo
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_mutable(session, role)
        return session

    def load_for_in_progress(
        self,
        session_id: uuid.UUID,
        role: RoleLabel,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica que está IN_PROGRESS e que o actor
        tem permissão. Usada por CreateExecutionRecordUseCase.
        """
        from ...domain.rules import TrainingSessionNotFound
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_in_progress(session, role)
        return session

    def load_for_transition(
        self,
        session_id: uuid.UUID,
        target_status: TrainingSessionStatus,
        role: RoleLabel,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica que a transição de status é válida.
        Usada por TransitionTrainingSessionUseCase.
        """
        from ...domain.rules import TrainingSessionNotFound
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_valid_transition(session, target_status, role)
        return session

    def load_for_read(
        self,
        session_id: uuid.UUID,
        role: RoleLabel,
        actor_id: uuid.UUID,
        athlete_ids: list | tuple,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica que o actor tem permissão de leitura.
        Usada por GetTrainingSessionUseCase.
        """
        from ...domain.rules import TrainingSessionNotFound
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_readable(session, role, actor_id, athlete_ids)
        return session

    def load_for_delete(
        self,
        session_id: uuid.UUID,
        role: RoleLabel,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica que o actor pode excluí-la (DR-TRAIN-027).
        Usada por DeleteTrainingSessionUseCase.
        """
        from ...domain.rules import TrainingSessionNotFound
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_deletable(session, role)
        return session

    def load_with_write_access(
        self,
        session_id: uuid.UUID,
        role: RoleLabel,
    ) -> TrainingSession:
        """
        Carrega a sessão e verifica role de escrita (sem checar estado).
        Usada por UseCases que aplicam suas próprias regras de estado
        (ex: CreateSessionObjectiveUseCase).
        """
        from ...domain.rules import TrainingSessionNotFound
        session = self._repo.get_by_id(session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {session_id} não encontrada")
        self._policy.require_write_access(role)
        return session
