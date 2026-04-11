#!/usr/bin/env python3
"""
4C.2.2D — uppercase-conversion script.

1. Converts all new DOMAIN_AXIOMS enum values to UPPER_SNAKE_CASE
2. Updates all contract files that reference these enums to use the new uppercase values
"""
import json
import pathlib
import unicodedata
import yaml

ROOT = pathlib.Path('/home/davis/HB-TRACK')


def to_upper_snake(v: str) -> str:
    normalized = ''.join(c for c in unicodedata.normalize('NFD', str(v)) if unicodedata.category(c) != 'Mn')
    normalized = normalized.replace('.', '').replace('-', '_').replace(' ', '_')
    if normalized and normalized[0].isdigit():
        normalized = 'PERIOD_' + normalized.replace('d', 'D').upper()
    else:
        normalized = normalized.upper()
    return normalized


def load_file(p: pathlib.Path):
    if p.suffix == '.json':
        return json.loads(p.read_text()), 'json'
    return yaml.safe_load(p.read_text()), 'yaml'


def save_file(p: pathlib.Path, obj, fmt: str):
    if fmt == 'json':
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
    else:
        p.write_text(yaml.dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False))


def get_node(obj, path: str):
    cur = obj
    for part in path.split('.'):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


# ────────────────────────────────────────────────────────────────
# 1. Update DOMAIN_AXIOMS
# ────────────────────────────────────────────────────────────────
axioms_file = ROOT / '.contract_driven/DOMAIN_AXIOMS.json'
data = json.loads(axioms_file.read_text())
domain_enums = data['domain_axioms']['domain_enums']

NEW_ENUM_NAMES = [
    "ai_ingestion_job_status", "analytics_aggregation_type", "athlete_age_group",
    "attention_queue_status", "attention_queue_item_type", "audit_outcome_label",
    "chat_context_screen", "chat_conversation_status", "chat_message_type",
    "chat_sender_role", "completion_evidence_type", "continuity_snapshot_type",
    "entity_lifecycle_status", "feedback_conversation_outcome", "ineligibility_reason",
    "ineligibility_reason_flag", "intervention_completion_status", "intervention_timing",
    "intervention_type", "load_chart_mode", "load_chart_range", "match_phase_label",
    "media_segment_state", "need_origin", "notification_channel",
    "notification_delivery_status", "notification_failure_reason", "objective_origin_label",
    "prescription_adjustment_reason", "recommendation_action_type", "recommendation_priority",
    "recommendation_status", "security_severity_label", "session_adjustment_type",
    "session_revocation_reason", "team_roster_change_type", "training_objective_category",
    "training_readiness_category", "training_suggestion_decision", "training_suggestion_reason",
    "training_suggestion_status", "user_account_status", "user_role_label",
    "video_capture_mode", "video_codec_key", "video_codec_label", "video_destination_type",
    "video_distribution_failure_reason", "video_retention_policy", "video_session_state",
    "video_target_type", "video_transcode_trigger", "wellness_readiness_trend",
]

enum_value_maps: dict[str, dict[str, str]] = {}  # enum_name → {old_val → new_val}
print("=== UPDATING DOMAIN_AXIOMS ===")
for enum_name in NEW_ENUM_NAMES:
    if enum_name not in domain_enums:
        continue
    spec = domain_enums[enum_name]
    old_values = spec.get('values', [])
    mapping = {v: to_upper_snake(v) for v in old_values if isinstance(v, str)}
    new_values = list(dict.fromkeys(mapping[v] for v in old_values if isinstance(v, str)))
    changed = any(mapping[v] != v for v in old_values if isinstance(v, str))
    if changed:
        spec['values'] = new_values
        low = [v for v in old_values if isinstance(v, str) and mapping[v] != v]
        print(f"  {enum_name}: {low[:4]} → {[mapping[v] for v in low[:4]]}")
    enum_value_maps[enum_name] = mapping

# Merge video_codec_key + video_codec_label → video_codec
if 'video_codec_key' in domain_enums and 'video_codec_label' in domain_enums:
    merged = list(dict.fromkeys(
        domain_enums['video_codec_key']['values'] +
        domain_enums['video_codec_label']['values']
    ))
    domain_enums['video_codec'] = {"strict_match": True, "closed_set": True, "values": merged}
    vmap = {}
    for k, v in enum_value_maps.get('video_codec_key', {}).items():
        vmap[k] = v
    for k, v in enum_value_maps.get('video_codec_label', {}).items():
        vmap[k] = v
    enum_value_maps['video_codec'] = vmap
    print(f"  Merged video_codec: {merged}")

axioms_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"DOMAIN_AXIOMS saved. Total enums: {len(domain_enums)}\n")

# ────────────────────────────────────────────────────────────────
# 2. Update contract files
# ────────────────────────────────────────────────────────────────
# (relpath, dotpath, enum_name)
# Include codec fields → video_codec
CONTRACT_UPDATES = [
    # adjustmentReason
    ("contracts/asyncapi/components/schemas/prescription_adjusted_payload.yaml", "properties.adjustmentReason", "prescription_adjustment_reason"),
    # adjustmentType
    ("contracts/asyncapi/components/schemas/session_adjustment_made_payload.yaml", "properties.adjustmentType", "session_adjustment_type"),
    # aggregationType
    ("contracts/openapi/components/schemas/analytics/analytics_snapshot.yaml", "properties.aggregationType", "analytics_aggregation_type"),
    # athleteAgeGroup
    ("contracts/schemas/training/athlete_chat_conversation.schema.json", "properties.athleteAgeGroup", "athlete_age_group"),
    # attention_queue_status (status in resolved)
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
    # codec (lowercase key) → video_codec
    ("contracts/asyncapi/components/schemas/video/segment_ready_payload.yaml", "properties.codec", "video_codec"),
    # codecLabel (display label) → video_codec
    ("contracts/asyncapi/components/schemas/video/transcode_completed_payload.yaml", "properties.codecLabel", "video_codec"),
    ("contracts/asyncapi/components/schemas/video/distribution_published_payload.yaml", "properties.availableRenditions.items.properties.codecLabel", "video_codec"),
    ("contracts/openapi/components/schemas/video/distribution_profile.yaml", "properties.codecLabel", "video_codec"),
    ("contracts/schemas/video/distribution_profile.schema.json", "properties.codecLabel", "video_codec"),
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
    # itemType
    ("contracts/asyncapi/components/schemas/attention_queue_item_created_payload.yaml", "properties.itemType", "attention_queue_item_type"),
    # messageType
    ("contracts/schemas/training/athlete_chat_message.schema.json", "properties.messageType", "chat_message_type"),
    # mode
    ("contracts/openapi/components/schemas/training/load_chart.yaml", "properties.mode", "load_chart_mode"),
    ("contracts/schemas/training/load_chart.schema.json", "properties.mode", "load_chart_mode"),
    # role labels
    ("contracts/asyncapi/components/schemas/user_role_changed_payload.yaml", "properties.newRoleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/user_role_changed_payload.yaml", "properties.previousRoleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/role_assigned_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/role_revoked_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/user_created_payload.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/openapi/components/schemas/users/user_profile.yaml", "properties.roleLabel", "user_role_label"),
    ("contracts/asyncapi/components/schemas/session_created_payload.yaml", "properties.roleLabels.items", "user_role_label"),
    # match status
    ("contracts/asyncapi/components/schemas/match_status_updated_payload.yaml", "properties.newStatus", "match_phase_label"),
    ("contracts/asyncapi/components/schemas/match_status_updated_payload.yaml", "properties.previousStatus", "match_phase_label"),
    ("contracts/schemas/matches/match.schema.json", "properties.statusLabel", "match_phase_label"),
    # notificationChannels items
    ("contracts/schemas/training/training_suggestion_approval.schema.json", "properties.notificationChannels.items", "notification_channel"),
    # objectives items
    ("contracts/schemas/training/athlete_chat_message.schema.json", "properties.suggestedTraining.properties.objectives.items", "training_objective_category"),
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.objectives.items", "training_objective_category"),
    # origin
    ("contracts/asyncapi/components/schemas/need_detected_created_payload.yaml", "properties.origin", "need_origin"),
    ("contracts/asyncapi/components/schemas/objective_created_payload.yaml", "properties.origin", "objective_origin_label"),
    # outcomeLabel
    ("contracts/asyncapi/components/schemas/audit_entry_created_payload.yaml", "properties.outcomeLabel", "audit_outcome_label"),
    ("contracts/asyncapi/components/schemas/audit_entry_security_flagged_payload.yaml", "properties.outcomeLabel", "audit_outcome_label"),
    # previousStatusLabel
    ("contracts/asyncapi/components/schemas/competition_phase_changed_payload.yaml", "properties.previousStatusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/season_status_updated_payload.yaml", "properties.previousStatusLabel", "entity_lifecycle_status"),
    # range
    ("contracts/openapi/components/schemas/training/load_chart.yaml", "properties.range", "load_chart_range"),
    ("contracts/schemas/training/load_chart.schema.json", "properties.range", "load_chart_range"),
    # readinessCategory
    ("contracts/asyncapi/components/schemas/training_readiness_assessed_payload.yaml", "properties.readinessCategory", "training_readiness_category"),
    # readinessTrend
    ("contracts/openapi/components/schemas/wellness/wellness_summary.yaml", "properties.readinessTrend", "wellness_readiness_trend"),
    # reason
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
    # state
    ("contracts/openapi/components/schemas/video/match_media_session.yaml", "properties.state", "video_session_state"),
    ("contracts/schemas/video/match_media_session.schema.json", "properties.state", "video_session_state"),
    ("contracts/openapi/components/schemas/video/media_segment.yaml", "properties.state", "media_segment_state"),
    ("contracts/schemas/video/media_segment.schema.json", "properties.state", "media_segment_state"),
    # status
    ("contracts/openapi/components/schemas/ai_ingestion/ingestion_job.yaml", "properties.status", "ai_ingestion_job_status"),
    ("contracts/openapi/components/schemas/training/training_suggestion.yaml", "properties.status", "training_suggestion_status"),
    ("contracts/schemas/training/training_suggestion.schema.json", "properties.status", "training_suggestion_status"),
    ("contracts/schemas/training/athlete_chat_conversation.schema.json", "properties.status", "chat_conversation_status"),
    # status training_session_published (PUBLISHED/SCHEDULED already uppercase → training_state)
    # statusLabel
    ("contracts/asyncapi/components/schemas/competition_phase_changed_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/season_status_updated_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
    ("contracts/asyncapi/components/schemas/team_created_payload.yaml", "properties.statusLabel", "entity_lifecycle_status"),
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

# Also need to update existing enums that reference feedback_context_type
# feedback_context_type already has UPPER_SNAKE_CASE values, no change needed

print("=== UPDATING CONTRACT FILES ===")
ok = 0
skip = 0
err = 0

for rel_path, dot_path, enum_name in CONTRACT_UPDATES:
    p = ROOT / rel_path
    if not p.exists():
        print(f"  MISSING: {rel_path}")
        err += 1
        continue

    value_map = enum_value_maps.get(enum_name, {})
    if not value_map:
        skip += 1
        continue  # no changes needed, already uppercase

    obj, fmt = load_file(p)
    node = get_node(obj, dot_path)
    if node is None:
        err += 1
        print(f"  NOT_FOUND: {rel_path.split('/')[-1]} @ {dot_path.split('.')[-1]}")
        continue

    if not isinstance(node, dict):
        err += 1
        continue

    enum_vals = node.get('enum')
    if not isinstance(enum_vals, list):
        skip += 1
        continue

    new_vals = [value_map.get(v, v) for v in enum_vals]
    if new_vals == enum_vals:
        skip += 1
        continue

    node['enum'] = new_vals
    # Update x-domain-enum-ref if pointing to old codec enums
    existing_ref = node.get('x-domain-enum-ref', '')
    if existing_ref in ('video_codec_key', 'video_codec_label'):
        node['x-domain-enum-ref'] = 'video_codec'

    save_file(p, obj, fmt)
    print(f"  OK: {rel_path.split('/')[-1]} @ {dot_path.split('.')[-1]} → {new_vals}")
    ok += 1

print(f"\nContract updates: {ok} done, {skip} skipped, {err} errors")

# ────────────────────────────────────────────────────────────────
# 3. Update x-domain-enum-ref for codec fields (video_codec_key/label → video_codec)
# ────────────────────────────────────────────────────────────────
codec_files = [
    ("contracts/asyncapi/components/schemas/video/segment_ready_payload.yaml", "properties.codec"),
    ("contracts/asyncapi/components/schemas/video/transcode_completed_payload.yaml", "properties.codecLabel"),
    ("contracts/asyncapi/components/schemas/video/distribution_published_payload.yaml", "properties.availableRenditions.items.properties.codecLabel"),
    ("contracts/openapi/components/schemas/video/distribution_profile.yaml", "properties.codecLabel"),
    ("contracts/schemas/video/distribution_profile.schema.json", "properties.codecLabel"),
]
print("\n=== UPDATING CODEC enum-refs ===")
for rel_path, dot_path in codec_files:
    p = ROOT / rel_path
    if not p.exists():
        continue
    obj, fmt = load_file(p)
    node = get_node(obj, dot_path)
    if isinstance(node, dict) and node.get('x-domain-enum-ref') in ('video_codec_key', 'video_codec_label', None):
        node['x-domain-enum-ref'] = 'video_codec'
        save_file(p, obj, fmt)
        print(f"  Updated codec ref: {rel_path.split('/')[-1]} @ {dot_path.split('.')[-1]}")

print("\n=== DONE ===")
