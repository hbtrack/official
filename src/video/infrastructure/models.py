"""
Django ORM models do módulo video.
Alinhados com: contracts/schemas/video/
ADR-031: Django ORM + Django Migrations
"""
import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class MatchMediaSessionModel(models.Model):
    """
    ORM: MatchMediaSession — agregado raiz do módulo video.
    Schema canônico: contracts/schemas/video/match_media_session.schema.json
    """
    STATE_CHOICES = [
        ("DRAFT", "DRAFT"),
        ("CAPTURING", "CAPTURING"),
        ("SYNCING", "SYNCING"),
        ("TRANSCODING", "TRANSCODING"),
        ("PUBLISHED", "PUBLISHED"),
    ]
    CAPTURE_MODE_CHOICES = [
        ("PANORAMIC", "PANORAMIC"),
        ("AUTO_FOLLOW", "AUTO_FOLLOW"),
        ("MULTI_ANGLE", "MULTI_ANGLE"),
    ]
    RETENTION_POLICY_CHOICES = [
        ("KEEP_7_DAYS", "KEEP_7_DAYS"),
        ("KEEP_30_DAYS", "KEEP_30_DAYS"),
        ("KEEP_90_DAYS", "KEEP_90_DAYS"),
        ("ARCHIVE_S3", "ARCHIVE_S3"),
        ("PUBLIC_FOREVER", "PUBLIC_FOREVER"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match_id = models.UUIDField(db_index=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="DRAFT", db_index=True)
    capture_mode = models.CharField(max_length=20, choices=CAPTURE_MODE_CHOICES)
    retention_policy = models.CharField(max_length=20, choices=RETENTION_POLICY_CHOICES, default="KEEP_7_DAYS")
    last_timecode = models.BigIntegerField(default=0)
    technical_contact_user_id = models.UUIDField(null=True, blank=True)
    created_by_user_id = models.UUIDField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "video_match_media_sessions"
        app_label = "video"

    def __str__(self) -> str:
        return f"MatchMediaSession({self.id}, match={self.match_id}, state={self.state})"


class MediaSegmentModel(models.Model):
    """
    ORM: MediaSegment — segmento imutável de mídia capturado pelo edge node.
    Schema canônico: contracts/schemas/video/media_segment.schema.json
    DR-VID-005: Imutável após FINALIZED (enforçado na camada domain/rules.py).
    """
    STATE_CHOICES = [
        ("OPEN", "OPEN"),
        ("FINALIZED", "FINALIZED"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        MatchMediaSessionModel,
        on_delete=models.CASCADE,
        related_name="segments",
        db_column="session_id",
    )
    timecode_logical = models.BigIntegerField(db_index=True)
    timecode_label = models.CharField(max_length=60)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="OPEN", db_index=True)
    codec_label = models.CharField(max_length=60, null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    source_edge_node_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "video_media_segments"
        app_label = "video"
        # DR-VID-001: timecode único por sessão (INV-VID-001)
        unique_together = [("session", "timecode_logical")]

    def __str__(self) -> str:
        return f"MediaSegment({self.id}, tc={self.timecode_logical}, state={self.state})"


class ClipDefinitionModel(models.Model):
    """
    ORM: ClipDefinition — recorte semântico de vídeo.
    Schema canônico: contracts/schemas/video/clip_definition.schema.json
    INV-VID-005: Exige ao menos um contexto semântico (enforçado em domain/entities.py).
    DR-VID-012: Idempotência por clip_id.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        MatchMediaSessionModel,
        on_delete=models.CASCADE,
        related_name="clips",
        db_column="session_id",
    )
    from_timecode = models.BigIntegerField()
    to_timecode = models.BigIntegerField()
    scout_event_id = models.UUIDField(null=True, blank=True, db_index=True)
    zone_label = models.CharField(max_length=80, null=True, blank=True, db_index=True)
    athlete_ids = ArrayField(models.UUIDField(), default=list, blank=True)
    context_label = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_user_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "video_clip_definitions"
        app_label = "video"

    def __str__(self) -> str:
        return f"ClipDefinition({self.id}, {self.from_timecode}→{self.to_timecode})"


class DistributionProfileModel(models.Model):
    """
    ORM: DistributionProfile — perfil de transcodificação e distribuição.
    Schema canônico: contracts/schemas/video/distribution_profile.schema.json
    DR-VID-002: Dual pipeline (técnico + público).
    DR-VID-009: Toda distribuição é auditada.
    """
    TARGET_TYPE_CHOICES = [
        ("TECHNICAL_INTERNAL", "TECHNICAL_INTERNAL"),
        ("PUBLIC_CDN", "PUBLIC_CDN"),
        ("BROADCAST_PARTNER", "BROADCAST_PARTNER"),
    ]
    CODEC_CHOICES = [
        ("H264", "H264"),
        ("H265", "H265"),
        ("VP9", "VP9"),
        ("AV1", "AV1"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        MatchMediaSessionModel,
        on_delete=models.CASCADE,
        related_name="distributions",
        db_column="session_id",
        null=True,
        blank=True,
    )
    profile_label = models.CharField(max_length=80)
    target_type = models.CharField(max_length=30, choices=TARGET_TYPE_CHOICES, db_index=True)
    codec_label = models.CharField(max_length=10, choices=CODEC_CHOICES)
    bitrate = models.IntegerField()
    published_at = models.DateTimeField(null=True, blank=True)
    published_by_user_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_distribution_profiles"
        app_label = "video"

    def __str__(self) -> str:
        return f"DistributionProfile({self.id}, {self.target_type}, {self.codec_label})"
