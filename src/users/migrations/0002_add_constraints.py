"""
Migration 0002 — users: CHECK constraints de integridade.
- role_label: 5 valores canônicos (ADR-008)
- status_label: 3 valores válidos (INV-USR)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="userprofilemodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    role_label__in=[
                        "admin", "coordinator", "coach", "athlete", "member"
                    ]
                ),
                name="users_profile_role_label_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="userprofilemodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    status_label__in=[
                        "ACTIVE", "PENDING_ACTIVATION", "SUSPENDED"
                    ]
                ),
                name="users_profile_status_label_valid",
            ),
        ),
    ]
