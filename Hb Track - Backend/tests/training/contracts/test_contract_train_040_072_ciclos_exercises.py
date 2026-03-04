"""
CONTRACT-TRAIN-040..072 + 076 — Ciclos, Microciclos, Exercícios, Templates, Analytics, Teams
Routers:
  - training_cycles.py      (prefix=/training-cycles)        → 040..045
  - training_microcycles.py (prefix=/training-microcycles)   → 046..052
  - exercises.py            (sem prefix dedicado)            → 053..062
  - session_templates.py    (prefix=/session-templates)      → 063..068
  - training_analytics.py   (prefix=/analytics)             → 069..072
  - teams.py                                                 → 076

PROIBIDO: CONTRACT-073..075, 077..085, 097..100 já cobertos — não recriar.
Abordagem: análise estática. Sem fixtures de DB.
"""
from pathlib import Path

ROUTERS = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

CYCLES_PATH     = ROUTERS / "training_cycles.py"
MICROCYCLES_PATH = ROUTERS / "training_microcycles.py"
EXERCISES_PATH  = ROUTERS / "exercises.py"
TEMPLATES_PATH  = ROUTERS / "session_templates.py"
ANALYTICS_PATH  = ROUTERS / "training_analytics.py"
TEAMS_PATH      = ROUTERS / "teams.py"


def _cycles():     return CYCLES_PATH.read_text(encoding="utf-8")
def _micro():      return MICROCYCLES_PATH.read_text(encoding="utf-8")
def _exercises():  return EXERCISES_PATH.read_text(encoding="utf-8")
def _templates():  return TEMPLATES_PATH.read_text(encoding="utf-8")
def _analytics():  return ANALYTICS_PATH.read_text(encoding="utf-8")
def _teams():      return TEAMS_PATH.read_text(encoding="utf-8")


# ===========================================================================
# CONTRACT-040..045  Training Cycles  /training-cycles
# ===========================================================================

class TestContractTrain040ListCycles:
    def test_router_file_exists(self):
        assert CYCLES_PATH.exists()

    def test_prefix_training_cycles(self):
        assert "/training-cycles" in _cycles()

    def test_get_list_route(self):
        content = _cycles()
        assert "@router.get" in content and '""' in content


class TestContractTrain041GetCycle:
    def test_get_by_id_route(self):
        content = _cycles()
        assert "/{cycle_id}" in content and "@router.get" in content


class TestContractTrain042CreateCycle:
    def test_post_create_route(self):
        assert "@router.post" in _cycles()


class TestContractTrain043UpdateCycle:
    def test_patch_update_route(self):
        assert "@router.patch" in _cycles()


class TestContractTrain044DeleteCycle:
    def test_delete_route(self):
        assert "@router.delete" in _cycles()


class TestContractTrain045ActiveCycles:
    def test_active_cycles_route(self):
        content = _cycles()
        assert "active" in content and "team_id" in content


# ===========================================================================
# CONTRACT-046..052  Training Microcycles  /training-microcycles
# ===========================================================================

class TestContractTrain046ListMicrocycles:
    def test_router_file_exists(self):
        assert MICROCYCLES_PATH.exists()

    def test_prefix_training_microcycles(self):
        assert "/training-microcycles" in _micro()

    def test_get_list_route(self):
        content = _micro()
        assert "@router.get" in content and '""' in content


class TestContractTrain047GetMicrocycle:
    def test_get_by_id_route(self):
        content = _micro()
        assert "microcycle_id" in content and "@router.get" in content


class TestContractTrain048CreateMicrocycle:
    def test_post_create_route(self):
        assert "@router.post" in _micro()


class TestContractTrain049UpdateMicrocycle:
    def test_patch_update_route(self):
        assert "@router.patch" in _micro()


class TestContractTrain050DeleteMicrocycle:
    def test_delete_route(self):
        assert "@router.delete" in _micro()


class TestContractTrain051CurrentMicrocycle:
    def test_current_microcycle_route(self):
        content = _micro()
        assert "current" in content and "team_id" in content


class TestContractTrain052MicrocycleSummary:
    def test_summary_route(self):
        content = _micro()
        assert "summary" in content and "microcycle_id" in content


# ===========================================================================
# CONTRACT-053..062  Exercises  /exercises / /exercise-tags / /exercise-favorites
# ===========================================================================

class TestContractTrain053ListExercises:
    def test_router_file_exists(self):
        assert EXERCISES_PATH.exists()

    def test_get_exercises_route(self):
        content = _exercises()
        assert '"/exercises"' in content and "@router.get" in content


class TestContractTrain054GetExercise:
    def test_get_exercise_by_id_route(self):
        content = _exercises()
        assert '"/exercises/{exercise_id}"' in content


class TestContractTrain055CreateExercise:
    def test_post_exercises_route(self):
        content = _exercises()
        assert "@router.post" in content and '"/exercises"' in content


class TestContractTrain056UpdateExercise:
    def test_patch_exercises_route(self):
        content = _exercises()
        assert "@router.patch" in content and '"/exercises/{exercise_id}"' in content


class TestContractTrain057ListTags:
    def test_get_exercise_tags_route(self):
        content = _exercises()
        assert '"/exercise-tags"' in content and "@router.get" in content


class TestContractTrain058CreateTag:
    def test_post_exercise_tags_route(self):
        content = _exercises()
        assert "@router.post" in content and '"/exercise-tags"' in content


class TestContractTrain059UpdateTag:
    def test_patch_tag_route(self):
        content = _exercises()
        assert '"/exercise-tags/{tag_id}"' in content


class TestContractTrain060ListFavorites:
    def test_get_exercise_favorites_route(self):
        content = _exercises()
        assert '"/exercise-favorites"' in content and "@router.get" in content


class TestContractTrain061AddFavorite:
    def test_post_exercise_favorites_route(self):
        content = _exercises()
        assert "@router.post" in content and '"/exercise-favorites"' in content


class TestContractTrain062RemoveFavorite:
    def test_delete_exercise_favorites_route(self):
        content = _exercises()
        assert '"/exercise-favorites/{exercise_id}"' in content


# ===========================================================================
# CONTRACT-063..068  Session Templates  /session-templates
# ===========================================================================

class TestContractTrain063ListTemplates:
    def test_router_file_exists(self):
        assert TEMPLATES_PATH.exists()

    def test_prefix_session_templates(self):
        assert "/session-templates" in _templates()

    def test_get_list_route(self):
        content = _templates()
        assert "@router.get" in content and '""' in content


class TestContractTrain064CreateTemplate:
    def test_post_create_route(self):
        assert "@router.post" in _templates()


class TestContractTrain065GetTemplate:
    def test_get_by_id_route(self):
        content = _templates()
        assert '"/{template_id}"' in content and "@router.get" in content


class TestContractTrain066UpdateTemplate:
    def test_patch_update_route(self):
        content = _templates()
        assert "@router.patch" in content and "template_id" in content


class TestContractTrain067ToggleFavoriteTemplate:
    def test_toggle_favorite_route(self):
        content = _templates()
        assert "favorite" in content


class TestContractTrain068DeleteTemplate:
    def test_delete_route(self):
        assert "@router.delete" in _templates()


# ===========================================================================
# CONTRACT-069..072  Training Analytics  /analytics/team/{team_id}/...
# ===========================================================================

class TestContractTrain069TeamSummary:
    def test_router_file_exists(self):
        assert ANALYTICS_PATH.exists()

    def test_prefix_analytics(self):
        assert '"/analytics"' in _analytics() or 'prefix="/analytics"' in _analytics()

    def test_team_summary_route(self):
        content = _analytics()
        assert "/team/{team_id}/summary" in content


class TestContractTrain070WeeklyLoad:
    def test_weekly_load_route(self):
        content = _analytics()
        assert "weekly-load" in content and "team_id" in content


class TestContractTrain071DeviationAnalysis:
    def test_deviation_analysis_route(self):
        content = _analytics()
        assert "deviation-analysis" in content and "team_id" in content


class TestContractTrain072PreventionEffectiveness:
    def test_prevention_effectiveness_route(self):
        content = _analytics()
        assert "prevention" in content and "team_id" in content


# ===========================================================================
# CONTRACT-076  GET /teams/{team_id}/wellness-top-performers
# ===========================================================================

class TestContractTrain076WellnessTopPerformers:
    def test_router_file_exists(self):
        assert TEAMS_PATH.exists()

    def test_wellness_top_performers_route(self):
        content = _teams()
        assert "wellness-top-performers" in content
