"""
Constraints de integridade — módulo video.
INV-VID: state FSM para MatchMediaSession e MediaSegment;
         capture_mode, retention_policy, target_type, codec_label (DistributionProfile).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video", "0001_initial"),
    ]

    operations = [
        # MatchMediaSessionModel — state
        migrations.AddConstraint(
            model_name="matchmediasessionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(state__in=[
                    "DRAFT", "CAPTURING", "SYNCING", "TRANSCODING", "PUBLISHED"
                ]),
                name="video_session_state_valid",
            ),
        ),
        # MatchMediaSessionModel — capture_mode
        migrations.AddConstraint(
            model_name="matchmediasessionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(capture_mode__in=[
                    "PANORAMIC", "AUTO_FOLLOW", "MULTI_ANGLE"
                ]),
                name="video_session_capture_mode_valid",
            ),
        ),
        # MatchMediaSessionModel — retention_policy
        migrations.AddConstraint(
            model_name="matchmediasessionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(retention_policy__in=[
                    "KEEP_7_DAYS", "KEEP_30_DAYS", "KEEP_90_DAYS",
                    "ARCHIVE_S3", "PUBLIC_FOREVER",
                ]),
                name="video_session_retention_policy_valid",
            ),
        ),
        # MediaSegmentModel — state
        migrations.AddConstraint(
            model_name="mediasegmentmodel",
            constraint=models.CheckConstraint(
                check=models.Q(state__in=["OPEN", "FINALIZED"]),
                name="video_segment_state_valid",
            ),
        ),
        # DistributionProfileModel — target_type
        migrations.AddConstraint(
            model_name="distributionprofilemodel",
            constraint=models.CheckConstraint(
                check=models.Q(target_type__in=[
                    "TECHNICAL_INTERNAL", "PUBLIC_CDN", "BROADCAST_PARTNER"
                ]),
                name="video_distribution_target_type_valid",
            ),
        ),
        # DistributionProfileModel — codec_label
        migrations.AddConstraint(
            model_name="distributionprofilemodel",
            constraint=models.CheckConstraint(
                check=models.Q(codec_label__in=["H264", "H265", "VP9", "AV1"]),
                name="video_distribution_codec_label_valid",
            ),
        ),
    ]
