"""
Mapa canônico de permissões — fonte única.

Regras:
- Não renomear permissões sem versionar.
- Não remover permissões já existentes.
- Pode alterar valores True/False e adicionar novas chaves (para todas as roles).
"""

from typing import Dict

# Mapa canônico: role -> permissões
ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
    "superadmin": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": True,
        "can_access_intake": True,

        # Controles integrados (sidebar)
        "can_manage_teams": True,
        "can_manage_athletes": True,
        "can_view_statistics": True,
        "can_use_live_scout": True,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": True,
        "can_manage_trainings": True,
        "can_manage_wellness": True,
        "can_view_athlete_360": True,
        "can_view_team_360": True,
        "can_generate_reports": True,

        # Legado granular
        "can_manage_org": True,
        "can_manage_users": True,
        "can_manage_seasons": True,
        "can_create_team": True,
        "can_edit_team": True,
        "can_delete_team": True,
        "can_view_teams": True,
        "can_create_athlete": True,
        "can_edit_athlete": True,
        "can_delete_athlete": True,
        "can_view_athletes": True,
        "can_create_training": True,
        "can_edit_training": True,
        "can_delete_training": True,
        "can_view_training": True,
        "can_create_match": True,
        "can_edit_match": True,
        "can_delete_match": True,
        "can_view_matches": True,
        "can_view_reports": True,
        "can_export_reports": True,
        "can_view_wellness": True,
        "can_edit_wellness": True,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": True,  # Correção de presenças pós-fechamento (R37)
    },

    "dirigente": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": True,
        "can_access_intake": True,

        # Controles integrados (sidebar)
        "can_manage_teams": True,
        "can_manage_athletes": True,
        "can_view_statistics": True,
        "can_use_live_scout": False,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": False,
        "can_manage_trainings": False,
        "can_manage_wellness": False,
        "can_view_athlete_360": True,
        "can_view_team_360": True,
        "can_generate_reports": True,

        # Legado granular
        "can_manage_org": True,
        "can_manage_users": True,
        "can_manage_members": True,  # Adicionar/remover membros de equipes (step 1)
        "can_manage_seasons": True,
        "can_create_team": True,
        "can_edit_team": True,
        "can_delete_team": True,
        "can_view_teams": True,
        "can_create_athlete": True,
        "can_edit_athlete": True,
        "can_delete_athlete": True,
        "can_view_athletes": True,
        "can_create_training": True,
        "can_edit_training": True,
        "can_delete_training": True,
        "can_view_training": True,
        "can_create_match": True,
        "can_edit_match": True,
        "can_delete_match": True,
        "can_view_matches": True,
        "can_view_reports": True,
        "can_export_reports": True,
        "can_view_wellness": True,
        "can_edit_wellness": True,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": True,  # Correção de presenças pós-fechamento (R37)
    },

    "coordenador": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": True,
        "can_access_intake": True,

        # Controles integrados (sidebar)
        "can_manage_teams": True,
        "can_manage_athletes": True,
        "can_view_statistics": True,
        "can_use_live_scout": True,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": True,
        "can_manage_trainings": True,
        "can_manage_wellness": True,
        "can_view_athlete_360": True,
        "can_view_team_360": True,
        "can_generate_reports": True,

        # Legado granular
        "can_manage_org": False,
        "can_manage_users": False,
        "can_manage_members": True,  # Adicionar/remover membros de equipes (step 1)
        "can_manage_seasons": False,
        "can_create_team": True,
        "can_edit_team": True,
        "can_delete_team": False,
        "can_view_teams": True,
        "can_create_athlete": True,
        "can_edit_athlete": True,
        "can_delete_athlete": False,
        "can_view_athletes": True,
        "can_create_training": True,
        "can_edit_training": True,
        "can_delete_training": True,
        "can_view_training": True,
        "can_create_match": True,
        "can_edit_match": True,
        "can_delete_match": False,
        "can_view_matches": True,
        "can_view_reports": True,
        "can_export_reports": False,
        "can_view_wellness": True,
        "can_edit_wellness": False,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": True,  # Correção de presenças pós-fechamento (R37)
    },

    "treinador": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": True,
        "can_access_intake": True,

        # Controles integrados (sidebar)
        "can_manage_teams": True,
        "can_manage_athletes": True,
        "can_view_statistics": True,
        "can_use_live_scout": True,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": True,
        "can_manage_trainings": True,
        "can_manage_wellness": True,
        "can_view_athlete_360": True,
        "can_view_team_360": True,
        "can_generate_reports": True,

        # Legado granular
        "can_manage_org": False,
        "can_manage_users": False,
        "can_manage_members": False,  # Treinadores não podem gerenciar membros (step 1)
        "can_manage_seasons": False,
        "can_create_team": True,  # RF6 atualizado: Treinadores podem criar equipes
        "can_edit_team": True,
        "can_delete_team": False,
        "can_view_teams": True,
        "can_create_athlete": True,
        "can_edit_athlete": True,
        "can_delete_athlete": False,
        "can_view_athletes": True,
        "can_create_training": True,
        "can_edit_training": True,
        "can_delete_training": True,
        "can_view_training": True,
        "can_create_match": False,
        "can_edit_match": True,
        "can_delete_match": False,
        "can_view_matches": True,
        "can_view_reports": True,
        "can_export_reports": False,
        "can_view_wellness": True,
        "can_edit_wellness": True,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": False,  # Treinadores não podem corrigir pós-fechamento
    },

    "atleta": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": False,
        "can_access_intake": False,

        # Controles integrados (sidebar)
        "can_manage_teams": False,
        "can_manage_athletes": False,
        "can_view_statistics": True,
        "can_use_live_scout": False,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": False,
        "can_manage_trainings": False,
        "can_manage_wellness": False,
        "can_view_athlete_360": True,
        "can_view_team_360": False,
        "can_generate_reports": True,

        # Legado granular
        "can_manage_org": False,
        "can_manage_users": False,
        "can_manage_members": False,  # Atletas não podem gerenciar membros (step 1)
        "can_manage_seasons": False,
        "can_create_team": False,
        "can_edit_team": False,
        "can_delete_team": False,
        "can_view_teams": True,
        "can_create_athlete": False,
        "can_edit_athlete": False,
        "can_delete_athlete": False,
        "can_view_athletes": True,
        "can_create_training": False,
        "can_edit_training": False,
        "can_delete_training": False,
        "can_view_training": True,
        "can_create_match": False,
        "can_edit_match": False,
        "can_delete_match": False,
        "can_view_matches": True,
        "can_view_reports": True,
        "can_export_reports": False,
        "can_view_wellness": True,
        "can_edit_wellness": True,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": False,  # Atletas não podem corrigir presenças
    },

    "membro": {
        # Acesso geral e navegação
        "public_access": True,
        "can_view_dashboard": True,
        "can_access_intake": False,

        # Controles integrados (sidebar)
        "can_manage_teams": False,
        "can_manage_athletes": False,
        "can_view_statistics": True,
        "can_use_live_scout": False,
        "can_view_calendar": True,
        "can_view_competitions": True,
        "can_view_training_schedule": True,
        "can_manage_matches": False,
        "can_manage_trainings": False,
        "can_manage_wellness": False,
        "can_view_athlete_360": True,
        "can_view_team_360": True,
        "can_generate_reports": False,

        # Legado granular
        "can_manage_org": False,
        "can_manage_users": False,
        "can_manage_members": False,  # Membros não podem gerenciar membros (step 1)
        "can_manage_seasons": False,
        "can_create_team": False,
        "can_edit_team": False,
        "can_delete_team": False,
        "can_view_teams": True,
        "can_create_athlete": False,
        "can_edit_athlete": False,
        "can_delete_athlete": False,
        "can_view_athletes": True,
        "can_create_training": False,
        "can_edit_training": False,
        "can_delete_training": False,
        "can_view_training": True,
        "can_create_match": False,
        "can_edit_match": False,
        "can_delete_match": False,
        "can_view_matches": True,
        "can_view_reports": False,
        "can_export_reports": False,
        "can_view_wellness": True,
        "can_edit_wellness": False,
        
        # Training - Correções administrativas (Step 11 - Refatoração)
        "can_correct_attendance": False,  # Membros não podem corrigir presenças
    },
}


def get_permissions_for_role(role_code: str) -> Dict[str, bool]:
    """
    Retorna permissões para uma role específica.

    Args:
        role_code: Código da role (superadmin, dirigente, coordenador, treinador, atleta, membro)

    Returns:
        Dict[str, bool]: Mapa de permissões

    Raises:
        ValueError: Se role_code não existir
    """
    if role_code not in ROLE_PERMISSIONS:
        raise ValueError(f"Role '{role_code}' não encontrada no mapa de permissões")

    return ROLE_PERMISSIONS[role_code]


def get_all_permission_keys() -> list[str]:
    """
    Retorna lista de todas as chaves de permissão disponíveis.

    Útil para validação e documentação.
    """
    return list(ROLE_PERMISSIONS["superadmin"].keys())
