from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from ninja import Schema
from exercises.domain.entities import Exercise, ExerciseVersion, ExerciseRelation, ExerciseACL


class ExerciseVersionOut(Schema):
    versionId: UUID
    exerciseId: UUID
    versionNumber: int
    name: str
    sessionPhase: str
    primaryObjective: str
    physicalLoad: str
    spaceRequired: str
    skillLevel: str
    complexity: int
    minAthletes: int
    maxAthletes: int
    estimatedDurationMinutes: int
    ageCategories: List[str]
    description: Optional[str] = None
    instructions: Optional[str] = None
    coachingCues: Optional[str] = None
    safetyNotes: Optional[str] = None
    secondaryObjective: Optional[str] = None
    gamePhases: List[str] = []
    materials: List[str] = []
    changeReason: Optional[str] = None

    @classmethod
    def from_domain(cls, v: ExerciseVersion):
        return cls(versionId=v.id, exerciseId=v.exercise_id, versionNumber=v.version_number,
            name=v.name, sessionPhase=v.session_phase, primaryObjective=v.primary_objective,
            physicalLoad=v.physical_load, spaceRequired=v.space_required, skillLevel=v.skill_level,
            complexity=v.complexity, minAthletes=v.min_athletes, maxAthletes=v.max_athletes,
            estimatedDurationMinutes=v.estimated_duration_minutes, ageCategories=v.age_categories,
            description=v.description, instructions=v.instructions, coachingCues=v.coaching_cues,
            safetyNotes=v.safety_notes, secondaryObjective=v.secondary_objective,
            gamePhases=v.game_phases or [], materials=v.materials or [], changeReason=v.change_reason)


class ExerciseOut(Schema):
    exerciseId: UUID
    scope: str
    visibilityMode: str
    editorialStatus: str
    createdByUserId: UUID
    organizationId: Optional[UUID] = None
    currentVersion: Optional[ExerciseVersionOut] = None

    @classmethod
    def from_domain(cls, e: Exercise):
        return cls(exerciseId=e.id, scope=e.scope, visibilityMode=e.visibility_mode,
            editorialStatus=e.editorial_status, createdByUserId=e.created_by_user_id,
            organizationId=e.organization_id,
            currentVersion=ExerciseVersionOut.from_domain(e.current_version) if e.current_version else None)


class ExercisePreviewOut(Schema):
    exerciseId: UUID
    name: str

    @classmethod
    def from_domain(cls, e: Exercise):
        name = e.current_version.name if e.current_version else ""
        return cls(exerciseId=e.id, name=name)


class ExerciseListOut(Schema):
    items: List[ExercisePreviewOut]
    page: int
    pageSize: int
    total: int


class CreateExerciseIn(Schema):
    name: str
    sessionPhase: str
    primaryObjective: str
    physicalLoad: str
    estimatedDurationMinutes: int
    spaceRequired: str
    ageCategories: List[str]
    skillLevel: str
    complexity: int
    minAthletes: int
    maxAthletes: int
    description: Optional[str] = None
    instructions: Optional[str] = None
    coachingCues: Optional[str] = None
    safetyNotes: Optional[str] = None
    secondaryObjective: Optional[str] = None
    gamePhases: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    visibilityMode: Optional[str] = "RESTRICTED"


class UpdateExerciseIn(Schema):
    changeReason: str
    name: Optional[str] = None
    sessionPhase: Optional[str] = None
    primaryObjective: Optional[str] = None
    physicalLoad: Optional[str] = None
    estimatedDurationMinutes: Optional[int] = None
    spaceRequired: Optional[str] = None
    ageCategories: Optional[List[str]] = None
    skillLevel: Optional[str] = None
    complexity: Optional[int] = None
    minAthletes: Optional[int] = None
    maxAthletes: Optional[int] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    coachingCues: Optional[str] = None
    safetyNotes: Optional[str] = None
    secondaryObjective: Optional[str] = None
    gamePhases: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    visibilityMode: Optional[str] = None


class DeleteExerciseIn(Schema):
    deletionReason: str


class ExerciseRelationOut(Schema):
    id: UUID
    fromExerciseId: UUID
    toExerciseId: UUID
    relationType: str

    @classmethod
    def from_domain(cls, r: ExerciseRelation):
        return cls(id=r.id, fromExerciseId=r.from_exercise_id,
            toExerciseId=r.to_exercise_id, relationType=r.relation_type)


class AddRelationIn(Schema):
    toExerciseId: UUID
    relationType: str


class ExerciseACLEntryOut(Schema):
    id: UUID
    exerciseId: UUID
    userId: UUID

    @classmethod
    def from_domain(cls, a: ExerciseACL):
        return cls(id=a.id, exerciseId=a.exercise_id, userId=a.user_id)


class AddACLEntryIn(Schema):
    userId: UUID


class ErrorOut(Schema):
    detail: str
