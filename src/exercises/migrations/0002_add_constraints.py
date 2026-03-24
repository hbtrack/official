"""
Constraints de integridade — módulo exercises.
INV-EXB: enums de scope, visibility_mode, editorial_status, session_phase,
          primary/secondary_objective, physical_load, space_required, skill_level,
          complexity [1-5], min_athletes [1-50], max_athletes [1-50],
          relation_type.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exercises", "0001_initial"),
    ]

    operations = [
        # ExerciseModel.scope
        migrations.AddConstraint(
            model_name="exercisemodel",
            constraint=models.CheckConstraint(
                check=models.Q(scope__in=["SYSTEM", "ORG"]),
                name="exercises_exercise_scope_valid",
            ),
        ),
        # ExerciseModel.visibility_mode
        migrations.AddConstraint(
            model_name="exercisemodel",
            constraint=models.CheckConstraint(
                check=models.Q(visibility_mode__in=["RESTRICTED", "ORG_WIDE"]),
                name="exercises_exercise_visibility_mode_valid",
            ),
        ),
        # ExerciseModel.editorial_status
        migrations.AddConstraint(
            model_name="exercisemodel",
            constraint=models.CheckConstraint(
                check=models.Q(editorial_status__in=["DRAFT", "ACTIVE", "ARCHIVED"]),
                name="exercises_exercise_editorial_status_valid",
            ),
        ),
        # ExerciseVersionModel.session_phase
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(session_phase__in=[
                    "WARMUP", "ACTIVATION", "TECHNICAL",
                    "DECISION_MAKING", "TACTICAL", "REDUCED_GAME", "COOLDOWN",
                ]),
                name="exercises_version_session_phase_valid",
            ),
        ),
        # ExerciseVersionModel.primary_objective
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(primary_objective__in=[
                    "TECHNICAL", "TACTICAL", "PHYSICAL", "DECISION_MAKING", "MIXED"
                ]),
                name="exercises_version_primary_objective_valid",
            ),
        ),
        # ExerciseVersionModel.physical_load
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(physical_load__in=["LOW", "MEDIUM", "HIGH", "MAXIMUM"]),
                name="exercises_version_physical_load_valid",
            ),
        ),
        # ExerciseVersionModel.space_required
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(space_required__in=[
                    "HALF_COURT", "FULL_COURT", "REDUCED_AREA", "NO_COURT"
                ]),
                name="exercises_version_space_required_valid",
            ),
        ),
        # ExerciseVersionModel.skill_level
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(skill_level__in=[
                    "BEGINNER", "INTERMEDIATE", "ADVANCED", "ELITE"
                ]),
                name="exercises_version_skill_level_valid",
            ),
        ),
        # ExerciseVersionModel.complexity [1-5] (INV-EXB-015)
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(complexity__gte=1, complexity__lte=5),
                name="exercises_version_complexity_range",
            ),
        ),
        # ExerciseVersionModel.min_athletes >= 1
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(min_athletes__gte=1),
                name="exercises_version_min_athletes_positive",
            ),
        ),
        # ExerciseVersionModel.max_athletes <= 50
        migrations.AddConstraint(
            model_name="exerciseversionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(max_athletes__lte=50),
                name="exercises_version_max_athletes_cap",
            ),
        ),
        # ExerciseRelationModel.relation_type
        migrations.AddConstraint(
            model_name="exerciserelationmodel",
            constraint=models.CheckConstraint(
                check=models.Q(relation_type__in=[
                    "PROGRESSION", "REGRESSION", "VARIATION", "CONTRAINDICATION"
                ]),
                name="exercises_relation_type_valid",
            ),
        ),
    ]
