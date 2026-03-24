"""
Migration 0003 — identity_access: índices de performance.
Task 4.2 — p95 < 200ms em listagens.

AuthSessionModel:
  - revoked_at: filtro de sessões ativas (listActiveSessions)
  - refresh_token_hash: lookup por token opaco
  - (revoked_at, principal_user_id): filtro composto mais comum
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("identity_access", "0003_add_hbtrack_user"),
    ]

    operations = [
        # revoked_at — filtro de sessões ativas
        migrations.AddIndex(
            model_name="authsessionmodel",
            index=models.Index(
                fields=["revoked_at"],
                name="ia_session_revoked_at_idx",
            ),
        ),
        # refresh_token_hash — lookup de renovação de token
        migrations.AddIndex(
            model_name="authsessionmodel",
            index=models.Index(
                fields=["refresh_token_hash"],
                name="ia_session_refresh_token_idx",
            ),
        ),
        # (revoked_at, principal_user_id) — listActiveSessions com filtro por usuário
        migrations.AddIndex(
            model_name="authsessionmodel",
            index=models.Index(
                fields=["revoked_at", "principal_user_id"],
                name="ia_session_revoked_user_idx",
            ),
        ),
    ]
