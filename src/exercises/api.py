from __future__ import annotations
from typing import Optional
from uuid import UUID
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest
from exercises.application.use_cases import (
    CreateExercise, ListExercises, GetExercise, UpdateExercise, DeleteExercise,
    CopyExerciseToOrg, ListExerciseVersions, GetExerciseVersion,
    ListExerciseRelations, AddExerciseRelation, DeleteExerciseRelation,
    GetExerciseACL, AddExerciseACLEntry, RemoveExerciseACLEntry,
)
from exercises.domain.rules import (
    RoleLabel, InsufficientPrivilege, ExerciseNotFound, ExerciseConflict,
)
from exercises.infrastructure.repository import ExerciseRepository
from exercises.schemas import (
    ExerciseOut, ExercisePreviewOut, ExerciseListOut, CreateExerciseIn,
    UpdateExerciseIn, DeleteExerciseIn, ExerciseVersionOut,
    ExerciseRelationOut, AddRelationIn, ExerciseACLEntryOut, AddACLEntryIn, ErrorOut,
)

router = Router()
_repo = ExerciseRepository()


def _get_role(request: HttpRequest) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


def _get_actor_id(request: HttpRequest) -> UUID:
    """Extrai actor_id do JWT validado."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")


def _get_org_id(request: HttpRequest) -> Optional[UUID]:
    v = getattr(request, "actor_org_id", None)
    return UUID(str(v)) if v else None


@router.get("", response={200: ExerciseListOut, 403: ErrorOut})
def list_exercises(request: HttpRequest, scope: Optional[str] = None,
                   sessionPhase: Optional[str] = None, primaryObjective: Optional[str] = None,
                   physicalLoad: Optional[str] = None, spaceRequired: Optional[str] = None,
                   skillLevel: Optional[str] = None, page: int = 1, pageSize: int = 50):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    uc = ListExercises(_repo)
    items, total = uc.execute(actor_role=role, actor_id=actor_id, actor_org_id=org_id,
        scope=scope, session_phase=sessionPhase, primary_objective=primaryObjective,
        physical_load=physicalLoad, space_required=spaceRequired, skill_level=skillLevel,
        page=page, page_size=pageSize)
    out_items = [ExercisePreviewOut.from_domain(e) for e in items]
    return 200, ExerciseListOut(items=out_items, page=page, pageSize=pageSize, total=total)


@router.post("", response={201: ExerciseOut, 403: ErrorOut, 422: ErrorOut})
def create_exercise(request: HttpRequest, payload: CreateExerciseIn):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    uc = CreateExercise(_repo)
    try:
        exercise = uc.execute(actor_role=role, actor_id=actor_id, actor_org_id=org_id,
            name=payload.name, session_phase=payload.sessionPhase, primary_objective=payload.primaryObjective,
            physical_load=payload.physicalLoad, space_required=payload.spaceRequired,
            skill_level=payload.skillLevel, complexity=payload.complexity,
            min_athletes=payload.minAthletes, max_athletes=payload.maxAthletes,
            estimated_duration_minutes=payload.estimatedDurationMinutes,
            age_categories=payload.ageCategories, description=payload.description,
            instructions=payload.instructions, coaching_cues=payload.coachingCues,
            safety_notes=payload.safetyNotes, secondary_objective=payload.secondaryObjective,
            game_phases=payload.gamePhases, materials=payload.materials,
            visibility_mode=payload.visibilityMode or "RESTRICTED")
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))
    return 201, ExerciseOut.from_domain(exercise)


@router.get("/{exercise_id}", response={200: ExerciseOut, 403: ErrorOut, 404: ErrorOut})
def get_exercise(request: HttpRequest, exercise_id: UUID):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        exercise = GetExercise(_repo).execute(exercise_id, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, ExerciseOut.from_domain(exercise)


@router.put("/{exercise_id}", response={200: ExerciseOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def update_exercise(request: HttpRequest, exercise_id: UUID, payload: UpdateExerciseIn):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        exercise = UpdateExercise(_repo).execute(
            exercise_id=exercise_id, actor_role=role, actor_id=actor_id,
            change_reason=payload.changeReason, name=payload.name,
            session_phase=payload.sessionPhase, primary_objective=payload.primaryObjective,
            physical_load=payload.physicalLoad, space_required=payload.spaceRequired,
            skill_level=payload.skillLevel, complexity=payload.complexity,
            min_athletes=payload.minAthletes, max_athletes=payload.maxAthletes,
            estimated_duration_minutes=payload.estimatedDurationMinutes,
            age_categories=payload.ageCategories, description=payload.description,
            instructions=payload.instructions, coaching_cues=payload.coachingCues,
            safety_notes=payload.safetyNotes, secondary_objective=payload.secondaryObjective,
            game_phases=payload.gamePhases, materials=payload.materials)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))
    return 200, ExerciseOut.from_domain(exercise)


@router.delete("/{exercise_id}", response={204: None, 403: ErrorOut, 404: ErrorOut})
def delete_exercise(request: HttpRequest, exercise_id: UUID, payload: DeleteExerciseIn):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        DeleteExercise(_repo).execute(exercise_id, role, actor_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 204, None


@router.post("/{exercise_id}/copy", response={201: ExerciseOut, 403: ErrorOut, 404: ErrorOut})
def copy_exercise_to_org(request: HttpRequest, exercise_id: UUID):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        exercise = CopyExerciseToOrg(_repo).execute(exercise_id, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 201, ExerciseOut.from_domain(exercise)


@router.get("/{exercise_id}/versions", response={200: list, 403: ErrorOut, 404: ErrorOut})
def list_exercise_versions(request: HttpRequest, exercise_id: UUID):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        versions = ListExerciseVersions(_repo).execute(exercise_id, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, [ExerciseVersionOut.from_domain(v).dict() for v in versions]


@router.get("/{exercise_id}/versions/{version_id}", response={200: ExerciseVersionOut, 403: ErrorOut, 404: ErrorOut})
def get_exercise_version(request: HttpRequest, exercise_id: UUID, version_id: UUID):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        version = GetExerciseVersion(_repo).execute(exercise_id, version_id, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, ExerciseVersionOut.from_domain(version)


@router.get("/{exercise_id}/relations", response={200: list, 403: ErrorOut, 404: ErrorOut})
def list_exercise_relations(request: HttpRequest, exercise_id: UUID):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        relations = ListExerciseRelations(_repo).execute(exercise_id, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, [ExerciseRelationOut.from_domain(r).dict() for r in relations]


@router.post("/{exercise_id}/relations", response={201: ExerciseRelationOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def add_exercise_relation(request: HttpRequest, exercise_id: UUID, payload: AddRelationIn):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        rel = AddExerciseRelation(_repo).execute(
            from_exercise_id=exercise_id, to_exercise_id=payload.toExerciseId,
            relation_type=payload.relationType, actor_role=role, actor_id=actor_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))
    return 201, ExerciseRelationOut.from_domain(rel)


@router.delete("/{exercise_id}/relations/{to_exercise_id}/{relation_type}",
               response={204: None, 403: ErrorOut, 404: ErrorOut})
def delete_exercise_relation(request: HttpRequest, exercise_id: UUID,
                              to_exercise_id: UUID, relation_type: str):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        DeleteExerciseRelation(_repo).execute(exercise_id, to_exercise_id, relation_type, role, actor_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 204, None


@router.get("/{exercise_id}/acl", response={200: list, 403: ErrorOut, 404: ErrorOut})
def get_exercise_acl(request: HttpRequest, exercise_id: UUID):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        entries = GetExerciseACL(_repo).execute(exercise_id, role, actor_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except (InsufficientPrivilege, ExerciseConflict) as e:
        return 403, ErrorOut(detail=str(e))
    return 200, [ExerciseACLEntryOut.from_domain(a).dict() for a in entries]


@router.post("/{exercise_id}/acl", response={201: ExerciseACLEntryOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def add_exercise_acl_entry(request: HttpRequest, exercise_id: UUID, payload: AddACLEntryIn):
    role, actor_id, org_id = _get_role(request), _get_actor_id(request), _get_org_id(request)
    try:
        entry = AddExerciseACLEntry(_repo).execute(exercise_id, payload.userId, role, actor_id, org_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except (InsufficientPrivilege) as e:
        return 403, ErrorOut(detail=str(e))
    except ExerciseConflict as e:
        return 422, ErrorOut(detail=str(e))
    return 201, ExerciseACLEntryOut.from_domain(entry)


@router.delete("/{exercise_id}/acl/{user_id}", response={204: None, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def remove_exercise_acl_entry(request: HttpRequest, exercise_id: UUID, user_id: UUID):
    role, actor_id = _get_role(request), _get_actor_id(request)
    try:
        RemoveExerciseACLEntry(_repo).execute(exercise_id, user_id, role, actor_id)
    except ExerciseNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ExerciseConflict as e:
        return 422, ErrorOut(detail=str(e))
    return 204, None
