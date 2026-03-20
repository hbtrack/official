"""
Testes de integração do módulo video.
Testam os endpoints Django Ninja com banco de dados em memória (pytest-django).
"""
import uuid
import pytest

# Marcamos como django_db para todos os testes desta classe
pytestmark = pytest.mark.django_db


class TestSessionEndpoints:
    def test_create_session_returns_201(self, client):
        payload = {
            "matchId": str(uuid.uuid4()),
            "captureMode": "PANORAMIC",
            "retentionPolicy": "KEEP_7_DAYS",
        }
        response = client.post(
            "/api/video/sessions",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["state"] == "DRAFT"
        assert data["captureMode"] == "PANORAMIC"

    def test_get_session_not_found_returns_404(self, client):
        response = client.get(f"/api/video/sessions/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_list_sessions_returns_200(self, client):
        response = client.get("/api/video/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data


class TestSegmentEndpoints:
    def _create_capturing_session(self, client) -> str:
        """Helper: cria sessão e a coloca em CAPTURING."""
        payload = {
            "matchId": str(uuid.uuid4()),
            "captureMode": "PANORAMIC",
            "retentionPolicy": "KEEP_7_DAYS",
        }
        resp = client.post("/api/video/sessions", data=payload, content_type="application/json")
        assert resp.status_code == 201
        session_id = resp.json()["id"]

        patch_resp = client.patch(
            f"/api/video/sessions/{session_id}",
            data={"state": "CAPTURING"},
            content_type="application/json",
        )
        assert patch_resp.status_code == 200
        return session_id

    def test_create_segment_returns_201(self, client):
        session_id = self._create_capturing_session(client)
        payload = {
            "sessionId": session_id,
            "timecodeLogical": 1000,
            "timecodeLabel": "00:00:01.000",
            "codecLabel": "H264",
            "bitrate": 2500,
            "durationMs": 5000,
        }
        response = client.post("/api/video/segments", data=payload, content_type="application/json")
        assert response.status_code == 201
        data = response.json()
        assert data["timecodeLogical"] == 1000
        assert data["state"] == "OPEN"

    def test_create_segment_conflict_on_duplicate_timecode(self, client):
        session_id = self._create_capturing_session(client)
        payload = {
            "sessionId": session_id,
            "timecodeLogical": 2000,
            "timecodeLabel": "00:00:02.000",
        }
        client.post("/api/video/segments", data=payload, content_type="application/json")
        response = client.post("/api/video/segments", data=payload, content_type="application/json")
        assert response.status_code == 409


class TestClipEndpoints:
    def test_create_clip_without_context_returns_422(self, client):
        payload = {
            "sessionId": str(uuid.uuid4()),
            "fromTimecode": 0,
            "toTimecode": 5000,
        }
        response = client.post("/api/video/clips", data=payload, content_type="application/json")
        assert response.status_code == 422

    def test_create_clip_with_zone_returns_201(self, client):
        # Criar sessão válida primeiro
        sess_payload = {
            "matchId": str(uuid.uuid4()),
            "captureMode": "PANORAMIC",
            "retentionPolicy": "KEEP_7_DAYS",
        }
        sess_resp = client.post("/api/video/sessions", data=sess_payload, content_type="application/json")
        assert sess_resp.status_code == 201
        session_id = sess_resp.json()["id"]

        payload = {
            "sessionId": session_id,
            "fromTimecode": 0,
            "toTimecode": 5000,
            "zoneLabel": "LEFT_WING",
        }
        response = client.post("/api/video/clips", data=payload, content_type="application/json")
        assert response.status_code == 201
        data = response.json()
        assert data["zoneLabel"] == "LEFT_WING"
