import pytest


@pytest.fixture
def scout_event_data():
    from uuid import uuid4
    from datetime import datetime, timezone
    return {
        "id": uuid4(),
        "match_id": uuid4(),
        "event_label": "GOAL",
        "recorded_at": datetime.now(timezone.utc),
    }
