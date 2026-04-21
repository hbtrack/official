"""
Django ORM models — módulo users.
Alinhado com: contracts/schemas/users/user_profile.schema.json
Regra: db_table usa snake_case plural; app_label = "users"
Boundary: sem campos de authn (INV-USR-003, INV-USR-004)
"""
from __future__ import annotations

import uuid

from django.db import models


class UserProfileModel(models.Model):
    """
    Persiste UserProfile.
    db_table: users_user_profiles
    Campos de authn/authz NÃO pertencem aqui (INV-USR-003).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=80, blank=True, default="")
    last_name = models.CharField(max_length=80, blank=True, default="")
    display_name = models.CharField(max_length=120)
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
    status_label = models.CharField(
        max_length=30,
        choices=[
            ("ACTIVE", "Active"),
            ("PENDING_ACTIVATION", "Pending Activation"),
            ("SUSPENDED", "Suspended"),
        ],
        default="PENDING_ACTIVATION",
    )
    position_label = models.CharField(max_length=80, blank=True, default="")
    preferred_language = models.CharField(max_length=16, blank=True, default="")
    avatar_url = models.URLField(max_length=2048, blank=True, default="")
    # Arrays armazenados como JSON (portável sem postgres ArrayField)
    preference_tags = models.JSONField(default=list, blank=True)
    team_ids = models.JSONField(default=list, blank=True)
    season_ids = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user_profiles"
        app_label = "users"
        indexes = [
            models.Index(fields=["role_label"]),
            models.Index(fields=["status_label"]),
            models.Index(fields=["organization_id", "role_label"]),
        ]

    def __repr__(self) -> str:
        return f"<UserProfileModel id={self.id} display_name={self.display_name!r}>"
