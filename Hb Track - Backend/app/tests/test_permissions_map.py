"""
Testes do mapa canônico de permissões.

Objetivo: garantir que cada role tenha o conjunto correto de chaves e valores
para as permissões novas (sidebar) e legadas (granulares).
"""

import pytest

from app.core.permissions_map import ROLE_PERMISSIONS, get_permissions_for_role


ROLES = ["superadmin", "dirigente", "coordenador", "treinador", "atleta", "membro"]


def test_role_permissions_map_exists():
    """Valida que o mapa canônico existe e tem 6 roles."""
    assert len(ROLE_PERMISSIONS) == 6
    for role in ROLES:
        assert role in ROLE_PERMISSIONS


def test_superadmin_permissions():
    """Superadmin tem tudo habilitado (novas e legadas)."""
    perms = get_permissions_for_role("superadmin")

    # Novas permissões (sidebar)
    assert perms["public_access"] is True
    assert perms["can_view_dashboard"] is True
    assert perms["can_manage_teams"] is True
    assert perms["can_manage_athletes"] is True
    assert perms["can_use_live_scout"] is True
    assert perms["can_manage_matches"] is True
    assert perms["can_manage_trainings"] is True
    assert perms["can_manage_wellness"] is True
    assert perms["can_view_athlete_360"] is True
    assert perms["can_view_team_360"] is True
    assert perms["can_generate_reports"] is True

    # Legado (amostra)
    assert perms["can_manage_org"] is True
    assert perms["can_manage_users"] is True
    assert perms["can_manage_members"] is True
    assert perms["can_manage_org"] is True
    assert perms["can_create_team"] is True
    assert perms["can_create_match"] is True
    assert perms["can_view_reports"] is True


def test_dirigente_permissions():
    perms = get_permissions_for_role("dirigente")

    # Novas permissões
    assert perms["public_access"] is True
    assert perms["can_view_dashboard"] is True
    assert perms["can_manage_teams"] is True
    assert perms["can_manage_athletes"] is True
    assert perms["can_use_live_scout"] is False
    assert perms["can_manage_matches"] is False
    assert perms["can_manage_trainings"] is False
    assert perms["can_manage_wellness"] is False
    assert perms["can_generate_reports"] is True

    # Legado (amostra)
    assert perms["can_manage_org"] is True
    assert perms["can_create_team"] is True
    assert perms["can_create_training"] is True


def test_coordenador_permissions():
    perms = get_permissions_for_role("coordenador")

    assert perms["public_access"] is True
    assert perms["can_view_dashboard"] is True
    assert perms["can_manage_teams"] is True
    assert perms["can_manage_athletes"] is True
    assert perms["can_use_live_scout"] is True
    assert perms["can_manage_matches"] is True
    assert perms["can_manage_trainings"] is True
    assert perms["can_manage_wellness"] is True
    assert perms["can_generate_reports"] is True

    # Legado (amostra)
    assert perms["can_delete_team"] is False
    assert perms["can_delete_match"] is False
    assert perms["can_export_reports"] is False


def test_treinador_permissions():
    perms = get_permissions_for_role("treinador")

    assert perms["public_access"] is True
    assert perms["can_view_dashboard"] is True
    assert perms["can_manage_teams"] is True
    assert perms["can_manage_athletes"] is True
    assert perms["can_use_live_scout"] is True
    assert perms["can_manage_matches"] is True
    assert perms["can_manage_trainings"] is True
    assert perms["can_manage_wellness"] is True
    assert perms["can_generate_reports"] is True

    # Legado (amostra)
    assert perms["can_create_match"] is False
    assert perms["can_edit_match"] is True
    assert perms["can_view_reports"] is True


def test_atleta_permissions():
    perms = get_permissions_for_role("atleta")

    assert perms["public_access"] is True
    assert perms["can_view_dashboard"] is False
    assert perms["can_manage_teams"] is False
    assert perms["can_manage_athletes"] is False
    assert perms["can_view_statistics"] is True
    assert perms["can_use_live_scout"] is False
    assert perms["can_manage_matches"] is False
    assert perms["can_manage_trainings"] is False
    assert perms["can_manage_wellness"] is False
    assert perms["can_view_athlete_360"] is True
    assert perms["can_view_team_360"] is False
    assert perms["can_generate_reports"] is True

    # Legado (amostra)
    assert perms["can_create_training"] is False
    assert perms["can_view_matches"] is True
    assert perms["can_view_reports"] is True


def test_unknown_role_raises_value_error():
    with pytest.raises(ValueError):
        get_permissions_for_role("role_invalido")


def test_all_roles_have_same_keys():
    """Todas as roles devem ter as mesmas chaves (novas + legadas)."""
    all_keys = set()
    for role in ROLES:
        all_keys.update(get_permissions_for_role(role).keys())

    for role in ROLES:
        assert set(get_permissions_for_role(role).keys()) == all_keys

    # Novas 15 + legadas 26 = 41 (includes can_manage_members, can_correct_attendance)
    assert len(all_keys) == 41


def test_permissions_are_boolean():
    """Todas as permissões devem ser boolean (True/False)."""
    for role, perms in ROLE_PERMISSIONS.items():
        for perm_name, perm_value in perms.items():
            assert isinstance(perm_value, bool), (
                f"Permissão {perm_name} da role {role} não é boolean: {type(perm_value)}"
            )
