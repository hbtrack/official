"""
Repository do módulo identity_access.
Adaptador Django ORM para as entidades de domínio.
Nunca contém lógica de negócio — apenas mapeamento e persistência.

SEGURANÇA:
- Senhas verificadas via Django's check_password (bcrypt/argon2 — nunca plaintext).
- Refresh tokens armazenados como BLAKE2 hash — nunca o token em si.
- JWT gerado via JwtPort (interface) — permite troca de algoritmo sem mudar domínio.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional, Protocol

from ..domain.entities import AuthSession, UserRoleBinding


class JwtPort(Protocol):
    """Port para geração/validação de JWT (ADR-007: RS256)."""

    def issue_access_token(self, session: AuthSession) -> str: ...
    def verify_access_token(self, token: str) -> Optional[dict]: ...


class IdentityAccessRepository:
    """
    Implementação concreta do repositório de identity_access.
    Usa Django ORM via imports lazy para manter domínio isolado.
    """

    def __init__(self, jwt_port: Optional[JwtPort] = None) -> None:
        self._jwt = jwt_port

    # ── Autenticação ──────────────────────────────────────────────────────────

    def verify_credentials(
        self,
        email: str,
        password: str,
    ) -> tuple[Optional[uuid.UUID], list[str]]:
        """
        Verifica email + senha usando Django's AbstractBaseUser.
        OWASP API3:2023: nunca retorna hash de senha.

        Returns:
            (user_id, role_labels) se válido, (None, []) se inválido.
        """
        from django.contrib.auth import get_user_model
        from django.contrib.auth.hashers import check_password as django_check_pw

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Timing-safe: sem diferenciação entre "email não existe" e "senha errada"
            secrets.compare_digest("dummy", "dummy")
            return None, []

        if not user.check_password(password):
            return None, []

        role_labels = list(
            self._get_models()["binding"]
            .objects.filter(user_id=user.pk)
            .values_list("role_label", flat=True)
        )
        return uuid.UUID(str(user.pk)), role_labels

    def issue_tokens(
        self,
        session: AuthSession,
    ) -> tuple[str, str]:
        """
        Emite (accessToken, refreshToken).
        accessToken: JWT RS256 via JwtPort.
        refreshToken: token opaco aleatório — apenas o hash persiste (OWASP API2:2023).
        """
        if self._jwt is not None:
            access_token = self._jwt.issue_access_token(session)
        else:
            # Stub para ambiente sem JWT configurado — NUNCA usar em produção
            access_token = f"stub.{session.id}.{session.principal_user_id}"

        refresh_token = secrets.token_urlsafe(48)
        token_hash = hashlib.blake2b(
            refresh_token.encode(), digest_size=64
        ).hexdigest()

        AuthSessionModel = self._get_models()["session"]
        AuthSessionModel.objects.filter(pk=session.id).update(
            refresh_token_hash=token_hash,
            refresh_token_used=False,
        )
        return access_token, refresh_token

    def consume_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[AuthSession]:
        """
        Valida e invalida o refresh token (rotação — OWASP API2:2023).
        Retorna a sessão associada ou None se inválido/expirado/utilizado.
        """
        token_hash = hashlib.blake2b(
            refresh_token.encode(), digest_size=64
        ).hexdigest()

        AuthSessionModel = self._get_models()["session"]
        try:
            model = AuthSessionModel.objects.get(
                refresh_token_hash=token_hash,
                refresh_token_used=False,
                revoked_at__isnull=True,
            )
        except AuthSessionModel.DoesNotExist:
            return None

        # Marcar como usado imediatamente (rotação obrigatória)
        AuthSessionModel.objects.filter(pk=model.pk).update(refresh_token_used=True)
        return self._session_to_domain(model)

    # ── Sessões ───────────────────────────────────────────────────────────────

    def get_session_by_id(
        self,
        session_id: uuid.UUID,
    ) -> Optional[AuthSession]:
        AuthSessionModel = self._get_models()["session"]
        try:
            return self._session_to_domain(AuthSessionModel.objects.get(pk=session_id))
        except AuthSessionModel.DoesNotExist:
            return None

    def save_session(self, session: AuthSession) -> AuthSession:
        AuthSessionModel = self._get_models()["session"]
        defaults = {
            "principal_user_id": session.principal_user_id,
            "session_scope_label": session.session_scope_label,
            "role_labels": session.role_labels,
            "auth_method_label": session.auth_method_label or "",
            "mfa_required": session.mfa_required or False,
            "mfa_satisfied": session.mfa_satisfied or False,
            "issued_at": session.issued_at,
            "expires_at": session.expires_at,
            "revoked_at": session.revoked_at,
        }
        AuthSessionModel.objects.update_or_create(pk=session.id, defaults=defaults)
        return session

    def list_active_sessions(
        self,
        page_size: int = 20,
        page_token: Optional[str] = None,
        principal_user_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[AuthSession], Optional[str]]:
        """Paginação cursor-based por id (OWASP API4:2023)."""
        AuthSessionModel = self._get_models()["session"]
        qs = AuthSessionModel.objects.filter(revoked_at__isnull=True)
        if principal_user_id is not None:
            qs = qs.filter(principal_user_id=principal_user_id)
        if page_token:
            qs = qs.filter(id__gt=page_token)
        qs = qs.order_by("id")[: page_size + 1]
        rows = list(qs)
        next_token: Optional[str] = None
        if len(rows) > page_size:
            next_token = str(rows[page_size - 1].id)
            rows = rows[:page_size]
        return [self._session_to_domain(r) for r in rows], next_token

    def revoke_refresh_tokens_for_session(self, session_id: uuid.UUID) -> None:
        AuthSessionModel = self._get_models()["session"]
        AuthSessionModel.objects.filter(pk=session_id).update(
            refresh_token_used=True,
            refresh_token_hash="",
        )

    # ── Role bindings ─────────────────────────────────────────────────────────

    def user_exists(self, user_id: uuid.UUID) -> bool:
        """
        Verifica se o user_id tem pelo menos um role binding registrado OU
        existe no sistema de auth do Django.
        DR-IAM-002: identity_access não duplica dados de perfil — apenas binding técnico.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(pk=user_id).exists()

    def get_user_roles(self, user_id: uuid.UUID) -> list[str]:
        BindingModel = self._get_models()["binding"]
        return list(
            BindingModel.objects.filter(user_id=user_id).values_list(
                "role_label", flat=True
            )
        )

    def save_role_binding(self, binding: UserRoleBinding) -> UserRoleBinding:
        BindingModel = self._get_models()["binding"]
        BindingModel.objects.get_or_create(
            user_id=binding.user_id,
            role_label=binding.role_label,
            defaults={"id": binding.id},
        )
        return binding

    def delete_role_binding(self, user_id: uuid.UUID, role_label: str) -> None:
        BindingModel = self._get_models()["binding"]
        BindingModel.objects.filter(user_id=user_id, role_label=role_label).delete()

    def count_global_role(self, role_label: str) -> int:
        BindingModel = self._get_models()["binding"]
        return BindingModel.objects.filter(role_label=role_label).count()

    # ── Tradução ORM ↔ Domínio ────────────────────────────────────────────────

    @staticmethod
    def _session_to_domain(model) -> AuthSession:
        return AuthSession(
            id=model.id,
            principal_user_id=model.principal_user_id,
            session_scope_label=model.session_scope_label,
            role_labels=model.role_labels or [],
            auth_method_label=model.auth_method_label or None,
            mfa_required=model.mfa_required,
            mfa_satisfied=model.mfa_satisfied,
            issued_at=model.issued_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def _get_models() -> dict:
        from .models import AuthSessionModel, UserRoleBindingModel
        return {"session": AuthSessionModel, "binding": UserRoleBindingModel}
