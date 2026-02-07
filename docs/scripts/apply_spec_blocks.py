"""
Apply SPEC blocks to INVARIANTS_TRAINING.md with complete metadata.
"""

import json
import re
from pathlib import Path

# Metadata extracted from document
METADATA = json.loads(r'''
{
  "004": {
    "class": "C2",
    "description": "Janela de edição por autoria/hierarquia e estado",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.function": "_validate_edit_permission",
      "code.constants": ["AUTHOR_EDIT_WINDOW_MINUTES", "SUPERIOR_EDIT_WINDOW_HOURS"]
    }
  },
  "005": {
    "class": "C2",
    "description": "Sessão > 60 dias vira readonly (imutabilidade)",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.function": "_validate_edit_permission",
      "code.constants": ["IMMUTABILITY_DAYS"]
    }
  },
  "006": {
    "class": "D",
    "description": "Lifecycle de status (DB enum + transições operacionais)",
    "anchors": {
      "db.table": "training_sessions",
      "db.constraint": "check_training_session_status",
      "celery.task": "update_training_session_statuses_task",
      "api.operation_id": ["publish_training_session_api_v1_training_sessions__training_session_id__publish_post", "close_training_session_api_v1_training_sessions__training_session_id__close_post"]
    }
  },
  "007": {
    "class": "E1",
    "description": "Timezone operacional (Celery usa UTC)",
    "anchors": {
      "code.file": "app/core/celery_tasks.py",
      "code.function": "update_training_session_statuses_task",
      "code.pattern": "datetime.now(timezone.utc)"
    }
  },
  "009": {
    "class": "A",
    "description": "Unicidade: 1 wellness_pre por athlete×session",
    "anchors": {
      "db.table": "wellness_pre",
      "db.constraint": "ux_wellness_pre_session_athlete",
      "db.sqlstate": "23505"
    }
  },
  "010": {
    "class": "A",
    "description": "Unicidade: 1 wellness_post por athlete×session",
    "anchors": {
      "db.table": "wellness_post",
      "db.constraint": "ux_wellness_post_session_athlete",
      "db.sqlstate": "23505"
    }
  },
  "011": {
    "class": "C2",
    "description": "Regras de desvio e justificativa mínima",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.constants": ["MIN_JUSTIFICATION_LENGTH"],
      "code.lines": [916, 928]
    }
  },
  "012": {
    "class": "C2",
    "description": "Rate limiting de export LGPD",
    "anchors": {
      "code.file": "app/services/export_service.py",
      "code.constants": ["ANALYTICS_PDF_DAILY_LIMIT", "ATHLETE_DATA_DAILY_LIMIT"]
    }
  },
  "013": {
    "class": "C2",
    "description": "Gamificação: critérios de badge (regras de elegibilidade)",
    "anchors": {
      "code.file": "app/services/wellness_gamification_service.py",
      "code.function": "_check_and_award_streak",
      "code.lines": [128, 147, 389]
    }
  },
  "014": {
    "class": "C2",
    "description": "Alertas: sobrecarga por multiplicador (>= 1.5× threshold)",
    "anchors": {
      "code.file": "app/services/training_alerts_service.py",
      "code.constants": ["alert_threshold_multiplier"]
    }
  },
  "015": {
    "class": "C1",
    "description": "Training Analytics (FR-012) exposto e ancorado em router/service",
    "anchors": {
      "code.file": "app/api/v1/routers/training_analytics.py",
      "code.service": "TrainingAnalyticsService",
      "api.endpoints": ["summary", "weekly-load", "deviation-analysis", "prevention-effectiveness"]
    }
  },
  "016": {
    "class": "C1",
    "description": "Attendance: rota base exige auth; rota scoped não exposta",
    "anchors": {
      "code.file": "app/api/v1/routers/attendance.py",
      "code.auth": "required",
      "code.note": "attendance_scoped não exposto em api.py"
    }
  },
  "018": {
    "class": "C2",
    "description": "Sessões criadas via microciclo: draft se incompleta, scheduled se completa",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.function": "create",
      "code.lines": [237, 239]
    }
  },
  "019": {
    "class": "C2",
    "description": "Audit log para ações de sessão (create/edit/publish/close)",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.functions": ["create", "update", "publish", "close"],
      "code.lines": [246, 341, 393, 764, 786]
    }
  },
  "020": {
    "class": "A",
    "description": "Cache invalidation automático após mudanças em sessões",
    "anchors": {
      "db.table": "training_sessions",
      "db.trigger": "tr_invalidate_analytics_cache"
    }
  },
  "021": {
    "class": "A",
    "description": "Internal load calculado por trigger no DB",
    "anchors": {
      "db.table": "wellness_post",
      "db.trigger": "tr_calculate_internal_load"
    }
  },
  "022": {
    "class": "C2",
    "description": "Atualização automática de performance cache ao registrar wellness_post",
    "anchors": {
      "code.file": "app/services/wellness_post_service.py",
      "code.lines": [268, 324]
    }
  },
  "023": {
    "class": "C2",
    "description": "Overload alerts disparados automaticamente por wellness_post",
    "anchors": {
      "code.file": "app/services/wellness_post_service.py",
      "code.function": "_trigger_overload_alert_on_wellness_post"
    }
  },
  "024": {
    "class": "C2",
    "description": "WebSocket broadcast e NotificationService para alerts/badges",
    "anchors": {
      "code.file": ["app/services/training_alerts_service.py", "app/services/wellness_gamification_service.py"],
      "code.lines": [364, 328]
    }
  },
  "025": {
    "class": "C1",
    "description": "Export LGPD via endpoints OpenAPI + Celery async + cleanup de jobs",
    "anchors": {
      "code.file": ["app/api/v1/routers/exports.py", "app/api/v1/routers/athlete_export.py"],
      "celery.task": ["generate_analytics_pdf_task", "cleanup_expired_export_jobs_task"]
    }
  },
  "026": {
    "class": "C2",
    "description": "LGPD access logging (staff lendo dados de outros atletas)",
    "anchors": {
      "code.file": ["app/services/wellness_pre_service.py", "app/services/wellness_post_service.py"],
      "code.pattern": "data_access_logs"
    }
  },
  "027": {
    "class": "D",
    "description": "Cache refresh daily para rankings/métricas",
    "anchors": {
      "celery.schedule": "refresh-analytics-cache",
      "celery.task": "refresh_training_rankings_task",
      "code.file": ["app/core/celery_app.py", "app/core/celery_tasks.py"]
    }
  },
  "029": {
    "class": "C2",
    "description": "Edição bloqueada após início da sessão",
    "anchors": {
      "code.file": "app/services/training_session_service.py",
      "code.function": "_validate_edit_permission",
      "code.lines": [441, 444, 447, 460]
    }
  },
  "030": {
    "class": "A",
    "description": "Correção de attendance exige campos de auditoria",
    "anchors": {
      "db.table": "attendance",
      "db.constraint": "ck_attendance_correction_fields",
      "db.sqlstate": "23514"
    }
  },
  "031": {
    "class": "A",
    "description": "Derivação automática de phase_focus a partir dos percentuais",
    "anchors": {
      "db.table": "training_sessions",
      "db.trigger": "tr_derive_phase_focus",
      "db.function": "fn_derive_phase_focus",
      "db.constraints": ["ck_phase_focus_attack_consistency", "ck_phase_focus_defense_consistency", "ck_phase_focus_transition_defense_consistency", "ck_phase_focus_transition_offense_consistency"]
    }
  },
  "032": {
    "class": "A",
    "description": "RPE da sessão deve estar entre 0 e 10",
    "anchors": {
      "db.table": "wellness_post",
      "db.constraint": "ck_wellness_post_rpe",
      "db.sqlstate": "23514"
    }
  },
  "033": {
    "class": "A",
    "description": "Horas de sono deve estar entre 0 e 24",
    "anchors": {
      "db.table": "wellness_pre",
      "db.constraint": "ck_wellness_pre_sleep_hours",
      "db.sqlstate": "23514"
    }
  },
  "034": {
    "class": "A",
    "description": "Qualidade do sono deve estar entre 1 e 5",
    "anchors": {
      "db.table": "wellness_pre",
      "db.constraint": "ck_wellness_pre_sleep_quality",
      "db.sqlstate": "23514"
    }
  },
  "035": {
    "class": "A",
    "description": "Nome de template de sessão é único por organização",
    "anchors": {
      "db.table": "session_templates",
      "db.constraint": "uq_session_templates_org_name",
      "db.sqlstate": "23505"
    }
  },
  "036": {
    "class": "A",
    "description": "Ranking de wellness é único por time e mês",
    "anchors": {
      "db.table": "team_wellness_rankings",
      "db.constraint": "uq_team_wellness_rankings_team_month",
      "db.sqlstate": "23505"
    }
  },
  "037": {
    "class": "A",
    "description": "Data de início do ciclo deve ser anterior à data de término",
    "anchors": {
      "db.table": "training_cycles",
      "db.constraint": "check_cycle_dates",
      "db.sqlstate": "23514"
    }
  }
}
''')

# Mapping of test patterns (from generate_spec_blocks.py output)
TEST_PATTERNS = {
    "004": "tests/unit/test_inv_train_004_edit_window_time.py",
    "005": "tests/unit/test_inv_train_005_immutability_60_days.py",
    "006": "tests/unit/test_inv_train_006_lifecycle_status.py",
    "007": "tests/unit/test_inv_train_007_celery_utc_timezone.py",
    "009": "tests/unit/test_inv_train_009_wellness_pre_uniqueness.py",
    "010": "tests/unit/test_inv_train_010_wellness_post_uniqueness.py",
    "011": "tests/unit/test_inv_train_011_deviation_rules.py",
    "012": "tests/unit/test_inv_train_012_export_rate_limit.py",
    "013": "tests/unit/test_inv_train_013_gamification_badge_rules.py",
    "014": "tests/unit/test_inv_train_014_overload_alert_threshold.py",
    "015": "tests/unit/test_inv_train_015_training_analytics_exposure.py",
    "016": "tests/training/invariants/test_inv_train_016_*.py",
    "018": "Hb Track - Backend/tests/unit/test_training_session_microcycle_status.py",
    "019": "Hb Track - Backend/tests/integration/test_training_session_audit_logs.py",
    "020": "tests/unit/test_inv_train_020_cache_invalidation_trigger.py",
    "021": "tests/unit/test_inv_train_021_internal_load_trigger.py",
    "022": "tests/unit/test_wellness_post_cache_invalidation.py",
    "023": "Hb Track - Backend/tests/unit/test_wellness_post_overload_alert_trigger.py",
    "024": "tests/unit/test_inv_train_024_websocket_broadcast.py",
    "025": "tests/unit/test_inv_train_025_export_lgpd_endpoints.py",
    "026": "tests/unit/test_inv_train_026_lgpd_access_logging.py",
    "027": "tests/unit/test_refresh_training_rankings_task.py",
    "029": "tests/unit/test_inv_train_029_edit_blocked_after_in_progress.py",
    "030": "tests/unit/test_inv_train_030_attendance_correction_fields.py",
    "031": "tests/unit/test_inv_train_031_derive_phase_focus.py",
    "032": "tests/training/invariants/test_inv_train_032_*.py",
    "033": "tests/unit/test_inv_train_033_wellness_pre_sleep_hours.py",
    "034": "tests/unit/test_inv_train_034_wellness_pre_sleep_quality.py",
    "035": "tests/unit/test_inv_train_035_session_templates_unique_name.py",
    "036": "tests/unit/test_inv_train_036_wellness_rankings_unique.py",
    "037": "tests/training/invariants/test_inv_train_037_*.py",
}


def format_anchor_value(key, value):
    """Format anchor value based on type."""
    if isinstance(value, list):
        if len(value) == 1:
            return f'"{value[0]}"'
        # Multi-item list
        items = "\n".join([f'        - "{item}"' for item in value])
        return f"\n{items}"
    else:
        return f'"{value}"'


def generate_spec_block(inv_id, metadata):
    """Generate complete SPEC block with metadata."""
    anchors_lines = []
    for key, value in metadata["anchors"].items():
        formatted_value = format_anchor_value(key, value)
        if "\n" in formatted_value:
            anchors_lines.append(f"      {key}:{formatted_value}")
        else:
            anchors_lines.append(f"      {key}: {formatted_value}")
    
    anchors_block = "\n".join(anchors_lines)
    
    spec = f'''**SPEC**:
```yaml
spec_version: "1.0"
id: "INV-TRAIN-{inv_id}"
status: "CONFIRMADA"
test_required: true

units:
  - unit_key: "main"
    class: "{metadata['class']}"
    required: true
    description: "{metadata['description']}"
    anchors:
{anchors_block}

tests:
  primary: "{TEST_PATTERNS[inv_id]}"
  node: "TestInvTrain{inv_id}"
```

'''
    return spec


def main():
    """Generate all SPEC blocks and print them grouped for manual insertion."""
    doc_path = Path(r"c:\HB TRACK\docs\02-modulos\training\INVARIANTS_TRAINING.md")
    content = doc_path.read_text(encoding="utf-8")
    
    # Find all INVs that don't have SPEC blocks yet
    inv_ids = sorted(METADATA.keys())
    
    print(f"Generating {len(inv_ids)} SPEC blocks...\n")
    print("=" * 80)
    
    for inv_id in inv_ids:
        # Find the INV header
        pattern = rf"^### INV-TRAIN-{inv_id} —"
        match = re.search(pattern, content, re.MULTILINE)
        if not match:
            print(f"WARNING: INV-TRAIN-{inv_id} not found in document")
            continue
        
        spec_block = generate_spec_block(inv_id, METADATA[inv_id])
        
        print(f"\n### INV-TRAIN-{inv_id}\n")
        print(spec_block)
        print("-" * 80)
    
    print(f"\n\nTotal: {len(inv_ids)} SPEC blocks generated")
    print("\nTo apply: Insert each SPEC block after its ### INV-TRAIN-XXX header")


if __name__ == "__main__":
    main()
