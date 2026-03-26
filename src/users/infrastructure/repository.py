"""
Repository — módulo users.
Adapter Django ORM para o domínio.
Nunca contém lógica de negócio — apenas queries.
"""
from __future__ import annotations

import base64
import json
from uuid import UUID

from .models import UserProfileModel
from ..domain.entities import RoleLabel, UserProfile, UserStatus


class UsersRepository:
    """
    Implementação Django ORM do repositório de UserProfile.
    Métodos sem lógica de domínio — apenas persistência.
    """

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: UUID) -> UserProfile | None:
        try:
            model = UserProfileModel.objects.get(pk=user_id)
            return self._to_domain(model)
        except UserProfileModel.DoesNotExist:
            return None

    def list_users(
        self,
        organization_id: UUID | None = None,
        team_id: UUID | None = None,
        role_label: "RoleLabel | None" = None,
        page_size: int = 50,
        page_token: str | None = None,
    ) -> tuple[list[UserProfile], str | None]:
        """
        Lista UserProfiles com paginação cursor-based.
        page_token = base64({"last_id": "<uuid>"})
        """
        qs = UserProfileModel.objects.all().order_by("id")

        if organization_id is not None:
            qs = qs.filter(organization_id=organization_id)
        if role_label is not None:
            qs = qs.filter(role_label=str(role_label))

        # Filtro por team_id: verificar no campo JSON (portável)
        if team_id is not None:
            # JSONField contains lookup: compatível com PostgreSQL e SQLite
            qs = qs.filter(team_ids__contains=str(team_id))

        # Cursor pagination
        if page_token:
            try:
                cursor = json.loads(base64.b64decode(page_token).decode())
                last_id = cursor.get("last_id")
                if last_id:
                    qs = qs.filter(id__gt=last_id)
            except Exception:
                pass  # token inválido → ignorar, retornar do início

        # Buscar page_size + 1 para determinar se há próxima página
        items_raw = list(qs[: page_size + 1])
        has_next = len(items_raw) > page_size
        items = items_raw[:page_size]

        next_token: str | None = None
        if has_next and items:
            cursor_data = {"last_id": str(items[-1].id)}
            next_token = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        return [self._to_domain(m) for m in items], next_token

    # ------------------------------------------------------------------
    # WRITE
    # ------------------------------------------------------------------

    def save(self, profile: UserProfile) -> UserProfile:
        """Cria ou atualiza UserProfile (upsert por id)."""
        model, _ = UserProfileModel.objects.update_or_create(
            pk=profile.id,
            defaults=self._to_model_dict(profile),
        )
        return self._to_domain(model)

    # ------------------------------------------------------------------
    # Converters
    # ------------------------------------------------------------------

    @staticmethod
    def _to_domain(model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            organization_id=model.organization_id,
            first_name=model.first_name or None,
            last_name=model.last_name or None,
            display_name=model.display_name,
            role_label=RoleLabel(model.role_label),
            status_label=UserStatus(model.status_label),
            position_label=model.position_label or None,
            preferred_language=model.preferred_language or None,
            preference_tags=list(model.preference_tags or []),
            team_ids=[UUID(t) for t in (model.team_ids or [])],
            season_ids=[UUID(s) for s in (model.season_ids or [])],
        )

    @staticmethod
    def _to_model_dict(profile: UserProfile) -> dict:
        return {
            "organization_id": profile.organization_id,
            "first_name": profile.first_name or "",
            "last_name": profile.last_name or "",
            "display_name": profile.display_name,
            "role_label": str(profile.role_label),
            "status_label": str(profile.status_label),
            "position_label": profile.position_label or "",
            "preferred_language": profile.preferred_language or "",
            "preference_tags": profile.preference_tags,
            "team_ids": [str(t) for t in profile.team_ids],
            "season_ids": [str(s) for s in profile.season_ids],
        }
