#!/usr/bin/env python3
"""
Validation script for AR_003: Schemas Pydantic Canônicos de Scout

Validation criteria:
1. Import ScoutEventCreate, ScoutEventRead, CanonicalEventType, EventType
2. CanonicalEventType does NOT contain: goal_7m, own_goal, shot_on_target, assist, technical_foul
3. ScoutEventCreate accepts DB-aligned fields: period_number, game_time_seconds, x_coord, y_coord, etc.
4. ScoutEventCreate validation: goalkeeper_save requires related_event_id (raises ValidationError if None)
5. EventType alias works correctly
"""

import sys
import os
from pathlib import Path
from uuid import uuid4

# Adicionar o Backend ao sys.path
backend_path = Path(__file__).parent.parent / "Hb Track - Backend"
sys.path.insert(0, str(backend_path))

try:
    print("[1/5] Testing imports...")
    from app.schemas.match_events import (
        ScoutEventCreate,
        ScoutEventRead,
        CanonicalEventType,
        EventType,
    )
    print("[PASS] All imports successful")

    print("\n[2/5] Testing CanonicalEventType enum values...")
    invalid_values = ['goal_7m', 'own_goal', 'shot_on_target', 'assist', 'technical_foul']
    enum_values = [e.value for e in CanonicalEventType]
    found_invalid = [v for v in invalid_values if v in enum_values]
    if found_invalid:
        print(f"[FAIL] Invalid values found in enum: {found_invalid}")
        sys.exit(1)
    print(f"[PASS] Enum clean: {len(enum_values)} valid types, no invalid codes")

    print("\n[3/5] Testing ScoutEventCreate with DB-aligned fields...")
    test_data = {
        'team_id': uuid4(),
        'period_number': 1,
        'game_time_seconds': 300,
        'phase_of_play': 'attack',
        'advantage_state': 'even',
        'score_our': 5,
        'score_opponent': 3,
        'event_type': 'goal',
        'outcome': 'success',
        'is_shot': True,
        'is_goal': True,
        'source': 'live',
        'x_coord': 50.0,
        'y_coord': 40.0,
    }
    event = ScoutEventCreate(**test_data)
    assert event.period_number == 1
    assert event.game_time_seconds == 300
    assert event.x_coord == 50.0
    assert event.y_coord == 40.0
    print("[PASS] ScoutEventCreate accepts DB-aligned fields correctly")

    print("\n[4/5] Testing goalkeeper_save validation (related_event_id required)...")
    test_data_save = {
        **test_data,
        'event_type': 'goalkeeper_save',
        'related_event_id': None,  # Should trigger ValidationError
    }
    try:
        ScoutEventCreate(**test_data_save)
        print("[FAIL] goalkeeper_save without related_event_id should raise ValidationError")
        sys.exit(1)
    except ValueError as e:
        if 'goalkeeper_save' in str(e).lower() and 'related_event_id' in str(e).lower():
            print(f"[PASS] ValidationError correctly raised: {e}")
        else:
            print(f"[FAIL] Wrong validation error: {e}")
            sys.exit(1)

    print("\n[5/5] Testing EventType alias...")
    assert EventType is CanonicalEventType
    print("[PASS] EventType alias works (backward compatibility preserved)")

    print("\n" + "="*60)
    print("[PASS] AR_003 objective achieved:")
    print("   - Canonical schemas implemented (ScoutEventCreate, ScoutEventRead)")
    print("   - CanonicalEventType has only valid event codes")
    print("   - DB-aligned fields accepted (period_number, game_time_seconds, x/y_coord)")
    print("   - goalkeeper_save validation enforces related_event_id requirement")
    print("   - EventType alias maintains backward compatibility")
    print("="*60)

except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Validation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
