"""
Service para gerenciamento de Itens Pendentes de Sessão de Treino.

Invariantes implementadas:
- INV-066: CRUD para training_pending_items (create/resolve/cancel/list)
- INV-067: Guard de sessão readonly + RBAC atleta/treinador

Ref: AR_155 — AR_153 (migration 0067_attendance_preconfirm_pending_items)
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    SessionClosedError,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Roles com permissão de treinador (podem ver/editar de qualquer atleta)
COACH_ROLES = {"treinador", "dirigente", "superadmin", "admin"}

# Status de sessão que bloqueia edição de pending items (INV-067)
READONLY_STATUSES = {"readonly"}

# Enums canônicos (ck_pending_item_type + ck_pending_item_status da migration 0067)
VALID_ITEM_TYPES = {"equipment", "material", "admin", "other"}
VALID_ITEM_STATUSES = {"open", "resolved", "cancelled"}


class TrainingPendingService:
    """
    Service de Itens Pendentes de Sessão de Treino.
    Ref: INV-066 (CRUD), INV-067 (RBAC + guard readonly)
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    # ─────────────────────────────────────────────────────────────
    # Helpers internos
    # ─────────────────────────────────────────────────────────────

    def _is_coach(self) -> bool:
        """Retorna True se o usuário atual tem papel de treinador/dirigente."""
        return self.context.role_code in COACH_ROLES

    async def _get_session_status(self, session_id: UUID) -> str:
        """
        Busca o status da training_session pelo id.
        Raises NotFoundError se não encontrada.
        """
        row = await self.db.execute(
            text(
                "SELECT status FROM training_sessions "
                "WHERE id = :session_id AND deleted_at IS NULL"
            ),
            {"session_id": str(session_id)},
        )
        result = row.fetchone()
        if result is None:
            raise NotFoundError(f"Sessão de treino {session_id} não encontrada")
        return result[0]

    async def _get_pending_item(self, item_id: UUID) -> dict[str, Any]:
        """
        Busca um pending item pelo id.
        Raises NotFoundError se não encontrado.
        Returns dict com campos do item.
        """
        row = await self.db.execute(
            text(
                "SELECT id, training_session_id, athlete_id, item_type, "
                "description, status, created_at, updated_at, "
                "resolved_at, resolved_by_user_id "
                "FROM training_pending_items WHERE id = :item_id"
            ),
            {"item_id": str(item_id)},
        )
        result = row.fetchone()
        if result is None:
            raise NotFoundError(f"Item pendente {item_id} não encontrado")
        return {
            "id": result[0],
            "training_session_id": result[1],
            "athlete_id": result[2],
            "item_type": result[3],
            "description": result[4],
            "status": result[5],
            "created_at": result[6],
            "updated_at": result[7],
            "resolved_at": result[8],
            "resolved_by_user_id": result[9],
        }

    def _assert_session_editable(self, session_status: str) -> None:
        """
        INV-067: Guard — sessão não pode estar em status readonly.
        Raises SessionClosedError se a sessão estiver fechada.
        """
        if session_status in READONLY_STATUSES:
            raise SessionClosedError(
                f"Sessão em status '{session_status}' — edição de itens pendentes não permitida"
            )

    def _assert_athlete_permission(
        self,
        item_athlete_id: Any,
        operation: str = "editar",
    ) -> None:
        """
        INV-067: RBAC — atleta só pode operar seus próprios items.
        Treinador/dirigente pode operar qualquer item.
        Raises ForbiddenError se acesso negado.
        """
        if self._is_coach():
            return  # Treinador tem acesso total

        # Atleta: apenas próprios items
        if str(self.context.user_id) != str(item_athlete_id):
            raise ForbiddenError(
                f"Atleta não tem permissão para {operation} item de outro atleta"
            )

    # ─────────────────────────────────────────────────────────────
    # Operações públicas
    # ─────────────────────────────────────────────────────────────

    async def create_pending_item(
        self,
        session_id: UUID,
        athlete_id: UUID,
        item_type: str,
        description: str,
        user_id: UUID,
    ) -> dict[str, Any]:
        """
        INV-066: Cria um item pendente para a sessão.
        Status inicial: 'open'.
        RBAC: treinador pode criar para qualquer atleta;
              atleta só pode criar para si mesmo.
        """
        if item_type not in VALID_ITEM_TYPES:
            raise ValidationError(
                f"item_type inválido: '{item_type}'. Válidos: {sorted(VALID_ITEM_TYPES)}",
                field="item_type",
            )
        if not description or not description.strip():
            raise ValidationError("description não pode ser vazio", field="description")

        # Guard RBAC: atleta só pode criar item para si mesmo
        if not self._is_coach() and str(self.context.user_id) != str(athlete_id):
            raise ForbiddenError(
                "Atleta não tem permissão para criar item pendente para outro atleta"
            )

        # Verificar que sessão existe
        await self._get_session_status(session_id)

        row = await self.db.execute(
            text(
                "INSERT INTO training_pending_items "
                "(training_session_id, athlete_id, item_type, description, status) "
                "VALUES (:session_id, :athlete_id, :item_type, :description, 'open') "
                "RETURNING id, training_session_id, athlete_id, item_type, "
                "description, status, created_at, updated_at, "
                "resolved_at, resolved_by_user_id"
            ),
            {
                "session_id": str(session_id),
                "athlete_id": str(athlete_id),
                "item_type": item_type,
                "description": description.strip(),
            },
        )
        result = row.fetchone()
        logger.info(
            "pending_item.created",
            extra={
                "item_id": str(result[0]),
                "session_id": str(session_id),
                "athlete_id": str(athlete_id),
                "created_by": str(user_id),
                "item_type": item_type,
            },
        )
        return {
            "id": result[0],
            "training_session_id": result[1],
            "athlete_id": result[2],
            "item_type": result[3],
            "description": result[4],
            "status": result[5],
            "created_at": result[6],
            "updated_at": result[7],
            "resolved_at": result[8],
            "resolved_by_user_id": result[9],
        }

    async def resolve_pending_item(
        self,
        item_id: UUID,
        resolved_by_user_id: UUID,
    ) -> dict[str, Any]:
        """
        INV-066: Resolve um item pendente — muda status para 'resolved' e seta resolved_at.
        INV-067: Guard — sessão não pode estar em readonly.
                 RBAC — atleta só pode resolver próprios items.
        """
        item = await self._get_pending_item(item_id)

        # Guard readonly
        session_status = await self._get_session_status(item["training_session_id"])
        self._assert_session_editable(session_status)

        # RBAC
        self._assert_athlete_permission(item["athlete_id"], operation="resolver")

        if item["status"] != "open":
            raise ValidationError(
                f"Item já está em status '{item['status']}' — não pode ser resolvido novamente",
                field="status",
            )

        now = datetime.now(timezone.utc)
        await self.db.execute(
            text(
                "UPDATE training_pending_items "
                "SET status = 'resolved', resolved_at = :resolved_at, "
                "resolved_by_user_id = :resolved_by, updated_at = :now "
                "WHERE id = :item_id"
            ),
            {
                "item_id": str(item_id),
                "resolved_at": now,
                "resolved_by": str(resolved_by_user_id),
                "now": now,
            },
        )
        logger.info(
            "pending_item.resolved",
            extra={
                "item_id": str(item_id),
                "resolved_by": str(resolved_by_user_id),
            },
        )
        return {**item, "status": "resolved", "resolved_at": now, "resolved_by_user_id": str(resolved_by_user_id)}

    async def cancel_pending_item(
        self,
        item_id: UUID,
        cancelled_by_user_id: UUID,
    ) -> dict[str, Any]:
        """
        INV-066: Cancela um item pendente — muda status para 'cancelled'.
        INV-067: Guard — sessão não pode estar em readonly.
                 RBAC — atleta só pode cancelar próprios items.
        """
        item = await self._get_pending_item(item_id)

        # Guard readonly
        session_status = await self._get_session_status(item["training_session_id"])
        self._assert_session_editable(session_status)

        # RBAC
        self._assert_athlete_permission(item["athlete_id"], operation="cancelar")

        if item["status"] in {"resolved", "cancelled"}:
            raise ValidationError(
                f"Item já está em status '{item['status']}' — não pode ser cancelado",
                field="status",
            )

        now = datetime.now(timezone.utc)
        await self.db.execute(
            text(
                "UPDATE training_pending_items "
                "SET status = 'cancelled', updated_at = :now "
                "WHERE id = :item_id"
            ),
            {"item_id": str(item_id), "now": now},
        )
        logger.info(
            "pending_item.cancelled",
            extra={
                "item_id": str(item_id),
                "cancelled_by": str(cancelled_by_user_id),
            },
        )
        return {**item, "status": "cancelled", "updated_at": now}

    async def list_pending_items(
        self,
        session_id: UUID,
        *,
        athlete_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        """
        INV-066: Lista todos os pending items da sessão.
        RBAC: treinador vê todos; atleta vê apenas os próprios.
        Filtro opcional athlete_id (apenas para coaches).
        """
        # RBAC: atleta só pode ver próprios items
        if not self._is_coach():
            athlete_filter = self.context.user_id
        else:
            athlete_filter = athlete_id  # None = todos

        query_parts = [
            "SELECT id, training_session_id, athlete_id, item_type, "
            "description, status, created_at, updated_at, "
            "resolved_at, resolved_by_user_id "
            "FROM training_pending_items "
            "WHERE training_session_id = :session_id"
        ]
        params: dict[str, Any] = {"session_id": str(session_id)}

        if athlete_filter is not None:
            query_parts.append("AND athlete_id = :athlete_id")
            params["athlete_id"] = str(athlete_filter)

        query_parts.append("ORDER BY created_at ASC")

        rows = await self.db.execute(
            text(" ".join(query_parts)),
            params,
        )
        return [
            {
                "id": row[0],
                "training_session_id": row[1],
                "athlete_id": row[2],
                "item_type": row[3],
                "description": row[4],
                "status": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "resolved_at": row[8],
                "resolved_by_user_id": row[9],
            }
            for row in rows.fetchall()
        ]
