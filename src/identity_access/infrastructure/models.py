"""
Django ORM models do módulo identity_access.
Alinhados com contracts/schemas/identity_access/auth_session.schema.json.
Boundary: NÃO há campos de perfil físico, esportivo ou clínico (INV-IAM-004).
"""
from __future__ import annotations

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class HBTrackUser(AbstractUser):
    """
    Custom User model com UUID primary key.
    AUTH_USER_MODEL = "identity_access.HBTrackUser"
    Garante que user.pk é sempre um UUID válido (required por identity_access.repository).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        db_table = "identity_access_users"
        app_label = "identity_access"

    def __str__(self) -> str:
        return self.email or self.username


class AuthSessionModel(models.Model):
    """
    Persiste AuthSession.
    db_table: identity_access_auth_sessions
    Contrato: contracts/schemas/identity_access/auth_session.schema.json
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # DR-IAM-002: principalUserId referencia users — sem FK para evitar acoplamento cross-module
    principal_user_id = models.UUIDField(db_index=True)
    session_scope_label = models.CharField(max_length=80)
    role_labels = ArrayField(
        base_field=models.CharField(max_length=40),
        default=list,
        blank=True,
    )
    auth_method_label = models.CharField(max_length=40, blank=True, default="")
    mfa_required = models.BooleanField(default=False)
    mfa_satisfied = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    # Refresh token opaco (OWASP API2:2023 — rotação obrigatória)
    refresh_token_hash = models.CharField(max_length=128, blank=True, default="")
    refresh_token_used = models.BooleanField(default=False)

    class Meta:
        db_table = "identity_access_auth_sessions"
        app_label = "identity_access"

    def __str__(self) -> str:
        return f"AuthSession({self.id}, user={self.principal_user_id})"


class UserRoleBindingModel(models.Model):
    """
    Binding de role RBAC para um usuário.
    db_table: identity_access_user_role_bindings
    DR-IAM-001: identity_access governa bindings de role.
    DR-IAM-003: roleLabel é contexto técnico (ADR-008).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Sem FK para users — acoplamento cross-module proibido por boundary
    user_id = models.UUIDField(db_index=True)
    role_label = models.CharField(
        max_length=40,
        choices=[
            ("admin", "Admin"),
            ("coordinator", "Coordinator"),
            ("coach", "Coach"),
            ("athlete", "Athlete"),
            ("member", "Member"),
        ],
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "identity_access_user_role_bindings"
        app_label = "identity_access"
        # INV-IAM-002 / uniqueness: um usuário não pode ter o mesmo role duas vezes
        unique_together = [("user_id", "role_label")]

    def __str__(self) -> str:
        return f"UserRoleBinding(user={self.user_id}, role={self.role_label})"
