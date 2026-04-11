#!/usr/bin/env python3
"""
4C.2.2D — Enum remediation script.

Actions:
1. Convert single-value enum fields to const: (removes cross-spec violation)
2. Add x-domain-enum-ref annotations to multi-value enum fields

Usage: python3 scripts/remediate_4c2_2d_enums.py
"""
import json
import pathlib
import yaml

ROOT = pathlib.Path('/home/davis/HB-TRACK')

# ──────────────────────────────────────────────────────────────────────────────
# CONST CONVERSIONS — single-value enums → const: (removes the violation cleanly)
# Format: (relative_file_path, dot-path to field)
# ──────────────────────────────────────────────────────────────────────────────
CONST_CONVERSIONS = [
    # eventType discriminators
    ("contracts/asyncapi/components/schemas/athlete_ineligible_for_prescription_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/attention_queue_item_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/attention_queue_item_resolved_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/coach_intervention_required_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/completion_evidence_provided_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/continuity_snapshot_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/execution_recorded_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/feedback_thread_closed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/feedback_thread_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/intervention_cycle_completed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/intervention_cycle_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/match_scheduled_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/need_detected_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/need_linked_to_objective_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/notification_delivery_failed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/notification_delivery_queued_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/notification_delivery_sent_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/objective_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/prescription_adjusted_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/recommendation_accepted_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/recommendation_dismissed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/recommendation_generated_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/session_adjustment_made_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/session_objective_achieved_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_readiness_assessed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_archived_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_cancelled_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_completed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_created_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_published_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/training_session_started_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/capture_started_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/distribution_failed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/distribution_published_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/segment_ready_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/sync_adjustment_applied_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/video/transcode_completed_payload.yaml", "properties.eventType"),
    ("contracts/asyncapi/components/schemas/wellness_entry_created_payload.yaml", "properties.eventType"),
    # statusLabel single-value
    ("contracts/asyncapi/components/schemas/ai_ingestion_job_completed_payload.yaml", "properties.statusLabel"),
    ("contracts/asyncapi/components/schemas/ai_ingestion_job_failed_payload.yaml", "properties.statusLabel"),
    ("contracts/asyncapi/components/schemas/ai_ingestion_job_queued_payload.yaml", "properties.statusLabel"),
    ("contracts/asyncapi/components/schemas/competition_created_payload.yaml", "properties.statusLabel"),
    ("contracts/asyncapi/components/schemas/season_created_payload.yaml", "properties.statusLabel"),
    ("contracts/asyncapi/components/schemas/match_scheduled_payload.yaml", "properties.statusLabel"),
    # deliveryStatusLabel single-value
    ("contracts/asyncapi/components/schemas/notification_delivery_failed_payload.yaml", "properties.deliveryStatusLabel"),
    ("contracts/asyncapi/components/schemas/notification_delivery_queued_payload.yaml", "properties.deliveryStatusLabel"),
    ("contracts/asyncapi/components/schemas/notification_delivery_sent_payload.yaml", "properties.deliveryStatusLabel"),
    # status single-value training session payloads
    ("contracts/asyncapi/components/schemas/training_session_archived_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/training_session_cancelled_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/training_session_completed_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/training_session_created_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/training_session_started_payload.yaml", "properties.status"),
    # other single-value
    ("contracts/asyncapi/components/schemas/recommendation_generated_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/attention_queue_item_created_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/feedback_thread_closed_payload.yaml", "properties.status"),
    ("contracts/asyncapi/components/schemas/video/segment_ready_payload.yaml", "properties.state"),
    ("contracts/asyncapi/components/schemas/video/sync_adjustment_applied_payload.yaml", "properties.adjustedByScoutSync"),
]

# ──────────────────────────────────────────────────────────────────────────────
# ENUM-REF ADDITIONS — add x-domain-enum-ref: canonical_name
# Format: (relative_file_path, dot-path to field, canonical_enum_name)
# ──────────────────────────────────────────────────────────────────────────────
ENUM_REF_ADDITIONS = [
    # adjustmentReason
    ("contracts/asyncapi/components/schemas/prescription_adjusted_payload.yaml", "properties.adjustmentReason", "prescription_adjustment_reason"),
    # adjustmentType
    ("contracts/asyncapi/components/schemas/session_adjustment_made_payload.yaml", "properties.adjustmentType", "session_adjustment_type"),
    # aggregationType
    ("contracts/openapi/components/schemas/analytics/analytics_snapshot.yaml", "properties.aggregationType", "analytics_aggregation_type"),
    # athleteAgeGroup
    ("contracts/schemas/training/athlete_chat_conversation.schema.json", "properties.athleteAgeGroup", "athlete_age_group"),
    # attention_queue_status (status in resolved payload)
    ("contracts/asyncapi/components/schemas/attention_queue_item_resolved_payload.yaml", "properties.status", "attention_queue_status"),
    # captureMode
    ("contracts/asyncapi/components/schemas/video/capture_started_payload.yaml", "properties.captureMode", "video_capture_mode"),
    ("contracts/asyncapi/components/schemas/video_session_created_payload.yaml", "properties.captureMode", "video_capture_mode"),
    ("contracts/openapi/components/schemas/video/match_media_session.yaml", "properties.captureMode", "video_capture_mode"),
    ("contracts/schemas/video/match_media_session.schema.json", "properties.captureMode", "video_capture_mode"),
    # changeTypeLabel
    ("contracts/asyncapi/components/schemas/team_roster_updated_payload.yaml", "properties.changeTypeLabel", "team_roster_change_type"),
    # channelLabel
    ("contracts/asyncapi/components/schemas/notification_delivery_failed_payload.yaml", "properties.channelLabel", "notification_channel"),
    ("contracts/asyncapi/components/schemas/notification_delivery_queued_payload.yaml", "properties.channelLabel", "notification_channel"),
    ("contracts/asyncapi/components/schemas/notification_delivery_sent_payload.yaml", "properties.channelLabel", "notification_channel"),
    # codec (lowercase codec key)
    ("contracts/asyncapi/components/schemas/video/segment_ready_payload.yaml", "properties.codec", "video_codec_key"),
    # codecLabel (display label)
    ("contracts/asyncapi/components/schemas/video/transcode_completed_payload.yaml", "properties.codecLabel", "video_codec_label"),
    ("contracts/asyncapi/components/schemas/video/distribution_published_payload.yaml", "properties.availableRenditions.items.properties.codecLabel", "video_codec_label"),
    ("contracts/openapi/components/schemas/video/distribution_profile.yaml", "properties.codecLabel", "video_codec_label"),
    ("contracts/schemas/video/distribution_profile.schema.json", "properties.codecLabel", "video_codec_label"),
    # completionStatus (intervention)
    ("contracts/asyncapi/components/schemas/intervention_cycle_completed_payload.yaml", "properties.completionStatus", "intervention_completion_status"),
    # contextType
    ("contracts/asyncapi/components/schemas/feedback_thread_created_payload.yaml", "properties.contextType", "feedback_context_type"),
    # conversationOutcome
    ("contracts/asyncapi/components/schemas/feedback_thread_closed_payload.yaml", "properties.conversationOutcome", "feedback_conversation_outcome"),
    # decision
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.approvalResponse.properties.decision", "training_suggestion_decision"),
    ("contracts/schemas/training/training_suggestion_approval.schema.json", "properties.decision", "training_suggestion_decision"),
    # destinationType
    ("contracts/asyncapi/components/schemas/video_distribution_published_payload.yaml", "properties.destinationType", "video_destination_type"),
    # evidenceType
    ("contracts/asyncapi/components/schemas/completion_evidence_provided_payload.yaml", "properties.evidenceType", "completion_evidence_type"),
    # executionType
    ("contracts/asyncapi/components/schemas/execution_recorded_payload.yaml", "properties.executionType", "execution_type"),
    # failureReason (video)
    ("contracts/asyncapi/components/schemas/video/distribution_failed_payload.yaml", "properties.failureReason", "video_distribution_failure_reason"),
    # failureReasonLabel (notification)
    ("contracts/asyncapi/components/schemas/notification_delivery_failed_payload.yaml", "properties.failureReasonLabel", "notification_failure_reason"),
    # ineligibilityReason
    ("contracts/asyncapi/components/schemas/athlete_ineligible_for_prescription_payload.yaml", "properties.ineligibilityReason", "ineligibility_reason"),
    # initiatedFromScreen (nested)
    ("contracts/schemas/training/athlete_chat_conversation.schema.json", "properties.context.properties.initiatedFromScreen", "chat_context_screen"),
    # interventionType
    ("contracts/asyncapi/components/schemas/coach_intervention_required_payload.yaml", "properties.interventionType", "intervention_type"),
    # itemType (attention queue)
    ("contracts/asyncapi/components/schemas/attention_queue_item_created_payload.yaml", "properties.itemType", "attention_queue_item_type"),
    # messageType
    ("contracts/schemas/training/athlete_chat_message.schema.json", "properties.messageType", "chat_message_type"),
    # mode (load chart)
    ("contracts/openapi/components/schemas/training/load_chart.yaml", "properties.mode", "load_chart_mode"),
    ("contracts/schemas/training/load_chart.schema.json", "properties.mode", "load_chart_mode"),
    # newRoleLabel / previousRoleLabel / roleLabel / roleLabels
    ("contracts/asyncapi/components/schemas/user_role_changed_payload.yaml", "properties.newRoleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/user_role_changed_payload.yaml", "properties.previousRoleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/role_assigned_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/role_revoked_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/user_created_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/openapi/components/schemas/users/user_profile.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/session_created_payload.yaml", "properties.roleLabels.items", "user_role_label"),
    # newStatus / previousStatus (match)
    ("contracts/asyncapi/components/schemas/match_status_updated_payload.yaml", "properties.newStatus", "match_phase_label"),
    ("contracts/asyncapi/components/schemas/match_status_updated_payload.yaml", "properties.previousStatus", "match_phase_label"),
    # notificationChannels items
    ("contracts/schemas/training/training_suggestion_approval.schema.json", "properties.notificationChannels.items", "notification_channel"),
    # objectives items
    ("contracts/schemas/training/athlete_chat_message.schema.json", "properties.suggestedTraining.properties.objectives.items", "training_objective_category"),
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.objectives.items", "training_objective_category"),
    # origin (need vs objective)
    ("contracts/asyncapi/components/schemas/need_detected_created_payload.yaml", "properties.origin", "need_origin"),
    ("contracts/asyncapi/components/schemas/objective_created_payload.yaml", "properties.origin", "objective_origin_label"),
    # outcomeLabel
    ("contracts/asyncapi/components/schemas/audit_entry_created_payload.yaml", "properties.outcomeLabel", "audit_outcome_label"),
    ("contracts/asyncapi/components/schemas/audit_entry_security_flagged_payload.yaml", "properties.outcomeLabel", "audit_outcome_label"),
    # previousStatusLabel
    ("contracts/asyncapi/components/schemas/competition_phase_changed_payload.yaml", "properties.previousStatusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/season_status_updated_payload.yaml", "properties.previousStatusLabel", "entity_lifecycle_status"),
    # range (load chart)
    ("contracts/openapi/components/schemas/training/load_chart.yaml", "properties.range", "load_chart_range"),
    ("contracts/schemas/training/load_chart.schema.json", "properties.range", "load_chart_range"),
    # readinessCategory
    ("contracts/asyncapi/components/schemas/training_readiness_assessed_payload.yaml", "properties.readinessCategory", "training_readiness_category"),
    # readinessTrend
    ("contracts/openapi/components/schemas/wellness/wellness_summary.yaml", "properties.readinessTrend", "wellness_readiness_trend"),
    # reason (training suggestion context)
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.context.properties.reason", "training_suggestion_reason"),
    # retentionPolicy
    ("contracts/asyncapi/components/schemas/video_distribution_published_payload.yaml", "properties.retentionPolicy", "video_retention_policy"),
    ("contracts/asyncapi/components/schemas/video_session_created_payload.yaml", "properties.retentionPolicy", "video_retention_policy"),
    ("contracts/asyncapi/components/schemas/video_session_published_payload.yaml", "properties.retentionPolicy", "video_retention_policy"),
    ("contracts/openapi/components/schemas/video/match_media_session.yaml", "properties.retentionPolicy", "video_retention_policy"),
    ("contracts/schemas/video/match_media_session.schema.json", "properties.retentionPolicy", "video_retention_policy"),
    # revocationReason
    ("contracts/asyncapi/components/schemas/session_revoked_payload.yaml", "properties.revocationReason", "session_revocation_reason"),
    # securitySeverityLabel
    ("contracts/asyncapi/components/schemas/audit_entry_security_flagged_payload.yaml", "properties.securitySeverityLabel", "security_severity_label"),
    # senderRole
    ("contracts/schemas/training/athlete_chat_message.schema.json", "properties.senderRole", "chat_sender_role"),
    # snapshotType
    ("contracts/asyncapi/components/schemas/continuity_snapshot_created_payload.yaml", "properties.snapshotType", "continuity_snapshot_type"),
    # state (video session)
    ("contracts/openapi/components/schemas/video/match_media_session.yaml", "properties.state", "video_session_state"),
    ("contracts/schemas/video/match_media_session.schema.json", "properties.state", "video_session_state"),
    # state (media segment)
    ("contracts/openapi/components/schemas/video/media_segment.yaml", "properties.state", "media_segment_state"),
    ("contracts/schemas/video/media_segment.schema.json", "properties.state", "media_segment_state"),
    # status (ai_ingestion job)
    ("contracts/openapi/components/schemas/ai_ingestion/ingestion_job.yaml", "properties.status", "ai_ingestion_job_status"),
    # status (training_suggestion OAS)
    ("contracts/openapi/components/schemas/training/training_suggestion.yaml", "properties.status", "training_suggestion_status"),
    # status (training_suggestion JSON)
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.status", "training_suggestion_status"),
    # status (chat_conversation)
    ("contracts/schemas/training/athlete_chat_conversation.schema.json", "properties.status", "chat_conversation_status"),
    # status training_session_published (2 values: PUBLISHED, SCHEDULED)
    ("contracts/asyncapi/components/schemas/training_session_published_payload.yaml", "properties.status", "training_state"),
    # statusLabel (competition/season/team active/archived/draft)
    ("contracts/asyncapi/components/schemas/competition_phase_changed_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/season_status_updated_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/team_created_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
    # statusLabel (match)
    ("contracts/asyncapi/components/schemas/match_status_updated_payload.yaml", "properties.statusLabel", "match_phase_label"),
    ("contracts/schemas/matches/match.schema.json", "properties.statusLabel", "match_phase_label"),
    # statusLabel (competition/season JSON)
    ("contracts/schemas/competitions/competition.schema.json", "properties.statusLabel", "entity_lifecycle_status"),
    ("contracts/schemas/seasons/season.schema.json", "properties.statusLabel", "entity_lifecycle_status"),
    # statusLabel (user)
    ("contracts/asyncapi/components/schemas/user_created_payload.yaml", "properties.statusLabel", "user_account_status"),
    ("contracts/openapi/components/schemas/users/user_profile.yaml", "properties.statusLabel", "user_account_status"),
    ("contracts/schemas/users/user_profile.schema.json", "properties.statusLabel", "user_account_status"),
    # targetType
    ("contracts/asyncapi/components/schemas/video/distribution_failed_payload.yaml", "properties.targetType", "video_target_type"),
    ("contracts/asyncapi/components/schemas/video/distribution_published_payload.yaml", "properties.targetType", "video_target_type"),
    ("contracts/openapi/components/schemas/video/distribution_profile.yaml", "properties.targetType", "video_target_type"),
    ("contracts/schemas/video/distribution_profile.schema.json", "properties.targetType", "video_target_type"),
    # timing
    ("contracts/asyncapi/components/schemas/coach_intervention_required_payload.yaml", "properties.timing", "intervention_timing"),
    # triggerType
    ("contracts/asyncapi/components/schemas/video_session_transcoding_payload.yaml", "properties.triggerType", "video_transcode_trigger"),
]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def parse_path(dot_path: str) -> list[str]:
    return dot_path.split(".")

def get_node(obj: dict, path_parts: list[str]):
    cur = obj
    for part in path_parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur

def set_node(obj: dict, path_parts: list[str], key: str, value):
    cur = obj
    for part in path_parts[:-1]:
        if not isinstance(cur, dict):
            return False
        cur = cur.get(part)
        if cur is None:
            return False
    if not isinstance(cur, dict):
        return False
    last = path_parts[-1]
    if last not in cur:
        return False
    target = cur[last]
    if not isinstance(target, dict):
        return False
    target[key] = value
    return True

def load_file(p: pathlib.Path):
    if p.suffix == ".json":
        return json.loads(p.read_text()), "json"
    else:
        return yaml.safe_load(p.read_text()), "yaml"

def save_file(p: pathlib.Path, obj, fmt: str):
    if fmt == "json":
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    else:
        p.write_text(yaml.dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False))

# ──────────────────────────────────────────────────────────────────────────────
# Apply const conversions
# ──────────────────────────────────────────────────────────────────────────────
print("=== CONST CONVERSIONS ===")
const_ok = 0
const_skip = 0
const_err = 0

for rel_path, dot_path in CONST_CONVERSIONS:
    p = ROOT / rel_path
    if not p.exists():
        print(f"  MISSING: {rel_path}")
        const_err += 1
        continue
    obj, fmt = load_file(p)
    path_parts = parse_path(dot_path)
    node = get_node(obj, path_parts)
    if node is None:
        print(f"  NOT_FOUND: {rel_path} @ {dot_path}")
        const_err += 1
        continue
    if not isinstance(node, dict):
        print(f"  NOT_DICT: {rel_path} @ {dot_path}")
        const_err += 1
        continue
    # Already converted?
    if "const" in node and "enum" not in node:
        const_skip += 1
        continue
    enum_val = node.get("enum")
    if not isinstance(enum_val, list) or len(enum_val) == 0:
        print(f"  NO_ENUM: {rel_path} @ {dot_path} (enum={enum_val})")
        const_skip += 1
        continue
    const_value = enum_val[0]
    # Replace enum with const
    node.pop("enum")
    node.pop("x-domain-enum-ref", None)  # remove if present (no longer needed for const)
    node["const"] = const_value
    save_file(p, obj, fmt)
    print(f"  OK const={repr(const_value)}: {rel_path.split('/')[-1]} @ {dot_path.split('.')[-1]}")
    const_ok += 1

print(f"\nConst conversions: {const_ok} done, {const_skip} skipped, {const_err} errors\n")

# ──────────────────────────────────────────────────────────────────────────────
# Apply enum-ref additions
# ──────────────────────────────────────────────────────────────────────────────
print("=== ENUM-REF ADDITIONS ===")
ref_ok = 0
ref_skip = 0
ref_err = 0

for rel_path, dot_path, enum_name in ENUM_REF_ADDITIONS:
    p = ROOT / rel_path
    if not p.exists():
        print(f"  MISSING: {rel_path}")
        ref_err += 1
        continue
    obj, fmt = load_file(p)
    path_parts = parse_path(dot_path)
    node = get_node(obj, path_parts)
    if node is None:
        print(f"  NOT_FOUND: {rel_path} @ {dot_path}")
        ref_err += 1
        continue
    if not isinstance(node, dict):
        print(f"  NOT_DICT: {rel_path} @ {dot_path}")
        ref_err += 1
        continue
    # Already has correct ref?
    if node.get("x-domain-enum-ref") == enum_name:
        ref_skip += 1
        continue
    node["x-domain-enum-ref"] = enum_name
    save_file(p, obj, fmt)
    print(f"  OK x-domain-enum-ref={enum_name}: {rel_path.split('/')[-1]} @ {dot_path.split('.')[-1]}")
    ref_ok += 1

print(f"\nEnum-ref additions: {ref_ok} done, {ref_skip} skipped, {ref_err} errors\n")
print("=== DONE ===")
