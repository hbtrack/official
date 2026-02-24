"""Validate AR_003 — Schemas Pydantic canonicos de scout (cmd-safe, deterministic)."""
import sys
import uuid

sys.path.insert(0, 'Hb Track - Backend')
from app.schemas.match_events import ScoutEventCreate, CanonicalEventType, EventType

FIXED = uuid.UUID('00000000-0000-0000-0000-000000000001')

# Enum nao deve conter valores invalidos
invalid = [v for v in ['goal_7m', 'own_goal', 'shot_on_target', 'assist', 'technical_foul']
           if v in [e.value for e in CanonicalEventType]]
assert not invalid, f'Enum invalido: {invalid}'

# ScoutEventCreate aceita campos canonicos
base = {
    'team_id': FIXED,
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
e = ScoutEventCreate(**base)
assert e.period_number == 1 and e.game_time_seconds == 300 and e.x_coord == 50.0 and e.y_coord == 40.0

# EventType deve ser alias de CanonicalEventType
assert EventType is CanonicalEventType

# goalkeeper_save requer related_event_id
gk_ok = False
try:
    ScoutEventCreate(**{**base, 'event_type': 'goalkeeper_save', 'related_event_id': None})
except ValueError as err:
    gk_ok = 'goalkeeper_save' in str(err).lower() and 'related_event_id' in str(err).lower()
assert gk_ok, 'goalkeeper_save nao levantou ValidationError correta'

print('PASS: Schemas Pydantic canonicos OK')
