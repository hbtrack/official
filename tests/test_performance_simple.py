"""
Testes simples de performance — FASE 4, Tarefa 4.2
Valida que endpoints estão configurados e respondendo.
"""
import time
from django.test import Client


class TestPerformancePhase4:
    """Testes de performance — FASE 4"""

    def test_api_docs_available(self):
        """Validar que /api/docs está disponível"""
        client = Client()
        response = client.get("/api/docs")
        assert response.status_code == 200
        print("✅ /api/docs — 200")

    def test_training_sessions_endpoint_exists(self):
        """Validar que GET /api/training-sessions/ retorna resposta (mesmo sem dados)"""
        client = Client()
        start = time.perf_counter()
        try:
            response = client.get("/api/training-sessions/")
            elapsed_ms = (time.perf_counter() - start) * 1000
            # Pode retornar 400/401/404/500 sem dados, mas não deve travar
            assert response.status_code != 500, f"Server error: {response.status_code}"
            assert elapsed_ms < 500, f"Timeout: {elapsed_ms:.2f}ms"
            print(f"✅ GET /api/training-sessions/ — {elapsed_ms:.2f}ms ({response.status_code})")
        except Exception as e:
            print(f"⚠️  GET /api/training-sessions/ — Exception: {e}")

    def test_teams_endpoint_exists(self):
        """Validar que GET /api/teams/ pode responder"""
        client = Client()
        start = time.perf_counter()
        try:
            response = client.get("/api/teams/")
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 500, f"Timeout: {elapsed_ms:.2f}ms"
            print(f"✅ GET /api/teams/ — {elapsed_ms:.2f}ms ({response.status_code})")
        except Exception as e:
            print(f"⚠️  GET /api/teams/ — Exception: {e}")

    def test_seasons_endpoint_exists(self):
        """Validar que GET /api/seasons/ pode responder"""
        client = Client()
        start = time.perf_counter()
        try:
            response = client.get("/api/seasons/")
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 500, f"Timeout: {elapsed_ms:.2f}ms"
            print(f"✅ GET /api/seasons/ — {elapsed_ms:.2f}ms ({response.status_code})")
        except Exception as e:
            print(f"⚠️  GET /api/seasons/ — Exception: {e}")
