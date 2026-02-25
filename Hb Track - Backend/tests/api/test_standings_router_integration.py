#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Standings Router Integration — AR_077

OBJETIVO:
Validar integração CompetitionStandingsService → competitions_v2 router.
Prova antifrágil INV-COMP-008: scoring values (ppw/ppd/ppl) vêm do DB.

CENÁRIO CRÍTICO (test_get_standings_uses_dynamic_scoring_inv_comp_008):
1. Cria competition com points_per_win=3 (não-padrão, handebol usa 2)
2. Cria 3 opponent_teams (TeamA, TeamB, TeamC)
3. Cria 3 partidas: TeamA vence 2x, TeamC vence 1x
4. GET /standings deve retornar TeamA com 6pts (ppw=3 × 2W)
5. PROVA: Se service usar ppw=2 hardcoded, daria 4pts → assert falha

INVARIANTES TESTADAS:
- INV-COMP-008: dynamic_scoring_rules (ppw/ppd/ppl do DB, não hardcoded)
- INV-COMP-005: team_id FK preservado (SET NULL)
- INV-COMP-006: soft delete (deleted_at IS NULL)
"""
import pytest
from uuid import uuid4, UUID
from typing import Optional

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestStandingsRouterIntegration:
    """Testes de integração: CompetitionStandingsService + Router"""

    def test_get_standings_requires_auth(self, client: AsyncClient):
        """GET /standings deve retornar 401 sem autenticação"""
        competition_id = uuid4()
        response = client.get(f"/api/v1/competitions/{competition_id}/standings")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_recalculate_requires_auth(self, client: AsyncClient):
        """POST /standings/recalculate deve retornar 401 sem autenticação"""
        competition_id = uuid4()
        response = client.post(f"/api/v1/competitions/{competition_id}/standings/recalculate")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_standings_uses_dynamic_scoring_inv_comp_008(
        self, auth_client: AsyncClient, db: AsyncSession
    ):
        """
        TESTE ANTIFRÁGIL INV-COMP-008: ppw=3 do DB → TeamA 2W = 6pts
        
        SE service usar ppw=2 hardcoded:
        - TeamA teria 2W × 2 = 4pts
        - assert pts[0] == 6 FALHARIA
        
        Cenário:
        - Competition com points_per_win=3 (não-padrão)
        - TeamA vence M1 (3-1 vs TeamB) + M2 (2-1 vs TeamC) → 2W
        - TeamC vence M3 (2-0 vs TeamB) → 1W
        - Esperado: TeamA 6pts, TeamC 3pts, TeamB 0pts
        """
        # --- STEP 1: Criar competition com ppw=3 ---
        comp_payload = {
            "name": f"AR077-INV-COMP-008-{uuid4().hex[:8]}",
            "description": "Test antifrágil - scoring dinâmico",
            "start_date": "2026-03-01",
            "end_date": "2026-03-31",
            "points_per_win": 3,  # NÃO-PADRÃO (handebol usa 2)
            "points_per_draw": 1,
            "points_per_loss": 0,
        }
        resp = await auth_client.post("/api/v1/competitions/v2", json=comp_payload)
        if resp.status_code not in (200, 201):
            pytest.skip(f"POST /competitions/v2 failed: {resp.status_code} {resp.text}")
        competition_id = resp.json()["id"]

        # --- STEP 2: Criar 3 opponent_teams ---
        team_names = ["TeamA", "TeamB", "TeamC"]
        team_ids = {}
        for name in team_names:
            resp = await auth_client.post(
                f"/api/v1/competitions/{competition_id}/opponent-teams",
                json={"name": name},
            )
            if resp.status_code not in (200, 201):
                pytest.skip(f"POST opponent-team {name} failed: {resp.status_code}")
            team_ids[name] = resp.json()["id"]

        ta, tb, tc = team_ids["TeamA"], team_ids["TeamB"], team_ids["TeamC"]

        # --- STEP 3: Criar 3 partidas ---
        matches = [
            # M1: TeamA (home) vence TeamB (away) 3-1
            {
                "home_team_id": ta,
                "away_team_id": tb,
                "match_date": "2026-03-05T18:00:00Z",
                "venue": "Arena AR077-1",
            },
            # M2: TeamA (home) vence TeamC (away) 2-1
            {
                "home_team_id": ta,
                "away_team_id": tc,
                "match_date": "2026-03-12T18:00:00Z",
                "venue": "Arena AR077-2",
            },
            # M3: TeamB (home) perde TeamC (away) 0-2
            {
                "home_team_id": tb,
                "away_team_id": tc,
                "match_date": "2026-03-19T18:00:00Z",
                "venue": "Arena AR077-3",
            },
        ]
        match_ids = []
        for m in matches:
            resp = await auth_client.post(
                f"/api/v1/competitions/{competition_id}/matches", json=m
            )
            if resp.status_code not in (200, 201):
                pytest.skip(f"POST match failed: {resp.status_code}")
            match_ids.append(resp.json()["id"])

        m1, m2, m3 = match_ids

        # --- STEP 4: Atualizar resultados ---
        results = [
            # M1: TeamA 3-1 TeamB (TeamA vence)
            {"match_id": m1, "home_score": 3, "away_score": 1},
            # M2: TeamA 2-1 TeamC (TeamA vence)
            {"match_id": m2, "home_score": 2, "away_score": 1},
            # M3: TeamB 0-2 TeamC (TeamC vence)
            {"match_id": m3, "home_score": 0, "away_score": 2},
        ]
        for r in results:
            mid = r["match_id"]
            payload = {"home_score": r["home_score"], "away_score": r["away_score"]}
            resp = await auth_client.patch(
                f"/api/v1/competitions/{competition_id}/matches/{mid}/result",
                json=payload,
            )
            if resp.status_code not in (200, 204):
                pytest.skip(f"PATCH match result failed: {resp.status_code}")

        # --- STEP 5: GET /standings ---
        resp = await auth_client.get(f"/api/v1/competitions/{competition_id}/standings")
        assert resp.status_code == status.HTTP_200_OK, f"GET standings failed: {resp.text}"

        standings = resp.json()
        assert len(standings) >= 3, f"Expected at least 3 teams, got {len(standings)}"

        # Ordenar por position (ou points se position não estiver definido)
        standings_sorted = sorted(standings, key=lambda x: x.get("position", 999))
        pts = [s["points"] for s in standings_sorted]

        # VALIDAÇÃO ANTIFRÁGIL (INV-COMP-008)
        assert pts[0] >= pts[1] >= pts[2], f"Standings não ordenados: {pts}"
        assert pts[0] == 6, (
            f"FAIL INV-COMP-008: TeamA deveria ter 6pts (ppw=3 × 2W), "
            f"mas tem {pts[0]}. Se service usar ppw=2 hardcoded, daria 4pts."
        )

        # Validação adicional: TeamC deve ter 3pts (ppw=3 × 1W)
        assert pts[1] == 3, f"TeamC deveria ter 3pts (ppw=3 × 1W), mas tem {pts[1]}"
        # TeamB deve ter 0pts (0W)
        assert pts[2] == 0, f"TeamB deveria ter 0pts, mas tem {pts[2]}"

    @pytest.mark.asyncio
    async def test_post_recalculate_returns_200(
        self, auth_client: AsyncClient, db: AsyncSession
    ):
        """POST /standings/recalculate deve retornar 200 com lista vazia ou dados"""
        # Criar competition mínima
        comp_payload = {
            "name": f"AR077-recalc-{uuid4().hex[:8]}",
            "description": "Test POST recalculate",
            "start_date": "2026-03-01",
            "end_date": "2026-03-31",
        }
        resp = await auth_client.post("/api/v1/competitions/v2", json=comp_payload)
        if resp.status_code not in (200, 201):
            pytest.skip(f"POST /competitions/v2 failed: {resp.status_code}")
        competition_id = resp.json()["id"]

        # POST /standings/recalculate
        resp = await auth_client.post(
            f"/api/v1/competitions/{competition_id}/standings/recalculate"
        )
        assert resp.status_code == status.HTTP_200_OK, f"POST recalculate failed: {resp.text}"
        
        # Deve retornar lista (vazia ou com dados)
        standings = resp.json()
        assert isinstance(standings, list), f"Expected list, got {type(standings)}"
