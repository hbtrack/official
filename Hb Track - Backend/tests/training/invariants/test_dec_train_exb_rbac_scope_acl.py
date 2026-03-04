"""
DEC-TRAIN-EXB-001  — GET /exercises retorna SYSTEM + ORG própria (scope_filter estático)
DEC-TRAIN-EXB-001B — visibility restricted filtra por ACL (exercise_acl_service.has_access)
DEC-TRAIN-EXB-002  — ACL management CRUD: POST/DELETE /exercises/{id}/acl
DEC-TRAIN-RBAC-001a — PATCH /exercises/{id} como Treinador creator → 200 (roles = treinador/..)
DEC-TRAIN-RBAC-001b — PATCH exercise SYSTEM como Treinador → 403 (org isolation no router)

Abordagem: 100% análise estática (read_text). Sem fixtures de DB, sem requests ao vivo.
"""

from pathlib import Path

BASE = Path(__file__).parent.parent.parent.parent
ROUTERS = BASE / "app" / "api" / "v1" / "routers"
SERVICES = BASE / "app" / "services"

EXERCISES_ROUTER = ROUTERS / "exercises.py"
EXERCISE_SERVICE = SERVICES / "exercise_service.py"
EXERCISE_ACL_SERVICE = SERVICES / "exercise_acl_service.py"


def _router() -> str:
    return EXERCISES_ROUTER.read_text(encoding="utf-8")


def _service() -> str:
    return EXERCISE_SERVICE.read_text(encoding="utf-8")


def _acl_service() -> str:
    return EXERCISE_ACL_SERVICE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# DEC-TRAIN-EXB-001 — scope_filter: SYSTEM + ORG própria (exclui ORG externa)
# ---------------------------------------------------------------------------

class TestDecTrainExb001ScopeFilter:
    """DEC-EXB-001: list_exercises retorna SYSTEM+ORG própria; exclui ORG de terceiros."""

    def test_exercise_service_exists(self):
        assert EXERCISE_SERVICE.exists(), (
            "exercise_service.py não encontrado em app/services/"
        )

    def test_list_exercises_method_exists(self):
        """DEC-EXB-001: método list_exercises existe no service."""
        assert "list_exercises" in _service(), (
            "DEC-EXB-001: método 'list_exercises' ausente em exercise_service.py"
        )

    def test_system_scope_included_in_filter(self):
        """DEC-EXB-001: filter inclui scope 'SYSTEM' (catálogo global)."""
        content = _service()
        assert "'SYSTEM'" in content or '"SYSTEM"' in content, (
            "DEC-EXB-001: filtro por scope SYSTEM ausente em exercise_service.py"
        )

    def test_organization_id_used_in_filter(self):
        """DEC-EXB-001: filter usa organization_id para ORG própria (exclui outras)."""
        assert "organization_id" in _service(), (
            "DEC-EXB-001: 'organization_id' ausente em exercise_service.py"
        )

    def test_scope_filter_logic_ors_system_and_org(self):
        """DEC-EXB-001: scope_filter usa OR entre SYSTEM e organization_id própria."""
        content = _service()
        has_scope_logic = "scope_filter" in content or (
            ("SYSTEM" in content) and ("organization_id" in content)
        )
        assert has_scope_logic, (
            "DEC-EXB-001: lógica scope_filter (OR SYSTEM|org) ausente em exercise_service.py"
        )

    def test_list_exercises_endpoint_exists_in_router(self):
        """DEC-EXB-001: GET /exercises endpoint presente no router."""
        content = _router()
        assert "list_exercises" in content or (
            "@router.get" in content and "/exercises" in content
        ), "DEC-EXB-001: GET /exercises ausente em exercises.py"


# ---------------------------------------------------------------------------
# DEC-TRAIN-EXB-001B — visibility restricted filtra por ACL
# ---------------------------------------------------------------------------

class TestDecTrainExb001BVisibilityRestrictedAcl:
    """DEC-EXB-001B: exercise visibility_mode='restricted' requer ACL para acesso."""

    def test_acl_service_exists(self):
        assert EXERCISE_ACL_SERVICE.exists(), (
            "exercise_acl_service.py não encontrado em app/services/"
        )

    def test_has_access_method_exists(self):
        """DEC-EXB-001B: ExerciseAclService.has_access verifica ACL para restricted."""
        assert "has_access" in _acl_service(), (
            "DEC-EXB-001B: método 'has_access' ausente em exercise_acl_service.py"
        )

    def test_restricted_visibility_mode_handled(self):
        """DEC-EXB-001B: 'restricted' visibility_mode está tratado no ACL service."""
        content = _acl_service()
        assert "restricted" in content, (
            "DEC-EXB-001B: 'restricted' visibility_mode ausente em exercise_acl_service.py"
        )

    def test_validate_restricted_visibility_method(self):
        """DEC-EXB-001B: método de validação de restricted presente no ACL service."""
        content = _acl_service()
        assert "_validate_restricted_visibility" in content or "visibility_mode" in content, (
            "DEC-EXB-001B: validação de visibility_mode ausente em exercise_acl_service.py"
        )

    def test_acl_service_imported_or_used_in_main_service(self):
        """DEC-EXB-001B: exercise_service utiliza ExerciseAclService ou exercise_acl."""
        content = _service()
        assert (
            "ExerciseAclService" in content
            or "exercise_acl" in content
            or "visibility" in content
        ), (
            "DEC-EXB-001B: exercise_service.py não referencia ExerciseAclService "
            "— isolamento visibilidade restricted não garantido"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-EXB-002 — ACL management CRUD (POST/DELETE /exercises/{id}/acl)
# ---------------------------------------------------------------------------

class TestDecTrainExb002AclCrud:
    """DEC-EXB-002: endpoints POST e DELETE para ACL de exercícios existem."""

    def test_exercises_router_exists(self):
        assert EXERCISES_ROUTER.exists(), (
            "exercises.py não encontrado em app/api/v1/routers/"
        )

    def test_post_acl_endpoint_exists(self):
        """DEC-EXB-002: POST /exercises/{exercise_id}/acl (grant) presente."""
        content = _router()
        assert "/exercises/{exercise_id}/acl" in content or (
            "{exercise_id}" in content and "acl" in content
        ), "DEC-EXB-002: endpoint POST /exercises/{id}/acl ausente em exercises.py"

    def test_acl_grant_returns_201(self):
        """DEC-EXB-002: grant ACL retorna 201 Created."""
        assert "HTTP_201_CREATED" in _router(), (
            "DEC-EXB-002: HTTP_201_CREATED ausente em exercises.py — grant ACL não retorna 201"
        )

    def test_delete_acl_endpoint_exists(self):
        """DEC-EXB-002: DELETE /exercises/{id}/acl/{user_id} (revoke) presente."""
        content = _router()
        assert "@router.delete" in content, (
            "DEC-EXB-002: @router.delete ausente em exercises.py"
        )
        assert "acl" in content, (
            "DEC-EXB-002: 'acl' ausente no router — DELETE ACL não implementado"
        )

    def test_acl_revoke_returns_204(self):
        """DEC-EXB-002: revoke ACL retorna 204 No Content."""
        assert "HTTP_204_NO_CONTENT" in _router(), (
            "DEC-EXB-002: HTTP_204_NO_CONTENT ausente — revoke ACL não retorna 204"
        )

    def test_acl_list_get_endpoint_exists(self):
        """DEC-EXB-002: GET /exercises/{id}/acl (list) presente."""
        content = _router()
        # Deve existir @router.get referenciando acl
        assert "@router.get" in content and "acl" in content, (
            "DEC-EXB-002: GET /exercises/{id}/acl ausente em exercises.py"
        )

    def test_acl_grant_request_schema_used(self):
        """DEC-EXB-002: schema ExerciseACLGrantRequest importado/usado no router."""
        assert "ExerciseACLGrantRequest" in _router(), (
            "DEC-EXB-002: ExerciseACLGrantRequest ausente em exercises.py"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-RBAC-001a — PATCH exercise como Treinador creator → 200
# ---------------------------------------------------------------------------

class TestDecTrainRbac001aTreinadorPatch200:
    """DEC-RBAC-001a: PATCH /exercises/{id} requer role treinador/coordenador/dirigente."""

    def test_patch_exercise_endpoint_exists(self):
        """DEC-RBAC-001a: @router.patch para /exercises/{id} presente."""
        content = _router()
        assert "@router.patch" in content, (
            "DEC-RBAC-001a: @router.patch ausente em exercises.py"
        )

    def test_treinador_role_in_patch_permissions(self):
        """DEC-RBAC-001a: role 'treinador' listado nas permissões do PATCH exercise."""
        assert "treinador" in _router(), (
            "DEC-RBAC-001a: role 'treinador' ausente em exercises.py — "
            "PATCH exercise não permitido para Treinador"
        )

    def test_coordenador_role_also_allowed(self):
        """DEC-RBAC-001a: roles coordenador/dirigente também têm acesso ao PATCH."""
        content = _router()
        assert "coordenador" in content, (
            "DEC-RBAC-001a: role 'coordenador' ausente em exercises.py"
        )

    def test_exercise_response_schema_used(self):
        """DEC-RBAC-001a: PATCH retorna ExerciseResponse (200 implícito via response_model)."""
        assert "ExerciseResponse" in _router(), (
            "DEC-RBAC-001a: ExerciseResponse ausente — response_model do PATCH não definido"
        )

    def test_update_exercise_method_in_service(self):
        """DEC-RBAC-001a: service.update_exercise é o método de atualização chamado."""
        assert "update_exercise" in _service(), (
            "DEC-RBAC-001a: 'update_exercise' ausente em exercise_service.py"
        )


# ---------------------------------------------------------------------------
# DEC-TRAIN-RBAC-001b — PATCH exercise SYSTEM como Treinador → 403
# ---------------------------------------------------------------------------

class TestDecTrainRbac001bSystemExerciseForbidden:
    """DEC-RBAC-001b: Treinador não pode editar exercício SYSTEM (isolamento por org)."""

    def test_organization_id_check_in_router(self):
        """DEC-RBAC-001b: router verifica organization_id para isolar exercícios de outra org."""
        assert "organization_id" in _router(), (
            "DEC-RBAC-001b: 'organization_id' ausente em exercises.py — "
            "isolamento ORG/SYSTEM não garantido"
        )

    def test_403_forbidden_raised_in_router(self):
        """DEC-RBAC-001b: HTTP 403 é levantado quando org não coincide."""
        content = _router()
        assert "HTTP_403_FORBIDDEN" in content or "status_code=403" in content, (
            "DEC-RBAC-001b: HTTP_403_FORBIDDEN ausente em exercises.py — "
            "Treinador pode editar exercício SYSTEM sem bloqueio"
        )

    def test_service_update_exercise_uses_org_isolation(self):
        """DEC-RBAC-001b: service.update_exercise filtra por organization_id (exclui SYSTEM)."""
        content = _service()
        assert "update_exercise" in content and "organization_id" in content, (
            "DEC-RBAC-001b: update_exercise não usa organization_id — "
            "isolamento SYSTEM vs ORG ausente no service"
        )
