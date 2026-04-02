from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


VALID_SCOPE = frozenset({"SYSTEM", "ORG"})
VALID_SESSION_PHASE = frozenset({"WARMUP", "ACTIVATION", "TECHNICAL", "DECISION_MAKING", "TACTICAL", "REDUCED_GAME", "COOLDOWN"})
VALID_OBJECTIVE = frozenset({"TECHNICAL", "TACTICAL", "PHYSICAL", "DECISION_MAKING", "MIXED"})
VALID_PHYSICAL_LOAD = frozenset({"LOW", "MEDIUM", "HIGH", "MAXIMUM"})
VALID_SPACE = frozenset({"HALF_COURT", "FULL_COURT", "REDUCED_AREA", "NO_COURT"})
VALID_AGE_CATEGORY = frozenset({"SUB_12", "SUB_14", "SUB_16", "SUB_18", "ADULT"})
VALID_SKILL_LEVEL = frozenset({"BEGINNER", "INTERMEDIATE", "ADVANCED", "ELITE"})
VALID_GAME_PHASE = frozenset({"POSITIONAL_ATTACK", "POSITIONAL_DEFENSE", "OFFENSIVE_TRANSITION", "DEFENSIVE_TRANSITION", "SET_PIECE"})
VALID_VISIBILITY_MODE = frozenset({"RESTRICTED", "ORG_WIDE"})
VALID_RELATION_TYPE = frozenset({"PROGRESSION", "REGRESSION", "VARIATION", "CONTRAINDICATION"})
VALID_EDITORIAL_STATUS = frozenset({"DRAFT", "ACTIVE", "ARCHIVED"})

# Source-graph projection anchors for transport/persistence-only fields that
# are still materialized outside the core dataclasses in the legacy runtime:
# thumbnail_url, current_version_number, deletion_reason, notes.


@dataclass
class ExerciseVersion:
    id: UUID
    exercise_id: UUID
    version_number: int
    name: str
    session_phase: str
    primary_objective: str
    physical_load: str
    space_required: str
    skill_level: str
    complexity: int
    min_athletes: int
    max_athletes: int
    estimated_duration_minutes: int
    age_categories: List[str] = field(default_factory=list)
    description: Optional[str] = None
    instructions: Optional[str] = None
    coaching_cues: Optional[str] = None
    safety_notes: Optional[str] = None
    secondary_objective: Optional[str] = None
    game_phases: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    change_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by_user_id: Optional[UUID] = None

    def validate_invariants(self) -> None:
        # INV-EXB-015: complexity 1-5
        if not (1 <= self.complexity <= 5):
            raise ValueError("complexity deve estar entre 1 e 5")
        # INV-EXB-016: estimated_duration_minutes 1-180
        if not (1 <= self.estimated_duration_minutes <= 180):
            raise ValueError("estimatedDurationMinutes deve estar entre 1 e 180")
        # INV-EXB-003/004: athletes range
        if self.min_athletes < 1:
            raise ValueError("minAthletes deve ser >= 1")
        if self.max_athletes > 50:
            raise ValueError("maxAthletes deve ser <= 50")
        if self.max_athletes < self.min_athletes:
            raise ValueError("maxAthletes deve ser >= minAthletes")
        # enums
        if self.session_phase not in VALID_SESSION_PHASE:
            raise ValueError(f"sessionPhase invalido: {self.session_phase}")
        if self.primary_objective not in VALID_OBJECTIVE:
            raise ValueError(f"primaryObjective invalido: {self.primary_objective}")
        if self.physical_load not in VALID_PHYSICAL_LOAD:
            raise ValueError(f"physicalLoad invalido: {self.physical_load}")
        if self.space_required not in VALID_SPACE:
            raise ValueError(f"spaceRequired invalido: {self.space_required}")
        if self.skill_level not in VALID_SKILL_LEVEL:
            raise ValueError(f"skillLevel invalido: {self.skill_level}")
        if not self.age_categories:
            raise ValueError("ageCategories deve ter pelo menos 1 item")
        for ac in self.age_categories:
            if ac not in VALID_AGE_CATEGORY:
                raise ValueError(f"ageCategory invalido: {ac}")


@dataclass
class Exercise:
    id: UUID
    scope: str
    created_by_user_id: UUID
    current_version_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    visibility_mode: str = "RESTRICTED"
    editorial_status: str = "ACTIVE"
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    current_version: Optional[ExerciseVersion] = None

    def validate_invariants(self) -> None:
        # INV-EXB-001: scope
        if self.scope not in VALID_SCOPE:
            raise ValueError(f"scope invalido: {self.scope}")
        # INV-EXB-002: org constraint
        if self.scope == "ORG" and self.organization_id is None:
            raise ValueError("organization_id obrigatorio para scope=ORG")
        if self.scope == "SYSTEM" and self.organization_id is not None:
            raise ValueError("organization_id deve ser NULL para scope=SYSTEM")
        if self.visibility_mode not in VALID_VISIBILITY_MODE:
            raise ValueError(f"visibilityMode invalido: {self.visibility_mode}")


@dataclass
class ExerciseRelation:
    id: UUID
    from_exercise_id: UUID
    to_exercise_id: UUID
    relation_type: str
    created_by_user_id: UUID
    created_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        # INV-EXB-014: nao reflexiva
        if self.from_exercise_id == self.to_exercise_id:
            raise ValueError("Relacao reflexiva nao e permitida")
        # INV-EXB-013: type valido
        if self.relation_type not in VALID_RELATION_TYPE:
            raise ValueError(f"relationType invalido: {self.relation_type}")


@dataclass
class ExerciseACL:
    id: UUID
    exercise_id: UUID
    user_id: UUID
    created_by_user_id: UUID
    created_at: Optional[datetime] = None
