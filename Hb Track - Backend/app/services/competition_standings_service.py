#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Competition Standings Service — Cálculo e Atualização de Classificações

INVARIANTES RESPEITADAS:
- INV-COMP-008 (dynamic_scoring_rules): MUST NOT hardcoded scoring values
  → compute_points() recebe ppw/ppd/ppl como parâmetros (sem defaults)
  → recalculate_standings() busca ppw/ppd/ppl via SELECT competition
- INV-COMP-005: Preserva team_id ao upsert standings (FK SET NULL)
- INV-COMP-006: Filtra deleted_at IS NULL em competition_matches
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select, and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.competition import Competition
from app.models.competition_match import CompetitionMatch
from app.models.competition_standing import CompetitionStanding
from app.core.exceptions import NotFoundError


class CompetitionStandingsService:
    """
    Serviço de classificação de competições com regras de pontuação dinâmicas.
    
    REGRA MANDATÓRIA (INV-COMP-008):
    - Valores de pontuação (ppw/ppd/ppl) NUNCA são hardcoded
    - Sempre carregados via SELECT da competition específica
    - compute_points() recebe parâmetros obrigatórios (sem defaults)
    """

    @staticmethod
    def compute_points(
        wins: int,
        draws: int,
        losses: int,
        points_per_win: int,
        points_per_draw: int,
        points_per_loss: int
    ) -> int:
        """
        Calcula pontuação total baseado em vitórias, empates e derrotas.
        
        IMPORTANTE (INV-COMP-008):
        - Método PURO: sem IO, sem DB, sem side effects
        - Todos os parâmetros são OBRIGATÓRIOS (sem valores default)
        - Caller DEVE fornecer ppw/ppd/ppl da competition específica
        
        REFERÊNCIA (INV-COMP-007):
        - competition.py:124-128: points_per_win DEFAULT 2 no DB (handebol padrão)
        - Mas este método NÃO assume defaults - recebe valores explicitamente
        
        Args:
            wins: Número de vitórias
            draws: Número de empates
            losses: Número de derrotas
            points_per_win: Pontos por vitória (ex: 2 para handebol, 3 para futebol)
            points_per_draw: Pontos por empate (ex: 1 para handebol)
            points_per_loss: Pontos por derrota (ex: 0 para handebol)
        
        Returns:
           int: Pontuação total calculada
        
        Examples:
            >>> # Handebol padrão: ppw=2, ppd=1, ppl=0
            >>> compute_points(wins=3, draws=1, losses=0, ppw=2, ppd=1, ppl=0)
            7
            
            >>> # Futebol: ppw=3, ppd=1, ppl=0
            >>> compute_points(wins=3, draws=1, losses=0, ppw=3, ppd=1, ppl=0)
            10
        """
        return wins * points_per_win + draws * points_per_draw + losses * points_per_loss

    async def recalculate_standings(
        self,
        competition_id: UUID,
        db: AsyncSession,
        phase_id: Optional[UUID] = None
    ) -> list[CompetitionStanding]:
        """
        Recalcula classificação de uma competição baseado em resultados de partidas.
        
        REGRA MANDATÓRIA (INV-COMP-008):
        1. SELECT competition para buscar points_per_win/draw/loss DO BANCO
        2. NÃO usar constantes ou defaults hardcoded
        3. Passar ppw/ppd/ppl explicitamente para compute_points()
        
        REGRAS DE NEGÓCIO:
        - Vitória: home_score > away_score (ou inverso para away)
        - Empate: home_score == away_score
        - Apenas partidas finalizadas (status='finished')
        - Exclui partidas com deleted_at IS NOT NULL (INV-COMP-006)
        - Preserva team_id existente ao upsert (INV-COMP-005)
        
        Args:
            competition_id: ID da competição
            db: Sessão async do SQLAlchemy
            phase_id: ID da fase (opcional - None = classificação geral)
        
        Returns:
            list[CompetitionStanding]: Lista de standings atualizada, ordenada por:
                1. points DESC
                2. goal_difference DESC
                3. goals_for DESC
        
        Raises:
            NotFoundError: Se competition_id não existe ou está deletada
        """
        # STEP 1: Buscar competition e regras de pontuação (INV-COMP-008)
        competition = await db.scalar(
            select(Competition)
            .where(
                and_(
                    Competition.id == competition_id,
                    Competition.deleted_at.is_(None)
                )
            )
        )
        
        if not competition:
            raise NotFoundError(f"Competition {competition_id} not found")
        
        # Buscar regras de pontuação DO BANCO (INV-COMP-008)
        points_per_win = competition.points_per_win
        points_per_draw = competition.points_per_draw
        points_per_loss = competition.points_per_loss
        
        # STEP 2: Buscar partidas finalizadas (INV-COMP-006: deleted_at IS NULL)
        match_filter = and_(
            CompetitionMatch.competition_id == competition_id,
            CompetitionMatch.status == 'finished',
            CompetitionMatch.deleted_at.is_(None),
            CompetitionMatch.home_score.isnot(None),
            CompetitionMatch.away_score.isnot(None)
        )
        
        if phase_id:
            match_filter = and_(match_filter, CompetitionMatch.phase_id == phase_id)
        
        matches = await db.scalars(select(CompetitionMatch).where(match_filter))
        matches_list = matches.all()
        
        # STEP 3: Agregar estatísticas por equipe
        team_stats = {}
        
        for match in matches_list:
            home_team_id = match.home_team_id
            away_team_id = match.away_team_id
            home_score = match.home_score
            away_score = match.away_score
            
            # Inicializar estatísticas se necessário
            if home_team_id not in team_stats:
                team_stats[home_team_id] = {
                    'wins': 0, 'draws': 0, 'losses': 0,
                    'goals_for': 0, 'goals_against': 0, 'played': 0
                }
            if away_team_id not in team_stats:
                team_stats[away_team_id] = {
                    'wins': 0, 'draws': 0, 'losses': 0,
                    'goals_for': 0, 'goals_against': 0, 'played': 0
                }
            
            # Atualizar estatísticas do home team
            team_stats[home_team_id]['played'] += 1
            team_stats[home_team_id]['goals_for'] += home_score
            team_stats[home_team_id]['goals_against'] += away_score
            
            if home_score > away_score:
                team_stats[home_team_id]['wins'] += 1
            elif home_score == away_score:
                team_stats[home_team_id]['draws'] += 1
            else:
                team_stats[home_team_id]['losses'] += 1
            
            # Atualizar estatísticas do away team
            team_stats[away_team_id]['played'] += 1
            team_stats[away_team_id]['goals_for'] += away_score
            team_stats[away_team_id]['goals_against'] += home_score
            
            if away_score > home_score:
                team_stats[away_team_id]['wins'] += 1
            elif away_score == home_score:
                team_stats[away_team_id]['draws'] += 1
            else:
                team_stats[away_team_id]['losses'] += 1
        
        # STEP 4: Calcular pontos usando regras dinâmicas (INV-COMP-008)
        standings_data = []
        for team_id, stats in team_stats.items():
            points = self.compute_points(
                wins=stats['wins'],
                draws=stats['draws'],
                losses=stats['losses'],
                points_per_win=points_per_win,
                points_per_draw=points_per_draw,
                points_per_loss=points_per_loss
            )
            
            goal_difference = stats['goals_for'] - stats['goals_against']
            
            standings_data.append({
                'team_id': team_id,
                'points': points,
                'played': stats['played'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_difference': goal_difference
            })
        
        # STEP 5: Ordenar por critérios de desempate
        standings_data.sort(
            key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
            reverse=True
        )
        
        # STEP 6: Upsert standings com position atualizada
        updated_standings = []
        for position, data in enumerate(standings_data, start=1):
            # Buscar standing existente
            existing = await db.scalar(
                select(CompetitionStanding).where(
                    and_(
                        CompetitionStanding.competition_id == competition_id,
                        CompetitionStanding.opponent_team_id == data['team_id'],
                        CompetitionStanding.phase_id == phase_id if phase_id else CompetitionStanding.phase_id.is_(None)
                    )
                )
            )
            
            if existing:
                # Update preservando team_id (INV-COMP-005)
                existing.points = data['points']
                existing.played = data['played']
                existing.wins = data['wins']
                existing.draws = data['draws']
                existing.losses = data['losses']
                existing.goals_for = data['goals_for']
                existing.goals_against = data['goals_against']
                existing.goal_difference = data['goal_difference']
                existing.position = position
                updated_standings.append(existing)
            else:
                # Insert novo standing
                new_standing = CompetitionStanding(
                    competition_id=competition_id,
                    phase_id=phase_id,
                    opponent_team_id=data['team_id'],
                    team_id=data['team_id'],  # Inicializa com team_id
                    points=data['points'],
                    played=data['played'],
                    wins=data['wins'],
                    draws=data['draws'],
                    losses=data['losses'],
                    goals_for=data['goals_for'],
                    goals_against=data['goals_against'],
                    goal_difference=data['goal_difference'],
                    position=position
                )
                db.add(new_standing)
                updated_standings.append(new_standing)
        
        await db.commit()
        
        # STEP 7: Retornar standings atualizada
        return updated_standings
