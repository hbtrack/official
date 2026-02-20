from pathlib import Path


SERVICE_PATH = Path("Hb Track - Backend/app/services/match_event_service.py")
ROUTER_PATH = Path("Hb Track - Backend/app/api/v1/routers/match_events.py")


def test_match_event_service_contract_smoke():
    content = SERVICE_PATH.read_text(encoding="utf-8")

    assert "async def create(self, match_id: UUID, data: ScoutEventCreate)" in content
    assert "period_number=data.period_number" in content
    assert "game_time_seconds=data.game_time_seconds" in content
    assert "x_coord=data.x_coord" in content
    assert "y_coord=data.y_coord" in content
    assert "is_shot=is_shot_db" in content
    assert "related_event must be a shot or seven_meter" in content
    assert "MatchRoster.is_available.is_(True)" in content


def test_add_event_router_contract_smoke():
    content = ROUTER_PATH.read_text(encoding="utf-8")

    assert "event = await service.create(match_id, payload)" in content
    assert "await db.commit()" in content
    assert "await db.refresh(event)" in content
    assert "created = await service.bulk_create(match_id, events)" in content
    assert "event_type canônicos (11)" in content
