from __future__ import annotations
from typing import Optional, List
from uuid import UUID

from exercises.domain.entities import Exercise, ExerciseVersion, ExerciseRelation, ExerciseACL
from exercises.infrastructure.models import (
    ExerciseModel, ExerciseVersionModel, ExerciseRelationModel, ExerciseACLModel
)


def _to_domain_version(m: ExerciseVersionModel) -> ExerciseVersion:
    return ExerciseVersion(
        id=m.id, exercise_id=m.exercise_id, version_number=m.version_number,
        name=m.name, description=m.description, instructions=m.instructions,
        coaching_cues=m.coaching_cues, safety_notes=m.safety_notes,
        session_phase=m.session_phase, primary_objective=m.primary_objective,
        secondary_objective=m.secondary_objective, game_phases=list(m.game_phases or []),
        age_categories=list(m.age_categories or []), skill_level=m.skill_level,
        complexity=m.complexity, physical_load=m.physical_load, min_athletes=m.min_athletes,
        max_athletes=m.max_athletes, estimated_duration_minutes=m.estimated_duration_minutes,
        space_required=m.space_required, materials=list(m.materials or []),
        change_reason=m.change_reason, created_at=m.created_at, created_by_user_id=m.created_by_user_id,
    )


def _to_domain(m: ExerciseModel, version: Optional[ExerciseVersionModel] = None) -> Exercise:
    return Exercise(
        id=m.id, scope=m.scope, organization_id=m.organization_id,
        created_by_user_id=m.created_by_user_id, current_version_id=m.current_version_id,
        visibility_mode=m.visibility_mode, editorial_status=m.editorial_status,
        is_deleted=m.is_deleted, deleted_at=m.deleted_at,
        created_at=m.created_at, updated_at=m.updated_at,
        current_version=_to_domain_version(version) if version else None,
    )


class ExerciseRepository:
    def save(self, exercise: Exercise) -> Exercise:
        obj, _ = ExerciseModel.objects.update_or_create(
            id=exercise.id,
            defaults={
                "scope": exercise.scope, "organization_id": exercise.organization_id,
                "created_by_user_id": exercise.created_by_user_id,
                "current_version_id": exercise.current_version_id,
                "visibility_mode": exercise.visibility_mode, "editorial_status": exercise.editorial_status,
                "is_deleted": exercise.is_deleted, "deleted_at": exercise.deleted_at,
            },
        )
        ver = None
        if exercise.current_version_id:
            try:
                ver = ExerciseVersionModel.objects.get(id=exercise.current_version_id)
            except ExerciseVersionModel.DoesNotExist:
                pass
        return _to_domain(obj, ver)

    def get_by_id(self, exercise_id: UUID) -> Optional[Exercise]:
        try:
            obj = ExerciseModel.objects.get(id=exercise_id)
        except ExerciseModel.DoesNotExist:
            return None
        ver = None
        if obj.current_version_id:
            try:
                ver = ExerciseVersionModel.objects.get(id=obj.current_version_id)
            except ExerciseVersionModel.DoesNotExist:
                pass
        return _to_domain(obj, ver)

    def list_exercises(self, scope: Optional[str] = None, session_phase: Optional[str] = None,
                        primary_objective: Optional[str] = None, physical_load: Optional[str] = None,
                        space_required: Optional[str] = None, skill_level: Optional[str] = None,
                        page: int = 1, page_size: int = 50) -> tuple:
        qs = ExerciseModel.objects.filter(is_deleted=False)
        if scope:
            qs = qs.filter(scope=scope)
        total = qs.count()
        offset = (page - 1) * page_size
        items = [_to_domain(m) for m in qs[offset: offset + page_size]]
        return items, total

    def save_version(self, version: ExerciseVersion) -> ExerciseVersion:
        obj = ExerciseVersionModel.objects.create(
            id=version.id, exercise_id=version.exercise_id, version_number=version.version_number,
            name=version.name, description=version.description, instructions=version.instructions,
            coaching_cues=version.coaching_cues, safety_notes=version.safety_notes,
            session_phase=version.session_phase, primary_objective=version.primary_objective,
            secondary_objective=version.secondary_objective, game_phases=version.game_phases,
            age_categories=version.age_categories, skill_level=version.skill_level,
            complexity=version.complexity, physical_load=version.physical_load, min_athletes=version.min_athletes,
            max_athletes=version.max_athletes, estimated_duration_minutes=version.estimated_duration_minutes,
            space_required=version.space_required, materials=version.materials,
            change_reason=version.change_reason, created_by_user_id=version.created_by_user_id,
        )
        return _to_domain_version(obj)

    def list_versions(self, exercise_id: UUID) -> List[ExerciseVersion]:
        qs = ExerciseVersionModel.objects.filter(exercise_id=exercise_id).order_by("-version_number")
        return [_to_domain_version(m) for m in qs]

    def get_version(self, version_id: UUID) -> Optional[ExerciseVersion]:
        try:
            return _to_domain_version(ExerciseVersionModel.objects.get(id=version_id))
        except ExerciseVersionModel.DoesNotExist:
            return None

    def get_max_version_number(self, exercise_id: UUID) -> int:
        qs = ExerciseVersionModel.objects.filter(exercise_id=exercise_id)
        if not qs.exists():
            return 0
        return qs.order_by("-version_number").first().version_number

    # Relations
    def save_relation(self, rel: ExerciseRelation) -> ExerciseRelation:
        obj = ExerciseRelationModel.objects.create(
            id=rel.id, from_exercise_id=rel.from_exercise_id, to_exercise_id=rel.to_exercise_id,
            relation_type=rel.relation_type, created_by_user_id=rel.created_by_user_id,
        )
        return ExerciseRelation(id=obj.id, from_exercise_id=obj.from_exercise_id,
            to_exercise_id=obj.to_exercise_id, relation_type=obj.relation_type,
            created_by_user_id=obj.created_by_user_id, created_at=obj.created_at)

    def list_relations(self, exercise_id: UUID) -> List[ExerciseRelation]:
        qs = ExerciseRelationModel.objects.filter(from_exercise_id=exercise_id)
        return [ExerciseRelation(id=m.id, from_exercise_id=m.from_exercise_id,
            to_exercise_id=m.to_exercise_id, relation_type=m.relation_type,
            created_by_user_id=m.created_by_user_id, created_at=m.created_at) for m in qs]

    def delete_relation(self, from_exercise_id: UUID, to_exercise_id: UUID, relation_type: str) -> bool:
        deleted, _ = ExerciseRelationModel.objects.filter(
            from_exercise_id=from_exercise_id, to_exercise_id=to_exercise_id, relation_type=relation_type
        ).delete()
        return deleted > 0

    # ACL
    def list_acl(self, exercise_id: UUID) -> List[ExerciseACL]:
        qs = ExerciseACLModel.objects.filter(exercise_id=exercise_id)
        return [ExerciseACL(id=m.id, exercise_id=m.exercise_id, user_id=m.user_id,
            created_by_user_id=m.created_by_user_id, created_at=m.created_at) for m in qs]

    def add_acl_entry(self, acl: ExerciseACL) -> ExerciseACL:
        obj, _ = ExerciseACLModel.objects.get_or_create(
            exercise_id=acl.exercise_id, user_id=acl.user_id,
            defaults={"id": acl.id, "created_by_user_id": acl.created_by_user_id},
        )
        return ExerciseACL(id=obj.id, exercise_id=obj.exercise_id, user_id=obj.user_id,
            created_by_user_id=obj.created_by_user_id, created_at=obj.created_at)

    def remove_acl_entry(self, exercise_id: UUID, user_id: UUID) -> bool:
        deleted, _ = ExerciseACLModel.objects.filter(exercise_id=exercise_id, user_id=user_id).delete()
        return deleted > 0

    def get_acl_user_ids(self, exercise_id: UUID) -> list:
        return list(ExerciseACLModel.objects.filter(exercise_id=exercise_id).values_list("user_id", flat=True))
