"""
Seed de dados demo — HB Track.
Cria 1 organização demo, 2 usuários, 1 time, 1 temporada e 5 sessões de treino.
Uso via management command: python manage.py seed_demo
     Ou diretamente: python scripts/seed.py
"""
from __future__ import annotations

import sys
import os
import uuid
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# Garante que src/ está no path
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


# ── IDs fixos para facilitar desenvolvimento local ───────────────────────────
ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
COACH_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
SEASON_ID = uuid.UUID("00000000-0000-0000-0000-000000000030")


def seed():
    User = get_user_model()

    # ── 1. Usuários Django ────────────────────────────────────────────────────
    # Lookup por id (UUID fixo) para evitar conflito de username em re-seeds.
    admin_user, created = User.objects.get_or_create(
        id=ADMIN_ID,
        defaults={
            "username": "admin@hbtrack.demo",
            "email": "admin@hbtrack.demo",
            "password": make_password("HBTrack@demo2026"),
            "is_staff": True,
        },
    )
    print(f"  [seed] Admin user: {admin_user.email} (created={created})")

    coach_user, created = User.objects.get_or_create(
        id=COACH_ID,
        defaults={
            "username": "coach@hbtrack.demo",
            "email": "coach@hbtrack.demo",
            "password": make_password("HBTrack@demo2026"),
        },
    )
    print(f"  [seed] Coach user: {coach_user.email} (created={created})")

    # ── 2. UserProfiles ───────────────────────────────────────────────────────
    from users.infrastructure.models import UserProfileModel

    UserProfileModel.objects.get_or_create(
        id=ADMIN_ID,
        defaults={
            "organization_id": ORG_ID,
            "display_name": "Admin Demo",
            "first_name": "Admin",
            "last_name": "Demo",
            "role_label": "admin",
            "status_label": "ACTIVE",
        },
    )
    UserProfileModel.objects.get_or_create(
        id=COACH_ID,
        defaults={
            "organization_id": ORG_ID,
            "display_name": "Treinador Demo",
            "first_name": "Treinador",
            "last_name": "Demo",
            "role_label": "coach",
            "status_label": "ACTIVE",
        },
    )
    print("  [seed] UserProfiles criados.")

    # ── 3. RoleBindings ───────────────────────────────────────────────────────
    from identity_access.infrastructure.models import UserRoleBindingModel

    UserRoleBindingModel.objects.get_or_create(
        user_id=ADMIN_ID, role_label="admin"
    )
    UserRoleBindingModel.objects.get_or_create(
        user_id=COACH_ID, role_label="coach"
    )
    print("  [seed] RoleBindings criados.")

    # ── 4. Time demo ──────────────────────────────────────────────────────────
    from teams.infrastructure.models import TeamModel

    team, created = TeamModel.objects.get_or_create(
        id=TEAM_ID,
        defaults={
            "organization_id": ORG_ID,
            "name": "HB Track Demo",
            "short_name": "HBD",
            "category_label": "adulto_masculino",
            "status_label": "ACTIVE",
            "staff_user_ids": [str(ADMIN_ID), str(COACH_ID)],
        },
    )
    print(f"  [seed] Time: {team.name} (created={created})")

    # ── 5. Temporada demo ─────────────────────────────────────────────────────
    from seasons.infrastructure.models import SeasonModel

    today = date.today()
    season, created = SeasonModel.objects.get_or_create(
        id=SEASON_ID,
        defaults={
            "organization_id": ORG_ID,
            "name": "Temporada 2026 — Demo",
            "sport_cycle_label": "handebol",
            "status_label": "ACTIVE",
            "start_date": today,
            "end_date": today + timedelta(days=180),
            "team_ids": [str(TEAM_ID)],
        },
    )
    print(f"  [seed] Temporada: {season.name} (created={created})")

    # ── 6. Sessões de treino demo ─────────────────────────────────────────────
    from training.infrastructure.models import TrainingSessionModel

    session_types = ["tactical", "physical", "technical", "mixed", "recovery"]
    for i, stype in enumerate(session_types, start=1):
        session_at = datetime.now(tz=timezone.utc) + timedelta(days=i)
        ts, created = TrainingSessionModel.objects.get_or_create(
            id=uuid.uuid5(SEASON_ID, f"demo_session_{i}"),
            defaults={
                "organization_id": ORG_ID,
                "team_id": TEAM_ID,
                "season_id": SEASON_ID,
                "session_at": session_at,
                "session_type": stype,
                "main_objective": f"Sessão demo #{i} — {stype}",
                "status": "SCHEDULED",
                "duration_planned_minutes": 90,
            },
        )
        print(f"  [seed] TrainingSession #{i} ({stype}): created={created}")

    print("\n✅ Seed demo concluído.")


if __name__ == "__main__":
    seed()
