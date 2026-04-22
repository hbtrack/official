"""Helpers de resolução de ator HTTP (training.api).

Encapsula a extração de RoleLabel, actor_id e AccessContext do request autenticado.
Substitui os helpers _get_actor_role/_get_actor_id do antigo api.py monolítico.

Extraído de api/_shared.py na Fase 1.4; expandido com AccessContext na Fase 2.
"""
from __future__ import annotations

import os
import uuid

from ninja.errors import HttpError

from ..application.common.access import AccessContext
from ..application.common.paging import CursorCodec
from ..domain.rules import RoleLabel


def _get_actor_role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


def _get_actor_id(request) -> uuid.UUID:
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return uuid.UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")


def resolve_access(request) -> AccessContext:
    """Constrói AccessContext completo a partir do request autenticado.

    Na Fase 2, os campos team_ids e athlete_ids ainda ficam vazios — a
    integração real com identity_access é um TODO da Fase 3+.

    Lança HttpError(401) se o request não estiver autenticado.
    """
    actor_id = _get_actor_id(request)
    role = _get_actor_role(request)

    organization_id_raw = getattr(request, "_organization_id", None)
    organization_id = uuid.UUID(str(organization_id_raw)) if organization_id_raw else None

    # TODO Fase 3: preencher team_ids e athlete_ids via identity_access
    return AccessContext(
        actor_id=actor_id,
        role=role,
        organization_id=organization_id,
        team_ids=(),
        athlete_ids=(),
    )


def get_cursor_codec() -> CursorCodec:
    """Fábrica de CursorCodec resolvida a partir de variável de ambiente.

    Resolução em ordem:
      1. TRAINING_CURSOR_SECRETS (CSV de secrets, novo,antigo) — suporte a rotação dual-key.
      2. TRAINING_CURSOR_SECRET (singular, backward compat).
      3. Fallback para SECRET_KEY do Django APENAS em ambiente não-produção
         (DEBUG=True E ENV não é "production"/"prod").

    Em produção, a ausência de TRAINING_CURSOR_SECRET(S) levanta RuntimeError.
    """
    # 1. Lista de secrets para rotação dual-key
    secrets_csv = os.environ.get("TRAINING_CURSOR_SECRETS", "").strip()
    if secrets_csv:
        secrets = [s.encode() for s in secrets_csv.split(",") if s.strip()]
        if secrets:
            return CursorCodec(secrets=secrets)

    # 2. Secret único (backward compat)
    secret_str = os.environ.get("TRAINING_CURSOR_SECRET")
    if secret_str:
        return CursorCodec(secret=secret_str.encode())

    # 3. Fallback para SECRET_KEY — apenas em dev (DEBUG=True E ENV != production)
    try:
        from django.conf import settings  # noqa: PLC0415

        is_debug = getattr(settings, "DEBUG", False)
        env_name = os.environ.get("ENV", "").lower()
        is_production = env_name in ("production", "prod")

        if is_production or not is_debug:
            raise RuntimeError(
                "TRAINING_CURSOR_SECRET não definida. "
                "Em produção, defina TRAINING_CURSOR_SECRET ou TRAINING_CURSOR_SECRETS "
                "explicitamente."
            )
        return CursorCodec(secret=settings.SECRET_KEY.encode())
    except ImportError:
        raise RuntimeError("TRAINING_CURSOR_SECRET não definida.")

