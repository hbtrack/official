from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from exercises.domain.entities import Exercise, ExerciseVersion, ExerciseRelation, ExerciseACL
from exercises.domain.rules import (
    RoleLabel, InsufficientPrivilege, ExerciseNotFound, ExerciseConflict,
    assert_can_create_exercise, assert_can_modify_exercise, assert_can_delete_exercise,
    can_read_exercise, assert_can_manage_acl, assert_can_manage_relations,
)
from exercises.infrastructure.repository import ExerciseRepository


class CreateExercise:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, actor_role: RoleLabel, actor_id: UUID, actor_org_id: Optional[UUID],
                name: str, session_phase: str, primary_objective: str, physical_load: str,
                space_required: str, skill_level: str, complexity: int, min_athletes: int,
                max_athletes: int, estimated_duration_minutes: int, age_categories: List[str],
                description: Optional[str] = None, instructions: Optional[str] = None,
                coaching_cues: Optional[str] = None, safety_notes: Optional[str] = None,
                secondary_objective: Optional[str] = None, game_phases: Optional[List[str]] = None,
                materials: Optional[List[str]] = None, visibility_mode: str = "RESTRICTED") -> Exercise:
        assert_can_create_exercise(actor_role)
        exercise_id = uuid4()
        version_id = uuid4()
        version = ExerciseVersion(
            id=version_id, exercise_id=exercise_id, version_number=1,
            name=name, description=description, instructions=instructions,
            coaching_cues=coaching_cues, safety_notes=safety_notes,
            session_phase=session_phase, primary_objective=primary_objective,
            secondary_objective=secondary_objective, game_phases=list(game_phases or []),
            age_categories=list(age_categories), skill_level=skill_level, complexity=complexity,
            physical_load=physical_load, min_athletes=min_athletes, max_athletes=max_athletes,
            estimated_duration_minutes=estimated_duration_minutes, space_required=space_required,
            materials=list(materials or []), change_reason="Initial version",
            created_by_user_id=actor_id,
        )
        version.validate_invariants()
        exercise = Exercise(
            id=exercise_id, scope="ORG", organization_id=actor_org_id,
            created_by_user_id=actor_id, current_version_id=version_id,
            visibility_mode=visibility_mode, editorial_status="ACTIVE",
        )
        exercise.validate_invariants()
        saved_version = self._repo.save_version(version)
        exercise.current_version = saved_version
        return self._repo.save(exercise)


class ListExercises:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, actor_role: RoleLabel, actor_id: UUID, actor_org_id: Optional[UUID],
                scope: Optional[str] = None, session_phase: Optional[str] = None,
                primary_objective: Optional[str] = None, physical_load: Optional[str] = None,
                space_required: Optional[str] = None, skill_level: Optional[str] = None,
                page: int = 1, page_size: int = 50) -> tuple:
        items, total = self._repo.list_exercises(
            scope=scope, session_phase=session_phase, primary_objective=primary_objective,
            physical_load=physical_load, space_required=space_required, skill_level=skill_level,
            page=page, page_size=page_size,
        )
        # Filter by visibility
        if actor_role != RoleLabel.ADMIN:
            visible = []
            for ex in items:
                acl_ids = self._repo.get_acl_user_ids(ex.id) if ex.scope == "ORG" else []
                if can_read_exercise(actor_role, actor_id, ex.scope, ex.visibility_mode,
                                     ex.organization_id, actor_org_id, ex.created_by_user_id, acl_ids):
                    visible.append(ex)
            return visible, len(visible)
        return items, total


class GetExercise:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID,
                actor_org_id: Optional[UUID]) -> Exercise:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None or exercise.is_deleted:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        acl_ids = self._repo.get_acl_user_ids(exercise_id) if exercise.scope == "ORG" else []
        if not can_read_exercise(actor_role, actor_id, exercise.scope, exercise.visibility_mode,
                                  exercise.organization_id, actor_org_id, exercise.created_by_user_id, acl_ids):
            raise InsufficientPrivilege("Sem acesso a este exercicio")
        return exercise


class UpdateExercise:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID, change_reason: str,
                **kwargs) -> Exercise:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None or exercise.is_deleted:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        assert_can_modify_exercise(actor_role, actor_id, exercise.scope, exercise.created_by_user_id)
        current = exercise.current_version
        new_version_number = self._repo.get_max_version_number(exercise_id) + 1
        new_version = ExerciseVersion(
            id=uuid4(), exercise_id=exercise_id, version_number=new_version_number,
            name=kwargs.get("name") or current.name,
            session_phase=kwargs.get("session_phase") or current.session_phase,
            primary_objective=kwargs.get("primary_objective") or current.primary_objective,
            physical_load=kwargs.get("physical_load") or current.physical_load,
            space_required=kwargs.get("space_required") or current.space_required,
            skill_level=kwargs.get("skill_level") or current.skill_level,
            complexity=kwargs.get("complexity") if kwargs.get("complexity") is not None else current.complexity,
            min_athletes=kwargs.get("min_athletes") if kwargs.get("min_athletes") is not None else current.min_athletes,
            max_athletes=kwargs.get("max_athletes") if kwargs.get("max_athletes") is not None else current.max_athletes,
            estimated_duration_minutes=kwargs.get("estimated_duration_minutes") if kwargs.get("estimated_duration_minutes") is not None else current.estimated_duration_minutes,
            age_categories=list(kwargs.get("age_categories") or current.age_categories),
            description=kwargs.get("description", current.description),
            instructions=kwargs.get("instructions", current.instructions),
            coaching_cues=kwargs.get("coaching_cues", current.coaching_cues),
            safety_notes=kwargs.get("safety_notes", current.safety_notes),
            secondary_objective=kwargs.get("secondary_objective", current.secondary_objective),
            game_phases=list(kwargs.get("game_phases") or current.game_phases),
            materials=list(kwargs.get("materials") or current.materials),
            change_reason=change_reason, created_by_user_id=actor_id,
        )
        new_version.validate_invariants()
        saved_v = self._repo.save_version(new_version)
        exercise.current_version_id = saved_v.id
        exercise.current_version = saved_v
        return self._repo.save(exercise)


class DeleteExercise:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID) -> None:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None or exercise.is_deleted:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        assert_can_delete_exercise(actor_role, actor_id, exercise.scope, exercise.created_by_user_id)
        exercise.is_deleted = True
        exercise.deleted_at = datetime.now(timezone.utc)
        self._repo.save(exercise)


class CopyExerciseToOrg:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID,
                actor_org_id: Optional[UUID]) -> Exercise:
        assert_can_create_exercise(actor_role)
        original = self._repo.get_by_id(exercise_id)
        if original is None or original.is_deleted:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        src = original.current_version
        new_ex_id = uuid4()
        new_ver_id = uuid4()
        version = ExerciseVersion(
            id=new_ver_id, exercise_id=new_ex_id, version_number=1,
            name=src.name, description=src.description, instructions=src.instructions,
            coaching_cues=src.coaching_cues, safety_notes=src.safety_notes,
            session_phase=src.session_phase, primary_objective=src.primary_objective,
            secondary_objective=src.secondary_objective, game_phases=list(src.game_phases),
            age_categories=list(src.age_categories), skill_level=src.skill_level,
            complexity=src.complexity, physical_load=src.physical_load,
            min_athletes=src.min_athletes, max_athletes=src.max_athletes,
            estimated_duration_minutes=src.estimated_duration_minutes,
            space_required=src.space_required, materials=list(src.materials),
            change_reason="Copiado de exercicio SYSTEM", created_by_user_id=actor_id,
        )
        exercise = Exercise(
            id=new_ex_id, scope="ORG", organization_id=actor_org_id,
            created_by_user_id=actor_id, current_version_id=new_ver_id,
            visibility_mode="RESTRICTED", editorial_status="ACTIVE",
        )
        exercise.validate_invariants()
        self._repo.save_version(version)
        return self._repo.save(exercise)


class ListExerciseVersions:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID,
                actor_org_id: Optional[UUID]) -> list:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        acl_ids = self._repo.get_acl_user_ids(exercise_id) if exercise.scope == "ORG" else []
        if not can_read_exercise(actor_role, actor_id, exercise.scope, exercise.visibility_mode,
                                  exercise.organization_id, actor_org_id, exercise.created_by_user_id, acl_ids):
            raise InsufficientPrivilege("Sem acesso")
        return self._repo.list_versions(exercise_id)


class GetExerciseVersion:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, version_id: UUID, actor_role: RoleLabel,
                actor_id: UUID, actor_org_id: Optional[UUID]) -> ExerciseVersion:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        acl_ids = self._repo.get_acl_user_ids(exercise_id) if exercise.scope == "ORG" else []
        if not can_read_exercise(actor_role, actor_id, exercise.scope, exercise.visibility_mode,
                                  exercise.organization_id, actor_org_id, exercise.created_by_user_id, acl_ids):
            raise InsufficientPrivilege("Sem acesso")
        version = self._repo.get_version(version_id)
        if version is None:
            raise ExerciseNotFound(f"Versao {version_id} nao encontrada")
        return version


class ListExerciseRelations:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID,
                actor_org_id: Optional[UUID]) -> list:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        acl_ids = self._repo.get_acl_user_ids(exercise_id) if exercise.scope == "ORG" else []
        if not can_read_exercise(actor_role, actor_id, exercise.scope, exercise.visibility_mode,
                                  exercise.organization_id, actor_org_id, exercise.created_by_user_id, acl_ids):
            raise InsufficientPrivilege("Sem acesso")
        return self._repo.list_relations(exercise_id)


class AddExerciseRelation:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, from_exercise_id: UUID, to_exercise_id: UUID, relation_type: str,
                actor_role: RoleLabel, actor_id: UUID) -> ExerciseRelation:
        from_exercise = self._repo.get_by_id(from_exercise_id)
        if from_exercise is None:
            raise ExerciseNotFound(f"Exercicio {from_exercise_id} nao encontrado")
        assert_can_manage_relations(actor_role, actor_id, from_exercise.created_by_user_id)
        rel = ExerciseRelation(
            id=uuid4(), from_exercise_id=from_exercise_id, to_exercise_id=to_exercise_id,
            relation_type=relation_type, created_by_user_id=actor_id,
        )
        rel.validate_invariants()
        return self._repo.save_relation(rel)


class DeleteExerciseRelation:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, from_exercise_id: UUID, to_exercise_id: UUID, relation_type: str,
                actor_role: RoleLabel, actor_id: UUID) -> None:
        from_exercise = self._repo.get_by_id(from_exercise_id)
        if from_exercise is None:
            raise ExerciseNotFound(f"Exercicio {from_exercise_id} nao encontrado")
        assert_can_manage_relations(actor_role, actor_id, from_exercise.created_by_user_id)
        self._repo.delete_relation(from_exercise_id, to_exercise_id, relation_type)


class GetExerciseACL:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, actor_role: RoleLabel, actor_id: UUID) -> list:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        assert_can_manage_acl(actor_role, actor_id, exercise.scope, exercise.created_by_user_id, exercise.visibility_mode)
        return self._repo.list_acl(exercise_id)


class AddExerciseACLEntry:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, user_id: UUID, actor_role: RoleLabel,
                actor_id: UUID, actor_org_id: Optional[UUID]) -> ExerciseACL:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        assert_can_manage_acl(actor_role, actor_id, exercise.scope, exercise.created_by_user_id, exercise.visibility_mode)
        # INV-EXB-011: user in same org
        if exercise.organization_id != actor_org_id:
            raise ExerciseConflict("Usuario deve pertencer a mesma organizacao do exercicio")
        acl_entry = ExerciseACL(id=uuid4(), exercise_id=exercise_id, user_id=user_id, created_by_user_id=actor_id)
        return self._repo.add_acl_entry(acl_entry)


class RemoveExerciseACLEntry:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def execute(self, exercise_id: UUID, user_id: UUID, actor_role: RoleLabel, actor_id: UUID) -> None:
        exercise = self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ExerciseNotFound(f"Exercicio {exercise_id} nao encontrado")
        assert_can_manage_acl(actor_role, actor_id, exercise.scope, exercise.created_by_user_id, exercise.visibility_mode)
        # INV-EXB-009: criador nao pode ser removido
        if user_id == exercise.created_by_user_id:
            raise ExerciseConflict("Criador nao pode ser removido da ACL")
        self._repo.remove_acl_entry(exercise_id, user_id)
