from django.db import models
import uuid


class ExerciseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.CharField(max_length=20)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_by_user_id = models.UUIDField(db_index=True)
    current_version_id = models.UUIDField(null=True, blank=True)
    visibility_mode = models.CharField(max_length=20, default="RESTRICTED")
    editorial_status = models.CharField(max_length=20, default="ACTIVE")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "exercises"
        db_table = "exercise"
        ordering = ["-created_at"]


class ExerciseVersionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise_id = models.UUIDField(db_index=True)
    version_number = models.IntegerField()
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    coaching_cues = models.CharField(max_length=1000, null=True, blank=True)
    safety_notes = models.CharField(max_length=500, null=True, blank=True)
    session_phase = models.CharField(max_length=30)
    primary_objective = models.CharField(max_length=30)
    secondary_objective = models.CharField(max_length=30, null=True, blank=True)
    game_phases = models.JSONField(default=list)
    age_categories = models.JSONField(default=list)
    skill_level = models.CharField(max_length=20)
    complexity = models.IntegerField()
    physical_load = models.CharField(max_length=20)
    min_athletes = models.IntegerField()
    max_athletes = models.IntegerField()
    estimated_duration_minutes = models.IntegerField()
    space_required = models.CharField(max_length=20)
    materials = models.JSONField(default=list)
    change_reason = models.CharField(max_length=500, null=True, blank=True)
    created_by_user_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "exercises"
        db_table = "exercise_version"
        unique_together = [("exercise_id", "version_number")]
        ordering = ["exercise_id", "-version_number"]


class ExerciseRelationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_exercise_id = models.UUIDField(db_index=True)
    to_exercise_id = models.UUIDField(db_index=True)
    relation_type = models.CharField(max_length=30)
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "exercises"
        db_table = "exercise_relation"
        unique_together = [("from_exercise_id", "to_exercise_id", "relation_type")]


class ExerciseACLModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise_id = models.UUIDField(db_index=True)
    user_id = models.UUIDField()
    created_by_user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "exercises"
        db_table = "exercise_acl"
        unique_together = [("exercise_id", "user_id")]
