"""
CONTRACT-TRAIN-086..095 — Analytics Exports + Athlete Export + Exercises ACL/Visibility
Routers:
  - exports.py       (sem prefix dedicado) → 086..089
  - athlete_export.py (prefix=/athletes)  → 090
  - exercises.py     (sem prefix dedicado) → 091..095

PROIBIDO: CONTRACT-073..075, 077..085, 097..100 já cobertos — não recriar.
Abordagem: análise estática. Sem fixtures de DB.
"""
from pathlib import Path

ROUTERS = Path(__file__).parent.parent.parent.parent / "app" / "api" / "v1" / "routers"

EXPORTS_PATH        = ROUTERS / "exports.py"
ATHLETE_EXPORT_PATH = ROUTERS / "athlete_export.py"
EXERCISES_PATH      = ROUTERS / "exercises.py"


def _exports():         return EXPORTS_PATH.read_text(encoding="utf-8")
def _athlete_export():  return ATHLETE_EXPORT_PATH.read_text(encoding="utf-8")
def _exercises():       return EXERCISES_PATH.read_text(encoding="utf-8")


# ===========================================================================
# CONTRACT-086..089  Analytics Exports
# ===========================================================================

class TestContractTrain086ExportPdf:
    def test_router_file_exists(self):
        assert EXPORTS_PATH.exists()

    def test_export_pdf_route(self):
        content = _exports()
        assert "export-pdf" in content


class TestContractTrain087GetExportJobStatus:
    def test_get_export_job_route(self):
        content = _exports()
        assert "exports" in content and "@router.get" in content
        # rota com job_id
        assert "job_id" in content


class TestContractTrain088ListExports:
    def test_list_exports_route(self):
        content = _exports()
        assert "exports" in content and "@router.get" in content


class TestContractTrain089ExportRateLimit:
    def test_rate_limit_route(self):
        content = _exports()
        assert "export-rate-limit" in content


# ===========================================================================
# CONTRACT-090  GET /athletes/me/export-data
# ===========================================================================

class TestContractTrain090AthleteExportData:
    def test_router_file_exists(self):
        assert ATHLETE_EXPORT_PATH.exists()

    def test_prefix_athletes(self):
        content = _athlete_export()
        assert "/athletes" in content

    def test_export_data_route(self):
        content = _athlete_export()
        assert "/me/export-data" in content or "export-data" in content


# ===========================================================================
# CONTRACT-091..095  Exercises ACL + Visibility + Copy-to-Org
# ===========================================================================

class TestContractTrain091GetExerciseAcl:
    def test_router_file_exists(self):
        assert EXERCISES_PATH.exists()

    def test_get_acl_route(self):
        content = _exercises()
        assert '"/exercises/{exercise_id}/acl"' in content and "@router.get" in content


class TestContractTrain092AddExerciseAcl:
    def test_post_acl_route(self):
        content = _exercises()
        assert "@router.post" in content and "/acl" in content


class TestContractTrain093RemoveExerciseAcl:
    def test_delete_acl_route(self):
        content = _exercises()
        assert "@router.delete" in content and "/acl/" in content


class TestContractTrain094UpdateExerciseVisibility:
    def test_visibility_route(self):
        content = _exercises()
        assert "/visibility" in content and "@router.patch" in content


class TestContractTrain095CopyExerciseToOrg:
    def test_copy_to_org_route(self):
        content = _exercises()
        assert "copy-to-org" in content and "@router.post" in content
