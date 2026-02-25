#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests — CompetitionStandingsService.compute_points()

OBJETIVO:
- Validar cálculo de pontos com regras dinâmicas (INV-COMP-008)
- Provar ausência de valores hardcoded (test_dynamic_rules_isolation)
- Testar cenários: round-robin, custom rules, edge cases

NOTA: recalculate_standings() requer integration tests (DB async).
Este arquivo testa apenas compute_points() (método estático puro).
"""
import pytest
from app.services.competition_standings_service import CompetitionStandingsService as CSS


class TestCompetitionStandingsServiceComputePoints:
    """
    Testes unitários para CompetitionStandingsService.compute_points()
    
    INVARIANTE INV-COMP-008:
    - compute_points() DEVE usar parâmetros recebidos (não hardcoded)
    - test_dynamic_rules_isolation prova isso: ppw=3 → resultado ≠ ppw=2
    """

    def test_three_match_scenario_default_handball_rules(self):
        """
        Cenário round-robin 3 equipes com regras handebol padrão (ppw=2, ppd=1, ppl=0).
        
        Partidas:
        - M1: TeamA 3x1 TeamB → TeamA: 1W, TeamB: 1L
        - M2: TeamA 2x2 TeamC → TeamA: 1D, TeamC: 1D
        - M3: TeamB 4x0 TeamC → TeamB: 1W, TeamC: 1L
        
        Classificação esperada:
        - TeamA (1W, 1D, 0L): 2*1 + 1*1 + 0*0 = 3 pts
        - TeamB (1W, 0D, 1L): 2*1 + 1*0 + 0*1 = 2 pts
        - TeamC (0W, 1D, 1L): 2*0 + 1*1 + 0*1 = 1 pt
        """
        # Handebol padrão: ppw=2, ppd=1, ppl=0
        ppw, ppd, ppl = 2, 1, 0
        
        # TeamA: 1 vitória, 1 empate, 0 derrotas
        teamA_pts = CSS.compute_points(1, 1, 0, ppw, ppd, ppl)
        assert teamA_pts == 3, f"TeamA deveria ter 3pts, obteve {teamA_pts}"
        
        # TeamB: 1 vitória, 0 empates, 1 derrota
        teamB_pts = CSS.compute_points(1, 0, 1, ppw, ppd, ppl)
        assert teamB_pts == 2, f"TeamB deveria ter 2pts, obteve {teamB_pts}"
        
        # TeamC: 0 vitórias, 1 empate, 1 derrota
        teamC_pts = CSS.compute_points(0, 1, 1, ppw, ppd, ppl)
        assert teamC_pts == 1, f"TeamC deveria ter 1pt, obteve {teamC_pts}"

    def test_dynamic_rules_isolation(self):
        """
        TESTE CRÍTICO (INV-COMP-008): Prova ausência de valores hardcoded.
        
        Se compute_points() tivesse ppw=2 hardcoded, este teste FALHARIA.
        
        Mesmo cenário do teste anterior, mas com ppw=3 (futebol-like):
        - TeamA (1W, 1D, 0L): 3*1 + 1*1 + 0*0 = 4 pts (NÃO 3 pts como em ppw=2)
        
        assert dyn==4 prova que o método usa o parâmetro ppw recebido,
        não um valor hardcoded.
        """
        # Regras customizadas: ppw=3 (futebol), ppd=1, ppl=0
        ppw_custom = 3
        ppd = 1
        ppl = 0
        
        # TeamA: 1 vitória, 1 empate, 0 derrotas
        teamA_pts_custom = CSS.compute_points(1, 1, 0, ppw_custom, ppd, ppl)
        
        # Com ppw=3, resultado DEVE ser 4 (não 3)
        assert teamA_pts_custom == 4, (
            f"INV-COMP-008 VIOLATION: ppw=3 deveria gerar 4pts, "
            f"obteve {teamA_pts_custom} (hardcoded ppw=2?)"
        )

    def test_compute_points_custom_rules(self):
        """
        Testa cálculo com regras customizadas (ppw=3, ppd=1, ppl=0).
        
        Valida que o método funciona corretamente com qualquer combinação
        de parâmetros, não apenas valores padrão de handebol.
        """
        # Futebol: ppw=3, ppd=1, ppl=0
        ppw, ppd, ppl = 3, 1, 0
        
        # 1 vitória, 1 empate, 0 derrotas = 3 + 1 = 4 pts
        result = CSS.compute_points(1, 1, 0, ppw, ppd, ppl)
        assert result == 4, f"Esperado 4pts (3+1), obteve {result}"
        
        # 2 vitórias, 1 empate, 1 derrota = 6 + 1 = 7 pts
        result2 = CSS.compute_points(2, 1, 1, ppw, ppd, ppl)
        assert result2 == 7, f"Esperado 7pts (6+1), obteve {result2}"

    def test_compute_points_all_wins(self):
        """
        Edge case: Equipe com apenas vitórias (handebol padrão).
        
        5 vitórias, 0 empates, 0 derrotas → 5 * 2 = 10 pts
        """
        ppw, ppd, ppl = 2, 1, 0
        
        result = CSS.compute_points(5, 0, 0, ppw, ppd, ppl)
        assert result == 10, f"Esperado 10pts (5*2), obteve {result}"

    def test_compute_points_zero_games(self):
        """
        Edge case: Equipe sem jogos (0 vitórias, 0 empates, 0 derrotas).
        
        Deve retornar 0 pts.
        """
        ppw, ppd, ppl = 2, 1, 0
        
        result = CSS.compute_points(0, 0, 0, ppw, ppd, ppl)
        assert result == 0, f"Esperado 0pts, obteve {result}"

    def test_compute_points_all_losses(self):
        """
        Edge case: Equipe com apenas derrotas (ppl=0 → 0 pts).
        
        0 vitórias, 0 empates, 5 derrotas → 0 pts (com ppl=0)
        """
        ppw, ppd, ppl = 2, 1, 0
        
        result = CSS.compute_points(0, 0, 5, ppw, ppd, ppl)
        assert result == 0, f"Esperado 0pts, obteve {result}"

    def test_compute_points_all_draws(self):
        """
        Edge case: Equipe com apenas empates.
        
        0 vitórias, 4 empates, 0 derrotas → 4 * 1 = 4 pts
        """
        ppw, ppd, ppl = 2, 1, 0
        
        result = CSS.compute_points(0, 4, 0, ppw, ppd, ppl)
        assert result == 4, f"Esperado 4pts (4*1), obteve {result}"

    def test_compute_points_with_loss_penalty(self):
        """
        Testa sistema com penalidade por derrota (ppl < 0).
        
        Alguns esportes não-convencionais podem usar ppl=-1.
        3 vitórias, 1 empate, 2 derrotas → 6 + 1 + (-2) = 5 pts
        """
        ppw, ppd, ppl = 2, 1, -1
        
        result = CSS.compute_points(3, 1, 2, ppw, ppd, ppl)
        assert result == 5, f"Esperado 5pts (6+1-2), obteve {result}"
